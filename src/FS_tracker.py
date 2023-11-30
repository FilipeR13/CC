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
        # dict of nodes and files: Key = name file; Value = {node : [chunks]}
        self.nodes = SafeMap()
        # dict of files: Key = name file : {chunks : hash}
        self.files = SafeMap()

    def handle_storage(self, _,name_node, payload):
        if not payload:
            return 
        files = payload.split(b'\t')
        for i in range(0, len(files), 3):
            file = files[i].decode('utf-8')
            chunks = list(range(0,int.from_bytes(files[i+1], byteorder='big')))
            
            hashes = files[i+2]
            hashes_list = []
            while (len(hashes) > 0):
                hashes_list.append(hashes[:40])
                hashes = hashes[40:]

            if not self.files.exists(file):
                self.files.put(file,{})

            if not self.nodes.exists(file):
                self.nodes.put(file,SafeMap())

            dict_files = self.files.get(file)
            for chunk, hash in zip(chunks, hashes_list):
                dict_files[chunk] = hash
            
            self.nodes.get(file).put(name_node,chunks)

    def handle_update(self, _, name_node, payload):
        if not payload:
            return
        file_name, chunks = payload[4:], payload[:4]
        chunk = int.from_bytes(chunks, byteorder='big')
        file_name = file_name.decode('utf-8')
        nodes = self.nodes.get(file_name)
        if nodes.exists(name_node):
            nodes.get(name_node).append(chunk)
        else:
            nodes.put(name_node, [chunk])

    def handle_order(self, socket_node, name_node, payload):
        # result is a dict (chunk,[names])
        result = {}
        file = payload.decode('utf-8')

        nodes = self.nodes.get(file)
        if nodes:
            for node, chunks in nodes.get_items():
                for chunk in chunks:
                    if chunk not in result:
                        result[chunk] = [node]
                    else:
                        result[chunk].append(node)
        self.handle_ship(socket_node, result, file)

    def handle_ship(self, socket_node, payload, file):
        if not payload:
            socket_node.send(TCP_Message.create_message(SHIP,b''))
            return
        print (payload)
        nodes = []
        for chunk, names in payload.items():
            nodes.append(chunk.to_bytes(4, byteorder='big') + arrayStringToBytes(names))
        if nodes:
            nodes.append(b''.join(self.files.get(file).values()))
        socket_node.send(TCP_Message.create_message(SHIP, (len(nodes) - 1).to_bytes(4, byteorder="big") + b' '.join(nodes)))

    def close_client(self, socket_node, name_node):
        print(f"Node {name_node} desconectado")
        for file_name,nodes in self.nodes.get_items():
            if nodes.exists(name_node):
                nodes.remove(name_node)
            if nodes.isEmpty():
                self.nodes.remove(file_name)
                self.files.remove(file_name)
        socket_node.close()

    def handle_client(self, socket_node, name_node):

        handle_flags = {
            STORAGE: self.handle_storage,
            UPDATE: self.handle_update,
            ORDER: self.handle_order,
        }

        while True:
            message_type, payload = TCP_Message.receive_message(socket_node)
            if not (payload or message_type):
                break
            handle_flags[message_type](socket_node, name_node, payload)

        self.close_client(socket_node, name_node)

    def start_connections(self):
        print(f"Servidor ativo em {self.server_socket.getsockname()[0]} porta {self.port}")
        try:
            while True:
                socket_node, address_node = self.server_socket.accept()
                name_node = socket.gethostbyaddr(address_node[0])[0][:-20]
                print(f"O Node {name_node} conectou-se ao servidor")

                thread_node = threading.Thread(target=self.handle_client, args=(socket_node,name_node,))    

                thread_node.start()
                
        except KeyboardInterrupt:
            print("\nServer disconnected")
            self.server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    tracker = fs_tracker(sys.argv[1])
    tracker.start_connections()