import socket
import time


class ClientError(Exception):
    pass


class Client:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.data = dict()

    def put(self, key, value, timestamp=None):
        timestamp = timestamp or str(int(time.time()))
        try:
            with socket.create_connection((self.host, self.port), self.timeout) as sock:
                sock.sendall(f'put {key} {value} {timestamp}\n'.encode('utf-8'))
        except socket.error:
            raise ClientError

    def get(self, key):

        try:
            with socket.create_connection((self.host, self.port), self.timeout) as sock:
                sock.sendall(f"get {key}\n".encode("utf-8"))

            data = sock.recv(1024)
            a = data.decode("utf-8")
            self.data = dict()
            if a == 'ok\n\n':
                return {}

            elif a == 'error\nwrong command\n\n':
                raise ClientError

            for row in a.split("\n")[1:-2]:
                key = str(row.split()[0])
                value = float(row.split()[1])
                timestamp = int(row.split()[2])

                if key not in self.data:
                    self.data[key] = []
                    self.data[key].append((timestamp, value))
                else:
                    self.data[key].append((timestamp, value))
            if key == '*':
                return self.data
            else:
                if key in self.data:
                    return {key: self.data[key]}
                else:
                    return {}

            
        except socket.error:
            raise ClientError
