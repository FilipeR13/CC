import socket
import sys
import os
import math
from Data import *
from Node_Connection import *


class fs_node():
    def __init__(self,path, host, port):
        if path[-1] != '/':
            path += '/'
        self.tcp_connection = Node_Connection(host, int(port), path)
    
    def handle_input(self,input):
        inputs = {
            'order' : self.tcp_connection.handle_order,
            'quit' : self.tcp_connection.handle_quit
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

    node.tcp_connection.send_name_files()

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