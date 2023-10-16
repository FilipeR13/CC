import socket


class fs_node():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost',9090))
        print("Coneção FS Track Protocol com servidor localhost porta 9090")

    def send_data(self, data):
        self.client_socket.send(data.encode())

if __name__ == "__main__":
    tracker_host = 'localhost'
    tracker_port = 12345
    node = fs_node('localhost', 54321)

    data1 = "Hello World!"

    node.send_data(data1)