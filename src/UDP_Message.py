import time

ORDER = 0x1
DATA = 0x2

PACKET_SIZE = 1024
class UDP_Message:
    def create_message_udp(flag, payload,chunk = 0, timestamp= round(time.time() * 1000) - 1700600000000):  
        return bytearray([flag]) + chunk.to_bytes(4, byteorder='big') + timestamp.to_bytes(4, byteorder='big') + payload
    
    def receive_message_udp(socket):
        data, ip = socket.recvfrom(1033) # 1024 bytes do chunk + 9 bytes do cabeçalho
        if not data:
            return None, None, None, None, None
        message_type, chunk, timestamp, payload = data[0], data[1:5], data[5:9], data[9:]
        return message_type, int.from_bytes(chunk, byteorder='big'), int.from_bytes(timestamp,byteorder='big'), payload, ip
    
    def send_message (socket, message, ip):
        socket.sendto(message, ip)

    def send_chunk (socket, ip, porta, chunk, payload, timestamp):
        message = UDP_Message.create_message_udp(DATA, payload, chunk, timestamp)
        UDP_Message.send_message(socket, message, (ip, porta))