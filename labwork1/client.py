import socket
import os
import sys

HOST = '127.0.0.1'
PORT = 65432
BUFFER_SIZE = 1024

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")
    except ConnectionRefusedError:
        print("Can not connect to server.")
        sys.exit(1)

    print("Available commands: ls, get, put, delete, rename, quit/bye")

    while True:
        try:
            user_input = input("client> ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()

            if command in ['bye', 'quit']:
                client_socket.send(command.encode('utf-8'))
                break

            # put command
            elif command == 'put':
                if len(parts) < 2:
                    print("Usage: put <local_file> [remote_filename]")
                    continue

                local_path = parts[1]
                remote_name = parts[2] if len(parts) > 2 else os.path.basename(local_path)

                if not os.path.isfile(local_path):
                    print(f"ERROR: File '{local_path}' does not exist on client machine.")
                    continue

                filesize = os.path.getsize(local_path)
                
                header = f"put {remote_name} {filesize}"
                client_socket.send(header.encode('utf-8'))

                response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                
                if response == "OK":
                    print(f"Uploading {local_path} ({filesize} bytes)...")
                    with open(local_path, 'rb') as f:
                        while True:
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read: break
                            client_socket.sendall(bytes_read)
                    print("Upload complete.")
                else:
                    print(f"Server rejected upload: {response}")

            elif command == 'get':
                if len(parts) < 2:
                    print("Usage: get <remote_file> [local_filename]")
                    continue

                remote_file = parts[1]
                local_name = parts[2] if len(parts) > 2 else remote_file

                client_socket.send(f"get {remote_file}".encode('utf-8'))

                response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                if response.startswith("OK"):
                    _, size_str = response.split()
                    filesize = int(size_str)
                    print(f"Downloading {remote_file} ({filesize} bytes)...")
                    
                    bytes_received = 0
                    with open(local_name, 'wb') as f:
                        while bytes_received < filesize:
                            chunk = client_socket.recv(min(BUFFER_SIZE, filesize - bytes_received))
                            if not chunk: break
                            f.write(chunk)
                            bytes_received += len(chunk)
                    print("Download complete.")
                else:
                    print(f"Server error: {response}")

            elif command in ['ls', 'delete', 'rename']:
                client_socket.send(user_input.encode('utf-8'))
                response = client_socket.recv(4096).decode('utf-8')
                print(response)

            else:
                print("Unknown command.")

        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            break

    client_socket.close()

if __name__ == '__main__':
    main()
