import socket
import hashlib
from UDP_Protocol import * 

class Node_Transfer:
    def __init__ (self, port):
        self.port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', port))
        self.files_hashes = {}
    
    def get_file(self, file, chunks, ip):
        message = UDP_Message.create_message_udp(ORDER,file.encode('uft-8') + b' ' + b','.join([chunk.to_bytes(4, byteorder='big') for chunk in range(0,len(chunks))]))
        # send order to get file
        UDP_Message.send_message(self.udp_socket, message, ip, self.port)
        return UDP_Message.receive_chunks(self.udp_socket, chunks, ip, self.port)


    def handle_udp (self):
        while True:
            message_type, chunk, payload, ip = UDP_Message.receive_message_udp(self.udp_socket)
            if message_type == ORDER:
                file, chunks = payload.split(b' ')
                self.files_hashes[file] = UDP_Message.send_chunks(self.udp_socket, file, [int.from_bytes(chunk,'big') for chunk in chunks.split(b',')] , ip, self.port)


    def close_connection (self):
        self.udp_socket.close()

    