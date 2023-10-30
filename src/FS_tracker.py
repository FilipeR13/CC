import socket
import threading
import struct
import sys
from Data import *
class fs_tracker():

    def __init__(self):
        self.host = 'localhost'
        self.port = 9093
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
        print(files)
        self.nodes[socket_node.getpeername()[1]]['files'] = files

    def handle_order(self, socket_node, payload):
        print("Request")
        print(payload)

    
    def handle_ship(self, socket_node, payload):
        print("Response")
        print(payload)

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
            data = socket_node.recv(PACKET_SIZE)
            if not data:
                break
            data_decoded = data.decode()

            if data_decoded == "Current nodes":
                print("Lista de nodes atualmente conectados:")
                for port, node in self.nodes.items():
                    print("[" + f"Porta -> {port}" + "," + f"Host -> {node['host']}" + f", Files -> {node['files']}" + "]")
            else:
                length, message_type, payload = struct.unpack(f'!IB{len(data) - 5}s', data)
                print(f"Data recebida pela porta {socket_node.getpeername()[1]}: {length} || {message_type} || {payload}")
                print (message_type)
                handle_flags[message_type](socket_node, payload)

        self.close_client(socket_node)

    def open_new_connection(self, socket_node):
        new_port = self.find_available_port(self.host, self.port + 1)
        if new_port is not None:
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.bind((self.host, new_port))
            client_socket.listen(1)

            response = str(new_port).encode('utf-8')
        else:
            response = "No available port".encode('utf-8')

        response_message = Message(LOGIN, response, f'!IB{len(response)}s').create_struct_message()
        socket_node.send(response_message)

        new_socket, address_node = client_socket.accept()
        client_thread = threading.Thread(target=self.handle_client, args=(new_socket,))
        client_thread.start()   
        return client_thread, new_socket

    def start_connections(self):
        print(f"Servidor ativo em {self.host} porta {self.port}")
        try:
            while True:
                socket_node, address_node = self.server_socket.accept() 

                host_node, porta_node = socket_node.getpeername()
                print(f"Node conectado a partir de {host_node} na porta {porta_node}")

                client_thread, new_socket = self.open_new_connection(socket_node)

                self.node_threads[new_socket.getpeername()[1]] = client_thread
                self.nodes[new_socket.getpeername()[1]] = {
                    'host': new_socket.getpeername()[0],
                    'files': []
                }
                
                socket_node.close()
                
                
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()