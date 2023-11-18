import socket
import hashlib
from UDP_Message import * 
from dataToBytes import * 
from SafeMap import * 

class Node_Transfer:
    def __init__ (self, port):
        self.port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', port))
        # dict of files. Key = Name File, Value = {number Chunk : Chunk}
        self.dict_files = SafeMap()
        # dict of chunks waiting to be received by the node. Key = chunk, Value = hash | when received is removed | doesnt have to be a safe map because only one thread is accessing it
        self.waitingchunks = {}
        self.downloading_file = ""

    def set_waitingchunks(self, hashes):
        i = 0
        for hash in hashes:
            self.waitingchunks[i] = hash

    def set_downloading_file(self, file):
        self.downloading_file = file

    def get_file(self, chunks, ip):
        for chunk in chunks:
            message = UDP_Message.create_message_udp(ORDER,self.downloading_file.encode('utf-8'), chunk)
            # send order to get file
            UDP_Message.send_message(self.udp_socket, message, ip, self.port)

    def handle_udp (self):
        while True:
            message_type, chunk, payload, ip = UDP_Message.receive_message_udp(self.udp_socket)
            if message_type == ORDER:
                    print (payload)
                    print (chunk)
                    print (ip)
                    print(self.dict_files.get(self.downloading_file))
                    UDP_Message.send_chunk(self.udp_socket, ip[0], self.port, chunk, self.dict_files.get(self.downloading_file)[chunk])
            elif message_type == DATA:
                if chunk in self.waitingchunks and hashlib.sha1(payload).hexdigest() == self.waitingchunks[chunk]:
                    self.dict_files.get(self.downloading_file)[chunk] = payload.decode('utf-8')
                    del self.waitingchunks[chunk]

                if not self.waitingchunks:
                    self.dict_files.save_file(self.downloading_file)
                    self.waitingchunks = {}
                    self.downloading_file = ""
    
    def save_file(self, file):
        data = self.dict_files.get(file)
        sorted_data = sorted(data.items())
        try:
            with open('example.txt', 'x') as file:
                for chunk in sorted_data:
                    file.write(chunk[1])

            print("File created successfully!")
        except FileExistsError:
            print(f"File {file} already exists.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def close_connection (self):
        self.udp_socket.close()