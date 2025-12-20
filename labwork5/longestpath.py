from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def divide_input(paths, num_parts):
    total_paths = len(paths)
    base_size = total_paths // num_parts
    remainder = total_paths % num_parts

    chunks = []
    start = 0
    for i in range(num_parts):
        chunk_size = base_size + (1 if i < remainder else 0)
        chunk = paths[start:start + chunk_size]
        chunks.append(chunk)
        start += chunk_size
    return chunks

def local_process(chunk):

    if not chunk:
        return (0, [])

    max_len = max(len(path.strip()) for path in chunk)
    longest_in_chunk = [path.strip() for path in chunk if len(path.strip()) == max_len]
    return (max_len, longest_in_chunk)

if rank == 0:
    if len(sys.argv) < 2:
        print("Usage: mpirun -n <size> python longest_path.py file1.txt file2.txt ...")
        sys.exit(1)

    all_paths = []
    for filename in sys.argv[1:]:
        try:
            with open(filename, 'r') as f:
                all_paths.extend(f.readlines())
        except IOError:
            print(f"Error reading {filename}")
            sys.exit(1)

    all_paths = [p.strip() for p in all_paths if p.strip()]

    chunks = divide_input(all_paths, size)
else:
    chunks = None

local_chunk = comm.scatter(chunks, root=0)
local_max_len, local_longest = local_process(local_chunk)
all_results = comm.gather((local_max_len, local_longest), root=0)

if rank == 0:
    if not all_results:
        print("No paths found.")
        sys.exit(0)

    global_max_len = max(m for m, _ in all_results)

    longest_paths = []
    for m, paths in all_results:
        if m == global_max_len:
            longest_paths.extend(paths)

    longest_paths = sorted(set(longest_paths))

    print("Longest path length:", global_max_len)
    print("Longest path(s):")
    for path in longest_paths:
        print(path)
