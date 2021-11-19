# COMP3331 Assignment
# Lucas Chu Barbosa (z5259433) | 21T3
# server.py contains all multi-threaded socket and server code

from socket import *
import threading
import signal
import atexit
import time
import json
import sys
from admin import Admin
from constants import IP, BUFF_SIZE, FORMAT, UPDATE_INTERVAL


if len(sys.argv) != 4:
    print("error: usage: python server.py <SERVER_PORT> <BLOCKING_TIME> <TIMEOUT>")
    sys.exit()

PORT = int(sys.argv[1])
BLOCK_DURATION = int(sys.argv[2])  # in seconds
MAX_TIMEOUT = int(sys.argv[3])  # in seconds
BLOCK_MAX = 3
ADDR = (IP, PORT)


user_manager = Admin(BLOCK_DURATION, MAX_TIMEOUT)
t_lock = threading.Condition()
clients = []
pending_messages = []
name_to_socket = {}


# helper function to send a message
def send_message(from_user, to_user, message, broadcast=False, login_broadcast=False, logout_broadcast=False):
    if to_user not in name_to_socket:
        print("ERROR", to_user, "not exist")
    else:
        to_user_socket = name_to_socket[to_user]
        action = "receive_message"
        if broadcast:
            action = "receive_broadcast"
        elif login_broadcast:
            action = "login_broadcast"
        elif logout_broadcast:
            action = "logout_broadcast"
        to_user_socket.send(json.dumps({"action": action, "from": from_user, "message": message}).encode())


# return a function as connection handler for a specific socket for multi threading
def connection_handler(connection_socket, client_address):
    def real_connection_handler():
        while True:
            data = connection_socket.recv(BUFF_SIZE).decode(FORMAT)
            if not data:
                # if data is empty, the socket is closed or is in the
                # process of closing. In this case, close this thread
                sys.exit()

            # received data from the client, now we know who we are talking with
            data = json.loads(data)
            action = data["action"]

            # get lock as we might me accessing some shared data structures
            with t_lock:
                server_message = {}
                server_message["action"] = action

                # current user name
                curr_user = user_manager.get_username(client_address)

                # update the time out when user send anything to server
                user_manager.refresh_user_timeout(curr_user)

                if action == "login":
                    # store client information (IP and Port No) in list
                    username = data["username"]
                    password = data["password"]
                    clients.append(client_address)
                    # auth the user and reply the status
                    status = user_manager.authenticate(username, password)
                    user_manager.set_address_username(client_address, username)
                    server_message["status"] = status
                    if status == "SUCCESS" or status == "USERNAME_NOT_EXIST":
                        # add the socket to the name-socket map
                        name_to_socket[username] = connection_socket
                        user_manager.set_private_port(username, int(data["private_port"]))
                        # broadcast new user login
                        for user in user_manager.all_users():
                            if user != username and user_manager.is_online(user):
                                send_message(username, user, "", login_broadcast=True)
                elif action == "logout":
                    # check if client already subscribed or not
                    user_manager.set_offline(user_manager.get_username(client_address))
                    if client_address in clients:
                        clients.remove(client_address)
                        server_message["reply"] = "logged out"
                        # broadcast user logout
                        for user in user_manager.all_users():
                            if user != curr_user and user_manager.is_online(user):
                                send_message(curr_user, user, "", logout_broadcast=True)
                    else:
                        server_message["reply"] = "You are not logged in"
                elif action == "message":
                    # user tries to send a message to other users
                    username = data["user"]
                    message = data["message"]
                    if curr_user == username:
                        server_message["status"] = "MESSAGE_SELF"
                    elif not user_manager.has_user(username):
                        server_message["status"] = "USER_NOT_EXIST"
                    elif user_manager.is_blocked_user(username, curr_user):
                        server_message["status"] = "USER_BLOCKED"
                    else:
                        server_message["status"] = "SUCCESS"
                        if user_manager.is_online(username):
                            send_message(curr_user, username, message)
                        else:
                            pending_messages.append({"from_user": curr_user, "to_user": username, "message": message})
                elif action == "broadcast":
                    # broadcast the message to online unblocked users
                    message = data["message"]
                    n_sent = 0
                    n_blocked = 0
                    for user in user_manager.all_users():
                        if user_manager.is_blocked_user(user, curr_user):
                            n_blocked += 1
                        elif not user_manager.is_online(user):
                            pass
                        elif user == curr_user:
                            pass
                        else:
                            n_sent += 1
                            send_message(curr_user, user, message, broadcast=True)
                    server_message["n_sent"] = n_sent
                    server_message["n_blocked"] = n_blocked
                elif action == "block":
                    user_to_block = data["user"]
                    if curr_user == user_to_block:
                        server_message["status"] = "MESSAGE_SELF"
                    elif not user_manager.has_user(user_to_block):
                        server_message["status"] = "USER_NOT_EXIST"
                    elif user_manager.is_blocked_user(curr_user, user_to_block):
                        server_message["status"] = "USER_ALREADY_BLOCKED"
                    else:
                        server_message["status"] = "SUCCESS"
                        user_manager.block(curr_user, user_to_block)
                elif action == "unblock":
                    user_to_unblock = data["user"]
                    if curr_user == user_to_unblock:
                        server_message["status"] = "MESSAGE_SELF"
                    elif not user_manager.has_user(user_to_unblock):
                        server_message["status"] = "USER_NOT_EXIST"
                    elif not user_manager.is_blocked_user(curr_user, user_to_block):
                        server_message["status"] = "USER_ALREADY_UNBLOCKED"
                    else:
                        server_message["status"] = "SUCCESS"
                        user_manager.unblock(curr_user, user_to_unblock)
                elif action == "whoelse":
                    online_users = user_manager.get_online_users()
                    online_users.remove(curr_user)
                    server_message["reply"] = list(online_users)
                elif action == "whoelsesince":
                    users = user_manager.get_users_logged_in_since(int(data["since"]))
                    if curr_user in users:
                        users.remove(curr_user)
                    server_message["reply"] = list(users)
                elif action == "startprivate":
                    # return user address and port if available
                    user = data["user"]
                    if not user_manager.has_user(user):
                        server_message["reply"] = "USER_NOT_EXIST"
                    elif user_manager.is_blocked_user(user, curr_user):
                        server_message["reply"] = "USER_BLOCKED"
                    elif user == curr_user:
                        server_message["reply"] = "USER_SELF"
                    elif not user_manager.is_online(user):
                        server_message["reply"] = "USER_OFFLINE"
                    else:
                        # can provide user details to user
                        server_message["reply"] = "SUCCESS"
                        user_socket = name_to_socket[user]
                        user_address = user_socket.getsockname()[0]
                        server_message["address"] = user_address
                        server_message["port"] = user_manager.get_private_port(user)
                        server_message["username"] = user
                else:
                    server_message["reply"] = "Unknown action"
                connection_socket.send(json.dumps(server_message).encode(FORMAT))
                t_lock.notify()

    return real_connection_handler


