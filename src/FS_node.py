import socket
import sys


class fs_node():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host,self.port))
        print("Coneção FS Track Protocol com servidor localhost porta 9090")

    def send_data(self, data):
        self.client_socket.send(data.encode())
    
def main():
    if len(sys.argv) != 4:
        print("Erro nos argumentos: FS_node.py <message> <host> <port>")
    node = fs_node(sys.argv[2],sys.argv[3])
    try:
        while True:
            user_input = input("Enter a message: ")
            if user_input:
                node.send_data(user_input)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        node.client_socket.close()
        sys.exit(0)



if __name__ == "__main__":
    main()
    # Ver multithreading em tcp: a porta do server recebe um pedido do cliente e depois cria uma nova thread que criará uma nova porta exclusiva para esse cliente.
    # Assim podemos evitar que quando um cliente esteja a utilizar a porta do server os outros tenham de ficar à espera.