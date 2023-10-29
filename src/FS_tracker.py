import socket
import threading
import struct
import sys
from Data import *
class fs_tracker():

    def __init__(self):
        self.host = 'localhost'
        self.port = 9090
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

    def handle_wake_up(self, socket_node, payload):
        files =  [file.decode('utf-8') for file in payload.split(b' ')]
        print(files)
        self.nodes[socket_node.getpeername()[1]]['files'] = files

    def handle_request(self, socket_node, payload):
        print("Request")
        print(payload)

    
    def handle_response(self, socket_node, payload):
        print("Response")
        print(payload)

    def close_client(self, socket_node):
        print(f"Node {socket_node.getpeername()[1]} desconectado")
        port = socket_node.getpeername()[1]
        if port in self.node_threads:
            self.node_threads[port].join()
            del self.node_threads[port]
        del self.nodes[port]
        socket_node.close()

    def handle_client(self, socket_node, connection_event):
        while True:
            connection_event.wait()

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

                if message_type == WAKE_UP:
                    self.handle_wake_up(socket_node, payload)
                elif message_type == REQUEST:
                    self.handle_request(socket_node, payload)
                elif message_type == RESPONSE:
                    self.handle_response(socket_node, payload)

        self.close_client(socket_node)


    def start_connections(self):
        print(f"Servidor ativo em {self.host} porta {self.port}")
        try:
            while True:
                socket_node, address_node = self.server_socket.accept() #função accept retorna um tuplo.

                host_node, porta_node = socket_node.getpeername()
                print(f"Node conectado a partir de {host_node} na porta {porta_node}")

                new_port = self.find_available_port(self.host, self.port + 1)
                if new_port is not None:
                    
                    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    new_socket.bind((self.host, new_port))
                    new_socket.listen(1)

                    connection_event = threading.Event()

                    client_thread = threading.Thread(target=self.handle_client, args=(new_socket,connection_event))
                    client_thread.start()

                    response = str(new_port).encode('utf-8')
                    response_message = Message(RESPONSE, response, f'!IB{len(response)}s').create_struct_message()
                    socket_node.send(response_message)


                else:
                    response = "No available port".encode('utf-8')
                    response_message = Message(RESPONSE, response, f'!IB{len(response)}s').create_struct_message()
                    socket_node.send(response_message)

                    self.nodes[new_port] = {
                        'host': host_node,
                        'files': []
                    }
                
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()