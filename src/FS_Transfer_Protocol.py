import socket
import hashlib
import os

class Node_Transfer:
    def __init__ (self, port, path):
        self.port = port
        self.path = path
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', port))
        self.files_hashes = {}
    
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

    