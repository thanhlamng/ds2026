import socket
import os

HOST = '127.0.0.1'
PORT = 65432
BUFFER_SIZE = 1024

def send_message(sock, message):
    sock.send(message.encode('utf-8'))

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    
    server_socket.bind((HOST, PORT))
    server_socket.listen()    
    server_socket.settimeout(1.0)
    
    print(f"Server listening on {HOST}:{PORT}...")

    try:
        while True:
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue
            
            conn.settimeout(None)
            
            print(f"Connected by {addr}")

            try:
                while True:
                    data = conn.recv(BUFFER_SIZE).decode('utf-8')
                    if not data: break
                    
                    parts = data.split()
                    command = parts[0]

                    # put command
                    if command == 'put':
                        filename = parts[1]
                        filesize = int(parts[2])

                        if os.path.exists(filename):
                            send_message(conn, "ERROR: File exists on server.")
                        else:
                            send_message(conn, "OK")
                            bytes_received = 0
                            with open(filename, 'wb') as f:
                                while bytes_received < filesize:
                                    chunk = conn.recv(min(BUFFER_SIZE, filesize - bytes_received))
                                    if not chunk: break
                                    f.write(chunk)
                                    bytes_received += len(chunk)
                            print(f"Received: {filename}")

                    elif command == 'get':
                        filename = parts[1]
                        if os.path.exists(filename):
                            filesize = os.path.getsize(filename)
                            send_message(conn, f"OK {filesize}")
                            with open(filename, 'rb') as f:
                                while True:
                                    bytes_read = f.read(BUFFER_SIZE)
                                    if not bytes_read: break
                                    conn.sendall(bytes_read)
                            print(f"Sent: {filename}")
                        else:
                            send_message(conn, "ERROR: File not found")

                    elif command == 'ls':
                        files = os.listdir('.')
                        send_message(conn, "\n".join(files) if files else "Empty dir")

                    elif command == 'delete':
                        filename = parts[1]
                        if os.path.exists(filename):
                            os.remove(filename)
                            send_message(conn, f"Deleted {filename}")
                        else:
                            send_message(conn, "ERROR: File not found")

                    elif command == 'rename':
                        if os.path.exists(parts[1]):
                            os.rename(parts[1], parts[2])
                            send_message(conn, "Renamed")
                        else:
                            send_message(conn, "ERROR: File not found")

                    elif command in ['quit', 'bye']:
                        print(f"Client {addr} disconnected")
                        break

            except Exception as e:
                print(f"Connection error: {e}")
            finally:
                conn.close()

    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == '__main__':
    start_server()
