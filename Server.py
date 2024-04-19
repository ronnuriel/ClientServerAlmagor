import datetime
import random
import socket
import glob
import os
import subprocess
import pyautogui
import shutil

SERVER_NAME = 'ALMOGOR SERVER'


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


def get_message(s, size_of_message):
    if size_of_message == 0:
        return ''
    return s.recv(size_of_message + 1024).decode()  # Adding 1024 to clean up the rest of the data in the socket


def clean_up_remain_data_in_socket(s):
    data = s.recv(1024)
    print(f"Cleaning up remaining data: {data.decode()}")


def send_photo(conn):
    # Get the image data
    with open("screenshot.png", "rb") as f:
        image = f.read()

    image_str_len = len(image)
    print(f"Image size length: {len(str(image_str_len))}")
    print(f"Image size length: {image_str_len}")
    image_str_len = len(str(image_str_len))

    header = image_str_len.to_bytes(4, byteorder='big')

    # Send the image size
    conn.send(header + image)

    print(f"Image size length sent: {image_str_len}")


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
                    send_message(conn, "WRONG PROTOCOL!!!")
                    clean_up_remain_data_in_socket(conn)
                    continue

                data = get_message(conn, msg_len)  # Get the message from the client

                if not data:
                    send_message(conn, "WRONG PROTOCOL!!!")  # Echo back the received message
                    continue

                if len(data) != msg_len:
                    print("Invalid message received: length does not match header")
                    send_message(conn, "WRONG PROTOCOL!!!")
                    if len(data) > msg_len:
                        print(f"Cleaning up remaining data: {data[msg_len:]}")
                    continue

                if data == 'EXIT':
                    print("Client has exited")
                    break

                if data[:3] == 'DIR':
                    location = data[4:]
                    print("Client has requested for directory listing")
                    print("Location: ", location)

                    if location:
                        files = glob.glob(location + "/*.*")
                        send_message(conn, str(files))

                    else:
                        send_message(conn, "WRONG PROTOCOL!!!")  # Echo back the received message
                    continue

                if data[:6] == 'DELETE':
                    file_name = data[7:]
                    if os.path.exists(file_name):
                        os.remove(file_name)
                        send_message(conn, f"File {file_name} has been deleted")
                    else:
                        send_message(conn, f"File {file_name} does not exist")

                    continue

                if data[:4] == 'COPY':
                    if len(data.split()) != 3:
                        send_message(conn, "WRONG COPY SYNTAX!!!")
                        continue

                    file1, file2 = data[5:].split()
                    if os.path.exists(file1):
                        shutil.copy(file1, file2)
                        send_message(conn, f"File {file1} has been copied to {file2}")
                    else:
                        send_message(conn, f"File {file1} does not exist")

                    continue

                # TODO: DELETE THE FOLLOWING CODE
                if data[:7] == 'EXECUTE':
                    cmd = data[8:]
                    if os.path.isfile(cmd):
                        send_message(conn, f"Executing {cmd}")
                        try:
                            subprocess.call(cmd, shell=True)
                            send_message(conn, f"Command {cmd} has been executed")
                        except Exception as e:
                            print(f"Error executing command: {e}")
                            send_message(conn, f"Error executing command: {e}")

                    else:
                        send_message(conn, f"Command {cmd} does not exist")

                    continue

                if data[:15] == 'TAKE SCREENSHOT':
                    image = pyautogui.screenshot()
                    image.save("screenshot.png")  # I don't want to save the image
                    send_photo(conn)
                    continue

                print(f"Received from client: {data}")
                send_message(conn, "WRONG PROTOCOL!!!")  # Echo back the received message


if __name__ == "__main__":
    start_server()
