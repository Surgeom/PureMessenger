from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR
from common.utils import send_message, get_message
import time
import sys
import json
import logging
from log import client_log_config
CLIENT_LOGGER = logging.getLogger('client')


def create_presence(account_name='Guest', msg=''):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
        'DATA': msg
    }
    return out


def process_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        CLIENT_LOGGER.error(f'400 : {message[ERROR]}')
        return f'400 : {message[ERROR]}'
    raise ValueError


def clients_sock(message=''):
    try:
        if len(sys.argv) == 3:
            ip_addr = sys.argv[1]
            port = int(sys.argv[2])
            if port < 1024 or port > 65535:
                CLIENT_LOGGER.error(f'Bad port = {port}')
                raise ValueError
        else:
            ip_addr = DEFAULT_IP_ADDRESS
            port = DEFAULT_PORT
    except IndexError as e:
        CLIENT_LOGGER.error(f'{e}')
        sys.exit(1)
    except ValueError as e:
        CLIENT_LOGGER.error(f'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.{e}')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((ip_addr, port))
    send_message(s, create_presence(msg=message))
    # s.send(mes.encode(ENCODING))
    # data = get_message(s)
    try:
        answer = process_ans(get_message(s))
        CLIENT_LOGGER.info(f' server response {answer}')
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOGGER.error('Не удалось декодировать сообщение сервера.')

    s.close()


if __name__ == '__main__':
    clients_sock('fdfdfdg')
