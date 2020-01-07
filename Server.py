import socket
import threading
import time

class Server:
    Clients = []
    logs = {}
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.network = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.network.bind((self.host, self.port))
        self.network.listen(20)

        print('The Server Listens at{}'.format(port))
        threading.Thread(target=self.pinger).start()

        # 心跳线程
    def pinger(self):
        while True:
            time.sleep(1)
            for client in Server.Clients:
                try:
                    msg = 'ß'.encode('ISO-8859-1')
                    # print('ß')
                    client.sock.send(msg)
                except ConnectionResetError:
                    print('ConnectionResetError')
                    client.terminate()
                    Server.Clients.remove(client)
                    pass
                except ConnectionAbortedError:
                    client.terminate()
                    Server.Clients.remove(client)
                    print('ConnectionAbortedError')
                    pass
    def start(self):
        while True:
            client_sock, client_addr = self.network.accept()
            print(f'client{client_addr}connected')

            client_sock.send('HLO'.encode())
            time.sleep(0.1)

            msg = ' '
            for client in Server.Clients:
                msg = msg + ' ' + client.clientID

            client_sock.send(msg.encode('utf-8'))

            client_thread = threading.Thread(target=self.wait_for_user_nickname, args=[client_sock])
            client_thread.start()

    def wait_for_user_nickname(self, client_sock):
        new_user_id = client_sock.recv(1024).decode('utf-8')
        print(new_user_id)

        for msgid in Server.logs.keys():
            msg = Server.logs[msgid]
            client_sock.sendall(msg.encode('ISO-8859-1'))

        client = Client(client_sock, new_user_id)
        Server.Clients.append(client)
        client.start()

class Client:
    msgID = 0
    def __init__(self, sock, clientID):
        self.sock = sock
        self.clientID = clientID
        self._run = True

    def terminate(self):
        self._run = False

    def start(self):
        while self._run:
            msg=''
            while True:
                data = self.sock.recv(1).decode('ISO-8859-1')
                msg += data
                if data == 'Ø':
                    break
            # print(msg)
            # time.sleep(0.1)
            Server.logs[Client.msgID] = msg

            if msg[0] in ['O', 'C', 'L', 'R', 'S', 'E', 'D', 'Z', 'T']:
                self.broadcast2Clients(msg)

            Client.msgID += 1
            pass

    def broadcast2Clients(self,msg):
        msg = msg.encode('ISO-8859-1')
        for client in Server.Clients:
            client.sock.sendall(msg)

if __name__ == '__main__':
    serve = Server('0.0.0.0',1111)
    serve.start()

