import logging
import logging.config

logging.config.fileConfig('logging.conf')
main_logger = logging.getLogger('main_logger')
user_logger = logging.getLogger('user_logger')
product_logger = logging.getLogger('product_logger')
board_logger = logging.getLogger('board_logger')
logging.getLogger('werkzeug').disabled=True

if __name__ == '__main__' :
    user_logger.debug('debug...')
    user_logger.info('info...')
    user_logger.warning('warning...')
    user_logger.error('error...')
    user_logger.critical('critical...')