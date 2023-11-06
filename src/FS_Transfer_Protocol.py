import socket

class FS_Transfer_Protocol:
    def __init__ (self, host, port):
        self.host = host
        self.port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((host, port))

    