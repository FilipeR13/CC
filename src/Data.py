import struct

# Define message flags
STORAGE = 0x01
ORDER = 0x02
SHIP = 0x03

PACKET_SIZE = 1024
class Message:
    def create_message(flag,payload):
        return bytearray([flag]) + len(payload).to_bytes(4, byteorder='big') + payload