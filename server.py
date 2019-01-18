import asyncio

my_dict = {}
error = 'error\nwrong command\n\n'.encode('utf8')
ok = 'ok\n\n'.encode('utf8')


class ClientServerProtocol(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self.trans = None

    def connection_made(self, trans):
        self.trans = trans

    def data_received(self, data):
        resp = process(data.decode('utf8').split())
        self.trans.write(resp)


def process(message):
    if message is not None:
        instruction, key, values = message[0], message[1], message[2:]

        if instruction == 'put':
            if len(message) > 2:
                if key not in my_dict:
                    my_dict[key] = []
                if values not in my_dict[key]:
                    my_dict[key].append(values)

                return ok

            else:
                return error

        elif instruction == 'get':
            answer_string = 'ok\n'
            try:
                symbol = message[1]

                if symbol == '*':
                    response = my_dict

                    for key in response:
                        for value in response[key]:
                            answer_string += key
                            for i in value:
                                answer_string += ' ' + i
                            answer_string += '\n'

                    answer_string += '\n'

                    return answer_string.encode('utf8')


                elif symbol is not None:
                    response = my_dict
                    key = symbol
                    for value in response[key]:
                        answer_string += key
                        for i in value:
                            answer_string += ' ' + i
                        answer_string += '\n'

                    answer_string += '\n'

                    return answer_string.encode('utf8')

                else:
                    return error

            except (KeyError, FileNotFoundError, IndexError):
                return ok

        else:
            return error
    else:
        return error


def run_server(host, port):
    loop = asyncio.get_event_loop()
    corutina = loop.create_server(ClientServerProtocol, host, port)
    server = loop.run_until_complete(corutina)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


run_server('127.0.0.1', 8888)
