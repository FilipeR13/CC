# Define message flags
STORAGE = 0x01
UPDATE = 0x02
ORDER = 0x03
SHIP = 0x04

class TCP_Message:
    def create_message(flag,payload):
        return bytearray([flag]) + len(payload).to_bytes(4, byteorder='big') + payload
    
    def receive_message(socket):
        data = socket.recv(5)
        if not data:
            return None, None
        message_type, length = data[0], data[1:5]
        int_length = int.from_bytes(length, byteorder="big")
        payload = b''
        length = 0
        while int_length > length:
            chunk = socket.recv(min(int_length - length, 1024))
            length += len(chunk)
            payload += chunk

        return message_type, payload