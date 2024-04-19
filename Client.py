import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65431

def get_message(s, size_of_message):
    if size_of_message == 0:
        return ''
    return s.recv(size_of_message + 1024).decode()  # Adding 1024 to clean up the rest of the data in the socket


def send_message(s, msg):
    msg = msg.encode()
    msg_len = len(msg)
    try:
        header = msg_len.to_bytes(4, byteorder='big')  # Convert length to 4 bytes
    except OverflowError:
        print("Message too long EXITS")
        msg = "EXIT".encode()
        s.send(len(msg).to_bytes(4, byteorder='big') + msg)  # Send header followed by the actual message
        return

    s.send(header + msg)  # Send header followed by the actual message

def clean_up_remain_data_in_socket(s):
    data = s.recv(1024)
    print(f"Cleaning up remaining data: {data.decode()}")


def start_client(server_host='127.0.0.1', server_port=65431):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, server_port))
        msg = input("Enter message: ")
        send_message(s, msg)

        while msg != 'EXIT':
            header = s.recv(4)
            if len(header) == 4:
                try:
                    msg_len = int.from_bytes(header, byteorder='big')  # Length of the message
                except ValueError:
                    print("Invalid header received: not an integer")
                    clean_up_remain_data_in_socket(s)
                    continue
            else:
                print("Invalid header received: not 4 bytes")
                clean_up_remain_data_in_socket(s)
                continue

            data = get_message(s, msg_len)  # Get the message from the client

            print(f"Received: {data}")


            msg = input("Enter message: ")
            send_message(s, msg)  # Recive the command from the user and send it to the server.


if __name__ == "__main__":
    start_client()
