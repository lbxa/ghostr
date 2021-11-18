import socket
from enum import Enum

IP = socket.gethostbyname(socket.gethostname())  # 127.0.0.1
BUFF_SIZE = 1024
FORMAT = "utf-8"

# error values
NO_ERR = "0"
ERR_WRONG_PASW = 1
ERR_INVALID_USER = 2
ERR_ALREADY_LOGGED_IN = 3

NEW_LINE = "\n"
SERVER_ALIAS = "!SERVER!"
EMPTY = ""


class CMPP(Enum):
    LOGON_REQ = 0
    AUTH_REQ = 1
    MSG_REQ = 2

    LOGON_RES = 3
    AUTH_RES = 4
    MSG_RES = 5
