# COMP3331 Assignment
# Lucas Chu Barbosa (z5259433) | 21T3
# admin.py contains all admin and management functions for all users

import sys
from time import time
from user import User


class Admin:
    # manage all user data, including credentials, block status,
    # user-to-user block status, time out, online status,
    # and last login status

    def __init__(self, block_duration, timeout):
        self.__database = {}
        self.__user_address_registry = {}
        self.__username_to_address_map = {}
        self.__block_duration = block_duration
        self.__timeout = timeout
        self.__read_credentials()

    def __read_credentials(self):
        try:
            with open("credentials.txt", "r") as credential_file:
                for credential in credential_file:
                    username, password = credential.strip().split()
                    self.__database[username] = User(username, password, self.__block_duration, self.__timeout)
        except Exception as msg:
            print(f"Error reading credentials.txt: {msg}")
            sys.exit()

    # add single user with (username, password)
    def __add_credentials(self, username, password):
        try:
            with open("credentials.txt", "a") as f:
                user_field = f"\n{username} {password}"
                f.write(user_field)
        except Exception as msg:
            print(f"Error reading credentials.txt: {msg}")
            sys.exit()

    def authenticate(self, username_input, password_input):
        if username_input not in self.__database:
            # username unknown
            self.__add_credentials(username_input, password_input)
            self.__read_credentials()
            return self.__database[username_input].authenticate(password_input)

        # else, delegate authenticate to specific user class
        return self.__database[username_input].authenticate(password_input)

    def set_address_username(self, address, username):
        self.__user_address_registry[address] = username
        self.__username_to_address_map[username] = address

    def get_username(self, address):
        if address in self.__user_address_registry:
            return self.__user_address_registry[address]
        else:
            return ""

    def get_address(self, username):
        if username in self.__username_to_address_map:
            return self.__username_to_address_map[username]
        else:
            return ""

    def set_offline(self, username):
        if username in self.__database:
            self.__database[username].set_offline()

    def update(self):
        # update all user's block status
        for user_credential in self.__database.values():
            user_credential.update()

    def block(self, from_username, to_block_username):
        if from_username in self.__database:
            self.__database[from_username].block(to_block_username)

    def unblock(self, from_username, to_block_username):
        if from_username in self.__database:
            self.__database[from_username].unblock(to_block_username)

    def is_blocked_user(self, from_username, to_block_username):
        return from_username in self.__database and self.__database[from_username].is_blocked_user(to_block_username)

    def has_user(self, username):
        return username in self.__database

    def is_online(self, username):
        return username in self.__database and self.__database[username].is_online()

    def all_users(self):
        return list(self.__database.keys())

    def get_timed_out_users(self):
        timed_out_users = set()
        for user in self.__database:
            if self.__database[user].update_time_out():
                timed_out_users.add(user)
        return timed_out_users

    def get_online_users(self):
        online_users = set()
        for user in self.__database:
            if self.__database[user].is_online():
                online_users.add(user)
        return online_users

    def get_users_logged_in_since(self, since):
        users = set()
        for user in self.__database:
            if self.__database[user].last_log_in() > time() - since:
                users.add(user)
        return users

    def refresh_user_timeout(self, username):
        # update last active time
        if username in self.__database:
            self.__database[username].refresh_user_timeout()

    def set_private_port(self, username, port):
        if username in self.__database:
            self.__database[username].set_private_port(port)

    def get_private_port(self, username):
        if username in self.__database:
            return self.__database[username].get_private_port()
        return 0
