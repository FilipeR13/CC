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
    tracker_port = 9090
    node = fs_node('localhost', 54321)

    # Enter a loop to read input from the terminal and send it to the tracker
    while True:
        user_input = input("Enter a message: ")
        if user_input:
            node.send_data(user_input)

    # Ver multithreading em tcp: a porta do server recebe um pedido do cliente e depois cria uma nova thread que criará uma nova porta exclusiva para esse cliente.
    # Assim podemos evitar que quando um cliente esteja a utilizar a porta do server os outros tenham de ficar à espera.