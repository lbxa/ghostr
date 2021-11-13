from socket import *
from constants import ADDR, SIZE, FORMAT


def main():
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to server")

    connected = True
    while connected:
        msg = input("> ")
        client.send(msg.encode(FORMAT))
        if msg == "!EXIT":
            connected = False
        else:
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")


if __name__ == "__main__":
    main()
