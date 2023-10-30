import socket
import sys
import os
from Data import *
import struct


class fs_node():
    def __init__(self,path, host, port):
        self.path = path
        self.host = host
        self.port = int(port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host,self.port))
        print("Coneção FS Track Protocol com servidor localhost porta 9090")

    def send_data(self, data):
        self.client_socket.send(data.encode())

    def send_name_files(self):
        files = [f.encode('utf-8') for f in os.listdir() if os.path.isfile(f)]
        print (files)
        total_length = sum(len(s) for s in files)
        print (total_length)

        # Pack the list of encoded strings into a struct
        packet = Message.create_message(STORAGE, b' '.join(files))
        self.client_socket.send(packet)

    def handle_order(self, payload):
        self.client_socket.send(Message.create_message(ORDER, payload[0].encode('utf-8')))
        message_type, payload = Message.receive_message(self.client_socket)

    def handle_quit(self, payload):
        self.client_socket.close()
        sys.exit(0)
    
    def handle_input(self,input):
        inputs = {
            'order' : self.handle_order,
            'quit' : self.handle_quit
        }
        command = input.split(' ')
        if (command[0] not in inputs):
            print("Comando inválido")
            return
        inputs[command[0]](command[1:])
    
def main():
    if len(sys.argv) != 4:
        print("Erro nos argumentos: FS_node.py <path> <host> <port>")

    node = fs_node(sys.argv[1],sys.argv[2],sys.argv[3])

    node.send_name_files()
    try:
        while True:
            user_input = input("> ")
            if user_input:
                node.handle_input(user_input)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        node.client_socket.close()
        sys.exit(0)



if __name__ == "__main__":
    main()