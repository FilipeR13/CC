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
        packet = Message(0x01, b' '.join(files), f'!IB{total_length}s').create_struct_message()
        self.client_socket.send(packet)
        # chunks = [packet[i:i + 1024] for i in range(0, len(packet), 1024)]

        # Send the chunks
        # for chunk in chunks:
        #    self.client_socket.send(chunk)

        
    
def main():
    if len(sys.argv) != 4:
        print("Erro nos argumentos: FS_node.py <path> <host> <port>")
    node = fs_node(sys.argv[1],sys.argv[2],sys.argv[3])
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
    # Ver multithreading em tcp: a porta do server recebe um pedido do cliente e depois cria uma nova thread que criará uma nova porta exclusiva para esse cliente.
    # Assim podemos evitar que quando um cliente esteja a utilizar a porta do server os outros tenham de ficar à espera.