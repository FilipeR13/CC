import socket
import sys
import os
from Data import Message
import struct


class fs_node():
    def __init__(self,path, host, port):
        self.path = path
        self.host = host
        self.port = int(port)
        self.exlusive_connection = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host,self.port))
        print("Coneção FS Track Protocol com servidor localhost porta 9090")

    def send_data(self, data):
        self.exlusive_connection.send(data.encode())


    def receive_new_port(self):
        response = self.client_socket.recv(1024)
        if response:
            length, message_type, payload = struct.unpack(f'!IB{len(response) - 5}s', response)
            if message_type == 0x03:
                new_port = int(payload.decode('utf-8'))
                print(f"Received new port: {new_port}")
                return new_port
        return None
    
    def create_new_connection(self, new_port):

        self.exlusive_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.exlusive_connection.connect((self.host, new_port))
        print(f"Conexão FS Track Protocol com servidor localhost porta {new_port}")

    def send_name_files(self):
        files = [f.encode('utf-8') for f in os.listdir() if os.path.isfile(f)]
        print (files)
        total_length = sum(len(s) for s in files)
        print (total_length)

        # Pack the list of encoded strings into a struct
        packet = Message(0x01, b' '.join(files), f'!IB{total_length}s').create_struct_message()
        self.exlusive_connection.send(packet)
        # chunks = [packet[i:i + 1024] for i in range(0, len(packet), 1024)]

        # Send the chunks
        # for chunk in chunks:
        #    self.client_socket.send(chunk)

        
    
def main():
    if len(sys.argv) != 4:
        print("Erro nos argumentos: FS_node.py <path> <host> <port>")

    node = fs_node(sys.argv[1],sys.argv[2],sys.argv[3])

    new_port = node.receive_new_port()

    if new_port is not None:
        node.create_new_connection(new_port)

    node.send_name_files()
    try:
        while True:
            user_input = input("> ")
            if user_input:
                node.send_data(user_input)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        node.client_socket.close()
        sys.exit(0)



if __name__ == "__main__":
    main()