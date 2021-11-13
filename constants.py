import socket

IP = socket.gethostbyname(socket.gethostname())  # 127.0.0.1
PORT = 3331
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
