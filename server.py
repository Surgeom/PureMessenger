import sys
import logging
from common import server_log_config
from decorators import log
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, ENCODING, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, MESSAGE_TEXT, MESSAGE, SENDER
from common.utils import get_message, send_message
import json
import select
import time

SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message, mes_list, client):
    SERVER_LOGGER.debug(f'Message from client : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':

        send_message(client, {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        mes_list.append((message[USER][ACCOUNT_NAME], message[MESSAGE_TEXT]))
        send_message(client, {RESPONSE: 200})
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


def runserver():
    try:
        if '-p' in sys.argv and '-a' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
            address = sys.argv[sys.argv.index('-a') + 1]
            if port < 1024 or port > 65535:
                SERVER_LOGGER.error(f'Bad port = {port}')
                raise ValueError
        else:
            port = DEFAULT_PORT
            address = ''
    except IndexError as e:
        SERVER_LOGGER.error(f'{e}')
        sys.exit(1)
    except ValueError as e:
        SERVER_LOGGER.error(f'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.{e}')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((address, port))
    s.settimeout(0.1)
    clients = []
    messages = []
    s.listen(MAX_CONNECTIONS)
    SERVER_LOGGER.info(f' Run server on port = {port}')

    while True:
        try:
            client, addr = s.accept()
        except OSError:
            pass
        else:
            clients.append(client)
        recv_data_lst = []
        send_data_lst = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 5)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    # data = get_message(client_with_message)
                    # SERVER_LOGGER.info(f'{data}')
                    # send_message(client_with_message, process_client_message(data))
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message)

                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message} '
                                       f'отключился от сервера.')
                    clients.remove(client_with_message)
        # print(messages)
        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Клиент {waiting_client} отключился от сервера!.')
                    clients.remove(waiting_client)

        # try:
        #     data = get_message(client)
        #     SERVER_LOGGER.info(f'{data}')
        #     msg = process_client_message(data)
        #     send_message(client, msg)
        #     client.close()
        # except (ValueError, json.JSONDecodeError):
        #     SERVER_LOGGER.error(f'Bad message {data}')
        #     msg = {
        #         RESPONSE: 400,
        #         ERROR: 'Bad Request'
        #     }
        #     send_message(client, msg)
        #     client.close()


if __name__ == '__main__':
    runserver()
