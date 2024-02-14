import os

def get_ab_offset(filename: str)->int:
    if filename is None or len(filename) == 0:
        return 23
    filename = os.path.basename(filename)
    offset = 23
    len_filename = len(filename)
    for i in range(3):
        index = len_filename - i - 1
        if index < 0: 
            break
        char = ord(filename[index])
        hash_code = char | (char << 16)
        offset += hash_code
    offset = max(1, abs(offset) % 256)
    return offset