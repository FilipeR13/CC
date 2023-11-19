import socket
from TCP_Message import *
from dataToBytes import *
from SafeMap import *
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
        dict_files = SafeMap()
        files = [f for f in os.listdir(self.path) if os.path.isfile(self.path + f)]
        result = b""
        for file_name in files:
            chunks_hash = {}

            # get hash of file in chunks
            sha1_hashes = []
            i = 1
            with open(self.path + file_name, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    chunks_hash[i] = data
                    i += 1
                    sha1_hash = hashlib.sha1(data)
                    sha1_hashes.append(sha1_hash.hexdigest())

            dict_files.put(file_name, chunks_hash)

            size = os.path.getsize(self.path + file_name)
            number_of_chunks = math.ceil(size / PACKET_SIZE)

            result += file_name.encode('utf-8') + b" " # name of file
            result += arrayIntToBytes(list(range(1,number_of_chunks+1))) + b" " # array of chunks
            result += arrayStringToBytes(sha1_hashes) + b" " # array of hashes of chunks

        # Pack the list of encoded strings into a struct
        packet = TCP_Message.create_message(STORAGE, result[:-1])
        print (packet)
        self.client_socket.send(packet)
        return dict_files

    def update_file(self, file_name, chunk, hash):
        message = TCP_Message.create_message(STORAGE, file_name.encode('utf-8') + b" " + chunk.to_bytes(4, byteorder='big') + b" " + hash.encode('utf-8'))
        # print (message)
        self.client_socket.send(message)

    def handle_order(self, payload):
        self.client_socket.send(TCP_Message.create_message(ORDER, payload.encode('utf-8')))
        _ , nodes = TCP_Message.receive_message(self.client_socket)
        print (nodes)
        list = nodes.split(b' ')
        hashes, nodes = arrayBytesToString(list[-1]), list[:-1]
        
        if nodes == []:
            print(f"Arquivo {payload} não encontrado")
            return None, None, None
        
        ips, chunks = [], []
        for i in range(0, len(nodes), 2):
            ips.append(nodes[i].decode('utf-8'))
            chunks.append(arrayBytesToInt(nodes[i+1]))
        
        print (ips, chunks, hashes)
        return ips[0], chunks[0], hashes
    
    def close_connection (self):
        self.client_socket.close()