import hashlib

ORDER = 0x1
ACK = 0x2
RESEND = 0x3
DATA = 0x4


class UDP_Message:
    def create_message_udp(flag, payload, chunk = 0):
        total_length = len(payload) + 9
        message = flag + chunk.to_bytes(4, byteorder='big') + total_length.to_bytes(4, byteorder='big') + payload
        return message + hashlib.sha1(message).hexdigest().encode('utf-8')
    
    def receive_message_udp(socket):
        data = socket.recv(1073) # 1024 bytes do chunk + 9 bytes do cabeçalho + 40 bytes do hash
        if not data:
            return None, None, None
        message_type, chunk, length, payload, hash = data[0], data[1:5], data[5:9], data[9:-40], data[-40:]
        int_length = int.from_bytes(length, "big")
        if int_length > 1073 - 49:
            while True:
                data = socket.recv(1073)
                if not data:
                    break
                payload += data
                if len(payload) == int_length:
                    break
        if hash != hashlib.sha1(data[:-40]).hexdigest().encode('utf-8'):
            return RESEND, chunk, payload, hash
        return message_type, chunk, payload, hash
    
    def send_message (socket, message, ip, port):
        socket.sendto(message, (ip, port))
        # socket.settimeout(0.5)

        message_type, chunk, payload, hash = UDP_Message.receive_message_udp(socket)

        if message_type == RESEND:
            UDP_Message.send_message(socket, message, ip, port)