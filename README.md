# Assignment Report

Lucas Barbosa (z5259433) COMP3331 21T3

# 1. Installation

## 1.1. Pyenv

Using Python version 3.7.0 (installed locally with pyenv) and managed using venv. 

```
$ pyenv install 3.7.0
$ pyenv local 3.7.0
$ python -m venv .venv
$ . .venv/bin/activate
(.venv) $ ...
```

For VSCode venv configuration add these lines to the `.vscode/settings.json` file

```json
"python.terminal.activateEnvironment": true
```

## 1.2. Regular Python

The version of Python used for this project was `3.7.0`.

## 1.3. Usage

On CSE machines:

- Server
    
    ```
    python3 server.py 3331 10 120
    ```
    
- Client
    
    ```
    python3 client.py 3331
    ```
    

# 2. Design Choices

## 2.1. Software

- Originally I designed an overcomplicated messaging protocol (XMPP) which made parsing messages between server and client more error prone.
    - A simple fix was to switch JSON format. The obvious advantages its lightweightness, user-friendlyness and wide adoption.
- Python was the choice of programming language because of its simplicity, especially for socket programming. Java and C would result in many more lines of code. The **tradeoff** was type and memory safety in exchange for a faster production time. This was a crucial factor considering the numerous deadlines in the final weeks of the term.
- Multi-threading was used heavily throughout both the client, server and P2P programs. Threads brought more flexibilty and control instead of using the `select` module.
    - Threads are easily inheritered by custom classes which carry all the functionality to make sending and receiving data asynchronously effortless.
    - Killing threads was very easy and made the program more stable in the case of an unexpected socket failure.
- Design patterns such as lookup tables were used to elliminate giant if/else blocks where possible (evident in client.py)

## 2.1. Data Structures

