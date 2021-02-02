from enum import Enum

class commands(Enum):
    CONNECT = 0
    LOGIN = 1
    LOGOUT = 2
    CLOSE = 3
    LOOKUP = 4
    MSG = 5
    SHOW = 6
    ERROR = 7
    REGISTER = 8

cmds = {
    ("/connect", 2) : commands.CONNECT,
    ("/login", 4) : commands.LOGIN,
    ("/logout", 0) : commands.LOGOUT,
    ("/register", 4) : commands.REGISTER,
    ("/close", 0) : commands.CLOSE,
    ("/lookup", 0) : commands.LOOKUP,
    ("/lookup", 1) : commands.LOOKUP, # number of args can be x <= 1
    ("/msg", 2) : commands.MSG,
    ("/show", 1) : commands.SHOW,
    ("/show", 0) : commands.SHOW # number of args can be x <= 1
}


def parse_command(user_input : str):
    if user_input:
        user_input = user_input.split()
        cmd = user_input[0]
        args = user_input[1::]
        argsn = len(args)
        cmd = cmds.get((cmd, argsn), commands.ERROR)
        if cmd == commands.ERROR:
            return cmd, []
        else:
            return cmd, args