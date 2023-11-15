import hashlib

def arrayIntToBytes(array):
    return b','.join([chunk.to_bytes(4, byteorder='big') for chunk in array])

def arrayBytesToInt(array):
    return [int.from_bytes(chunk,'big') for chunk in array.split(b',')]

def arrayBytesToString(array):
    return [chunk.decode('utf-8') for chunk in array.split(b',')]

def arrayStringToBytes(array):
    return b','.join([chunk.encode('utf-8') for chunk in array])

def arrayBytesToSha1(array):
    return [hashlib.sha1(chunk).hexdigest() for chunk in array]

def arraySha1ToBytes(array):
    return b','.join([chunk.encode('utf-8') for chunk in array])