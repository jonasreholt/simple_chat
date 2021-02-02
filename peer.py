from client import Client
from command import parse_command, commands
import global_constants as GC

def close_wrapper(elm: list, client: Client):
    elm[0] = False if client.close() else True

def login_wrapper(args: list, client: Client):
    client.login(args[0], args[1], (args[2], int(args[3])))

def peer_app():
    client = Client()
    running = [True]

    while running:
        user_input = input(">> Enter command: ")
        if not user_input: # Input empty line or EOF
            continue
        cmd, args = parse_command(user_input)

        switcher = {
            # Problem med at den fuldfører kaldet client.login på trods af
            # at det ikke er den, som bliver kaldt get på. Wrapper virker ikke
            commands.CONNECT: client.connect((args[0], int(args[1]))),
            commands.LOGIN: login_wrapper(args, client),
            commands.REGISTER: client.register(args[0], args[1], (args[2], int(args[3]))),
            commands.LOGOUT: client.logout(),
            commands.CLOSE: close_wrapper(running, client),
            commands.ERROR: print(">> Invalid command.")
        }
        try:
            switcher.get(cmd, print("[ERROR] peer switcher missing command."))
        except ValueError as e:
            print(">> port was not a decimal value: ", e)

peer_app()