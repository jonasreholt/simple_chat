from socket import socket, SOCK_STREAM, AF_INET
from command import commands
from messenger import Messenger
import global_constants as GC
from typing import Tuple


class Client(Messenger):
    def __init__(self):
        Messenger.__init__(self)
        try:
            self.name_server = socket(AF_INET, SOCK_STREAM)
        except Exception as e:
            print(">> Could not open socket: ", e)
        self.connected = False
        self.logged_in = False
        #self.messages = []


    def connect(self, server_addr: Tuple[str, int]):
        """Connects to a name server.

        Args:
            server_addr (str, int): (IP-address, port)
        """
        if self.connected:
            print(">> You are already connected")
        else:
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
        """
        if self.logged_in or not self.connected:
            print(f">> Could not log in; you are connected:{self.connected}; you are logged in:{self.logged_in}")
        else:
            self.send_msg(self.name_server, f"/login {username} {passw} {my_addr[0]} {my_addr[1]}")
            if self.receive_msg(self.name_server) == GC.LOGIN_SUCCESS:
                self.username = username
                self.password = passw
                self.my_addr = my_addr
                self.logged_in = True
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
        """
        if self.logged_in or not self.connected:
            print(f">> Could not log in; you are connected:{self.connected}; you are logged in:{self.logged_in}")
        else:
            self.send_msg(self.name_server, f"/register {username} {passw} {my_addr[0]} {my_addr[1]}")
            if self.receive_msg(self.name_server) == GC.REGISTER_SUCCESS:
                self.username = username
                self.password = passw
                self.my_addr = my_addr
                self.logged_in = True
                print(">> Succesfully registred and logged in to name server.")
            else:
                print(">> Could not register to name server.")


    def logout(self):
        """Tries to logout of self.name_server.
        """
        if not self.logged_in:
            print(">> You are not logged in")
            return GC.EXIT_FAILURE

        self.send_msg(self.name_server, "/logout")
        if self.receive_msg(self.name_server) == GC.LOGOUT_SUCCESS:
            self.logged_in = False
            print(">> Succesfully logged out.")
            return GC.EXIT_SUCCESS
        print(">> Could not log out of server.")
        return GC.EXIT_FAILURE


    def lookup(self, nickname: str):
        if not self.logged_in or not self.connected:
            print(f">> Could not lookup; you are connected:{self.connected}; you are logged in:{self.logged_in}")
        else:
            self.send_msg(self.name_server, "/lookup " + nickname)

            while True:
                msg = self.receive_msg(self.name_server)
                if msg == GC.LOOKUP_DONE or not msg:
                    break
                print(msg)


    def close(self):
        """Tries to close connection with self.name_server.

        Returns:
            int: 1 for success, and 0 for failure.
        """
        if self.logged_in and not self.logout():
            return GC.EXIT_FAILURE

        if self.connected:
            try:
                self.send_msg(self.name_server, "/close")
                self.name_server.close()
                self.connected = False
                print(">> Closing program.")
                return GC.EXIT_SUCCESS
            except Exception as e:
                print(">> Could not close connection: ", e)
                return GC.EXIT_FAILURE