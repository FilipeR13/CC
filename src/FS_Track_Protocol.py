import socket
from Data import *
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
        print("Coneção FS Track Protocol com servidor localhost porta 9090")

    def send_data(self, data):
        self.client_socket.send(data.encode())

    def send_name_files(self):
        files = [f for f in os.listdir() if os.path.isfile(f)] 
        result = ""
        for file in files:
            size = os.path.getsize(file)
            number_of_chunks = math.ceil(size / PACKET_SIZE)
            result += f"{file} {number_of_chunks} "

        # Pack the list of encoded strings into a struct
        packet = Message.create_message(STORAGE, result[:-1].encode('utf-8'))
        self.client_socket.send(packet)

    def handle_order(self, payload):
        self.client_socket.send(Message.create_message(ORDER, payload[0].encode('utf-8')))
        message_type, nodes = Message.receive_message(self.client_socket)
        list_nodes = nodes.split(b' ')
        for i in range(0, len(list_nodes), 3):
            print(f"Node ({list_nodes[i].decode('utf-8')},{int.from_bytes(list_nodes[i+1],'big')}) tem os chunks {[int.from_bytes(chunk,'big') for chunk in list_nodes[i+2].split(b',')]} do arquivo {payload[0]}")

    def handle_quit(self, payload):
        self.client_socket.close()
        sys.exit(0)