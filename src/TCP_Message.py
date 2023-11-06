# Define message flags
STORAGE = 0x01
ORDER = 0x02
SHIP = 0x03

PACKET_SIZE = 1024
class Message:
    def create_message(flag,payload):
        return bytearray([flag]) + len(payload).to_bytes(4, byteorder='big') + payload
    
    def receive_message(socket):
        data = socket.recv(PACKET_SIZE)
        if not data:
            return None, None
        message_type, length, payload = data[0], data[1:5], data[5:]
        int_length = int.from_bytes(length, "big")
        if int_length > PACKET_SIZE - 5:
            while True:
                data = socket.recv(PACKET_SIZE)
                if not data:
                    break
                payload += data
                if len(payload) == int_length:
                    break
    #    print(f"Data recebida pela porta {socket.getpeername()[1]}: {length} || {message_type} || {payload}")
        return message_type, payload