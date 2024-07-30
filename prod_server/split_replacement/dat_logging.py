import logging

logger = None


def initialize_logger():
    global logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='logging/read_dats.log',
                        encoding='utf-8',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s')


def log_non_fatal_error(msg):
    global logger
    logger.error(msg)


def log_fatal_error(msg):
    global logger
    logger.critical(msg)


def log_warning(msg):
    global logger
    logger.warning(msg)


def log_info(msg):
    global logger
    logger.info(msg)
