import hashlib

ORDER = 0x1
ACK = 0x2
RESEND = 0x3
DATA = 0x4


class UDP_Message:
    def create_message_udp(flag, payload, chunk = 0):
        message = flag + chunk.to_bytes(4, byteorder='big') + payload
        return message + hashlib.sha1(message).hexdigest().encode('utf-8')
    
    def receive_message_udp(socket):
        data = socket.recv(1073) # 1024 bytes do chunk + 9 bytes do cabeçalho + 40 bytes do hash
        if not data:
            return None, None, None
        message_type, chunk, payload, hash = data[0], data[1:5], data[5:-40], data[-40:]
        if hash != hashlib.sha1(data[:-40]).hexdigest().encode('utf-8'):
            return RESEND, chunk, payload
        return message_type, chunk, payload,ip
    
    def send_message (socket, message, ip, port):
        socket.sendto(message, (ip, port))
        # socket.settimeout(0.5)
        message_type, chunk, payload = UDP_Message.receive_message_udp(socket)

        if message_type == RESEND:
            chunk, payload = UDP_Message.send_message(socket, message, ip, port)

        return chunk,payload

    def receive_chunks (socket, chunks, ip, porta):
        chunks = {}
        while chunks:
            message_type, chunk, payload = UDP_Message.receive_message_udp(socket)
            if message_type == DATA:
                chunks[chunk] = payload
                UDP_Message.send_message(socket, UDP_Message.create_message_udp(ACK, b''), ip, porta)
        return chunks
    
    def send_chunks (socket, file, path, ip, porta):
        message = UDP_Message.create_message_udp(DATA, path.encode('utf-8'))