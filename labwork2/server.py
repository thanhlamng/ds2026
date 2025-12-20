import os
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import Binary

SERVER_DIR = './server_files/'

if not os.path.exists(SERVER_DIR):
    os.makedirs(SERVER_DIR)
    print(f"Created server directory: {SERVER_DIR}")

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/server_files',)

with SimpleXMLRPCServer(('localhost', 8000),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()
    print("Server listening on port 8000...")

    def put(file_name, data):
        file_path = os.path.join(SERVER_DIR, file_name)
        
        if os.path.exists(file_path):
            return "ERROR: File exists on server."
        else:
            try:
                with open(file_path, 'wb') as f:
                    f.write(data.data)
                return f"Upload completed: {file_name}"
            except Exception as e:
                return f"ERROR: {e}"
    server.register_function(put, "put")

    def get(file_name):
        file_path = os.path.join(SERVER_DIR, file_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    return Binary(f.read()) 
            except Exception as e:
                return f"ERROR during read: {e}"
        else:
            return "ERROR: File not found"
    server.register_function(get, "get")

    def ls():
        files = os.listdir(SERVER_DIR) 
        if not files:
            return "Directory is empty."
        return "\n".join(files)
    server.register_function(ls, "ls")

    def rename(old_name, new_name):
        old_path = os.path.join(SERVER_DIR, old_name)
        new_path = os.path.join(SERVER_DIR, new_name)
        
        if not os.path.exists(old_path):
            return f"ERROR: File '{old_name}' not found"        
        try:
            os.rename(old_path, new_path)
            return f"Renamed '{old_name}' to '{new_name}'"
        except Exception as e:
            return f"ERROR: {e}"
    server.register_function(rename, "rename")

    server.serve_forever()
