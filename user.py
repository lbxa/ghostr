from constants import ERR_WRONG_PASW, ERR_INVALID_USER, ERR_ALREADY_LOGGED_IN


class User:
    ACTIVE_USERS = []

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

    def search_active(self, username):
        return username in [user["username"] for user in self.ACTIVE_USERS]

    def auth(self, username, password):
        user_credentials = [(user["username"], user["password"]) for user in self.readall()]
        return (username, password) in user_credentials

    def login(self, username, password):
        # case(1): user does not exist
        if not self.search(username):
            print("user does not exist")
            return ERR_INVALID_USER

        # case(2): already logged on
        if self.search_active(username):
            print("already logged on")
            return ERR_ALREADY_LOGGED_IN

        # case(3): username/password incorrect
        if not self.auth(username, password):
            print("username/password combo incorrect, try again")
            return ERR_WRONG_PASW

        self.ACTIVE_USERS.append({"username": username, "password": password})
        return True

    def logout_user(self, username, password):
        pass


# if __name__ == "__main__":
#     User().login("hans", "falcon*solo")
#     print(User().auth("hans", "falcon*solo"))
