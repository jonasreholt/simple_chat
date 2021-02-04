from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
import sys

from command import parse_command, commands
from person import Person
import global_constants as GC


# Global constants
PORT = 8800
IP_ADDR = "localhost"
MAX_USERS = 2

# Global variables
active_users = {}
active_users_lock = Lock()

registered_users = {}
registered_users_lock = Lock()


def server_init(addr : str, port : int, max_users : int):
    """Sets up TCP socket and start listening on addr and port.

    Args:
        addr (str): IPv4-address.
        port (int): port number.
        max_users (int): maximum ongoing connections.

    Returns:
        socket: server socket.
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
    """Sends msg encoded as utf-8 to socket s.

    Args:
        s (socket): socket to retrieve msg.
        msg (str): message to encode and form bytes for sending to s.
    """
    try:
        s.sendall(bytes(msg, GC.ENCODING))
    except Exception as e:
        print("[EXCEPTION] Could not send message: ", e)


def recieve_msg(client_socket: socket):
    try:
        return client_socket.recv(GC.BUFFSIZE).decode()
    except Exception as e:
        print("client timed out: ", e)
        return ""


def login(person: Person):
    """Handles login and register for a client. Should work threaded
        TODO: active_users value should not be password, but (user_ip, user_port)
    Args:
        client_socket (socket): The client to register/login

    Returns:
        bool: True if logged in, else False
    """
    while True:
        msg = recieve_msg(person.connection)
        cmd, args = parse_command(msg)

        if cmd == commands.LOGIN:
            username = args[0]
            passw = args[1]

            registered_users_lock.acquire()
            active_users_lock.acquire()
            if username in registered_users and registered_users[username] == passw and not username in active_users:
                # User is valid
                person.set_login(username, passw, (args[2], args[3]))
                active_users[username] = person
                message(person.connection, GC.LOGIN_SUCCESS)

                active_users_lock.release()
                registered_users_lock.release()
                return True
            # User not valid
            message(person.connection, GC.LOGIN_FAILURE)

            active_users_lock.release()
            registered_users_lock.release()
            #return False

        elif cmd == commands.REGISTER:
            username = args[0]
            passw = args[1]

            registered_users_lock.acquire()
            if not (username in registered_users):
                # User not already registred
                person.set_login(username, passw, (args[2], args[3]))

                registered_users[username] = passw
                active_users_lock.acquire()
                active_users[username] = person
                active_users_lock.release()
                registered_users_lock.release()

                message(person.connection, GC.REGISTER_SUCCESS)
                return True
            # User already in register
            message(person.connection, GC.REGISTER_FAILURE)
            registered_users_lock.release()
            #return False

        elif cmd == commands.CLOSE:
            return False

        else:
            # Invalid command
            message(person.connection, GC.LOGIN_INV_COMMAND)


def handle_connection(person: Person):
    """Handles connection for a client (used threaded for each user)

    Raises:
        NotImplementedError: [description]
    """
    ongoing_connection = True
    while ongoing_connection and login(person):
    #if login(person):
        # Handle connection
        print(f"User {person.connection.getpeername()} logged in")
        print(registered_users)

        running = True
        while running:
            msg = recieve_msg(person.connection)
            cmd, args = parse_command(msg)

            if cmd == commands.LOOKUP:
                raise NotImplementedError

            elif cmd == commands.LOGOUT:
                try:
                    active_users_lock.acquire()
                    active_users.pop(person.username)
                    message(person.connection, GC.LOGOUT_SUCCESS)
                    running = False
                except KeyError as e:
                    print("[EXCEPTION] Could not remove user: ", e)
                    message(person.connection, GC.LOGOUT_FAILURE)
                finally:
                    active_users_lock.release()

            elif cmd == commands.MSG:
                raise NotImplementedError

            elif cmd == commands.SHOW:
                raise NotImplementedError

            elif cmd == commands.CLOSE:
                running = False
                ongoing_connection = False

            else:
                # Invalid command
                message(person.connection, GC.LOGGEDIN_INV_COMMAND)

    # Client is done using the server
    print(f"Closing down user {person.connection.getpeername()}")
    person.connection.close()


if __name__ == "__main__":
    print("server turned on.")
    s = server_init(IP_ADDR, PORT, MAX_USERS)
    print("Server listening for connections.")
    running = True
    while running:
        conn, addr = s.accept()
        person = Person(conn)
        print(f"User {addr} connected to server.")
        # Might have to give a copy of conn to the thread.
        thread = Thread(target=handle_connection, args=(person,))
        thread.start()
    