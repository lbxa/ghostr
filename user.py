from datetime import datetime, timedelta
from constants import SERVER_ALIAS, EMPTY

ACTIVE_USERS = []
BLOCKED_USERS = []


class User:
    def __init__(self):
        self.credentials_file = "credentials.txt"

    # Returns dictionary of all users that exist in the credentials.txt file
    # @return {"username": string, "password": string}
    def read_users_file(self):
        users = []
        with open(self.credentials_file, "r") as f:
            user_list = f.readlines()

        for user in user_list:
            user_data = user.strip().split(" ")
            users.append({"username": user_data[0], "password": user_data[1]})

        return users

    # add single user with (username, password)
    def add(self, username, password):
        with open(self.credentials_file, "a") as f:
            user_field = f"{username} {password}\n"
            f.write(user_field)

    def get_all_users(self):
        return [user["username"] for user in self.read_users_file()]

    # search user database by username
    def search(self, username):
        return username in [user["username"] for user in self.read_users_file()]

    def search_online(self, username):
        return username in [user["username"] for user in ACTIVE_USERS]

    def get_all_online_users(self, except_for):
        online_users = []
        for user in ACTIVE_USERS:
            if user["username"] != except_for and not self.is_blocked_by(user["username"], except_for):
                online_users.append(user["username"])
        return online_users

    def get_all_online_users_since(self, except_for, interval):
        online_users = []
        for user in ACTIVE_USERS:
            if user["username"] != except_for and not self.is_blocked_by(user["username"], except_for):
                if datetime.now() - timedelta(0, interval, 0) <= user["logon_time"]:
                    online_users.append(user["username"])

        return online_users

    def auth(self, username, password):
        user_credentials = [(user["username"], user["password"]) for user in self.read_users_file()]
        return (username, password) in user_credentials

    # return True if blocked, False otherwise
    def is_blocked(self, username):
        for user in BLOCKED_USERS:
            if user["username"] == username:
                return datetime.now() < user["end"] if user["blocked_by"] == SERVER_ALIAS else True
        return False

    def is_blocked_by(self, blocker, blockee):
        for user in BLOCKED_USERS:
            if user["username"] == blockee and user["blocked_by"] == blocker:
                return True
        return False

    def password_block(self, username, start, end):
        global BLOCKED_USERS
        BLOCKED_USERS.append({"username": username, "start": start, "end": end, "blocked_by": SERVER_ALIAS})

    def block(self, blocker, blockee):
        global BLOCKED_USERS
        BLOCKED_USERS.append({"username": blockee, "start": EMPTY, "end": EMPTY, "blocked_by": blocker})
        # DEBUG
        print(f"BLOCKED USERS AFTER {blocker} blocked {blockee}")
        for user in ACTIVE_USERS:
            print(user)

    def unblock(self, blocker, blockee):
        global BLOCKED_USERS
        for idx, user in enumerate(BLOCKED_USERS):
            if user["username"] == blockee and user["blocked_by"] == blocker:
                del BLOCKED_USERS[idx]
        # DEBUG
        print(f"BLOCKED USERS AFTER {blocker} unblocked {blockee}")
        for user in ACTIVE_USERS:
            print(user)

    def login(self, username, password):
        global ACTIVE_USERS
        ACTIVE_USERS.append({"username": username, "password": password, "logon_time": datetime.now()})
        # DEBUG
        print(f"ACTIVE USERS AFTER {username} LOGIN")
        for user in ACTIVE_USERS:
            print(user)

    def logout(self, username):
        global ACTIVE_USERS
        ACTIVE_USERS = list(filter(lambda user: user["username"] != username, ACTIVE_USERS))
        # DEBUG
        print(f"ACTIVE USERS AFTER {username} LOGOUT")
        for user in ACTIVE_USERS:
            print(user)


# if __name__ == "__main__":
#     User().login("hans", "falcon*solo")
#     print(User().auth("hans", "falcon*solo"))
