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
        # dict of chunks waiting to be received by the node. Key = Name File, Value = [number Chunk]
        self.waitingchunks = SafeMap()
        # dict of ips. Key = ip, Value = file_name that the ip is sending
        self.ips = SafeMap()



    def get_file(self, file, chunks, ip):
        self.waitingchunks.put(file, chunks)
        self.ips.put(ip, file)
        for chunk in chunks:
            message = UDP_Message.create_message_udp(ORDER,file.encode('utf-8'), chunk)
            # send order to get file
            UDP_Message.send_message(self.udp_socket, message, ip, self.port)

    def handle_udp (self):
        while True:
            message_type, chunk, payload, ip = UDP_Message.receive_message_udp(self.udp_socket)
            if message_type == ORDER:
                    UDP_Message.send_chunk(self.udp_socket, self.dict_files[payload], chunk, ip, self.port)
            elif message_type == DATA:
                name_file = self.ips.get(ip)
                if self.dict_files.exists(name_file) and chunk in self.waitingchunks.get(name_file):
                    self.dict_files.get(name_file)[chunk] = payload
                    self.waitingchunks.get(name_file).remove(chunk)
                
    def close_connection (self):
        self.udp_socket.close()