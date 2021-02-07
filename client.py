from socket import socket, SOCK_STREAM, AF_INET
from threading import Thread, Lock
from typing import Tuple
from collections import namedtuple
import sys

from common.messenger import Messenger
import common.global_constants as GC


MAX_USERS = 3

User_info = namedtuple("User_info", ["is_online", "IP", "port"])

class Client(Messenger):
    def __init__(self):
        """
        Raises:
            SystemExit: When it cannot open a socket.
        """
        Messenger.__init__(self)
        try:
            self.name_server = socket(AF_INET, SOCK_STREAM)
        except Exception as e:
            sys.exit(e)

        self.connected = False
        self.logged_in = False

        self.peer_messages = {}
        self.peer_messages_lock = Lock()


    def receive_peer_msg(self, s: socket):
        """Receives a message from a peer (The outer while-loop is
        superfluous, but there as a robustness measure, if a connection
        is made outside of the msg method).

        Args:
            s (socket): incoming connection to retreive message from.
        """
        # peer username is forcily prepended to all its messages
        private_messenger = Messenger()

        # While loop terminates if connection to peer lost, or
        # user logged out:
        while self.logged_in: # Maybe race condition?
            # TODO: Might get stuck at receive (no, cause the connection is closed down
            # immediately from senders side.)
            msg = private_messenger.receive_msg(s)
            if not msg:
                # Lost connection to peer
                break
            msg_sender = msg[:msg.find(':')]
            with self.peer_messages_lock:
                if msg_sender in self.peer_messages:
                    # Already logged messages from peer
                    self.peer_messages[msg_sender].append(msg)
                else:
                    # First contact with peer
                    self.peer_messages[msg_sender] = [msg]
        s.close()

    def receive_peer_connections(self):
        """ While client logged in, it will wait and listen for peer connections.
        It then opens a new thread, retreiving the message from the peer.
        accept() is cancelled when logged out by a local connection.
        Raises:
            SystemExit: When it cannot open listening socket, or someone failed connection.
        """
        assert(self.logged_in), ">> You are not logged in to name server"

        try:
            # Setting up listen socket
            listen_socket = socket(AF_INET, SOCK_STREAM)
            listen_socket.bind(self.my_addr)
            listen_socket.listen(MAX_USERS)
        except Exception as e:
            sys.exit(e)

        while self.logged_in: # Maybe race condition?
            try:
                conn, addr = listen_socket.accept()
                thread = Thread(target=self.receive_peer_msg, args=(conn,))
                thread.start()
            except Exception as e:
                sys.exit(e)

        listen_socket.close()


    def connect(self, server_addr: Tuple[str, int]):
        """Connects to a name server.

        Args:
            server_addr (str, int): (IP-address, port)
        
        Raises:
            AssertionError: When client is already connected.
        """
        assert(not self.connected), ">> You are already connected"

        try:
            self.name_server_addr = server_addr
            self.name_server.connect(server_addr)
            self.connected = True
            print(f">> Connected to name server {server_addr}")
        except Exception as e:
            print(">> Could not connect to socket: ", e)


    def login(self, username: str, passw: str, my_addr: Tuple[str, int]):
        """Tries to login to self.name_server.

        Args:
            username (str): username to login with.
            passw (str): password to login with.
            my_addr (str, int): (my IP-address, my port) used to confer messages
                                between peers.
        
        Raises:
            AssertionError: When client already logged in or not connected
        """
        assert(not self.logged_in and self.connected), f">> Could not log in: Either already logged in or not connected"

        self.send_msg(self.name_server, f"/login {username} {passw} {my_addr[0]} {my_addr[1]}")
        if self.receive_msg(self.name_server) == GC.LOGIN_SUCCESS:
            # Setting variables:
            self.username = username
            self.password = passw
            self.my_addr = my_addr
            self.logged_in = True

            # Starting peer channel
            thread = Thread(target=self.receive_peer_connections)
            thread.start()
            print(">> Logged in to name server.")
        else:
            print(">> Could not log in to name server.")


    def register(self, username: str, passw: str, my_addr: Tuple[str, int]):
        """Tries to register this user.

        Args:
            username (str): username to register.
            passw (str): password to register with.
            my_addr (str, int): (my IP-address, my port) used to confer messages
                                between peers.

        Raises:
            AssertionError: When client already logged in or not connected
        """
        assert(not self.logged_in and self.connected), f">> Could not register: Either already logged in or not connected"

        self.send_msg(self.name_server, f"/register {username} {passw} {my_addr[0]} {my_addr[1]}")
        if self.receive_msg(self.name_server) == GC.REGISTER_SUCCESS:
            # Setting variables
            self.username = username
            self.password = passw
            self.my_addr = my_addr
            self.logged_in = True

            # Starting peer channel
            thread = Thread(target=self.receive_peer_connections)
            thread.start()
            print(">> Succesfully registred and logged in to name server.")
        else:
            print(">> Could not register to name server.")


    def logout(self):
        """Tries to logout of self.name_server. Shuts down peer channel by a local
        connection.

        Raises:
            AssertionError: When client not logged in to name server
        """
        assert(self.logged_in), ">> You are not logged in"

        self.send_msg(self.name_server, "/logout")
        if self.receive_msg(self.name_server) == GC.LOGOUT_SUCCESS:
            self.logged_in = False
            # Also needs to communicate to peer channel, that it should no longer
            # wait in accept
            with socket(AF_INET, SOCK_STREAM) as s:
                s.connect(self.my_addr)

            print(">> Succesfully logged out.")
        else:
            print(">> Could not log out of server.")


    def lookup(self, nickname: str, printer: bool):
        """If nickname == "" looks up all online users on the name server;
        if nickname represents a user, it looks up whether the specific
        user is online.

        Args:
            nickname (str): User to lookup or ""
            printer (bool): Whether to print or return info

        Raises:
            AssertionError: If client is not logged in or connected

        Returns:
            namedtuple Userinfo: if printer == false
            None: If printer == true
        """
        retVal = User_info(False, "", -1)

        assert(self.logged_in and self.connected), ">> Could not lookup: Either not logged in or connected"

        self.send_msg(self.name_server, "/lookup " + nickname)

        while True:
            msg = self.receive_msg(self.name_server)
            if msg == GC.LOOKUP_DONE or not msg:
                break
            if printer:
                print(msg)
            else:
                # Decode information about nickname
                if f"{nickname} is online" in msg:
                    retVal = retVal._replace(is_online = True)
                elif "IP" in msg:
                    retVal = retVal._replace(IP = msg[msg.find(':')+2:])
                elif "Port" in msg:
                    retVal = retVal._replace(port = int(msg[msg.find(':')+1:]))
        return retVal if not printer else None


    def show(self, nickname: str):
        """Shows messages sent to client: If nickname == "" show messages from all;
        if nickname == "[some nick]" show message from 'some nick'.

        Args:
            nickname (str): eiter "" or a nickname of user online on the name server.

        Raises:
            AssertionError: If client is not logged in
        """
        def expression(elm: list):
            print(*elm, sep='\n')
            elm.clear()
        assert(self.logged_in), ">> Could not show messages: You ar enot logged in to name server"

        with self.peer_messages_lock:
            if nickname:
                # Print all messages from specific user
                if not nickname in self.peer_messages:
                    print(f">> No messages from {nickname} (or invalid nickname)")
                elif nickname in self.peer_messages and not self.peer_messages[nickname]:
                    print(f">> No new messages from {nickname}")
                else:
                    print(*self.peer_messages[nickname], sep='\n')
                    self.peer_messages[nickname] = []
            else:
                # Print messages from all users
                # Condition whether there are no new messages
                msg_unread = bool([elm for elm in self.peer_messages.values() if elm])
                if not msg_unread:
                    print(">> No new messages from any user.")
                else:
                    print("Messages pending:")
                    [expression(elm) for elm in self.peer_messages.values()]


    def msg(self, nickname: str, msg: str):
        """send msg to nickname; nickname must be logged in to the name server.

        Args:
            nickname (str): User to send msg to
            msg (str): Given message to send

        Raises:
            AssertionError: If client not logged in
        """
        assert(self.logged_in), ">> Could not send message: You are not logged in to name server"

        target_info = self.lookup(nickname, False)
        if not target_info.is_online:
            # Target user not logged in
            print(GC.LOOKUP_FAILED(nickname))
        else:
            # Target user is logged in:
            # Connect to target listen_socket; send message; close connection
            with socket(AF_INET, SOCK_STREAM) as s:
                s.connect((target_info.IP, target_info.port))
                self.send_msg(s, f"{self.username}: " + msg)


    def close(self):
        """Tries to close connection with self.name_server.

        Returns:
            bool: whether connection was closed successfully.
        """
        try:
            if self.logged_in:
                self.logout()
            if self.connected:
                self.send_msg(self.name_server, "/close")
                self.name_server.close()
                self.connected = False
                print(">> closing program")
                return True
        except Exception as e:
            print(">> Could not close connection: ", e)
            return False