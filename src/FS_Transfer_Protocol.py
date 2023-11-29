import socket
import hashlib
import os
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
        name_node = socket.gethostname() + ".cc"
        self.ip = socket.gethostbyname(name_node)
        self.udp_socket.bind((self.ip, port))
        # dict of information of other nodes. Key = nomeNodo | Value = [TIME_ACC,MSS_SEND, MSS_RCV]
        self.nodes = {}
        self.max_rtt = 1000
        # dict of chunks waiting to be received by the node. Key = chunk, Value = hash | when received is removed
        self.waitingchunks = SafeMap()
        self.timeout = 0.5
        self.threads_timeout = SafeMap()
        self.downloading_file = ""

    def set_waitingchunks(self, hashes):
        i = 0
        for hash in hashes:
            self.waitingchunks.put(i, hash)
            i+=1

    def set_downloading_file(self, file):
        self.downloading_file = file
        with open(self.path + file, 'w+b') as f:
            f.seek(0)
            f.truncate()
            f.close()

    def get_chunk(self, socket_to_send, chunks, name):
        for chunk in chunks:
            message = UDP_Message.create_message_udp(ORDER,self.downloading_file.encode('utf-8'), chunk)
            self.nodes[name][1] += 1
            ip_to_send = socket.gethostbyname(name + ".cc")
            # send order to get file
            timeout = TimeOutThread(self.timeout, self.get_chunk, chunk, name)
            self.threads_timeout.put(chunk, timeout)
            timeout.start()
            UDP_Message.send_message(socket_to_send, message, (ip_to_send, self.port))
        socket_to_send.close()

    def get_file(self, chunks_names):
        names_chunks = search_chunks(chunks_names, self.nodes, self.max_rtt)
        for name, chunks in names_chunks.items():
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            new_socket.bind((self.ip,0))
            thread_socket = threading.Thread(target=self.get_chunk, args=(new_socket, chunks, name,))
            thread_socket.start()

    def update_nodes(self, name_node, time_stamp_env, timestamp_now):
        rtt = timestamp_now - time_stamp_env
        # update node
        time_acc, mss_send, mss_rcv = self.nodes[name_node]
        self.nodes[name_node] = [time_acc + rtt, mss_send, mss_rcv + 1]
        # update max_rtt
        self.max_rtt = max(self.max_rtt, rtt)

    def handle_udp (self):
        while True:
            message_type, n_chunk, time_stamp_env, payload, ip = UDP_Message.receive_message_udp(self.udp_socket)
            if message_type == ORDER:
                data = payload.decode('utf-8')
                if os.path.isfile(self.path + data):
                    with open(self.path + data, 'r+b') as file:
                        file.seek(n_chunk * PACKET_SIZE)
                        content = file.read(PACKET_SIZE)
                        file.flush()
                        file.close()
                    
                    UDP_Message.send_chunk(self.udp_socket, ip[0], self.port, n_chunk, content, time_stamp_env)
                    
            elif message_type == DATA:
                timestamp_now = round(time.time() * 1000) - 170000000000
                name_node = socket.gethostbyaddr(ip[0])[0][:-20]
                self.update_nodes(name_node, time_stamp_env, timestamp_now)

                expected_hash = self.waitingchunks.get(n_chunk)
                if self.waitingchunks.exists(n_chunk) and hashlib.sha1(payload).hexdigest() == expected_hash:
                    # stop timeout thread
                    self.threads_timeout.get(n_chunk).stop_event.set()
                    self.threads_timeout.remove(n_chunk)
                    # update file
                    self.tcp_connection.update_file(self.downloading_file, n_chunk, expected_hash)
                    # save chunk
                    with open(self.path + self.downloading_file, 'r+b') as f:    
                        f.seek(n_chunk * PACKET_SIZE)
                        f.write(payload)
                        f.flush()
                        f.close()
                    # remove chunk from waitingchunks
                    self.waitingchunks.remove(n_chunk)

                # if all chunks received reset waitingchunks and save file
                if self.waitingchunks.isEmpty():
                    print("All chunks received!")
                    self.waitingchunks = SafeMap()
                    self.downloading_file = ""

    def close_connection (self):
        self.udp_socket.close()