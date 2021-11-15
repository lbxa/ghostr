import sys
from socket import *
from threading import Thread
from constants import IP, BUFF_SIZE, FORMAT
from protocol import message_type, parse_message

if len(sys.argv) != 2:
    print("error: usage: python client.py <SERVER_PORT>")
    exit(0)

PORT = int(sys.argv[1])
ADDR = (IP, PORT)


def recv_msg():
    while True:
        msg = client.recv(BUFF_SIZE).decode(FORMAT)
        # only print out actual messages
        if message_type(msg) == "MSG":
            print(parse_message(msg)["FROM"] + ": " + parse_message(msg)["BODY"])


def send_msg():
    # -------------------------------------------------- /AUTH
    username = input("Username: ")
    msg = f"""TYPE: LOGON\nWHO: {username}"""

    # server logon response
    client.send(msg.encode(FORMAT))
    msg = client.recv(BUFF_SIZE).decode(FORMAT)
    existing_user = int(parse_message(msg)["RET"])

    # --------------------------------- /NEW USERS
    if not existing_user:
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
                client.close()
                exit(0)

            print("Invalid Password. Please try again")
            password = input("Password: ")
            msg = f"TYPE: AUTH\nWHO: {username}\nPASW: {password}\nNEW: 0"
            client.send(msg.encode(FORMAT))

            msg = client.recv(BUFF_SIZE).decode(FORMAT)
            correct_pasw = int(parse_message(msg)["PASW"])
            attempts_left = int(parse_message(msg)["ATMP"])

    print(f"[CONNECTED] Client connected to server")

    # -------------------------------------------------- /CHAT
    connected = True
    while connected:
        user_input = input()
        if user_input == "!EXIT":
            connected = False
        else:
            msg = f"TYPE: MSG\nFROM: {username}\nTO: broadcast\nBODY: {user_input}"
            client.send(msg.encode(FORMAT))
            msg = client.recv(BUFF_SIZE).decode(FORMAT)

    client.close()


if __name__ == "__main__":
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(ADDR)
    recv_thread = Thread(target=recv_msg)
    recv_thread.start()
    send_msg()
