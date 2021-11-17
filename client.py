import sys
from socket import *
from threading import Thread
from constants import IP, BUFF_SIZE, FORMAT
from protocol import message_type, parse_message, remove_first_word, unpack_message

if len(sys.argv) != 2:
    print("error: usage: python client.py <SERVER_PORT>")
    exit(0)

PORT = int(sys.argv[1])
ADDR = (IP, PORT)


def recv_msg():
    connected = True
    while connected:
        try:
            msg = client.recv(BUFF_SIZE).decode(FORMAT)
            if message_type(msg) == "MSG":
                print(parse_message(msg)["FROM"] + ": " + parse_message(msg)["BODY"])
            elif message_type(msg) == "WHOELSE":
                print(parse_message(msg)["BODY"])
            elif message_type(msg) == "LOGOUT":
                print(parse_message(msg)["WHO"] + " logged out")
                connected = False
            else:
                # undefined server behaviour
                pass
        except Exception as err_msg:
            pass

    # exit the thread
    sys.exit()


def user_auth():
    # -------------------------------------------------- /AUTH
    username = input("Username: ")
    msg = f"""TYPE: LOGON\nWHO: {username}"""

    # server logon response
    client.send(msg.encode(FORMAT))
    msg = client.recv(BUFF_SIZE).decode(FORMAT)

    # auth flags
    authorised_logon = int(parse_message(msg)["RET"])
    new_user = int(parse_message(msg)["NEW"])
    err_code = parse_message(msg)["ERR"]

    if not authorised_logon and err_code != "0":
        print(err_code)
        return False
    # --------------------------------- /NEW USERS
    elif new_user:
        password = input("This is a new user. Enter a password: ")
        msg = f"TYPE: AUTH\nWHO: {username}\nPASW: {password}\nNEW: 1"
        client.send(msg.encode(FORMAT))
    else:
        # ----------------------------- /EXISTING USERS
        # initial password prompt
        password = input("Password: ")
        msg = f"TYPE: AUTH\nWHO: {username}\nPASW: {password}\nNEW: 0"
        client.send(msg.encode(FORMAT))

        msg = client.recv(BUFF_SIZE).decode(FORMAT)
        correct_pasw = int(parse_message(msg)["PASW"])
        attempts_left = int(parse_message(msg)["ATMP"])

        # keep prompting until correct
        while not correct_pasw:
            if attempts_left == 0:
                print("Invalid Password. Your account has been blocked. Please try again later")
                return False

            print("Invalid Password. Please try again")
            password = input("Password: ")
            msg = f"TYPE: AUTH\nWHO: {username}\nPASW: {password}\nNEW: 0"
            client.send(msg.encode(FORMAT))

            msg = client.recv(BUFF_SIZE).decode(FORMAT)
            correct_pasw = int(parse_message(msg)["PASW"])
            attempts_left = int(parse_message(msg)["ATMP"])

    print(f"[CONNECTED] Client connected to server")
    return username


def send_msg(username):
    # -------------------------------------------------- /CHAT
    connected = True
    while connected:
        user_input = input()
        if user_input == "logout":
            msg = f"TYPE: LOGOUT\nWHO: {username}"
            connected = False
        elif "broadcast" in user_input:
            msg = f"TYPE: BROADCAST\nFROM: {username}\nBODY: {remove_first_word(user_input)}"
        elif "message" in user_input:
            recipient, body = unpack_message(user_input)
            msg = f"TYPE: MSG\nFROM: {username}\nTO: {recipient}\nBODY: {body}"
        elif user_input == "whoelse":
            msg = f"TYPE: WHOELSE\nFROM: {username}"
        else:
            print("Error. Invalid command")
            continue  # avoid sending an empty message (restart loop)

        client.send(msg.encode(FORMAT))


if __name__ == "__main__":
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(ADDR)
    recv_thread = Thread(target=recv_msg)
    recv_thread.start()

    authed_username = user_auth()
    if not authed_username:
        client.close()
        sys.exit()
    else:
        send_msg(authed_username)
        # once loop finished
        client.close()
        sys.exit()
