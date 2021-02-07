from common.command import parse_command, commands

def test_parse_command():
    ########## TEST FOR PARSE_COMMAND ###########
    print("TESTING PARSE_COMMAND:")
    ### CONNECT
    command = "connect"
    arg0 = "ip"
    arg1 = "port"
    cmd, args = parse_command(f"/{command} {arg0} {arg1}")

    res = (cmd == commands.CONNECT and len(args) == 2)
    res = res and (args[0] == arg0 and args[1] == arg1)

    print("   %s: %s command" %(res, command))


    ### LOGIN
    command = "login"
    arg0 = "usrname"
    arg1 = "passw"
    arg2 = "ip_address"
    arg3 = "port"
    cmd, args = parse_command(f"/{command} {arg0} {arg1} {arg2} {arg3}")

    res = (cmd == commands.LOGIN and len(args) == 4)
    res = res and (args[0] == arg0 and args[1] == arg1)
    res = res and (args[2] == arg2 and args[3] == arg3)

    print("   %s: %s command" %(res, command))


    ### REGISTER
    command = "register"
    arg0 = "usrname"
    arg1 = "passw"
    arg2 = "ip_address"
    arg3 = "port"
    cmd, args = parse_command(f"/{command} {arg0} {arg1} {arg2} {arg3}")

    res = (cmd == commands.REGISTER and len(args) == 4)
    res = res and (args[0] == arg0 and args[1] == arg1)
    res = res and (args[2] == arg2 and args[3] == arg3)

    print("   %s: %s command" %(res, command))


    ### LOGOUT
    command = "logout"
    cmd, args = parse_command(f"/{command}")

    res = (cmd == commands.LOGOUT and len(args) == 0)

    print("   %s: %s command" %(res, command))


    ### CLOSE
    command = "close"
    cmd, args = parse_command(f"/{command}")

    res = (cmd == commands.CLOSE and len(args) == 0)

    print("   %s: %s command" %(res, command))


    ### LOOKUP
    command = "lookup"
    cmd, args = parse_command(f"/{command}")

    res = (cmd == commands.LOOKUP and len(args) == 0)

    print("   %s: %s command(argn=0)" %(res, command))

    command = "lookup"
    arg0 = "usrname"
    cmd, args = parse_command(f"/{command} {arg0}")

    res = (cmd == commands.LOOKUP and len(args) == 1)
    res = res and (args[0] == arg0)

    print("   %s: %s command(argn=1)" %(res, command))


    ### MSG
    command = "msg"
    arg0 = "nickname"
    arg1 = "Pua is the best in the world!"
    cmd, args = parse_command(f"/{command} {arg0} {arg1}")

    res = (cmd == commands.MSG and len(args) == 2)
    res = res and (args[0] == arg0 and args[1] == arg1)

    print("   %s: %s command" %(res, command))


    ### SHOW
    command = "show"
    cmd, args = parse_command(f"/{command}")

    res = (cmd == commands.SHOW and len(args) == 0)

    print("   %s: %s command(argn=0)" %(res, command))

    command = "show"
    arg0 = "nickname"
    cmd, args = parse_command(f"/{command} {arg0}")

    res = (cmd == commands.SHOW and len(args) == 1)
    res = res and (args[0] == arg0)

    print("   %s: %s command(argn=1)" %(res, command))


    ### ERROR
    command = "register"
    cmd, args = parse_command(f"/{command} wrong number of inputs here")

    res = (cmd == commands.ERROR and len(args) == 0)

    print("   %s: error command" %res)

test_parse_command()