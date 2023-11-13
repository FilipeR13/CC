import sys
from FS_Track_Protocol import *
from FS_Transfer_Protocol import *
import threading

class fs_node():
    def __init__(self,path, host, port):
        if path[-1] != '/':
            path += '/'
        self.tcp_connection = Node_Connection(host, int(port), path)
        self.udp_connection = Node_Transfer(int(port))
    
    def handle_order(self, payload):
        ip, chunks = self.tcp_connection.handle_order(payload)
        if ip:
            self.udp_connection.get_file(payload,ip, chunks)

    def handle_quit(self, payload):
        self.tcp_connection.close_connection()
        self.udp_connection.close_connection()
        sys.exit(0)

    def handle_input(self,input):
        inputs = {
            'order' : self.handle_order,
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