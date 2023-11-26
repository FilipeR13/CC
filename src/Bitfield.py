def lsb_is_set(bitfield):
    return bitfield & 1 == 1

def get_bitfield_chunks(bitfield):
    chunks = []
    i = 0
    while bitfield > 0:
        if lsb_is_set(bitfield):
            chunks.append(i)
        bitfield = bitfield >> 1
        i += 1
    return chunks

def calculate_bitfield_chunk (bitfield, chunk):
    return bitfield | (1 << chunk)
