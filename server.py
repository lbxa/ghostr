import sys
from socket import *
from threading import Thread, active_count
from constants import IP, SIZE, FORMAT
from protocol import parse_message, message_type
from user import User

if len(sys.argv) != 3:
    print("error: usage: python server.py <SERVER_PORT> <BLOCKING_NO>")
    exit(0)

PORT = int(sys.argv[1])
BLOCK_MAX = int(sys.argv[2])
ADDR = (IP, PORT)


class ServerCore(Thread):
    def __init__(self, sock, addr):
        Thread.__init__(self)
        self.addr = addr
        self.sock = sock
        self.host, self.port = addr
        print(f"[NEW CONN] {addr} connected")
        self.alive = True

    def run(self):
        msg = ""
        blocking_count = BLOCK_MAX
        while self.alive:
            msg = self.sock.recv(SIZE).decode(FORMAT)
            print("-" * 10)
            print(msg)
            print("-" * 10)
            if msg == "!EXIT":
                self.alive = False
                msg = f"Goodbye #{self.port}"
                print(f"[EXIT] {msg}")
            elif message_type(msg) == "LOGON":
                username = parse_message(msg)["WHO"]
                msg = f"TYPE: LOGON\nRET: {int(User().search(username))}"
                self.sock.send(msg.encode(FORMAT))
            elif message_type(msg) == "AUTH":
                username = parse_message(msg)["WHO"]
                password = parse_message(msg)["PASW"]
                new_user = int(parse_message(msg)["NEW"])
                if not new_user:
                    valid_login = int(User().auth(username, password))
                    if not valid_login:
                        blocking_count -= 1
                    msg = f"TYPE: AUTH\nPASW: {valid_login}\nATMP: {blocking_count}"
                else:
                    User().add(username, password)
                    msg = f"TYPE: AUTH\nPASW: 1\nATMP: {BLOCK_MAX}"

                self.sock.send(msg.encode(FORMAT))
            elif message_type(msg) == "MSG":
                message_contents = parse_message(msg)["BODY"]
                print(f"[{self.port}, MSG] {message_contents}")
                self.sock.send("Message sent".encode(FORMAT))

        self.sock.close()


def main():
    print("[START] Server is starting")
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(ADDR)

    while True:
        server.listen()
        sock, addr = server.accept()
        client_thread = ServerCore(sock, addr)
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {active_count() - 1}")


if __name__ == "__main__":
    main()
