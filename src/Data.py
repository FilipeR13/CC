import struct
# Define message types
REQUEST = 0x01
RESPONSE = 0x02
DATA = 0x03

# Define message flags
ACK = 0x01
SYN = 0x02
ACK_SYN = 0x03
FIN = 0x04


class Message:
    def create_struct_message(message_type, message_subtype, payload = b''):
        # Pack message header
        header = struct.pack('!IB', len(payload) + 5, message_type << 4 | message_subtype)
        return header + payload
    
    def unpack_header(struct_message):
        # Unpack message header
        length, message_type_subtype = struct.unpack('!IB', struct_message[:5])
        # Extract message type and subtype
        message_type = message_type_subtype >> 4
        message_subtype = message_type_subtype & 0x0F

        return message_type, message_subtype, length - 2


# socket.send (Message.create_struct_message (0x01,0x02, "Hello World"))
# message_type,message_subtype, length =  Message.unpack_header (socket.recv (5))

# Verificar header types
# Verificar se o payload é maior que 0
# Verificar se o payload é do tipo bytes
# Verificar se o message type é um dos 3 definidos
# Verificar se o message subtype é um dos 4 definidos
# Verificar se o message type e subtype são válidos
# socket.recv (length)