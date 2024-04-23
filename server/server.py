import shutil
import socket
import os
import subprocess
from protocol import create_msg, get_msg
import glob
import pyautogui

# Constants for the server
IP = '127.0.0.1'
PORT = 1234
PHOTO_PATH = "screenshot.png"  # Example path where the screenshot will be saved


def check_client_request(cmd):
    """Check if the command and params from the client are valid."""
    # Example command: "'0051DIR /Users/ronnuriel/git/ClientServerAlmagor/server'"
    if not cmd[0]:
        return False, "", []

    parts = cmd[1].split()

    command = parts[0]
    params = parts[1:]

    # Example: Check if the command is 'DIR' and if the directory exists
    if command == "DIR" and len(params) > 0 and os.path.isdir(params[0]):
        return True, command, params
    # Example: Check if the command is 'DELETE' and if the file exists
    elif command == "DELETE" and len(params) > 0 and os.path.isfile(params[0]):
        return True, command, params
    # Example: Check if the command is 'COPY' and if the source file exists
    elif command == "COPY" and len(params) > 0 and os.path.isfile(params[0]):
        return True, command, params
    # Example: Check if the command is 'EXECUTE' and if the command exists
    elif command == "EXECUTE" and len(params) > 0 and shutil.which(params[0]):
        return True, command, params
    # Example: Check if the command is 'TAKE_SCREENSHOT' and if the path exists
    elif command == "TAKE_SCREENSHOT":
        return True, command, params
    # Example: Check if the command is 'SEND_PHOTO'
    elif command == "SEND_PHOTO":
        return True, command, params
    else:
        return False, command, params


def handle_client_request(command, params, client_socket):
    """Generate a response based on the command and parameters."""
    if command == "DIR":
        # List directory contents
        try:
            response = str(glob.glob(params[0] + "/*.*"))
        except OSError as e:
            response = f'Error: {str(e)}'

    elif command == "DELETE":
        # Delete a file
        try:
            os.remove(params[0])
            response = f'File {params[0]} has been deleted'
        except OSError as e:
            response = f'Error: {str(e)}'

    elif command == "COPY":
        # Copy a file
        try:
            shutil.copy(params[0], params[1])
            response = f'File {params[0]} has been copied to {params[1]}'
        except OSError as e:
            response = f'Error: {str(e)}'

    elif command == "EXECUTE":
        # Execute a command
        try:
            subprocess.call(params[0], shell=True)
            response = f'Command {params[0]} has been executed'
        except Exception as e:
            response = f'Error: {str(e)}'

    elif command == "TAKE_SCREENSHOT":
        # Take a screenshot
        try:
            pyautogui.screenshot().save(PHOTO_PATH)
            response = 'Screenshot taken'
        except Exception as e:
            response = f'Error: {str(e)}'


    elif command == "SEND_PHOTO":
        # Send the size of the photo
        try:
            if not os.path.isfile(PHOTO_PATH):
                response = 'Error: Screenshot not found'
                return response

            file_size = os.path.getsize(PHOTO_PATH)
            response = str(file_size)
            res = create_msg(response)
            client_socket.sendall(res)

            with open(PHOTO_PATH, 'rb') as file:
                photo = file.read()
            response = photo
            client_socket.sendall(response)
            return

        except OSError as e:
            response = f'Error: {str(e)}'
    else:
        response = 'Unsupported command'
    return response


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(1)
    print(f"Listening for connections on {IP}:{PORT}...")

    client_socket, client_address = server_socket.accept()
    print(f"Connected to {client_address}")

    try:
        while True:
            # Receiving the command from the client
            cmd = get_msg(client_socket)

            if not cmd:
                break  # client has closed the connection

            valid_cmd, command, params = check_client_request(cmd)
            if valid_cmd:
                response = handle_client_request(command, params, client_socket)

                if command == "SEND_PHOTO" and response != 'Error: Screenshot not found':
                    continue

                res = create_msg(response)
                client_socket.sendall(res)
            else:
                client_socket.sendall('Invalid command or parameters'.encode())
    finally:
        client_socket.close()
        server_socket.close()
        print("Connection closed.")


if __name__ == '__main__':
    main()

# def test_check_client_request():
#     # WORKING DIR PATH
#     current_directory = os.getcwd()
#
#     assert check_client_request(f"DIR {current_directory}/") == (True, 'DIR', [current_directory + '/'])
#     # WORKING FILE PATH
#     assert check_client_request(f"DELETE {current_directory}/example.txt") == (
#     True, 'DELETE', [current_directory + '/example.txt'])
#     # WORKING FILE PATH
#     assert check_client_request(f"COPY {current_directory}/source.txt {current_directory}/dest.txt") == (
#     True, 'COPY', [current_directory + '/source.txt', current_directory + '/dest.txt'])
#     # WORKING COMMAND
#     assert check_client_request(f"EXECUTE {current_directory}/test.sh") == (
#     True, 'EXECUTE', [f"{current_directory}/test.sh"])
#     # WORKING DIR PATH
#     assert check_client_request("TAKE_SCREENSHOT") == (True, 'TAKE_SCREENSHOT', [])
#     # WORKING DIR PATH
#     assert check_client_request("SEND_PHOTO") == (True, 'SEND_PHOTO', [])
#     # INVALID COMMAND
#     assert check_client_request("INVALID") == (False, 'INVALID', [])
#     # INVALID COMMAND
#     assert check_client_request("DIR") == (False, 'DIR', [])
#     # INVALID COMMAND
#     assert check_client_request("DELETE") == (False, 'DELETE', [])
#     # INVALID COMMAND
#     assert check_client_request("COPY") == (False, 'COPY', [])
