import sys
from socket import *
from threading import Thread, active_count
from constants import IP, BUFF_SIZE, FORMAT
from protocol import parse_message, message_type
from user import User

if len(sys.argv) != 3:
    print("error: usage: python server.py <SERVER_PORT> <BLOCKING_NO>")
    exit(0)

PORT = int(sys.argv[1])
BLOCK_MAX = int(sys.argv[2])
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

    def run(self):
        msg = ""
        blocking_count = BLOCK_MAX
        while self.alive:
            msg = self.client.recv(BUFF_SIZE).decode(FORMAT)
            # print("-" * 10)
            # print(self.CLIENTS)
            # print("-" * 10)
            if msg == "!EXIT":
                self.alive = False
                msg = f"Goodbye #{self.port}"
                print(f"[EXIT] {msg}")
            elif message_type(msg) == "LOGON":
                username = parse_message(msg)["WHO"]
                msg = f"TYPE: LOGON\nRET: {int(User().search(username))}"
                self.client.send(msg.encode(FORMAT))
            elif message_type(msg) == "AUTH":
                username = parse_message(msg)["WHO"]
                password = parse_message(msg)["PASW"]
                new_user = int(parse_message(msg)["NEW"])
                if not new_user:
                    valid_login = int(User().auth(username, password))
                    if not valid_login:
                        blocking_count -= 1
                    msg = f"TYPE: AUTH\nPASW: {valid_login}\nATMP: {blocking_count}"
                    self.CLIENTS[self.client] = username
                else:
                    User().add(username, password)
                    msg = f"TYPE: AUTH\nPASW: 1\nATMP: {BLOCK_MAX}"
                    self.CLIENTS[self.client] = username

                self.client.send(msg.encode(FORMAT))
            elif message_type(msg) == "MSG":
                sender = parse_message(msg)["FROM"]
                message_contents = parse_message(msg)["BODY"]
                for client in self.CLIENTS:
                    msg = f"TYPE: MSG\nFROM: {sender}\nTO: broadcast\nBODY: {message_contents}"
                    client.send(msg.encode(FORMAT))

        self.client.close()


def main():
    print("[START] Server is starting")
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(ADDR)

    while True:
        server.listen()
        client, addr = server.accept()
        client_thread = ServerCore(client, addr)
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {active_count() - 1}")


if __name__ == "__main__":
    main()
