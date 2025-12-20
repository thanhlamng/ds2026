from mpi4py import MPI
import os

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 1:
    while True:
        cmd = comm.recv(source=0, tag=0)
        if cmd == "exit":
            break
        parts = cmd.split()
        if len(parts) == 0:
            comm.send("Invalid command", dest=0, tag=7)
            continue

        if parts[0] == "ls":
            files = "\n".join(os.listdir("."))
            comm.send(files, dest=0, tag=1)

        elif parts[0] == "get":
            if len(parts) < 2:
                comm.send(0, dest=0, tag=2)
                continue
            filename = parts[1]
            if not os.path.exists(filename):
                comm.send(-1, dest=0, tag=2)
                continue
            with open(filename, "rb") as f:
                data = f.read()
            comm.send(len(data), dest=0, tag=2)
            if len(data) > 0:
                comm.Send([data, MPI.BYTE], dest=0, tag=3)

        elif parts[0] == "put":
            if len(parts) < 2:
                comm.send("Invalid filename", dest=0, tag=7)
                continue

            filename = parts[1]
            size = comm.recv(source=0, tag=4)

            buf = bytearray(size)

            if size > 0:
                comm.Recv([buf, MPI.BYTE], source=0, tag=5)
                with open(filename, "wb") as f:
                    f.write(buf)

            comm.send("Upload finished", dest=0, tag=6)

        else:
            comm.send("Unknown command", dest=0, tag=7)

if rank == 0:
    while True:
        print("-"*50)
        cmd = input().strip()
        if cmd == "":
            continue
        comm.send(cmd, dest=1, tag=0)
        if cmd == "exit":
            break
        parts = cmd.split()

        if parts[0] == "ls":
            result = comm.recv(source=1, tag=1)
            print(result)

        elif parts[0] == "get":
            if len(parts) < 2:
                print("Usage: get <file>")
                continue
            filename = parts[1]
            size = comm.recv(source=1, tag=2)
            if size == -1:
                print("File not found on server")
                continue
            buf = bytearray(size)
            if size > 0:
                comm.Recv([buf, MPI.BYTE], source=1, tag=3)
                with open("get_" + filename, "wb") as f:
                    f.write(buf)
                print("Downloaded:", filename)
            else:
                with open("get_" + filename, "wb") as f:
                    pass
                print("Downloaded empty file:", filename)

        elif parts[0] == "put":
            if len(parts) < 2:
                print("Usage: put <file>")
                continue
            filename = parts[1]
            if not os.path.exists(filename):
                print("Local file not found")
                continue
            with open(filename, "rb") as f:
                data = f.read()
            size = len(data)
            comm.send(size, dest=1, tag=4)
            if size > 0:
                comm.Send([data, MPI.BYTE], dest=1, tag=5)
            msg = comm.recv(source=1, tag=6)
            print(msg)

        else:
            result = comm.recv(source=1, tag=7)
            print(result)
