LENGTH_FIELD_SIZE = 4
PORT = 12345


def check_cmd(cmd):
    """
    Check if the command is defined in the protocol, including all parameters
    For example, 'DELETE c:\\work\\file.txt' is good, but 'DELETE' alone is not
    """
    valid_commands = ["TAKE_SCREENSHOT", "SEND_PHOTO", "DIR", "DELETE", "COPY", "EXECUTE", "EXIT"]
    parts = cmd.split()
    if parts[0] in valid_commands:
        if parts[0] in ["DELETE", "DIR", "COPY", "EXECUTE"]:
            #TODO: Check if PARAMS are valid
            return len(parts) > 0
        return True
    return False


def create_msg(data):
    """
    Create a valid protocol message, with length field
    """
    data = data.encode()
    length = len(data)
    return f"{length:04d}".encode() + data


def get_msg(my_socket):
    """
    Extract message from protocol, without the length field
    If length field does not include a number, returns False, "Error"
    """
    length_field = my_socket.recv(LENGTH_FIELD_SIZE)
    if not length_field.isdigit():
        return False, "Error"

    length = int(length_field)
    return True, my_socket.recv(length).decode()
