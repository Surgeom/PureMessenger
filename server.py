import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, ENCODING, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR
from common.utils import get_message, send_message
import json


def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def runserver():
    try:
        if '-p' in sys.argv and '-a' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
            address = sys.argv[sys.argv.index('-a') + 1]
            if port < 1024 or port > 65535:
                raise ValueError
        else:
            port = DEFAULT_PORT
            address = ''
    except IndexError as e:
        print(e)
        sys.exit(1)
    except ValueError as e:
        print(e)
        print(
            'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.listen(MAX_CONNECTIONS)
    while True:
        client, addr = s.accept()
        try:
            data = get_message(client)
            print(data)
            msg = process_client_message(data)
            send_message(client, msg)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')
            msg = {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            }
            send_message(client, msg)
            client.close()


if __name__ == '__main__':
    # runserver()
    print(process_client_message({ USER: {ACCOUNT_NAME: 'Guest'}}))
