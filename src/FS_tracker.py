import socket
import threading
import sys
from TCP_Message import *
from dataToBytes import *
from SafeMap import *
class fs_tracker():

    def __init__(self):
        self.name = socket.gethostname()
        self.port = 9090
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)
        self.node_threads = SafeMap()
        # dict of nodes and files: Key = (host,port); Value = {name file : [chunks]}
        self.nodes = SafeMap()
        # dict of files: Key = name file : {chunks : hash}
        self.files = SafeMap()

    def handle_storage(self, socket_node, payload):
        files =payload.split(b' ')
        print (files)
        for i in range(0, len(files), 3):
            name = files[i].decode('utf-8')
            chunks = arrayBytesToInt(files[i+1])
            hashes = arrayBytesToString(files[i+2])
            if not self.files.exists(name):
                self.files.put(name,{})

            dict_files = self.files.get(name)
            for chunk, hash in zip(chunks, hashes):
                # ! verificar se quando faco get(name) se retorna o mesmo objeto
                dict_files[chunk] = hash
            
            self.nodes.get(socket_node.getpeername())[name] = chunks

    def handle_order(self, socket_node, payload):
        result = []
        file = payload.decode('utf-8')
        node_who_asked = socket_node.getpeername()
        for key, value in self.nodes.get_items():
            if key != node_who_asked:
                if file in value:
                    # result is a list of tuples (node, chunks)
                    result.append((key, value.get(file)))
        self.handle_ship(socket_node, result, file)

    def handle_ship(self, socket_node, payload, file):
        nodes = []
        print (payload)
        for key, chunks in payload:
            nodes.append(key[0].encode('utf-8'))
            nodes.append(key[1].to_bytes(4, byteorder='big'))
            nodes.append(arrayIntToBytes(chunks))
        if nodes:
            nodes.append(arrayStringToBytes(self.files.get(file).values()))
        socket_node.send(TCP_Message.create_message(SHIP, b' '.join(nodes)))

    def close_client(self, socket_node):
        key = socket_node.getpeername()
        print(f"Node {key} desconectado")
        self.node_threads.remove(key)
        self.nodes.remove(key)
        socket_node.close()

    def handle_client(self, socket_node):

        handle_flags = {
            STORAGE: self.handle_storage,
            ORDER: self.handle_order,
        }

        while True:
            message_type, payload = TCP_Message.receive_message(socket_node)
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
                self.node_threads.put(address_node, thread_node)
                self.nodes.put(address_node, {})

                thread_node.start()
                
        except KeyboardInterrupt:
            print("\nServer disconnected")
            self.server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()