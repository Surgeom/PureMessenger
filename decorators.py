import sys

sys.path.append('..')
import logging
from common import client_log_config, server_log_config
import traceback
import inspect

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):
    def wrapper(*args, **kwargs):
        f = func(*args, **kwargs)
        # print(LOGGER)
        # print(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. ')
        LOGGER.debug(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                     f'Вызов из модуля {func.__module__}. Вызов из'
                     f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return f

    return wrapper
