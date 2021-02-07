from socket import socket
from typing import Tuple

class Person:
    def __init__(self, conn: socket):
        self.connection = conn

    def set_login(self, username: str, passw: str, listen_addr: Tuple[str, int]):
        self.username = username
        self.passw = passw
        self.listen_addr = listen_addr