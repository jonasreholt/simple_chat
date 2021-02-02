from client import Client
from command import parse_command, commands
import global_constants as GC

def connect_wrapper(args: list, client: Client):
    client.connect((args[0], int(args[1])))

def login_wrapper(args: list, client: Client):
    client.login(args[0], args[1], (args[2], int(args[3])))

def register_wrapper(args: list, client: Client):
    client.register(args[0], args[1], (args[2], int(args[3])))

def logout_wrapper(args: list, client: Client):
    # Arguments are included to match the wrapper pattern
    client.logout()

def error_wrapper(args: list, client: Client):
    # Arguments are included to match the wrapper pattern
    print(">> Invalid command")


def peer_app():
    """Handles the peer application side through the command-line.
    """
    client = Client()
    running = True

    while running:
        user_input = input(">> Enter command: ")
        if not user_input: # Input empty line or EOF
            continue
        cmd, args = parse_command(user_input)

        switcher = {
            commands.CONNECT: connect_wrapper,
            commands.LOGIN: login_wrapper,
            commands.REGISTER: register_wrapper,
            commands.LOGOUT: logout_wrapper,
            commands.ERROR: error_wrapper
        }
        try:
            if cmd == commands.CLOSE:
                running = not client.close()
            else:
                switcher[cmd](args, client)
        except ValueError as e:
            print(">> port was not a decimal value: ", e)
        except KeyError as e:
            print("[ERROR] peer switcher missing command.")


peer_app()