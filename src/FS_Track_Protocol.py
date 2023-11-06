import socket
from TCP_Message import *
import sys
import os
import math

class Node_Connection:
    def __init__ (self, host, port, path):
        self.host = host
        self.port = port
        self.path = path
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host,self.port))
        print(f"Coneção FS Track Protocol com servidor localhost porta {port}")

    def send_data(self, data):
        self.client_socket.send(data.encode())

    def send_name_files(self):
        files = [f for f in os.listdir() if os.path.isfile(f)] 
        result = b""
        for file in files:
            size = os.path.getsize(file)
            number_of_chunks = math.ceil(size / PACKET_SIZE)
            result += file.encode('utf-8') + b" " + b','.join([chunk.to_bytes(4, byteorder='big') for chunk in range(1,number_of_chunks+1)]) + b" "

        # Pack the list of encoded strings into a struct
        packet = Message.create_message(STORAGE, result[:-1])
        self.client_socket.send(packet)

    def handle_order(self, payload):
        self.client_socket.send(Message.create_message(ORDER, payload[0].encode('utf-8')))
        message_type, nodes = Message.receive_message(self.client_socket)
        list_nodes = nodes.split(b' ')
        if list_nodes == [b'']:
            print(f"Arquivo {payload[0]} não encontrado")
            return
        for i in range(0, len(list_nodes), 3):
            print(f"Node ({list_nodes[i].decode('utf-8')},{int.from_bytes(list_nodes[i+1],'big')}) tem os chunks {[int.from_bytes(chunk,'big') for chunk in list_nodes[i+2].split(b',')]} do arquivo {payload[0]}")

    def handle_quit(self, payload):
        self.client_socket.close()
        sys.exit(0)