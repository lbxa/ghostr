from user import User


def check_unicast_block(sender, receiver):
    # sender blocked by receiver
    err_msg = f"TYPE: BLOCK;;WHO: {sender};;BLOCKER: {receiver};;RET: 0;;ERR: {receiver} has blocked you;;"
    return err_msg if User().is_blocked_by(blocker=receiver, blockee=sender) else False


def check_broadcast_block(sender):
    err_txt = "Your message could not be delivered to some recipients"
    for user in User().get_all_users():
        if User().is_blocked_by(blocker=user, blockee=sender):
            return f"TYPE: BLOCK;;WHO: {sender};;BLOCKER: {user};;RET: 0;;ERR: {err_txt};;"
    return False
