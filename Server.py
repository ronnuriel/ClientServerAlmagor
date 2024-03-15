import datetime
import random
import socket

SERVER_NAME = 'ALMOGOR SERVER'


def get_message(s, size_of_message):
    if size_of_message == 0:
        return ''
    return s.recv(size_of_message + 1024).decode()  # Adding 1024 to clean up the rest of the data in the socket


def clean_up_remain_data_in_socket(s):
    data = s.recv(1024)
    print(f"Cleaning up remaining data: {data.decode()}")


def start_server(host='127.0.0.1', port=65430):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        data = ''
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while data != 'EXIT':
                header = conn.recv(4)
                if len(header) == 4:
                    try:
                        msg_len = int.from_bytes(header, byteorder='big')  # Length of the message
                    except ValueError:
                        print("Invalid header received: not an integer")
                        clean_up_remain_data_in_socket(conn)
                        continue
                else:
                    print("Invalid header received: not 4 bytes")
                    conn.send("WRONG PROTOCOL!!!".encode())
                    clean_up_remain_data_in_socket(conn)
                    continue

                data = get_message(conn, msg_len)  # Get the message from the client

                if not data:
                    conn.send("WRONG PROTOCOL!!!".encode())  # Echo back the received message
                    continue

                if len(data) != msg_len:
                    print("Invalid message received: length does not match header")
                    conn.send("WRONG PROTOCOL!!!".encode())
                    if len(data) > msg_len:
                        print(f"Cleaning up remaining data: {data[msg_len:]}")
                    continue

                if data == 'EXIT':
                    print("Client has exited")
                    break

                if data == 'TIME':
                    print("Client has requested for time")
                    time = str(datetime.datetime.now().ctime())

                    conn.send(time.encode())
                    continue

                if data == 'WHOR':
                    print("Client has requested for hostname")
                    conn.send(SERVER_NAME.encode())
                    continue

                if data == 'RAND':
                    print("Client has requested for random number")
                    conn.send(str.encode(str(random.randint(1, 10))))
                    continue

                print(f"Received from client: {data}")
                conn.send("WRONG PROTOCOL!!!".encode())  # Echo back the received message


if __name__ == "__main__":
    start_server()
