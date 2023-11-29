import socket
import threading
import sys
from TCP_Message import *
from dataToBytes import *
from SafeMap import *
class fs_tracker():

    def __init__(self, port):
        self.name = socket.gethostname() + ".cc"
        self.port = int(port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((socket.gethostbyname(self.name), self.port))
        self.server_socket.listen(5)
        self.node_threads = SafeMap()
        # dict of nodes and files: Key = (host,port); Value = {name file : [chunks]}
        self.nodes = SafeMap()
        # dict of files: Key = name file : {chunks : hash}
        self.files = SafeMap()

    def handle_storage(self, socket_node, payload):
        if not payload:
            return 
        files = payload.split(b'\t')
        for i in range(0, len(files), 3):
            name = files[i].decode('utf-8')
            chunks = list(range(0,int.from_bytes(files[i+1], byteorder='big')))
            
            hashes = files[i+2]
            hashes_list = []
            while (len(hashes) > 0):
                hashes_list.append(hashes[:40])
                hashes = hashes[40:]

            if not self.files.exists(name):
                self.files.put(name,{})

            dict_files = self.files.get(name)
            for chunk, hash in zip(chunks, hashes_list):
                dict_files[chunk] = hash
            
            self.nodes.get(socket_node.getpeername())[name] = dict_files.keys()

    def handle_update(self, socket_node, payload):
        if not payload:
            return
        file_name, chunks = payload[4:], payload[:4]
        chunk = int.from_bytes(chunks, byteorder='big')
        print (payload, chunk)
        file_name = file_name.decode('utf-8')
        files = self.nodes.get(socket_node.getpeername())
        if file_name in files:
            files[file_name].append(chunk)
        else:
            files[file_name] = [chunk]

    def handle_order(self, socket_node, payload):
        # result is a dict (chunk,[ips])
        result = {}
        file = payload.decode('utf-8')
        node_who_asked = socket_node.getpeername()
        for key, value in self.nodes.get_items():
            if key != node_who_asked and file in value:
                chunks = value.get(file)
                for chunk in chunks:
                    if chunk not in result:
                        result[chunk] = [key[0]]
                    else:
                        result[chunk].append(key[0])
        self.handle_ship(socket_node, result, file)

    def handle_ship(self, socket_node, payload, file):
        if not payload:
            socket_node.send(TCP_Message.create_message(SHIP,b''))
            return
        
        nodes = []
        for chunk, ips in payload.items():
            nodes.append(chunk.to_bytes(4, byteorder='big') + arrayStringToBytes(ips))
        if nodes:
            nodes.append(b''.join(self.files.get(file).values()))
        socket_node.send(TCP_Message.create_message(SHIP, (len(nodes) - 1).to_bytes(4, byteorder="big") + b' '.join(nodes)))

    def close_client(self, socket_node):
        key = socket_node.getpeername()
        print(f"Node {key} desconectado")
        self.node_threads.remove(key)
        self.nodes.remove(key)
        socket_node.close()

    def handle_client(self, socket_node):

        handle_flags = {
            STORAGE: self.handle_storage,
            UPDATE: self.handle_update,
            ORDER: self.handle_order,
        }

        while True:
            message_type, payload = TCP_Message.receive_message(socket_node)
            if not (payload or message_type):
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
    tracker = fs_tracker(sys.argv[1])
    tracker.start_connections()