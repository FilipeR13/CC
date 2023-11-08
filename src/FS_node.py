import sys
import hashlib
from TCP_Message import *
from FS_Track_Protocol import *
from FS_Transfer_Protocol import *
import threading

class fs_node():
    def __init__(self,path, host, port):
        if path[-1] != '/':
            path += '/'
        self.tcp_connection = Node_Connection(host, int(port), path)
        self.udp_connection = Node_Transfer(host, int(port), path)
    
    def handle_quit(self, payload):
        self.tcp_connection.close_connection()
        self.udp_connection.close_connection()
        sys.exit(0)

    def handle_input(self,input):
        inputs = {
            'order' : self.tcp_connection.handle_order,
            'quit' : self.handle_quit,
            'q' : self.handle_quit
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

    node.udp_connection.get_hashes_files()

    udpprotocol = threading.Thread(target=node.udp_connection.handle_udp)
    udpprotocol.daemon = True  # Mark as a daemon thread
    udpprotocol.start()
    try:
        while True:
            user_input = input("> ")
            if user_input:
                node.handle_input(user_input)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        node.handle_quit(None)

if __name__ == "__main__":
    main()