# inbound data
def recv_handler():
    global t_lock
    global clients
    global serverSocket
    print("Server is up.")
    while True:
        connection_socket, client_address = serverSocket.accept()
        socket_handler = connection_handler(connection_socket, client_address)

        socket_thread = threading.Thread(name=str(client_address), target=socket_handler)
        socket_thread.daemon = False
        socket_thread.start()


# outbound data
def send_handler():
    global t_lock
    global clients
    global serverSocket
    while True:
        with t_lock:
            # check if any pending messages can be send to any users who is online
            for message in pending_messages:
                if user_manager.is_online(message["to_user"]):
                    send_message(message["from_user"], message["to_user"], message["message"])
                    pending_messages.remove(message)
            for user in user_manager.get_timed_out_users():
                if user in name_to_socket:
                    user_manager.set_offline(user)
                    name_to_socket[user].send(json.dumps({"action": "timeout"}).encode(FORMAT))
            t_lock.notify()
        time.sleep(UPDATE_INTERVAL)


# catch the ctrl+c exit signal
def keyboard_interrupt_handler(signal, frame):
    print("\r[Terminating server...]")
    sys.exit()


# close the socket when exit
def on_close():
    serverSocket.close()


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)
serverSocket.listen(1)

recv_thread = threading.Thread(name="recv_handler", target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

send_thread = threading.Thread(name="send_handler", target=send_handler)
send_thread.daemon = True
send_thread.start()

# control functions
signal.signal(signal.SIGINT, keyboard_interrupt_handler)
atexit.register(on_close)

while True:
    time.sleep(0.1)
    user_manager.update()
