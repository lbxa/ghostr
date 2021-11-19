# COMP3331 Assignment
# Lucas Chu Barbosa (z5259433) | 21T3
# user.py contains all admin and management functions for specific users

from time import time


class User:
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
        self.__is_online = False

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
        self.__is_online = False
        self.__consecutive_fails = 0
        self.__blocked_since = 0
        self.__private_port = 0

    def is_online(self):
        return self.__is_online

    def update_time_out(self):
        if self.is_online() and self.__inactive_since + self.__timeout < time():
            self.set_offline()
            return True
        return False

    def refresh_user_timeout(self):
        self.__inactive_since = time()

    def last_log_in(self):
        return self.__last_login

    def authenticate(self, password_input):

        if self.__is_online:
            return "ALREADY_LOGGED_IN"

        if self.__blocked:
            return "BLOCKED"

        if self.__password != password_input:
            self.__consecutive_fails += 1
            if self.__consecutive_fails >= 3:
                self.__blocked_since = time()
                self.__blocked = True
                return "INVALID_PASSWORD_BLOCKED"
            return "INVALID_PASSWORD"

        # is able to login. update status
        self.__is_online = True
        self.__last_login = int(time())
        self.refresh_user_timeout()
        return "SUCCESS"

    def new_user_login(self):
        # is able to login. update status
        self.__is_online = True
        self.__last_login = int(time())
        self.refresh_user_timeout()
        return "USERNAME_NOT_EXIST"
