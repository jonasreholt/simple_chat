from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from command import parse_command, commands
import global_constants as GC
import sys

# Global constants
PORT = 5500
IP_ADDR = "localhost"
MAX_USERS = 2

# Global variables
active_users = {}
active_users_lock = Lock()

registered_users = {"jonas" : "hej"}
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
        sys.exit(GC.EXIT_FAILURE)

def message(s: socket, msg: str):
    try:
        s.sendall(bytes(msg, GC.ENCODING))
    except Exception as e:
        print("[EXCEPTION] Could not send message: ", e)

def login(client_socket: socket):
    while True:
        msg = client_socket.recv(GC.BUFFSIZE).decode()
        cmd, args = parse_command(msg)

        if cmd == commands.LOGIN:
            username = args[0]
            passw = args[1]

            registered_users_lock.acquire()
            active_users_lock.acquire()
            if username in registered_users and registered_users[username] == passw and not username in active_users:
                # User is valid
                active_users[username] = passw
                message(client_socket, GC.LOGIN_SUCCESS)

                active_users_lock.release()
                registered_users_lock.release()
                return True
            else:
                # User not valid
                message(client_socket, GC.LOGIN_FAILURE)

                active_users_lock.release()
                registered_users_lock.release()
                return False

        elif cmd == commands.REGISTER:
            username = args[0]
            passw = args[1]

            registered_users_lock.acquire()
            if not (username in registered_users):
                # User not already registred
                registered_users[username] = passw
                active_users_lock.acquire()
                active_users[username] = passw # This should be (user_ip, user_port)
                active_users_lock.release()
                registered_users_lock.release()
                return True
            # User already in register
            message(client_socket, GC.REGISTER_FAILURE)
            registered_users_lock.release()
            return False

        elif cmd == commands.CLOSE:
            return False

        else:
            # Invalid command
            message(client_socket, GC.LOGIN_INV_COMMAND)

def handle_connection(client_socket: socket):
    """Handles connection for a client (used threaded for each user)

    Raises:
        NotImplementedError: [description]
    """
    if login(client_socket):
        # Handle connection
        print(f"User {client_socket.getpeername()} logged in")
        print(registered_users)
        raise NotImplementedError
    # Client is done using the server
    print(f"Closing down user {client_socket.getpeername()}")
    client_socket.close()


if __name__ == "__main__":
    print("server turned on.")
    s = server_init(IP_ADDR, PORT, MAX_USERS)
    print("Server listening for connections.")
    running = True
    while running:
        conn, addr = s.accept()
        print(f"User {addr} connected to server.")
        # Might have to give a copy of conn to the thread.
        thread = Thread(target=handle_connection, args=(conn,))
        thread.start()
    