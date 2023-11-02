import socket
import threading
import sys
from Data import *
class fs_tracker():

    def __init__(self):
        self.host = 'localhost'
        self.port = 9091
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.node_threads = {}
        self.nodes = {}

    def handle_storage(self, socket_node, payload):
        files =  [file.decode('utf-8') for file in payload.split(b' ')]
        self.nodes[socket_node.getpeername()]= [(files[i], list(range(1,int(files[i + 1])+1))) for i in range(0, len(files), 2)]
        print (f"Node {socket_node.getpeername()} tem os arquivos {self.nodes[socket_node.getpeername()]}")

    def handle_order(self, socket_node, payload):
        result = []
        file = payload.decode('utf-8')
        for key, value in self.nodes.items():
            if key != socket_node.getpeername():
                for file_node in value:
                    if file_node[0] == file:
                        # result is a list of tuples (node, chunks)
                        result.append((key,file_node[1]))
                        break
        self.handle_ship(socket_node, result)

    def handle_ship(self, socket_node, payload):
        nodes = []
        for key, chunks in payload:
            nodes.append(key[0].encode('utf-8'))
            nodes.append(key[1].to_bytes(4, byteorder='big'))
            nodes.append(b','.join([chunk.to_bytes(4, byteorder='big') for chunk in chunks]))
        socket_node.send(Message.create_message(SHIP, b' '.join(nodes)))

    def close_client(self, socket_node):
        print(f"Node {socket_node.getpeername()} desconectado")
        del self.node_threads[socket_node.getpeername()]
        del self.nodes[socket_node.getpeername()]
        socket_node.close()

    def handle_client(self, socket_node):

        handle_flags = {
            STORAGE: self.handle_storage,
            ORDER: self.handle_order,
            SHIP: self.handle_ship
        }

        while True:
            message_type, payload = Message.receive_message(socket_node)
            if not payload:
                break
            handle_flags[message_type](socket_node, payload)

        self.close_client(socket_node)

    def start_connections(self):
        print(f"Servidor ativo em {self.host} porta {self.port}")
        try:
            while True:
                socket_node, address_node = self.server_socket.accept()

                host_node, porta_node = socket_node.getpeername()
                print(f"Node conectado a partir de {host_node} na porta {porta_node}")

                thread_node = threading.Thread(target=self.handle_client, args=(socket_node,))
                self.node_threads[(host_node,porta_node)] = thread_node
                self.nodes[(host_node,porta_node)] = []

                thread_node.start()
                
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()