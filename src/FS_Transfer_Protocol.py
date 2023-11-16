import socket
import hashlib
from UDP_Protocol import * 
from dataToBytes import * 
from SafeMap import * 

class Node_Transfer:
    def __init__ (self, port):
        self.port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', port))
        # dict of files. Key = Name File, Value = {number Chunk : Chunk}
        self.dict_files = SafeMap()

    def get_file(self, file, chunks, ip):
        message = UDP_Message.create_message_udp(ORDER,file.encode('utf-8') + b' ' + arrayIntToBytes(range(0,len(chunks))))
        # send order to get file
        UDP_Message.send_message(self.udp_socket, message, ip, self.port)

        message_type, chunk, payload, ip_dest = UDP_Message.receive_message_udp(self.udp_socket)
        if message_type == ACK:
            while chunks:
                number, chunk = UDP_Message.receive_chunk(self.udp_socket, chunks, ip, self.port)
                chunks.remove(number)
                self.dict_files.get(file)[number] = chunk
        elif message_type == None:
            return self.get_file(file, chunks, ip)    


    def handle_udp (self):
        while True:
            message_type, chunk, payload, ip = UDP_Message.receive_message_udp(self.udp_socket)
            if message_type == ORDER:
                file, chunks = payload.split(b' ')
                UDP_Message.send_chunks(self.udp_socket, self.dict_files[file], arrayBytesToInt(chunks), ip, self.port)


    def close_connection (self):
        self.udp_socket.close()

    