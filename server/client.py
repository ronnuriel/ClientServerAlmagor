import socket
from protocol import check_cmd, create_msg, get_msg

IP = '127.0.0.1'
PORT = 12345
SAVED_PHOTO_LOCATION = "received_screenshot.png"  # Where the client saves received screenshots

def handle_server_response(my_socket, cmd):
    """
    Receive the response from the server and handle it according to the request.
    Note that SEND_PHOTO needs special handling.
    """
    success, response = get_msg(my_socket)
    if not success:
        print("Failed to receive valid response")
        return

    if cmd.startswith("SEND_PHOTO"):
        # Here we assume the server sends the file size first, followed by the file bytes
        file_size = int(response)
        received_data = my_socket.recv(file_size)
        with open(SAVED_PHOTO_LOCATION, 'wb') as file:
            file.write(received_data)
        print(f"Photo received and saved to {SAVED_PHOTO_LOCATION}")
    else:
        print(response)

def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))

    print('Welcome to the remote computer application. Available commands are:')
    print('TAKE_SCREENSHOT, SEND_PHOTO, DIR, DELETE, COPY, EXECUTE, EXIT')

    while True:
        cmd = input("Please enter command:\n")
        if check_cmd(cmd):
            packet = create_msg(cmd)
            my_socket.send(packet)
            handle_server_response(my_socket, cmd)
            if cmd == 'EXIT':
                break
        else:
            print("Not a valid command, or missing parameters\n")

    my_socket.close()

if __name__ == '__main__':
    main()
