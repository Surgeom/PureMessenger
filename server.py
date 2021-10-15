import sys
import logging
from common import server_log_config
from decorators import log
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, ENCODING, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, MESSAGE_TEXT, MESSAGE, SENDER, DESTINATION, EXIT
from common.utils import get_message, send_message
import json
import select
import time

SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message, mes_list, client, clients, names):
    SERVER_LOGGER.debug(f'Message from client : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        ''' Registration '''
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200})
        else:
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Имя пользователя уже занято'
            })
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message and DESTINATION in message:

        mes_list.append(message)
        send_message(client, {RESPONSE: 200})
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                           f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


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
    names = dict()
    # names = {'1': 1}
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
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message} '
                                       f'отключился от сервера.')
                    clients.remove(client_with_message)
        for mes in messages:
            try:
                process_message(mes, names, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клиентом с именем {mes[DESTINATION]} была потеряна')
                clients.remove(names[mes[DESTINATION]])
                del names[mes[DESTINATION]]
            messages.clear()


if __name__ == '__main__':
    runserver()
