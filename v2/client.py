# COMP3331 Assignment
# Lucas Chu Barbosa (z5259433) | 21T3
# client.py contains all multi-threaded socket client code

from socket import *
import json
import atexit
import threading
import time
import sys
import signal
from constants import IP, BUFF_SIZE, FORMAT
from library import (
    ACTION_LOOKUP_TABLE,
    chat_print,
    private_recv_handler,
    private_disconnect,
    private_message,
    private_recv_port,
)

if len(sys.argv) != 2:
    chat_print("error: usage: python client.py <SERVER_PORT>")
    sys.exit()

PORT = int(sys.argv[1])
ADDR = (IP, PORT)

to_exit = False
is_timeout = False

# connect to the server
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(ADDR)
t_lock = threading.Condition()


# get the username and password and login
username = input("Username: ")
USERNAME = username

message = json.dumps(
    {"action": "login", "username": username, "password": input("Password: "), "private_port": private_recv_port}
)


# logout handler
def logout():
    if is_timeout:
        chat_print("\rYou are timed out.")
    else:
        chat_print("\rYou are logged out.")
        clientSocket.send(json.dumps({"action": "logout"}).encode())
        clientSocket.close()


# handles all incoming data and selectively display useful information to user
def recv_handler():
    global to_exit, is_timeout
    while True:
        login_result = clientSocket.recv(BUFF_SIZE).decode(FORMAT)
        data = json.loads(login_result)
        if data["action"] in list(ACTION_LOOKUP_TABLE.keys()):
            ACTION_LOOKUP_TABLE[data["action"]](data)
        elif data["action"] == "timeout":
            # client timed out by the server
            to_exit = True
            is_timeout = True
        else:
            # unexpected format
            chat_print(data)


# handles all outgoing data
def send_handler():
    global to_exit
    while True:
        # handle input and send to server
        command = input("# ").strip()
        if command.startswith("logout"):
            to_exit = True
        elif command.startswith("message"):
            _, user, message = command.split(" ", 2)
            clientSocket.send(json.dumps({"action": "message", "message": message, "user": user}).encode())
        elif command.startswith("broadcast"):
            _, message = command.split(" ", 1)
            clientSocket.send(
                json.dumps(
                    {
                        "action": "broadcast",
                        "message": message,
                    }
                ).encode(FORMAT)
            )
        elif command.startswith("block"):
            _, user = command.split()
            clientSocket.send(
                json.dumps(
                    {
                        "action": "block",
                        "user": user,
                    }
                ).encode(FORMAT)
            )
        elif command.startswith("unblock"):
            _, user = command.split()
            clientSocket.send(
                json.dumps(
                    {
                        "action": "unblock",
                        "user": user,
                    }
                ).encode(FORMAT)
            )
        elif command.startswith("whoelsesince"):
            _, since = command.split()
            clientSocket.send(json.dumps({"action": "whoelsesince", "since": since}).encode())
        elif command.startswith("whoelse"):
            clientSocket.send(json.dumps({"action": "whoelse"}).encode())
        elif command.startswith("startprivate"):
            _, user = command.split()
            clientSocket.send(json.dumps({"action": "startprivate", "user": user}).encode())
        elif command.startswith("stopprivate"):
            _, user = command.split()
            private_disconnect(user)
        elif command.startswith("private"):
            _, user, message = command.split(" ", 2)
            private_message(user, message)


# start the interaction between client and server
def interact():
    global private_recv_socket
    recv_thread = threading.Thread(name="recv_handler", target=recv_handler)
    recv_thread.daemon = True
    recv_thread.start()

    send_thread = threading.Thread(name="send_handler", target=send_handler)
    send_thread.daemon = True
    send_thread.start()

    recv_thread = threading.Thread(name="priv_recv_handler", target=private_recv_handler)
    recv_thread.daemon = True
    recv_thread.start()

    while True:
        time.sleep(0.1)

        # when set true, exit the main thread
        if to_exit:
            sys.exit()


# log in then start interaction if successfully authenticated
def log_in():
    global message
    clientSocket.send(message.encode(FORMAT))
    login_result = json.loads(clientSocket.recv(BUFF_SIZE).decode(FORMAT))

    if login_result["action"] == "login":
        if login_result["status"] == "SUCCESS" or login_result["status"] == "USERNAME_NOT_EXIST":
            if login_result["status"] == "USERNAME_NOT_EXIST":
                print(f"Welcome new user {username}!"),
            else:
                # successfully authenticated
                print("You are logged in")

            # register on logout cleanup
            atexit.register(logout)
            # start interaction
            interact()
        elif login_result["status"] == "ALREADY_LOGGED_IN":
            print("You have already logged in")
        elif login_result["status"] == "INVALID_PASSWORD_BLOCKED":
            print("Invalid password. Your account has been blocked. Please try again later")
        elif login_result["status"] == "BLOCKED":
            print("Your account is blocked due to multiple login failures. Please try again later")
        elif login_result["status"] == "INVALID_PASSWORD":
            # invalid password, try again
            message = json.dumps(
                {
                    "action": "login",
                    "username": username,
                    "password": input("Invalid password. Please try again: "),
                    "private_port": private_recv_port,
                }
            )
            log_in()
        elif login_result["status"] == "ALREADY_LOGGED_IN":
            print("Already logged in")
        else:
            # things unexpected
            print("FATAL: unexpected message")
            sys.exit()


def keyboard_interrupt_handler(signal, frame):
    sys.exit()


# register keyboard interrupt handler
signal.signal(signal.SIGINT, keyboard_interrupt_handler)

if __name__ == "__main__":
    # start to authenticate user
    log_in()
