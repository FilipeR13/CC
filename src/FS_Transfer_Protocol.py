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
        # dict of chunks waiting to be received
        self.waitingchunks = SafeMap()

    def get_file(self, file, chunks, ip):
        self.waitingchunks.put(file, chunks)
        message = UDP_Message.create_message_udp(ORDER,file.encode('utf-8') + b' ' + arrayIntToBytes(list(range(0,len(chunks)))))
        # send order to get file
        UDP_Message.send_message(self.udp_socket, message, ip, self.port)

    def handle_udp (self):
        while True:
            message_type, chunk, payload, ip = UDP_Message.receive_message_udp(self.udp_socket)
            if message_type == ORDER:
                data = payload.split(b' ')
                if len(data) == 2:
                    UDP_Message.send_chunks(self.udp_socket, self.dict_files[data[0]], arrayBytesToInt(data[1]), ip, self.port)
            elif message_type == DATA:
                self.dict_files.exists()
                
    def close_connection (self):
        self.udp_socket.close()