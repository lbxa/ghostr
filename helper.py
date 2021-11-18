from user import User


def check_unicast_block(sender, receiver):
    if User().is_blocked_by(blocker=receiver, blockee=sender):
        # sender blocked by receiver
        return f"TYPE: BLOCK;;WHO: {sender};;BLOCKER: {receiver};;RET: 0;;ERR: {receiver} has blocked you;;"
    else:
        return False


# def check_broadcast_block(sender):
#     user_directory = User().get_all_users()
