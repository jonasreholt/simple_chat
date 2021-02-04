from socket import socket

class Person:
    def __init__(self, conn: socket):
        self.connection = conn

    def set_login(self, username: str, passw: str, listen_addr: (str, int)):
        self.username = username
        self.passw = passw
        self.listen_addr = listen_addr