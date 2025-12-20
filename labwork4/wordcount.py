from mpi4py import MPI
import string

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
    
input_text = """
three swiss witch-bitches, which wished to be switched swiss witch-bitches, watch three swiss swatch watch switches. which swiss witch-bitch, which wishes to be a switched witch-bitch, wishes to watch which swiss swatch watch switch?
"""

def divide_input(text, num_parts):
    text = text.lower()
    translator = str.maketrans('', '', string.punctuation)
    clean_text = text.translate(translator)
    
    words = clean_text.split()
    total_words = len(words)
    
    base_size = total_words // num_parts
    remainder = total_words % num_parts
    
    chunks = []
    start = 0
    for i in range(num_parts):
        chunk_size = base_size + (1 if i < remainder else 0)
        chunk = words[start : start + chunk_size]
        chunks.append(chunk)
        start += chunk_size
    return chunks

def local_combine(word_list):
    counts = {}
    for word in word_list:
        counts[word] = counts.get(word, 0) + 1
    return list(counts.items())

def local_reduce(all_results):
    final_word_counts = {}
    for worker_list in all_results:
        for word, count in worker_list:      
            final_word_counts[word] = final_word_counts.get(word, 0) + count
            
    return sorted(final_word_counts.items())

if rank == 0:
    chunks = divide_input(input_text, size)
else:
    chunks = None

local_words = comm.scatter(chunks, root=0)
local_counts = local_combine(local_words)
all_results = comm.gather(local_counts, root=0)

if rank == 0:
    final_result = local_reduce(all_results)
    print("Word count result:")
    for word, count in final_result:
        print(f"<{word}, {count}>")
