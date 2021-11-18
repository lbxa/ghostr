import sys
from socket import *
from datetime import timedelta, datetime
from threading import Thread, active_count
from constants import IP, BUFF_SIZE, FORMAT, NO_ERR, NEW_LINE
from protocol import parse_message, message_type
from user import User
from helper import check_unicast_block

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
        print(f"[NEW CONN] {addr} connected")
        self.alive = True

    # returns tuple: (success_flag, err_msg)
    def validate_block(self, blocker, blockee):
        if blocker == blockee:
            return 0, "Error. Cannot block self"

        if not User().search(blockee):
            return 0, f"Error. {blockee} does not exist"

        if User().is_blocked_by(blocker, blockee):
            return 0, f"Error. {blockee} already blocked"

        return 1, NO_ERR

    # returns tuple: (success_flag, err_msg)
    def validate_unblock(self, blocker, blockee):
        if blocker == blockee:
            return 0, "Error. Cannot block self"

        if not User().search(blockee):
            return 0, "Error. {blockee} does not exist"

        if not User().is_blocked_by(blocker, blockee):
            return 0, f"Error. {blockee} is not blocked"

        return 1, NO_ERR

    # send to every client thread except for the active one
    def broadcast(self, sender, message):
        for client in self.CLIENTS:
            if self.CLIENTS[client] != sender:
                client.send(message.encode(FORMAT))

    # sender should be set to False if not being used
    def unicast(self, sender, receiver, message):
        is_blocked_status = check_unicast_block(sender, receiver)

        if not is_blocked_status:
            for client in self.CLIENTS:
                if self.CLIENTS[client] == receiver:
                    client.send(message.encode(FORMAT))
        else:
            for client in self.CLIENTS:
                if self.CLIENTS[client] == sender:
                    client.send(is_blocked_status.encode(FORMAT))

    def run(self):
        msg = ""
        blocking_count = BLOCK_MAX
        while self.alive:
            msg = self.client.recv(BUFF_SIZE).decode(FORMAT)
            # --------------------------------------------------------- /LOGOUT
            if message_type(msg) == "LOGOUT":
                self.alive = False
                logged_out_user = parse_message(msg)["WHO"]

                msg = f"TYPE: LOGOUT;;WHO: {logged_out_user};;"
                self.client.send(msg.encode(FORMAT))

                del self.CLIENTS[self.client]
                User().logout(logged_out_user)

                # broadcast logout
                print(self.CLIENTS)
                msg = f"TYPE: LOGGEDOUT;;WHO: {logged_out_user};;"
                self.broadcast(logged_out_user, msg)

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

                msg = f"TYPE: LOGON;;RET: {auth_login};;NEW: {new_user};;ERR: {error_msg};;"
                self.client.send(msg.encode(FORMAT))
            # --------------------------------------------------------- /AUTH
            elif message_type(msg) == "AUTH":
                username = parse_message(msg)["WHO"]
                password = parse_message(msg)["PASW"]
                new_user = int(parse_message(msg)["NEW"])
                logon_verified = True

                if not new_user:
                    valid_login = int(User().auth(username, password))

                    if not valid_login:
                        blocking_count -= 1
                        logon_verified = False

                        if blocking_count == 0:
                            block_finish_time = datetime.now() + timedelta(0, BLOCK_DURATION, 0)
                            User().password_block(username, datetime.now(), block_finish_time)

                    msg = f"TYPE: AUTH;;PASW: {valid_login};;ATMP: {blocking_count};;"
                else:
                    User().add(username, password)
                    msg = f"TYPE: AUTH;;PASW: 1;;ATMP: {BLOCK_MAX};;"

                self.client.send(msg.encode(FORMAT))

                if logon_verified:
                    self.CLIENTS[self.client] = username
                    User().login(username, password)
                    self.broadcast(username, f"TYPE: LOGGEDIN;;WHO: {username};;")
            # --------------------------------------------------------- /WHOELSE
            elif message_type(msg) == "WHOELSE":
                user_req = parse_message(msg)["FROM"]
                online_users = User().get_all_online_users(except_for=user_req)
                msg = f"TYPE: WHOELSE;;FROM: {user_req};;BODY: {NEW_LINE.join(online_users)};;"
                self.unicast(sender=False, receiver=user_req, message=msg)
            # --------------------------------------------------------- /WHOELSESINCE
            elif message_type(msg) == "WHOELSESINCE":
                user_req = parse_message(msg)["FROM"]
                since = float(parse_message(msg)["WHEN"])
                online_users = User().get_all_online_users_since(except_for=user_req, interval=since)
                msg = f"TYPE: WHOELSE;;FROM: {user_req};;BODY: {NEW_LINE.join(online_users)};;"
                self.unicast(sender=False, receiver=user_req, message=msg)
            # --------------------------------------------------------- /BLOCK
            elif message_type(msg) == "BLOCK":
                blockee = parse_message(msg)["WHO"]
                blocker = parse_message(msg)["BLOCKER"]
                successful_block_flag, block_respose = self.validate_block(blocker, blockee)
                if successful_block_flag:
                    User().block(blocker, blockee)
                msg = f"TYPE: BLOCK;;WHO: {blockee};;BLOCKER: {blocker};;RET: {successful_block_flag};;ERR: {block_respose};;"
                self.unicast(sender=False, receiver=blocker, message=msg)
            # --------------------------------------------------------- /UNBLOCK
            elif message_type(msg) == "UNBLOCK":
                blockee = parse_message(msg)["WHO"]
                blocker = parse_message(msg)["BLOCKER"]
                successful_unblock_flag, unblock_respose = self.validate_unblock(blocker, blockee)
                if successful_unblock_flag:
                    User().unblock(blocker, blockee)
                msg = f"TYPE: UNBLOCK;;WHO: {blockee};;BLOCKER: {blocker};;RET: {successful_unblock_flag};;ERR: {unblock_respose};;"
                self.unicast(sender=False, receiver=blocker, message=msg)
            # --------------------------------------------------------- /BROADCAST
            elif message_type(msg) == "BROADCAST":
                sender = parse_message(msg)["FROM"]
                message_contents = parse_message(msg)["BODY"]
                msg = f"TYPE: MSG;;FROM: {sender};;TO: broadcast;;BODY: {message_contents};;"
                self.broadcast(sender, msg)
            # --------------------------------------------------------- /MESSAGE
            elif message_type(msg) == "MSG":
                sender = parse_message(msg)["FROM"]
                recipient = parse_message(msg)["TO"]
                message_contents = parse_message(msg)["BODY"]
                msg = f"TYPE: MSG;;FROM: {sender};;TO: {recipient};;BODY: {message_contents};;"
                self.unicast(sender, recipient, msg)

        self.client.shutdown(SHUT_RDWR)
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
