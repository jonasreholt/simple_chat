from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from command import parse_command, commands
import global_constants as GV
import sys

# Global constants
PORT = 5500
IP_ADDR = "localhost"
MAX_USERS = 2

# Global variables
active_users = {}
active_users_lock = Lock()

registered_users = {}
registered_users_lock = Lock()


def server_init(addr : str, port : int, max_users : int):
    """Sets up TCP socket and start listening on addr and port

    Args:
        addr (str): IPv4-address
        port (int): port number
        max_users (int): maximum ongoing connections

    Returns:
        socket: server socket
    """
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((addr, port))
        s.listen(max_users)
        return s
    except Exception as e:
        print("[Exception] Could not initiate server: ", e)
        sys.exit(GV.EXIT_FAILURE)

def message(s: socket, msg: bytes):
    try:
        s.sendall(msg)
    except Exception as e:
        print("[EXCEPTION] Could not send message: ", e)

def login(client_socket: socket):
    while True:
        msg = client_socket.recv(GV.BUFFSIZE).decode()
        cmd, args = parse_command(msg)

        if cmd == commands.LOGIN:
            username = args[0]
            passw = args[1]

            registered_users_lock.acquire()
            active_users_lock.acquire()
            if username in registered_users and registered_users[username] == passw and not username in active_users:
                # User is valid
                active_users[username] = passw
                msg = bytes(GV.LOGIN_SUCCESS, GV.ENCODING)
                message(client_socket, msg)
            else:
                msg = bytes(GV.LOGIN_FAILURE)
                message(client_socket, msg)

            active_users_lock.release()
            registered_users_lock.release()
            return True

        elif cmd == commands.REGISTER:
            username = args[0]
            passw = args[1]

            registered_users_lock.acquire()
            if not (username in registered_users):
                # User not already registred
                registered_users[username] = passw
                active_users_lock.acquire()
                active_users[username] = passw
                active_users_lock.release()
            else:
                msg = bytes(GV.REGISTER_FAILURE)
                message(client_socket, msg)

            registered_users_lock.release()
            return True

        elif cmd == commands.CLOSE:
            return False

        else:
            # Invalid command
            msg = bytes(GV.LOGIN_INV_COMMAND, GV.ENCODING)
            try:
                client_socket.sendall(msg)
            except Exception as e:
                print("[EXCEPTION] Could not send message: ", e)

def handle_connection(client_socket: socket):
    """Handles connection for a client (used threaded for each user)

    Raises:
        NotImplementedError: [description]
    """
    if login(client_socket):
        # Handle connection
        raise NotImplementedError
    # Client is done using the server
    client_socket.close()


if __name__ == "__main__":
    print("server turned on.")
    s = server_init(IP_ADDR, PORT, MAX_USERS)
    print("Server listening for connections.")
    running = True
    while running:
        conn, addr = s.accept()
        print(f"User {addr} connected to server.")
        thread = Thread(target=handle_connection, args=(conn,))
        '''
        while 1:
            msg = conn.recv(GV.BUFFSIZE)
            if not msg:
                break
            conn.sendall(msg)
        conn.close()
        '''
    