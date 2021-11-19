# COMP3331 Assignment
# Lucas Chu Barbosa (z5259433) | 21T3
# library.py contains all admin and management functions for each user

import sys
from time import time


class User:
    # manage all user data, including credentials, block status,
    # user-to-user block status, time out, online status,
    # and last login status

    def __init__(self, block_duration, time_out):
        self.__user_map = dict()
        self.__address_to_username_map = dict()
        self.__username_to_address_map = dict()
        self.__block_duration = block_duration
        self.__time_out = time_out
        self.__read_credentials()

    def __read_credentials(self):
        try:
            with open("credentials.txt", "r") as credential_file:
                for credential in credential_file:
                    username, password = credential.strip().split()
                    self.__user_map[username] = User.__Worker(
                        username, password, self.__block_duration, self.__time_out
                    )
        except Exception as msg:
            print(f"Error reading credentials.txt: {msg}")
            sys.exit()

    # add single user with (username, password)
    def add_credentials(self, username, password):
        try:
            with open("credentials.txt", "a") as f:
                user_field = f"\n{username} {password}"
                f.write(user_field)
        except:
            print("Error reading credentials.txt")
            sys.exit()

    def authenticate(self, username_input, password_input):
        # authenticate user and update status
        # return updated status in a string format

        if username_input not in self.__user_map:
            # username unknown
            self.add_credentials(username_input, password_input)
            self.__read_credentials()
            return self.__user_map[username_input].authenticate(password_input)

        # else, delegate authenticate to specific user class
        return self.__user_map[username_input].authenticate(password_input)

    def set_address_username(self, address, username):
        self.__address_to_username_map[address] = username
        self.__username_to_address_map[username] = address

    def get_username(self, address):
        if address in self.__address_to_username_map:
            return self.__address_to_username_map[address]
        else:
            return ""

    def get_address(self, username):
        if username in self.__username_to_address_map:
            return self.__username_to_address_map[username]
        else:
            return ""

    def set_offline(self, username):
        if username in self.__user_map:
            self.__user_map[username].set_offline()

    def update(self):
        # update all user's block status
        for user_credential in self.__user_map.values():
            user_credential.update()

    def block(self, from_username, to_block_username):
        if from_username in self.__user_map:
            self.__user_map[from_username].block(to_block_username)

    def unblock(self, from_username, to_block_username):
        if from_username in self.__user_map:
            self.__user_map[from_username].unblock(to_block_username)

    def is_blocked_user(self, from_username, to_block_username):
        return from_username in self.__user_map and self.__user_map[from_username].is_blocked_user(to_block_username)

    def has_user(self, username):
        return username in self.__user_map

    def is_online(self, username):
        return username in self.__user_map and self.__user_map[username].is_online()

    def all_users(self):
        return list(self.__user_map.keys())

    def get_timed_out_users(self):
        timed_out_users = set()
        for user in self.__user_map:
            if self.__user_map[user].update_time_out():
                timed_out_users.add(user)
        return timed_out_users

    def get_online_users(self):
        online_users = set()
        for user in self.__user_map:
            if self.__user_map[user].is_online():
                online_users.add(user)
        return online_users

    def get_users_logged_in_since(self, since):
        users = set()
        for user in self.__user_map:
            if self.__user_map[user].last_log_in() > time() - since:
                users.add(user)
        return users

    def refresh_user_timeout(self, username):
        # update last active time
        if username in self.__user_map:
            self.__user_map[username].refresh_user_timeout()

    def set_private_port(self, username, port):
        if username in self.__user_map:
            self.__user_map[username].set_private_port(port)

    def get_private_port(self, username):
        if username in self.__user_map:
            return self.__user_map[username].get_private_port()
        return 0

    class __Worker:
        def __init__(self, username, password, block_duration, timeout):
            self.__username = username
            self.__password = password
            self.__blocked = False
            self.__consecutive_fails = 0
            self.__blocked_since = 0
            self.__inactive_since = int(time())
            self.__blocked_users = set()
            self.__last_login = 0
            self.__private_port = 0
            self.__block_duration = block_duration
            self.__timeout = timeout
            self.__online = False

        def block(self, username):
            self.__blocked_users.add(username)

        def unblock(self, username):
            if username in self.__blocked_users:
                self.__blocked_users.remove(username)

        def set_private_port(self, port):
            self.__private_port = port

        def get_private_port(self):
            return self.__private_port

        def is_blocked_user(self, username):
            return username in self.__blocked_users

        def update(self):
            if self.__blocked and self.__blocked_since + self.__block_duration < time():
                self.__blocked = False

        def set_offline(self):
            self.__online = False
            self.__consecutive_fails = 0
            self.__blocked_since = 0
            self.__private_port = 0

        def is_online(self):
            return self.__online

        def update_time_out(self):
            # update time out status, return true if should lof out this user because of timeout
            if self.is_online() and self.__inactive_since + self.__timeout < time():
                self.set_offline()
                return True
            return False

        def refresh_user_timeout(self):
            self.__inactive_since = time()

        def last_log_in(self):
            return self.__last_login

        def authenticate(self, password_input):
            # authenticate, return the status of the updated user

            if self.__online:
                # user is already logged in
                return "ALREADY_LOGGED_IN"

            if self.__blocked:
                # user is blocked
                return "BLOCKED"

            if self.__password != password_input:
                # incorrect password
                self.__consecutive_fails += 1
                if self.__consecutive_fails >= 3:
                    self.__blocked_since = time()
                    self.__blocked = True
                    return "INVALID_PASSWORD_BLOCKED"
                return "INVALID_PASSWORD"

            # is able to login. update status
            self.__online = True
            self.__last_login = int(time())
            self.refresh_user_timeout()
            return "SUCCESS"

        def new_user_login(self):
            # is able to login. update status
            self.__online = True
            self.__last_login = int(time())
            self.refresh_user_timeout()
            return "USERNAME_NOT_EXIST"
