import sys
from socket import *
from constants import IP, SIZE, FORMAT, ERR_WRONG_PASW, ERR_INVALID_USER, ERR_ALREADY_LOGGED_IN
from protocol import parse_message

if len(sys.argv) != 2:
    print("error: usage: python client.py <SERVER_PORT>")
    exit(0)

PORT = int(sys.argv[1])
ADDR = (IP, PORT)


def main():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(ADDR)

    # -------------------------------------------------- /AUTH
    username = input("Username: ")
    msg = f"""TYPE: LOGON\nWHO: {username}"""

    # server logon response
    client.send(msg.encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
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

        msg = client.recv(SIZE).decode(FORMAT)
        correct_pasw = int(parse_message(msg)["PASW"])
        attempts_left = int(parse_message(msg)["ATMP"])

        # keep prompting until correct
        while not correct_pasw:
            print(msg)
            if attempts_left == 0:
                print("Invalid Password. Your account has been blocked. Please try again later")
                client.close()
                exit(0)

            print("Invalid Password. Please try again")
            password = input("Password: ")
            msg = f"TYPE: AUTH\nWHO: {username}\nPASW: {password}\nNEW: 0"
            client.send(msg.encode(FORMAT))

            msg = client.recv(SIZE).decode(FORMAT)
            correct_pasw = int(parse_message(msg)["PASW"])
            attempts_left = int(parse_message(msg)["ATMP"])

    print(f"[CONNECTED] Client connected to server")

    # -------------------------------------------------- /CHAT
    connected = True
    while connected:
        user_input = input("> ")
        if user_input == "!EXIT":
            connected = False
        else:
            msg = f"TYPE: MSG\nFROM: {username}\nTO: broadcast\nBODY: {user_input}"
            client.send(msg.encode(FORMAT))
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")

    client.close()


if __name__ == "__main__":
    main()