- Python sets were used where a data structure that ensured no duplicate items was needed.
- Classes were used to encapsulate multiple functions that belonged to the same domain of functionality (e.g. User class in `user.py`)
- Codebase was split into multiple files (Python modules) for organisation based on functionality
    - [server.py](http://server.py) handles all the server functionality
    - [client.py](http://client.py) handles all client functionality including P2P connections
    - [user.py](http://user.py) contains all management and CRUD operations for users
    - [protocol.py](http://protocol.py) contains all functions responsible for parsing messages between server and client
    - [library.py](http://library.py) contains any helper or auxiliary methods
    - [constants.py](http://constants.py) holds all constant values common to all modules

# 3. Protocol

For this assignment, I am adapting my own messaging protocol which is inspired by the [XMPP protocol](https://en.wikipedia.org/wiki/XMPP) used by WhatsApp.

Eventually it became way too overkill and I integrated it with JSON to simplify the program logic. Having a more complex protocol layer also made the server more prone to message parsing and encoding errors. 

## 3.1. Logging On

```
# Request
TYPE: LOGON;;
WHO: <username>;;

# Response
TYPE: LOGON;;
RET: <1|0>;;
NEW: <1|0>;;
ERR: <0|string>;;
```

### 3.1.1. Logged In

The server will notify the client when a user has successfully logged in

```
# Response
TYPE: LOGGEDIN;;
WHO: <username>;;
```

## 3.2. Auth

```
# Request
TYPE: AUTH;;
WHO: <username>;;
PASW: <password>;;
NEW: <1|0>;;

# Response
TYPE: AUTH;;
PASW: <1|0>;;
ATMP: <int>;;
```

```json
{
  "action": "login",
  "username": "username",
  "password": "password",
	"private_port": "private_recv_port"
}
```

| action | Description of action the server is taking next. |
| --- | --- |
| username | String |
| password | String |
| private_port | Each user is assigned a private port upon authentication. This enables the P2P connection for private messaging.  |

## 3.3. Messaging

For a unicast message (send and received by one person):

```
TYPE: MSG;;
FROM: <username>;;
TO:   <username>;;
BODY: <string>;;
```

For a broadcasted message (sent by one and receivd by many):

```
TYPE: BROADCAST;;
FROM: <username>;;
BODY: <string>;;
```

```json
{
  "action": "message",
  "message": "message_contents",
	"user": "username"
}
```

## 3.4. Auxilliary Commands

### 3.4.1. Whoelse

```
# Request
TYPE: WHOELSE;;
FROM: <username>;;

# Response
TYPE: WHOELSE;;
FROM: <username>;;
BODY: <string>;;
```

| TYPE | Command signature |
| --- | --- |
| FROM | The user who issued the command |
| BODY | Comma-separated list of names of users that are currently online |

### 3.4.2. Whoelsesince

```
# Request
TYPE: WHOELSESINCE;;
WHEN: <time>;;
FROM: <username>;;

# Response
TYPE: WHOELSESINCE;;
WHEN: <time>;;
FROM: <username>;;
BODY: <string>;;
```

| TYPE | Command signature |
| --- | --- |
| WHEN | Time to check since users were last active |
| FROM | The user who issued the command |
| BODY | Comma-separated list of names of users that are currently online since TIME x in seconds |

## 3.5. Blocking

Blocks user with a `username` for an indefinite period of time.

```
# Request
TYPE: BLOCK|UNBLOCK;;
WHO: <blockee>;;
BLOCKER: <username>;;

# Response
TYPE: BLOCK|UNBLOCK;;
WHO: <blockee>;;
BLOCKER: <username>;;
RET: <1|0>;;
ERR: <0|string>;;
```

### 3.5.1. Server Blocking

If a user is blocked by the server from multiple incorrect password attempts the field in the blocked data structure would look like this:

```json
{
	"username": "string",
	"start": "string",
	"end": "string",
	"blocked_by": "!SERVER!"
}
```

| START | Time when server blocked user. |
| --- | --- |
| END | Timestamp for when server blocking expires. |
| BLOCKED_BY | Differentiates between regular use and daemon process. |

### 3.5.2. User Blocking

If a user blocks another user manually it will look slightly differently:

```json
{
	"username": "string",
	"start": "",
	"end": "",
	"blocked_by": "string"
}
```

| START | Not required. |
| --- | --- |
| END | Not required. |
| BLOCKED_BY | Regular user who has blocked username |

When a user is blocked/unblocked by another user the JSON message follows this structure:

```json
{
  "action": "block/unblock",
  "user": "username",
}
```

## 3.6. Private

### 3.6.1. Start Private

```
# Request
TYPE: PRIVREQ;;
TO: <username>;;
FROM: <username>;;

# Response
TYPE: PRIVREQ;;
TO: <username>;;
FROM: <username>;;
RET: <0|1>;;
DEST: <port>;;
```

| TO | User on the other side of the private message request. |
| --- | --- |
| RET | Flag to verify whether user has accepted the invitation to a private chat. |
| DEST | Port destination for the current client to communicate with in order to bypass the server. |

### 3.6.2. Private Messages

```
# Request
TYPE: PRIVMSG;;
TO: <username>;;
FROM: <username>;;
BODY: <string>;;

# Response
TYPE: PRIVMSG;;
TO: <username>;;
FROM: <username>;;
BODY: <string>;;
```

### 3.6.3. Stop Private

```
# Request
TYPE: PRIVSTOP;;
TO: <username>;;
FROM: <username>;;

# Response
TYPE: PRIVSTOP;;
TO: <username>;;
FROM: <username>;;
RET: <0|1>;;
```

## 3.7 Logout

```
# Request
TYPE: LOGOUT;;
WHO: <username>;;

# Response
TYPE: LOGOUT;;
WHO: <username>;;

# Response
TYPE: LOGGEDOUT;;
WHO: <username>;;
```

# 4. Improvements

- Add a type-checking system for Python to ensure maximal type safety (such as mypy)
- More error checking for incorrect command syntax from the user
- Adding a `--help` option that lists all available commands and how to use them
- Support for file upload and download
- Support for communicating beyond a single machine (hosting on a web server)

# 5. Acknowledgments

- COMP3331 21T3 provided [TCPClient.py](http://TCPClient.py) and [TCPServer.py](http://TCPServer.py) multi-threaded examples
- Rui Li's explanation of P2P during Week 10 Lab
- Salil's COMP331 Lecture material on TCP connections and socket programming
- Various Youtube tutorials on Python socket programming and multi-threading
- [Stackoverflow.com](http://Stackoverflow.com) for Pythonic design principles and syntactical sugar
    - Example of how to print to the terminal safely when asynchronously receiving messages from the server that will also be displayed on the terminal
        
        ```python
        import readline
        def chat_print(*args):
            sys.stdout.write("\r" + " " * (len(readline.get_line_buffer()) + 2) + "\r")
            print(*args)
            sys.stdout.write("# " + readline.get_line_buffer())
            sys.stdout.flush()
        ```
