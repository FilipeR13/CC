import hashlib

ORDER = 0x1
DATA = 0x2

class UDP_Message:
    def create_message_udp(flag, payload, file, chunk = 0):
        return bytearray([flag]) +file.encode('utf-8') + chunk.to_bytes(4, byteorder='big') + payload
    
    def receive_message_udp(socket):
        data, ip = socket.recvfrom(1033) # 1024 bytes do chunk + 9 bytes do cabeçalho + 40 bytes do hash
        if not data:
            return None, None, None, None
        message_type, file, chunk, payload = data[0], data[1:5], data[5:]
        return message_type, file, chunk, payload, ip
    
    def send_message (socket, message, ip, port):
        socket.sendto(message, (ip, port))
        # socket.settimeout(0.5)
        message_type, chunk, payload, _ = UDP_Message.receive_message_udp(socket)
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

