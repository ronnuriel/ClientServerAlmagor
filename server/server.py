import shutil
import socket
import os
import subprocess

import pyautogui

# Constants for the server
IP = 'localhost'
PORT = 12345
PHOTO_PATH = "screenshot.png"  # Example path where the screenshot will be saved


def check_client_request(cmd):
    """Check if the command and params from the client are valid."""
    # Example command: "DIR c:\\cyber"
    parts = cmd.split()
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


def handle_client_request(command, params):
    """Generate a response based on the command and parameters."""
    if command == "DIR":
        # List directory contents
        try:
            files = os.listdir(params[0])
            response = '\n'.join(files)
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
            file_size = os.path.getsize(PHOTO_PATH)
            response = str(file_size)
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
            cmd = client_socket.recv(1024).decode()
            if not cmd:
                break  # client has closed the connection

            valid_cmd, command, params = check_client_request(cmd)
            if valid_cmd:
                response = handle_client_request(command, params)
                client_socket.sendall(response.encode())
            else:
                client_socket.sendall('Invalid command or parameters'.encode())
    finally:
        client_socket.close()
        server_socket.close()
        print("Connection closed.")


def test_check_client_request():
    # WORKING DIR PATH
    current_directory = os.getcwd()
    assert check_client_request(f"DIR {current_directory}/") == (True, 'DIR', [current_directory + '/'])
    # WORKING FILE PATH
    assert check_client_request(f"DELETE {current_directory}/example.txt") == (True, 'DELETE', [current_directory + '/example.txt'])
    # WORKING FILE PATH
    assert check_client_request(f"COPY {current_directory}/source.txt {current_directory}/dest.txt") == (True, 'COPY', [current_directory + '/source.txt', current_directory + '/dest.txt'])
    # WORKING COMMAND
    assert check_client_request(f"EXECUTE {current_directory}/test.sh") == (True, 'EXECUTE', [f"{current_directory}/test.sh"])
    # WORKING DIR PATH
    assert check_client_request("TAKE_SCREENSHOT") == (True, 'TAKE_SCREENSHOT', [])
    # WORKING DIR PATH
    assert check_client_request("SEND_PHOTO") == (True, 'SEND_PHOTO', [])
    # INVALID COMMAND
    assert check_client_request("INVALID") == (False, 'INVALID', [])
    # INVALID COMMAND
    assert check_client_request("DIR") == (False, 'DIR', [])
    # INVALID COMMAND
    assert check_client_request("DELETE") == (False, 'DELETE', [])
    # INVALID COMMAND
    assert check_client_request("COPY") == (False, 'COPY', [])


if __name__ == '__main__':
    print(check_client_request("DIR c:\\cyber"))  # Should return (True, 'DIR', ['c:\\cyber'])
    print(check_client_request("DELETE example.txt"))  # Example assuming 'example.txt' exists
    print(check_client_request("COPY source.txt dest.txt"))  # Example assuming 'source.txt' exists
    print(check_client_request("EXECUTE notepad.exe"))  # Example assuming notepad.exe exists
    # print(check_client_request("TAKE_SCREENSHOT"))  # Should return (True, 'TAKE_SCREENSHOT', [])
    print(check_client_request("SEND_PHOTO"))  # Should return (True, 'SEND_PHOTO', [])
    # main()
