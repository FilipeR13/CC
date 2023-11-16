import hashlib

def arrayIntToBytes(array):
    result = b''
    for element in array:
        result += element.to_bytes(4, byteorder='big')
    return result

def arrayBytesToInt(array):
    result = []
    for i in range(0, len(array), 4):
        value = int.from_bytes(array[i:i+4], byteorder='big')
        result.append(value)    
    return result

def arrayBytesToString(array):
    return [chunk.decode('utf-8') for chunk in array.split(b',')]

def arrayStringToBytes(array):
    return b','.join([chunk.encode('utf-8') for chunk in array])

def arrayBytesToSha1(array):
    return [hashlib.sha1(chunk).hexdigest() for chunk in array]