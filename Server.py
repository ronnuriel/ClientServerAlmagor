import datetime
import random
import socket
import glob
import os
import subprocess
# import pyautogui
import shutil

SERVER_NAME = 'ALMOGOR SERVER'


def get_message(s, size_of_message):
    if size_of_message == 0:
        return ''
    return s.recv(size_of_message + 1024).decode()  # Adding 1024 to clean up the rest of the data in the socket


def clean_up_remain_data_in_socket(s):
    data = s.recv(1024)
    print(f"Cleaning up remaining data: {data.decode()}")


def start_server(host='127.0.0.1', port=65431):
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

                if data[:3] == 'DIR':
                    location = data[4:]
                    print("Client has requested for directory listing")
                    print("Location: ", location)

                    if location:
                        files = glob.glob(location + "/*.*")
                        conn.send(str(files).encode())

                    else:
                        conn.send("WRONG PROTOCOL!!!".encode())  # Echo back the received message
                    continue

                if data[:6] == 'DELETE':
                    file_name = data[7:]
                    if os.path.exists(file_name):
                        os.remove(file_name)
                        conn.send(f"File {file_name} has been deleted".encode())
                    else:
                        conn.send(f"File {file_name} does not exist".encode())

                    continue

                if data[:4] == 'COPY':
                    if len(data.split()) != 3:
                        conn.send("WRONG COPY SYNTAX!!!".encode())
                        continue

                    file1, file2 = data[5:].split()
                    if os.path.exists(file1):
                        shutil.copy(file1, file2)
                        conn.send(f"File {file1} has been copied to {file2}".encode())
                    else:
                        conn.send(f"File {file1} does not exist".encode())

                    continue

                #TODO: DELETE THE FOLLOWING CODE
                if data[:7] == 'EXECUTE':
                    cmd = data[8:]
                    if os.path.isfile(cmd):
                        conn.send(f"Executing {cmd}".encode())
                        try:
                            subprocess.call(cmd, shell=True)
                            conn.send(f"Command {cmd} has been executed".encode())
                        except Exception as e:
                            print(f"Error executing command: {e}")
                            conn.send(f"Error executing command: {e}".encode())

                    else:
                        conn.send(f"Command {cmd} does not exist".encode())

                    continue

                if data == 'TAKE SCREENSHOT':
                    continue

                print(f"Received from client: {data}")
                conn.send("WRONG PROTOCOL!!!".encode())  # Echo back the received message


if __name__ == "__main__":
    start_server()
