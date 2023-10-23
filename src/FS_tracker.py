import socket
import threading
import struct
import sys
class fs_tracker():

    def __init__(self):
        self.host = 'localhost'
        self.port = 9091
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.node_threads = {}
        self.nodes = {}

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

    def handle_client(self, socket_node):
        handle_flags =  {
            0x01: self.handle_wake_up,
            0x02: self.handle_request,
            0x03: self.handle_response
        }
        while True:
            data = socket_node.recv(1024)
            if not data:
                break
            data_decoded = data.decode()
            if data_decoded  == "Current nodes":
                print("Lista de nodes atualmente conectados:")
                for port, node in self.nodes.items():
                    print("[" + f"Porta -> {node['port']}" + "," + f"Host -> {node['host']}" + f", Files -> {node['files']}" +"]")
            else:
                length, message_type, payload = struct.unpack(f'!IB{len(data) - 5}s', data)
                print(f"Data recebida pela porta {socket_node.getpeername()[1] }: {length} || {message_type} || {payload}")
                handle_flags[message_type](socket_node, payload)
        socket_node.close()

    def start_connections(self):
        print(f"Servidor ativo em {self.host} porta {self.port}")
        try:
            while True:
                socket_node, address_node = self.server_socket.accept() #função accept retorna um tuplo.

                host_node, porta_node = socket_node.getpeername()
                print(f"Node conectado a partir de {host_node} na porta {porta_node}")


                thread_node = threading.Thread(target=self.handle_client, args=(socket_node,))
                self.node_threads[porta_node] = thread_node
                thread_node.start()

                self.nodes[porta_node] = {
                    'host': host_node,
                    'port': porta_node
                }
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()