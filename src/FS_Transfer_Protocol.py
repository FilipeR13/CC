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
            message, address = self.udp_socket.recvfrom(1024)
            message = message.decode('utf-8')
            if message == 'GET':
                self.udp_socket.sendto(self.files_hashes, address)
            elif message == 'PUT':
                file_name, file_hash = address
                self.files_hashes[file_name] = file_hash
            else:
                print("Mensagem inválida")     

    def close_connection (self):
        self.udp_socket.close()

    