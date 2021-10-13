import logging
import logging.handlers
import sys
import os
from common.variables import LOGGING_LEVEL

sys.path.append('..')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH[:-6], 'log', 'server.log')

logger = logging.getLogger('server')
logger.setLevel(LOGGING_LEVEL)
formatter = logging.Formatter("%(asctime)s - %(levelname)s  - %(name)s - %(message)s")
sh_logger = logging.StreamHandler(sys.stdout)
sh_logger.setFormatter(formatter)
logger.handlers.clear()
logger.addHandler(sh_logger)
fh = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
fh.setFormatter(formatter)
fh.setLevel(LOGGING_LEVEL)
logger.addHandler(fh)

if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
