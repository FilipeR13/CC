import struct

# Define message flags
WAKE_UP = 0x01
REQUEST = 0x02
RESPONSE = 0x03

#normalmente format_message vai ser '!IBB' mas para ficheiros é '!IB{total_length}s'
class Message:
    def __init__ (self, message_type, payload, format_message = '!IB'):
        self.message_type = message_type
        self.payload = payload
        self.format_message = format_message

    def create_struct_message(self):
        # Pack message header
        packet = struct.pack(self.format_message, len(self.payload), self.message_type, self.payload)
        print(packet, len(packet))
        return packet
   
    '''
    def unpack_header(struct_message):
        # Unpack message header
        length, message_type, payload = struct.unpack('!IB', struct_message[:5])
        # Extract message type and subtype

        return message_type, length, payload

    '''