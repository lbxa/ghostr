# COMP3331 Assignment
# Lucas Chu Barbosa (z5259433) | 21T3
# library.py contains all helper and auxilliary functions

import sys
import json
import readline
import threading
from socket import *
from constants import IP, BUFF_SIZE, FORMAT


def chat_print(*args):
    sys.stdout.write("\r" + " " * (len(readline.get_line_buffer()) + 2) + "\r")
    print(*args)
    sys.stdout.write("# " + readline.get_line_buffer())
    sys.stdout.flush()


# map of username to private tcp socket
private_socket_map = dict()

# private connection socket
private_recv_socket = socket(AF_INET, SOCK_STREAM)
private_recv_socket.bind((IP, 0))
private_recv_socket.listen(1)
private_recv_port = private_recv_socket.getsockname()[1]

# return a function as connection handler for a specific socket for multi threading
def private_connection_handler(connection_socket, client_address):
    def real_connection_handler():
        while True:
            data = connection_socket.recv(BUFF_SIZE).decode(FORMAT)
            if not data:
                # if data is empty, the socket is closed or is in the
                # process of closing. In this case, close this thread
                chat_print("Private connection stopped.")
                sys.exit()

            # received data from the client, now we know who we are talking with
            data = json.loads(data)
            from_user = data["from"]
            message = data["message"]

            chat_print(from_user, "(private): ", message)

    return real_connection_handler


# handles all incoming data and replies to those
def private_recv_handler():
    while True:
        # create a new connection for a new client
        connection_socket, client_address = private_recv_socket.accept()
        chat_print("Private connection started.")

        # create a new function handler for the client
        private_socket_handler = private_connection_handler(connection_socket, client_address)

        # create a new thread for the client socket
        private_socket_thread = threading.Thread(name=str(client_address), target=private_socket_handler)
        private_socket_thread.daemon = False
        private_socket_thread.start()


def private_connect(address, port, username):
    # connect with address directly in p2p mode
    new_private_socket = socket(AF_INET, SOCK_STREAM)
    new_private_socket.connect((address, port))
    private_socket_map[username] = new_private_socket
    chat_print("Private connection connected.")


def private_disconnect(username):
    # disconnect with user
    if username in private_socket_map and private_socket_map[username]:
        private_socket_map[username].close()
        chat_print("Closed.")
    else:
        chat_print("Not connected.")


def private_message(username, message):
    # send a private message to user
    USERNAME = username
    if username in private_socket_map and private_socket_map[username]:
        private_socket_map[username].send(json.dumps({"from": USERNAME, "message": message}).encode())
    else:
        chat_print("Not connected.")


# -----------------------------------------------------------------------------------------------------


def __action_message(data):
    # reply to a user-initiated message
    if data["status"] == "MESSAGE_SELF":
        chat_print("Cannot message yourself.")
    elif data["status"] == "USER_NOT_EXIST":
        chat_print("User does not exist.")
    elif data["status"] == "USER_BLOCKED":
        chat_print("That user blocked you.")
    elif data["status"] == "SUCCESS":
        # message sent successfully
        pass


def __action_bock(data):
    # reply to a user-initiated block
    if data["status"] == "MESSAGE_SELF":
        chat_print("Cannot block yourself.")
    elif data["status"] == "USER_NOT_EXIST":
        chat_print("User does not exist.")
    else:
        chat_print("Block success.")


def __action_unblock(data):
    # reply to a user-initiated unblock
    if data["status"] == "MESSAGE_SELF":
        chat_print("Cannot unblock yourself.")
    elif data["status"] == "USER_NOT_EXIST":
        chat_print("User does not exist.")
    else:
        chat_print("Unblock success.")


def __action_receive_message_or_broadcast(data):
    # receiving a message
    chat_print(data["from"], ":", data["message"])


def __action_broadcast(data):
    # reply to a user-initiated broadcast
    chat_print("sent to", data["n_sent"], "user(s).")
    if int(data["n_blocked"]) > 0:
        chat_print("Your message could not be delivered to some recipients")


def __action_whoelse(data):
    # reply to a user-initiated whoelse
    chat_print("Currently online:")
    chat_print("\n".join(data["reply"]))


def __action_whoelsesince(data):
    # reply to a user-initiated whoelsesince
    chat_print("Currently online since:")
    chat_print("\n".join(data["reply"]))


def __action_login_broadcast(data):
    # receive login braodcast
    chat_print(data["from"], "is logged in.")


def __action_logout_broadcast(data):
    # receive login braodcast
    chat_print(data["from"], "is logged out.")


def __startprivate(data):
    # receive login braodcast
    if data["reply"] == "USER_NOT_EXIST":
        chat_print("startprivate: user does not exist.")
    elif data["reply"] == "USER_SELF":
        chat_print("startprivate: cannot private yourself.")
    elif data["reply"] == "USER_BLOCKED":
        chat_print("startprivate: that user blocked you.")
    elif data["reply"] == "USER_OFFLINE":
        chat_print("startprivate: that user is offline.")
    elif data["reply"] == "SUCCESS":
        address = data["address"]
        port = int(data["port"])
        username = data["username"]
        private_connect(address, port, username)
    else:
        chat_print("Unexpected reply.")


ACTION_LOOKUP_TABLE = {
    "message": __action_message,
    "block": __action_bock,
    "unblock": __action_unblock,
    "receive_message": __action_receive_message_or_broadcast,
    "receive_broadcast": __action_receive_message_or_broadcast,
    "broadcast": __action_broadcast,
    "whoelse": __action_whoelse,
    "whoelsesince": __action_whoelsesince,
    "login_broadcast": __action_login_broadcast,
    "logout_broadcast": __action_logout_broadcast,
    "startprivate": __startprivate,
}
