import struct

# Define message flags
LOGIN = 0x01
STORAGE = 0x02
ORDER = 0x03
SHIP = 0x04

PACKET_SIZE = 1024

#normalmente format_message vai ser '!IBB' mas para ficheiros é '!IB{total_length}s'
# temos de adicionar o numero de segmento.
class Message:
    def __init__ (self, message_type, payload, format_message = '!IB'):
        self.message_type = message_type
        self.payload = payload
        self.format_message = format_message

# quando criarmos a struct, podemos calcular o numero de segmentos que vamos ter de enviar (ex: len(payload)/1024 (mais 5 bytes para cada header))
# dps devolvemos uma lista com os segmentos(structs)
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