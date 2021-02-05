from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
import sys

from command import parse_command, commands
from messenger import Messenger
from person import Person
import global_constants as GC


# Global constants
PORT = 8800
IP_ADDR = "localhost"
MAX_USERS = 2

# Global variables
'''
active_users = {}
active_users_lock = Lock()

registered_users = {}
registered_users_lock = Lock()
'''

class Server(Messenger):
    def __init__(self, addr: str, port: int, max_users: int):
        """Sets up TCP socket and start listening on addr and port.

        Args:
            addr (str): IPv4-address.
            port (int): port number.
            max_users (int): maximum ongoing connections.
        """
        Messenger.__init__(self)
        try:
            self.listen_socket = socket(AF_INET, SOCK_STREAM)
            self.listen_socket.bind((addr, port))
            self.listen_socket.listen(max_users)

            #self.messages = []
            self.active_users = {}
            self.active_users_lock = Lock()

            self.registered_users = {}
            self.registered_users_lock = Lock()
        except Exception as e:
            print("[Exception] Could not initiate server: ", e)
            sys.exit(GC.EXIT_FAILURE)


    def login(self, person: Person):
        """Handles login and register for a client. Should work threaded
            TODO: active_users value should not be password, but (user_ip, user_port)
        Args:
            client_socket (socket): The client to register/login

        Returns:
            bool: True if logged in, else False
        """
        while True:
            msg = self.receive_msg(person.connection)
            cmd, args = parse_command(msg)

            if cmd == commands.LOGIN:
                username = args[0]
                passw = args[1]

                self.registered_users_lock.acquire()
                self.active_users_lock.acquire()
                if username in self.registered_users and self.registered_users[username] == passw and not username in self.active_users:
                    # User is valid
                    person.set_login(username, passw, (args[2], args[3]))
                    self.active_users[username] = person
                    self.send_msg(person.connection, GC.LOGIN_SUCCESS)

                    self.active_users_lock.release()
                    self.registered_users_lock.release()
                    return True
                # User not valid
                self.send_msg(person.connection, GC.LOGIN_FAILURE)

                self.active_users_lock.release()
                self.registered_users_lock.release()
                #return False

            elif cmd == commands.REGISTER:
                username = args[0]
                passw = args[1]

                self.registered_users_lock.acquire()
                if not (username in self.registered_users):
                    # User not already registred
                    person.set_login(username, passw, (args[2], args[3]))

                    self.registered_users[username] = passw
                    self.active_users_lock.acquire()
                    self.active_users[username] = person
                    self.active_users_lock.release()
                    self.registered_users_lock.release()

                    self.send_msg(person.connection, GC.REGISTER_SUCCESS)
                    return True
                # User already in register
                self.send_msg(person.connection, GC.REGISTER_FAILURE)
                self.registered_users_lock.release()
                #return False

            elif cmd == commands.CLOSE:
                return False

            else:
                # Invalid command
                self.send_msg(person.connection, GC.LOGIN_INV_COMMAND)


    def handle_connection(self, person: Person):
        """Handles connection for a client (used threaded for each user)

        Raises:
            NotImplementedError: [description]
        """
        ongoing_connection = True
        while ongoing_connection and self.login(person):
            print(f"User {person.connection.getpeername()} logged in")
            print(self.registered_users)

            running = True
            while running:
                msg = self.receive_msg(person.connection)
                cmd, args = parse_command(msg)

                if cmd == commands.LOOKUP:
                    if not len(args):
                        # lookup all active users
                        self.active_users_lock.acquire()
                        self.send_msg(person.connection, f">> {len(self.active_users)} user(s) online. The list follows:")
                        for user in self.active_users.values():
                            msg = f">> {user.username} is online:\n"
                            msg = msg + f">> IP: {user.listen_addr[0]}\n"
                            msg = msg + f">> Port: {user.listen_addr[1]}"
                            self.send_msg(person.connection, msg)
                            #send_msg(person.connection, f">> {user.username} is online:")
                            #send_msg(person.connection, f">> IP: {user.listen_addr[0]}")
                            #send_msg(person.connection, f">> Port: {user.listen_addr[1]}")
                        self.active_users_lock.release()
                    else:
                        # Lookup user in args[0] (also check whether user found)
                        print("Looking up one user")
                        self.active_users_lock.acquire()
                        user = self.active_users.get(args[0])
                        self.active_users_lock.release()

                        if user:
                            self.send_msg(person.connection, f">> {user.username} is online:")
                            self.send_msg(person.connection, f">> IP: {user.listen_addr[0]}")
                            self.send_msg(person.connection, f">> Port: {user.listen_addr[1]}")
                        else:
                            self.send_msg(person.connection, f">> {args[0]} is not online (or username invalid)")
                    print("sending lookup done")
                    self.send_msg(person.connection, GC.LOOKUP_DONE)

                elif cmd == commands.LOGOUT:
                    try:
                        self.active_users_lock.acquire()
                        self.active_users.pop(person.username)
                        self.send_msg(person.connection, GC.LOGOUT_SUCCESS)
                        running = False
                    except KeyError as e:
                        print("[EXCEPTION] Could not remove user: ", e)
                        self.send_msg(person.connection, GC.LOGOUT_FAILURE)
                    finally:
                        self.active_users_lock.release()

                elif cmd == commands.MSG:
                    raise NotImplementedError

                elif cmd == commands.SHOW:
                    raise NotImplementedError

                elif cmd == commands.CLOSE:
                    running = False
                    ongoing_connection = False

                else:
                    # Invalid command
                    self.send_msg(person.connection, GC.LOGGEDIN_INV_COMMAND)

        # Client is done using the server
        print(f"Closing down user {person.connection.getpeername()}")
        person.connection.close()

if __name__ == "__main__":
    print("server turned on.")
    server = Server(IP_ADDR, PORT, MAX_USERS)
    print("Server listening for connections.")
    running = True
    while running:
        try:
            conn, addr = server.listen_socket.accept()
            person = Person(conn)
            print(f"User {addr} connected to server.")
            thread = Thread(target=server.handle_connection, args=(person,))
            thread.start()
        except Exception as e:
            print("[EXCEPTION] ", e)
            break
'''
if __name__ == "__main__":
    print("server turned on.")
    s = server_init(IP_ADDR, PORT, MAX_USERS)
    print("Server listening for connections.")
    running = True
    while running:
        try:
            conn, addr = s.accept()
            person = Person(conn)
            print(f"User {addr} connected to server.")
            # Might have to give a copy of conn to the thread.
            thread = Thread(target=handle_connection, args=(person,))
            thread.start()
        except Exception as e:
            print("[EXCEPTION] ", e)
            break
'''