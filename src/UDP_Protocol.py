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
        data, ip = socket.recvfrom(1073) # 1024 bytes do chunk + 9 bytes do cabeçalho + 40 bytes do hash
        if not data:
            return None, None, None, None
        message_type, chunk, payload, hash = data[0], data[1:5], data[5:-40], data[-40:]
        if hash != hashlib.sha1(data[:-40]).hexdigest().encode('utf-8'):
            socket.sendto(UDP_Message.create_message_udp(RESEND, b''), ip)
            return UDP_Message.receive_message_udp(socket)
        return message_type, chunk, payload, ip
    
    def send_message (socket, message, ip, port):
        socket.sendto(message, (ip, port))
        # socket.settimeout(0.5)
        message_type, chunk, payload = UDP_Message.receive_message_udp(socket)
        # ! verificar
        if message_type == None:
            chunk, payload = UDP_Message.send_message(socket, message, ip, port)

        return chunk,payload
    
    def receive_chunk(socket, ip, porta):
        message_type, chunk, payload = UDP_Message.receive_message_udp(socket)
        if message_type == DATA:
            UDP_Message.send_message(socket, UDP_Message.create_message_udp(ACK, b''), ip, porta)
            return chunk, payload


    def send_chunks (socket, dict_chunks, chunks_to_send, ip, porta):
        if not chunks_to_send:
            return
        chunk = chunks_to_send[0]
        message = UDP_Message.create_message_udp(DATA, dict_chunks[chunk], chunk)
        UDP_Message.send_message(socket, message, ip, porta)
        message_type, _, _, _ = UDP_Message.receive_message_udp(socket)
        if message_type == ACK:
            chunks_to_send.remove(chunk)
        UDP_Message.send_chunks(socket, dict_chunks, chunks_to_send, ip, porta)

