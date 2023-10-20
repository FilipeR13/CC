import socket
import threading

class fs_tracker():

    def __init__(self):
        self.host = 'localhost'
        self.port = 9090
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.node_threads = {}
        self.nodes = {}

    def handle_client(self, socket_node):
        while True:
            data = socket_node.recv(1024)
            if not data:
                break
            if data.decode()  == "Current nodes":
                print("Lista de nodes atualmente conectados:")
                for port, node in self.nodes.items():
                    print("[" + f"Porta -> {node['port']}" + "," + f"Host -> {node['host']}" + "]")
            else:
                print(f"Data recebida pela porta {socket_node.getpeername()[1] }: {data.decode()}")
        socket_node.close()

    def start_connections(self):
        print(f"Servidor ativo em {self.host} porta {self.port}")
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


if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()