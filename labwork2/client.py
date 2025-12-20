import xmlrpc.client
import os
import sys

SERVER_DIR = "http://localhost:8000/server_files"

try:
    proxy = xmlrpc.client.ServerProxy(SERVER_DIR)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

if __name__ == "__main__":
    while True:
        inp = input("client> ").strip()

        if inp == "ls":
            result = proxy.ls()
            print(result)

        elif inp.startswith("put "):
            parts = inp.split(" ", 1)
            if len(parts) == 2:
                file_name = parts[1]
                if not os.path.exists(file_name):
                    print("ERROR: file not found")
                else:
                    with open(file_name, "rb") as handle:
                        data = xmlrpc.client.Binary(handle.read())
                    result = proxy.put(os.path.basename(file_name), data)
                    print(result)
            else:
                print("Usage: put <filename>")

        elif inp.startswith("get "):
            parts = inp.split(" ", 1)
            if len(parts) == 2:
                file_name = parts[1]
                result = proxy.get(file_name)
                if isinstance(result, str) and result.startswith("ERROR"):
                    print(result)
                else:
                    with open(file_name, "wb") as handle:
                        handle.write(result.data)
                    print("Download successful")
            else:
                print("Usage: get <filename>")

        elif inp.startswith("rename "):
            parts = inp.split(" ")
            if len(parts) == 3:
                old_name = parts[1]
                new_name = parts[2]
                result = proxy.rename(old_name, new_name)
                print(result)
            else:
                print("Usage: rename <old> <new>")

        elif inp == "exit":
            sys.exit(0)

        else:
            print("Commands: ls, put <file>, get <file>, rename <old> <new>, exit")
