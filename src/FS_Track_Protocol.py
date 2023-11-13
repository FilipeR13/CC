import socket
from TCP_Message import *
import sys
import os
import math
import hashlib

class Node_Connection:
    def __init__ (self, host, port, path):
        self.host = host
        self.port = port
        self.path = path
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host,self.port))
        print(f"Coneção FS Track Protocol com servidor {self.host} porta {port}")

    def send_name_files(self):
        files = [f for f in os.listdir(self.path) if os.path.isfile(self.path + f)]
        result = b""
        for file_name in files:
            # get hash of file in chunks
            sha1_hashes = []
            with open(self.path + file_name, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    sha1_hash = hashlib.sha1(data)
                    sha1_hashes.append(sha1_hash.hexdigest())

            size = os.path.getsize(self.path + file_name)
            number_of_chunks = math.ceil(size / PACKET_SIZE)

            result += file_name.encode('utf-8') + b" " # name of file
            result += b','.join([chunk.to_bytes(4, byteorder='big') for chunk in range(1,number_of_chunks+1)]) + b" " # array of chunks
            result += b','.join([sha1_hash.encode('utf-8') for sha1_hash in sha1_hashes]) + b" " # array of hashes of chunks

        # Pack the list of encoded strings into a struct
        packet = TCP_Message.create_message(STORAGE, result[:-1])
        self.client_socket.send(packet)

    def handle_order(self, payload):
        self.client_socket.send(TCP_Message.create_message(ORDER, payload[0].encode('utf-8')))
        message_type, nodes = TCP_Message.receive_message(self.client_socket)
        list = nodes.split(b' ')
        hashes, nodes = list[-1].split(b','), list[:-1]
        if nodes == []:
            print(f"Arquivo {payload[0]} não encontrado")
            return None
        ips, chunks = [], []
        pos = 0
        for i in range(0, len(nodes), 3):
            ips[pos] = nodes[i].decode('utf-8')
            chunks[pos] = [int.from_bytes(chunk,'big') for chunk in nodes[i+2].split(b',')]
            pos += 1
        print (ips, chunks)
        return ips[0], chunks[0]
    def close_connection (self):
        self.client_socket.close()