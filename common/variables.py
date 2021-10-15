import logging

DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LEN = 1024
ENCODING = 'utf-8'
LOGGING_LEVEL = logging.ERROR
"""Protocol JIM"""
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

""" Other protocol`s keys """
PRESENCE = 'presense'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
SENDER = 'sender'
DESTINATION = 'destination'
EXIT = 'exit'
