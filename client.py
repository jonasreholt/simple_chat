from socket import socket, SOCK_STREAM, AF_INET
from command import commands
import global_constants as GC


class Client:
    def __init__(self):
        try:
            self.name_server = socket(AF_INET, SOCK_STREAM)
        except Exception as e:
            print(">> Could not open socket: ", e)
        self.connected = False
        self.logged_in = False


    def communicate(self, msg: str):
        """Sends msg as utf-8 encoded bytes to self.name_server.
        (If sendall() fails on the background of lost connection,
        it tries to reconect)

        Args:
            msg (str): msg to encode and send
        """
        try:
            self.name_server.sendall(bytes(msg, GC.ENCODING))
        except Exception as e:
            self.connect(self.name_server_addr)
            print(e)


    def recieve_msg(self):
        """Waits for and retrieves message form self.name_server.

        Returns:
            str: decoded message retrieved.
        """
        try:
            return self.name_server.recv(GC.BUFFSIZE).decode()
        except Exception as e:
            print(">> Could not recieve message: ", e)
            return ""


    def connect(self, server_addr: (str, int)):
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


    def login(self, username: str, passw: str, my_addr: (str, int)):
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
            self.communicate(f"/login {username} {passw} {my_addr[0]} {my_addr[1]}")
            if self.recieve_msg() == GC.LOGIN_SUCCESS:
                self.username = username
                self.password = passw
                self.my_addr = my_addr
                self.logged_in = True
                print(">> Logged in to name server.")
            else:
                print(">> Could not log in to name server.")


    def register(self, username: str, passw: str, my_addr: (str, int)):
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
            self.communicate(f"/register {username} {passw} {my_addr[0]} {my_addr[1]}")
            if self.recieve_msg() == GC.REGISTER_SUCCESS:
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

        self.communicate("/logout")
        if self.recieve_msg() == GC.LOGOUT_SUCCESS:
            self.logged_in = False
            print(">> Succesfully logged out.")
            return GC.EXIT_SUCCESS
        print(">> Could not log out of server.")
        return GC.EXIT_FAILURE


    def close(self):
        """Tries to close connection with self.name_server.

        Returns:
            int: 1 for success, and 0 for failure.
        """
        if self.logged_in and not self.logout():
            return GC.EXIT_FAILURE

        if self.connected:
            try:
                self.communicate("/close")
                self.name_server.close()
                self.connected = False
                print(">> Closing program.")
                return GC.EXIT_SUCCESS
            except Exception as e:
                print(">> Could not close connection: ", e)
                return GC.EXIT_FAILURE