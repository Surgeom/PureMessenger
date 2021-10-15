import logging
from common import client_log_config
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
from common.utils import send_message, get_message
import time
import sys
import json
import argparse
import threading

CLIENT_LOGGER = logging.getLogger('client')


def create_presence(account_name='Guest', exitmmsg=''):
    if exitmmsg and exitmmsg == 'exit':
        out = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }
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


def message_from_server(sock, username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE:
                # SENDER in message and MESSAGE_TEXT in message:
                print(f'Получено сообщение от пользователя '
                      f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                                   f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.debug(f'Получено некорректное сообщение с сервера: {message}')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            break


def create_message(sock, account_name='Guest'):
    while True:
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(sock, message_dict)
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            sys.exit(1)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port


def light_gui_for_client(sock, username):
    print(f'Hi {username}!')
    create_presence(account_name=username)
    while True:
        command = input('Введите команду(sendmes /exit):  ')
        if command == 'sendmes':
            create_message(sock, username)

        elif command == 'exit':
            send_message(sock, create_presence(username, exitmmsg='exit'))
            print('Завершение соединения.')
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова.')


def clients_sock():
    client_name = input("Введите ваще имя ")
    ip_addr, port = arg_parser()
    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {ip_addr}, '
        f'порт: {port}')
    try:
        user_sock = socket(AF_INET, SOCK_STREAM)
        user_sock.connect((ip_addr, port))
        send_message(user_sock, create_presence(client_name))
        answer = process_ans(get_message(user_sock))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную JSON строку.')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу {ip_addr}:{port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    except Exception as e:
        print(e)
    else:
        receiver = threading.Thread(target=message_from_server, args=(user_sock, client_name), daemon=True)
        receiver.start()

        user_interface = threading.Thread(target=light_gui_for_client, args=(user_sock, client_name), daemon=True)
        user_interface.start()
        CLIENT_LOGGER.debug('Запущены процессы')
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    clients_sock()
