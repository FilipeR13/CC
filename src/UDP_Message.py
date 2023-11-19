import hashlib

ORDER = 0x1
DATA = 0x2

class UDP_Message:
    def create_message_udp(flag, payload, chunk = 0):
        return bytearray([flag]) + chunk.to_bytes(4, byteorder='big') + payload
    
    def receive_message_udp(socket):
        data, ip = socket.recvfrom(1029) # 1024 bytes do chunk + 5 bytes do cabeçalho
        if not data:
            return None, None, None, None
        message_type, chunk, payload = data[0], data[1:5], data[5:]
        return message_type, chunk, payload, ip
    
    def send_message (socket, message, ip):
        socket.sendto(message, ip)
        # socket.settimeout(0.5)
    
    def receive_chunk(socket, ip, porta):
        message_type, chunk, payload = UDP_Message.receive_message_udp(socket)


    def send_chunk (socket, ip, chunk, payload):
        message = UDP_Message.create_message_udp(DATA, payload, chunk)
        UDP_Message.send_message(socket, message, ip)
        

