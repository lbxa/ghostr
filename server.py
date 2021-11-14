from socket import *
import sys
from threading import Thread, active_count
from constants import IP, SIZE, FORMAT

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
        while self.alive:
            msg = self.sock.recv(SIZE).decode(FORMAT)
            if msg == "!EXIT":
                self.alive = False
                msg = f"Goodbye #{self.port}"
                print(f"[EXIT] {msg}")
            else:
                print(f"[{self.port}, MSG] {msg}")
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
