# returns message as python dict (key, value)
def parse_message(message):
    msg_struct = {}
    for line in message.split(";;")[:-1]:
        premature_line = line.split(":")
        # print("Premanture line: ----------")
        # print(premature_line)
        premature_line[1] = premature_line[1].strip()
        msg_struct[premature_line[0]] = premature_line[1]

    return msg_struct


def message_type(message):
    return parse_message(message)["TYPE"]


def pack_message(message={}, message_type=0):
    pass


# remove first word from command "broadcast hello everyone" -> "hello everyone"
def remove_first_word(command):
    return " ".join(command.split(" ")[1:])


def unpack_message(command):
    sender = command.split(" ")[1]
    message_contents = " ".join(command.split(" ")[2:])
    return (sender, message_contents)


# if __name__ == "__main__":
#     msg1 = "TYPE: LOGON\nWHO: lucasbrsa"
#     msg2 = "TYPE: AUTH\nWHO: lucasbrsa\nPASW: hi_there"
#     msg3 = "TYPE: MSG\nFROM: lucasbrsa\nTO: broadcast\nBODY: hey there guys"
#     msg4 = f"TYPE: AUTH\nWHO: lucasbrsa\nPASW: hi_there"

#     print(parse_message(msg1)["TYPE"])
#     print(parse_message(msg2)["TYPE"])
#     print(parse_message(msg3)["TYPE"])
#     print(parse_message(msg4)["TYPE"])
