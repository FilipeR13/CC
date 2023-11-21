import socket
import hashlib
from UDP_Message import * 
from dataToBytes import * 
from SafeMap import * 
from Timeout import * 
from Algorithm import * 

class Node_Transfer:
    def __init__ (self, port, path, tcp_connection):
        self.port = port
        self.path = path
        self.tcp_connection = tcp_connection
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', port))
        # dict of information of other nodes. Key = ip | Value = (TIME_ACC,MSS_SEND, MSS_RCV)
        self.nodes = {}
        self.max_rtt = 1000
        # dict of files. Key = Name File, Value = {number Chunk : Chunk}
        self.dict_files = SafeMap()
        # dict of chunks waiting to be received by the node. Key = chunk, Value = hash | when received is removed
        self.waitingchunks = SafeMap()
        self.timeout = 0.5
        self.threads_timeout = SafeMap()
        self.downloading_file = ""

    def set_waitingchunks(self, hashes):
        i = 1
        for hash in hashes:
            self.waitingchunks.put(i, hash)
            i+=1

    def set_downloading_file(self, file):
        self.downloading_file = file
        self.dict_files.put(file, {})

    def get_chunk(self, socket, chunks, ip):
        for chunk in chunks:
            message = UDP_Message.create_message_udp(ORDER,self.downloading_file.encode('utf-8'), chunk)
            # send order to get file
            UDP_Message.send_message(socket, message, (ip, self.port))
            timeout = TimeOutThread(self.timeout, self.get_chunk, chunk, ip)
            self.threads_timeout.put(timeout, chunk)
            timeout.start()
        socket.close()

    def get_file(self, chunks_ips):
        ips_chunks = search_chunks(chunks_ips, self.nodes, self.max_rtt)
        for ip, chunks in ips_chunks.items():
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            new_socket.bind(('',0))
            thread_socket = threading.Thread(target=self.get_chunk, args=(new_socket, chunks, ip,))
            thread_socket.start()

    def handle_udp (self):
        while True:
            message_type, chunk, payload, ip = UDP_Message.receive_message_udp(self.udp_socket)
            n_chunk = int.from_bytes(chunk, byteorder='big')
            data = payload.decode('utf-8')
            if message_type == ORDER:
                if self.dict_files.exists(data):
                    print(f"Sending chunk {n_chunk} of file {data}")
                    UDP_Message.send_chunk(self.udp_socket, ip, n_chunk, self.dict_files.get(data)[n_chunk])
                    
            elif message_type == DATA:
                expected_hash = self.waitingchunks.get(n_chunk)
                print(f"comparaHash {n_chunk}: {hashlib.sha1(payload).hexdigest() == expected_hash}")
                if self.waitingchunks.exists(n_chunk) and hashlib.sha1(payload).hexdigest() == expected_hash:
                    # stop timeout thread
                    self.threads_timeout.get(n_chunk).stop_event.set()
                    self.threads_timeout.remove(n_chunk)
                    # update file
                    self.tcp_connection.update_file(self.downloading_file, n_chunk, expected_hash)
                    # save chunk
                    self.dict_files.get(self.downloading_file)[n_chunk] = data
                    # remove chunk from waitingchunks
                    self.waitingchunks.remove(n_chunk)

                # if all chunks received reset waitingchunks and save file
                if self.waitingchunks.isEmpty():
                    print("All chunks received!")
                    self.save_file(self.downloading_file)
                    self.waitingchunks = SafeMap()
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