import socket
import hashlib
from UDP_Message import * 
from dataToBytes import * 
from SafeMap import * 

class Node_Transfer:
    def __init__ (self, port, path, tcp_connection):
        self.port = port
        self.path = path
        self.tcp_connection = tcp_connection
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', port))
        # dict of files. Key = Name File, Value = {number Chunk : Chunk}
        self.dict_files = SafeMap()
        # dict of chunks waiting to be received by the node. Key = chunk, Value = hash | when received is removed | doesnt have to be a safe map because only one thread is accessing it
        self.waitingchunks = {}
        self.downloading_file = ""

    def set_waitingchunks(self, hashes):
        i = 1
        for hash in hashes:
            self.waitingchunks[i] = hash
            i+=1

    def set_downloading_file(self, file):
        self.downloading_file = file
        self.dict_files.put(file, {})

    def get_file(self, chunks, ip):
        for chunk in chunks:
            message = UDP_Message.create_message_udp(ORDER,self.downloading_file.encode('utf-8'), chunk)
            # send order to get file
            UDP_Message.send_message(self.udp_socket, message, ip, self.port)

    def handle_udp (self):
        while True:
            message_type, chunk, payload, ip = UDP_Message.receive_message_udp(self.udp_socket)
            n_chunk = int.from_bytes(chunk, byteorder='big')
            data = payload.decode('utf-8')
            if message_type == ORDER:
                    if self.dict_files.exists(data):
                        print(f"Sending chunk {n_chunk} of file {data}")
                        UDP_Message.send_chunk(self.udp_socket, ip[0], ip[1], n_chunk, self.dict_files.get(data)[n_chunk])
                    
            elif message_type == DATA:
                print(f"Received chunk {n_chunk} of file {self.downloading_file}")
                if n_chunk in self.waitingchunks and hashlib.sha1(payload).hexdigest() == self.waitingchunks[n_chunk]:
                    self.tcp_connection.update_file(self.downloading_file, n_chunk, self.waitingchunks[n_chunk])
                    self.dict_files.get(self.downloading_file)[n_chunk] = data
                    del self.waitingchunks[n_chunk]

                if not self.waitingchunks:
                    self.save_file(self.downloading_file)
                    self.waitingchunks = {}
                    self.downloading_file = ""
    
    def save_file(self, file_name):
        data = self.dict_files.get(file_name)
        sorted_data = sorted(data.items())
        try:
            with open(self.path + file_name, 'w') as file:
                for chunk in sorted_data:
                    file.write(chunk[1])
        except FileExistsError:
            print(f"File {file_name} already exists.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def close_connection (self):
        self.udp_socket.close()