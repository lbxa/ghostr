from datetime import datetime

ACTIVE_USERS = []
BLOCKED_USERS = []


class User:
    def __init__(self):
        self.credentials_file = "credentials.txt"

    # Returns dictionary of all users that exist in the credentials.txt file
    # @return {"username": string, "password": string}
    def readall(self):
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

    # search user database by username
    def search(self, username):
        return username in [user["username"] for user in self.readall()]

    def search_online(self, username):
        print("Currently online")
        print(ACTIVE_USERS)
        return username in [user["username"] for user in ACTIVE_USERS]

    def get_all_online_users(self):
        return [user["username"] for user in ACTIVE_USERS]

    def auth(self, username, password):
        user_credentials = [(user["username"], user["password"]) for user in self.readall()]
        return (username, password) in user_credentials

    # return True if blocked, False otherwise
    def is_blocked(self, username):
        for user in BLOCKED_USERS:
            if user["username"] == username:
                return datetime.now() < user["end"]
        return False

    def block(self, username, start, end, by=False):
        global BLOCKED_USERS
        if by:
            BLOCKED_USERS.append({"username": username, "start": start, "end": end, "by": by})
        else:
            BLOCKED_USERS.append({"username": username, "start": start, "end": end})
        return True

    def login(self, username, password):
        global ACTIVE_USERS
        ACTIVE_USERS.append({"username": username, "password": password})

    def logout(self, username):
        global ACTIVE_USERS
        ACTIVE_USERS = list(filter(lambda user: user["username"] != username, ACTIVE_USERS))


# if __name__ == "__main__":
#     User().login("hans", "falcon*solo")
#     print(User().auth("hans", "falcon*solo"))
