import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65431


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
