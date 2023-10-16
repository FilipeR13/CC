import socket


class fs_tracker():

    def __init__(self):
        self.host = 'localhost'
        self.port = 9090
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

    def start_connections(self):
        print("Servidor ativo em " + self.host + " porta " + str(self.port))
        while True:
            client_socket, client_address = self.server_socket.accept()
            data = client_socket.recv(1024)
            print(data.decode())


if __name__ == "__main__":
    tracker = fs_tracker()
    tracker.start_connections()


