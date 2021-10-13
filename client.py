import logging
from common import client_log_config
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import send_message, get_message
import time
import sys
import json
import argparse

CLIENT_LOGGER = logging.getLogger('client')


def create_presence(account_name='Guest', msg=''):
    if msg:
        out = {
            ACTION: MESSAGE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            },
            MESSAGE_TEXT: msg
        }
        print('+++++')
    else:
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
    return out


def process_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        CLIENT_LOGGER.error(f'400 : {message[ERROR]}')
        return f'400 : {message[ERROR]}'
    raise ValueError


def message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
                               f'допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def clients_sock():
    ip_addr, port, client_mode = arg_parser()
    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {ip_addr}, '
        f'порт: {port}, режим работы: {client_mode}')
    try:
        user_sock = socket(AF_INET, SOCK_STREAM)
        user_sock.connect((ip_addr, port))
        send_message(user_sock, create_presence())
        answer = process_ans(get_message(user_sock))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу {ip_addr}:{port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    except Exception as e:
        print(e)
    else:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')

    while True:
        if client_mode == 'send':
            try:
                msg = input('введите сообщение  ')
                if msg == 'exit':
                    break
                send_message(user_sock, create_presence(msg=msg))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                CLIENT_LOGGER.error(f'Соединение с сервером {ip_addr} было потеряно.')
                sys.exit(1)
        if client_mode == 'listen':
            try:
                message_from_server(get_message(user_sock))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                CLIENT_LOGGER.error(f'Соединение с сервером {ip_addr} было потеряно.')
                sys.exit(1)

    # while True:
    #     s = socket(AF_INET, SOCK_STREAM)
    #     s.connect((ip_addr, port))

    # msg = input('Ваше сообщение: ')
    # if msg == 'exit':
    #     break
    # send_message(s, create_presence(msg=msg))
    # try:
    #     answer = process_ans(get_message(s))
    #     CLIENT_LOGGER.info(f' server response {answer}')
    # except (ValueError, json.JSONDecodeError):
    #     CLIENT_LOGGER.error('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    clients_sock()
