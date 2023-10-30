import socket
import threading
import struct
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

    def find_available_port(self,host, starting_port, attempts=100):
        for port in range(starting_port, starting_port + attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_socket:
                    new_socket.bind((host, port))
                    return port
            except OSError:
                pass
        return None

    def handle_storage(self, socket_node, payload):
        files =  [file.decode('utf-8') for file in payload.split(b' ')]
        self.nodes[socket_node.getpeername()[1]]['files'] = files

    def handle_order(self, socket_node, payload):
        result = []
        file = payload.decode('utf-8')
        for key, value in self.nodes.items():
            if key != socket_node.getpeername()[1]:
                if file in value['files']:
                    result.append(key)
        self.handle_ship(socket_node, result)

    
    def handle_ship(self, socket_node, payload):
        nodes = [node.to_bytes(4,"big") for node in payload]
        socket_node.send(Message.create_message(SHIP, b' '.join(nodes)))

    def close_client(self, socket_node):
        print(f"Node {socket_node.getpeername()[1]} desconectado")
        del self.node_threads[socket_node.getpeername()[1]]
        del self.nodes[socket_node.getpeername()[1]]
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
                self.node_threads[porta_node] = thread_node
                self.nodes[porta_node] = {
                    'host': host_node,
                    'files': []
                }
                
                thread_node.start()
                
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()