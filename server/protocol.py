#   Ex. 2.7 template - protocol


LENGTH_FIELD_SIZE = 4
PORT = 8820


def check_cmd(data):
    """
    Check if the command is defined in the protocol, including all parameters
    For example, DELETE c:\work\file.txt is good, but DELETE alone is not
    """

    # (3)
    return True


def create_msg(data):
    """
    Create a valid protocol message, with length field
    """

    # (4)
    return "0002OK".encode()


def get_msg(my_socket):
    """
    Extract message from protocol, without the length field
    If length field does not include a number, returns False, "Error"
    """

    # (5)
    return True, "OK"


