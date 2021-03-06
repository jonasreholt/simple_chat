EXIT_SUCCESS = 1
EXIT_FAILURE = 0

BUFFSIZE = 1024
ENCODING = "utf-8"
END_MARKER = '\0'

LOGIN_SUCCESS = ">> login success"
LOGIN_FAILURE = ">> login failed"
REGISTER_SUCCESS = ">> register sucess"
REGISTER_FAILURE = ">> register failed"
LOGOUT_SUCCESS = ">> logout success"
LOGOUT_FAILURE = ">> logout failure"
LOGIN_INV_COMMAND = ">> Invalid command. Current valid commands: login, register, close"
LOGGEDIN_INV_COMMAND = ">> Invalid command. Current valid commands: msg, show, lookup, logout"
LOOKUP_DONE = ">> No more users online"
LOOKUP_FAILED = lambda x: f">> {x} is not online (or username invalid)"