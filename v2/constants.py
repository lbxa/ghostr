# COMP3331 Assignment
# Lucas Chu Barbosa (z5259433) | 21T3
# constants.py contains useful constants used across the codebase

from enum import Enum

IP = "127.0.0.1"
BUFF_SIZE = 1024
FORMAT = "utf-8"

# error values
NO_ERR = "0"
ERR_WRONG_PASW = 1
ERR_INVALID_USER = 2
ERR_ALREADY_LOGGED_IN = 3
UPDATE_INTERVAL = 1


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
