ACTIVE_USERS = []

# Returns dictionary of all users that exist in the credentials.txt file
# @return {"username": string, "password": string}
def read_users():
    users = []
    with open("credentials.txt", "r") as f:
        user_list = f.readlines()

    for user in user_list:
        user_data = user.strip().split(" ")
        users.append({"username": user_data[0], "password": user_data[1]})

    return users


# add single user with (username, password)
def add_user(username, password):
    with open("credentials.txt", "a") as f:
        user_field = f"{username} {password}\n"
        f.write(user_field)


# search user database by username
def search_user(username):
    return username in [user["username"] for user in read_users()]


def search_online_users(username):
    return username in [user["username"] for user in ACTIVE_USERS]


def auth_user(username, password):
    user_credentials = [(user["username"], user["password"]) for user in read_users()]
    return (username, password) in user_credentials


def login_user(username, password):
    # case(1): user does not exist
    if not search_user(username):
        return "user does not exist"
    # case(2): already logged on
    if search_online_users(username):
        return "already logged on"

    # case(3): username/password incorrect
    if not auth_user(username, password):
        return "username/password combo incorrect, try again"

    ACTIVE_USERS.append({"username": username, "password": password})


def logout_user(username, password):
    pass


login_user("lucasbrsa", "hi_there")
print(auth_user("lucasbrsa", "hi_there"))
