import sys
from socket import *
from datetime import timedelta, datetime
from threading import Thread, active_count
from constants import IP, BUFF_SIZE, FORMAT, NO_ERR
from protocol import parse_message, message_type
from user import User

if len(sys.argv) != 4:
    print("error: usage: python server.py <SERVER_PORT> <BLOCKING_TIME> <TIMEOUT>")
    sys.exit()

PORT = int(sys.argv[1])
BLOCK_DURATION = int(sys.argv[2])  # in seconds
MAX_TIMEOUT = int(sys.argv[3])  # in seconds
BLOCK_MAX = 3
ADDR = (IP, PORT)


class ServerCore(Thread):
    CLIENTS = {}

    def __init__(self, client, addr):
        Thread.__init__(self)
        self.addr = addr
        self.client = client
        self.host, self.port = addr
        self.CLIENTS[client] = "<anonymous>"
        print(f"[NEW CONN] {addr} connected")
        self.alive = True

    # send to every client thread except for the active one
    def broadcast(self, sender, message):
        for client in self.CLIENTS:
            if self.CLIENTS[client] != sender:
                client.send(message.encode(FORMAT))

    def unicast(self, recipient, message):
        for client in self.CLIENTS:
            if self.CLIENTS[client] == recipient:
                client.send(message.encode(FORMAT))

    def run(self):
        msg = ""
        blocking_count = BLOCK_MAX
        while self.alive:
            msg = self.client.recv(BUFF_SIZE).decode(FORMAT)
            # --------------------------------------------------------- /LOGOUT
            if message_type(msg) == "LOGOUT":
                self.alive = False
                logged_out_user = parse_message(msg)["WHO"]
                msg = f"TYPE: LOGOUT\nWHO: {logged_out_user}"

                del self.CLIENTS[self.client]
                User().logout(logged_out_user)

                # broadcast logout
                print(self.CLIENTS)
                for client in self.CLIENTS:
                    print("@")
                    client.send(msg.encode(FORMAT))
            # --------------------------------------------------------- /LOGON
            elif message_type(msg) == "LOGON":
                username = parse_message(msg)["WHO"]
                auth_login = 1
                error_msg = NO_ERR
                new_user = 1 if not User().search(username) else 0

                # check user is not already online
                if User().search_online(username):
                    auth_login = 0
                    error_msg = "User already online"

                # check user is not blocked
                if User().is_blocked(username):
                    auth_login = 0
                    error_msg = "Your account is blocked due to multiple login failures. Please try again later"

                msg = f"TYPE: LOGON\nRET: {auth_login}\nNEW: {new_user}\nERR: {error_msg}"
                self.client.send(msg.encode(FORMAT))
            # --------------------------------------------------------- /AUTH
            elif message_type(msg) == "AUTH":
                username = parse_message(msg)["WHO"]
                password = parse_message(msg)["PASW"]
                new_user = int(parse_message(msg)["NEW"])
                if not new_user:
                    valid_login = int(User().auth(username, password))
                    if not valid_login:
                        blocking_count -= 1

                    if blocking_count == 0:
                        block_finish_time = datetime.now() + timedelta(0, BLOCK_DURATION, 0)
                        User().block(username, datetime.now(), block_finish_time)

                    msg = f"TYPE: AUTH\nPASW: {valid_login}\nATMP: {blocking_count}"
                else:
                    User().add(username, password)
                    msg = f"TYPE: AUTH\nPASW: 1\nATMP: {BLOCK_MAX}"

                User().login(username, password)
                self.CLIENTS[self.client] = username
                self.client.send(msg.encode(FORMAT))
            # --------------------------------------------------------- /WHOELSE
            elif message_type(msg) == "WHOELSE":
                sender = parse_message(msg)["FROM"]
                online_users = User().get_all_online_users(except_for=sender)
                msg = f"TYPE: WHOELSE\nFROM: {sender}\nBODY: {', '.join(online_users)}"
                self.unicast(sender, msg)
            # --------------------------------------------------------- /BROADCAST
            elif message_type(msg) == "BROADCAST":
                sender = parse_message(msg)["FROM"]
                message_contents = parse_message(msg)["BODY"]
                msg = f"TYPE: MSG\nFROM: {sender}\nTO: broadcast\nBODY: {message_contents}"
                self.broadcast(sender, msg)
            # --------------------------------------------------------- /MESSAGE
            elif message_type(msg) == "MSG":
                sender = parse_message(msg)["FROM"]
                recipient = parse_message(msg)["TO"]
                message_contents = parse_message(msg)["BODY"]
                msg = f"TYPE: MSG\nFROM: {sender}\nTO: {recipient}\nBODY: {message_contents}"
                self.unicast(recipient, msg)

        self.client.close()


def main():
    print("[START] Server is starting")
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind(ADDR)

    while True:
        server.listen()
        client, addr = server.accept()
        client_thread = ServerCore(client, addr)
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {active_count() - 1}")


if __name__ == "__main__":
    main()
