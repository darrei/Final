import asyncio


class MySubError(Exception):
    pass


class Protocol:

    def encode(self, serv_ans):
        encode_list = []
        for i in serv_ans:
            if i is None:
                continue

            for key in i.keys():
                for ke in i[key]:
                    ke = list(ke)
                    encode_list.append("{} {} {}".format(key, ke[1], ke[0]))

        response = 'ok\n'

        if encode_list:
            for i in encode_list:
                response += str(i) + '\n'

        response += '\n'
        return response

    def decode(self, data):
        request = []
        try:
            decode_list = data.strip().split()
            if decode_list[0] == "put":
                request.append((decode_list[0], decode_list[1], float(decode_list[2]), int(decode_list[3])))
            elif decode_list[0] == "get":
                request.append((decode_list[0], decode_list[1]))
            else:
                raise MySubError()
        except:
            raise MySubError()
        return request


class ServerCommand:
    def __init__(self, infobox):
        self.infobox = infobox

    def run(self, command, *args):
        if command == "put":
            return self.infobox.put(*args)
        elif command == "get":
            return self.infobox.get(*args)
        else:
            raise MySubError()


class Metrics:
    def __init__(self):
        self.data = {}
        self.result = {}

    def put(self, key, value, timestamp=0):
        if key not in self.data:
            self.data[key] = {}
        self.data[key][timestamp] = value

    def get(self, key):
        new_data = self.data
        if key != "*":
            val = new_data.get(key, {})
            new_data = {key: val}

        self.result = {}
        for key in new_data.keys():
            tmp = new_data[key]
            self.result[key] = sorted(tmp.items())
        return self.result


class ClientServerProtocol(asyncio.Protocol):
    metric = Metrics()

    def __init__(self):
        super().__init__()

        self.protocol = Protocol()
        self.executor = ServerCommand(self.metric)
        self.str_byte = b''

    def income_server_command(self, data):
        commands = self.protocol.decode(data)

        answer = []
        for args in commands:
            answer.append(self.executor.run(*args))
        return self.protocol.encode(answer)

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.str_byte += data
        try:
            str_byte = self.str_byte.decode()
        except:
            return

        if not str_byte.endswith('\n'):
            return

        self.str_byte = b''

        try:
            request = self.income_server_command(str_byte)
        except MySubError as err:
            self.transport.write("error\n{}\n\n".format(err).encode())
            return

        self.transport.write(request.encode())


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(ClientServerProtocol, host, port)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


run_server('127.0.0.1', 8888)
