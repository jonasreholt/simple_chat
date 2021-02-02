from socket import socket, SOCK_STREAM, AF_INET
from command import commands
import global_constants as GV


class Client:
    def __init__(self):
        try:
            self.name_server = socket(AF_INET, SOCK_STREAM)
        except Exception as e:
            print(">> Could not open socket: ", e)
        self.connected = False
        self.logged_in = False

    def communicate(self, msg: bytes):
        try:
            self.name_server.sendall(msg)
        except Exception as e:
            self.connect(self.name_server_addr)
            print(e)

    def recieve_msg(self):
        try:
            return self.name_server.recv(GV.BUFFSIZE).decode()
        except Exception as e:
            print(">> Could not recieve message: ", e)
            return ""

    def connect(self, server_addr: (str, int)):
        if self.connected:
            print(">> You are already connected")

        try:
            self.name_server_addr = server_addr
            self.name_server.connect(server_addr)
            self.connected = True
            print(f">> Connected to name server {server_addr}")
        except Exception as e:
            print(">> Could not connect to socket: ", e)

    def login(self, username: str, passw: str, my_addr: (str, int)):
        if self.logged_in or not self.connected:
            print(f">> Could not log in; you are connected:{self.connected}; you are logged in:{self.logged_in}")

        msg = bytes(f"/login {username} {passw} {my_addr[0]} {my_addr[1]}", GV.ENCODING)
        self.communicate(msg)
        if self.recieve_msg() == GV.LOGIN_SUCCESS:
            self.username = username
            self.password = passw
            self.my_addr = my_addr
            self.logged_in = True
            print(">> Logged in to name server.")
        else:
            print(">> Could not log in to name server.")

    def register(self, username: str, passw: str, my_addr: (str, int)):
        if self.logged_in or not self.connected:
            print(f">> Could not log in; you are connected:{self.connected}; you are logged in:{self.logged_in}")

        msg = bytes(f"/register {username} {passw} {my_addr[0]} {my_addr[1]}", GV.ENCODING)
        self.communicate(msg)
        if self.recieve_msg() == GV.REGISTER_SUCCESS:
            self.username = username
            self.password = passw
            self.my_addr = my_addr
            self.logged_in = True
            print(">> Succesfully registred and logged in to name server.")
        else:
            print(">> Could not register to name server.")

    def logout(self):
        if not self.logged_in:
            print(">> You are not logged in")

        msg = bytes(f"/logout", GV.ENCODING)
        self.communicate(msg)
        if self.recieve_msg() == GV.LOGOUT_SUCCESS:
            self.logged_in = False
            print(">> Succesfully logged out.")
        else:
            print(">> Could not log out of server.")

    def close(self):
        if self.logged_in or self.connected:
            # Logging out of server before closing
            if self.logout() == GV.EXIT_FAILURE:
                return GV.EXIT_FAILURE

        try:
            self.name_server.close()
            self.connected = False
            print(">> Closing program.")
            return GV.EXIT_SUCCESS
        except Exception as e:
            print(">> Could not close connection: ", e)
            return GV.EXIT_FAILURE

