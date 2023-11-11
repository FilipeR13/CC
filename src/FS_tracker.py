import socket
import threading
import sys
from TCP_Message import *
class fs_tracker():

    def __init__(self):
        self.name = socket.gethostname()
        self.port = 9090
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)
        self.node_threads = {}
        # dict of nodes and files: Key = (host,port); Value = [(name file, [chunks], [hashes])]
        self.nodes = {}
        self.l = threading.Lock()

    def handle_storage(self, socket_node, payload):
        files =payload.split(b' ')
        print(files)
        with self.l:
            self.nodes[socket_node.getpeername()]= [
                    (
                        files[i].decode('utf-8') ,
                        [int.from_bytes(chunk,'big') for chunk in files[i+1].split(b',')] ,
                        [hash.decode('utf-8') for hash in files[i+2].split(b',')]
                    ) 
                    for i in range(0, len(files), 3)
                ]

    def handle_order(self, socket_node, payload):
        result = []
        file = payload.decode('utf-8')
        print(file)
        with self.l:
            for key, value in self.nodes.items():
                if key != socket_node.getpeername():
                    print (value)
                    for file_node in value:
                        if file_node[0] == file:
                            # result is a list of tuples (node, chunks, hashes)
                            result.append((key,file_node[1], file_node[2]))
                            break
        self.handle_ship(socket_node, result)

    def handle_ship(self, socket_node, payload):
        nodes = []
        print (payload)
        for key, chunks, hashes in payload:
            nodes.append(key[0].encode('utf-8'))
            nodes.append(key[1].to_bytes(4, byteorder='big'))
            nodes.append(b','.join([chunk.to_bytes(4, byteorder='big') for chunk in chunks]))
            nodes.append(b','.join([hash.encode('utf-8') for hash in hashes]))
        socket_node.send(Message.create_message(SHIP, b' '.join(nodes)))

    def close_client(self, socket_node):
        print(f"Node {socket_node.getpeername()} desconectado")
        with self.l:
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
        print(f"Servidor ativo em {self.server_socket.getsockname()[0]} porta {self.port}")
        try:
            while True:
                socket_node, address_node = self.server_socket.accept()
                print(f"Node conectado a partir de {address_node[0]} na porta {address_node[1]}")

                thread_node = threading.Thread(target=self.handle_client, args=(socket_node,))
                with self.l:
                    self.node_threads[address_node] = thread_node
                    self.nodes[address_node] = []

                thread_node.start()
                
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            self.server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()