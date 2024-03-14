import socket


def send_message(s, msg):
    msg = msg.encode()
    msg_len = len(msg)
    header = msg_len.to_bytes(4, byteorder='big')  # Convert length to 4 bytes
    s.send(header + msg)  # Send header followed by the actual message


def start_client(server_host='127.0.0.1', server_port=65430):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, server_port))
        msg = input("Enter message: ")
        send_message(s, msg)

        while msg != 'EXIT':
            data = s.recv(1024)
            print(f"Received from server: {data.decode()}")

            msg = input("Enter message: ")
            send_message(s, msg)  # Recive the command from the user and send it to the server.


if __name__ == "__main__":
    start_client()
