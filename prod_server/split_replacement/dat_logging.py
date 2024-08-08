import logging


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename='logging/read_dats.log',
                            encoding='utf-8',
                            level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s')

    def log_non_fatal_error(self, msg):
        self.logger.error(msg)

    def log_fatal_error(self, msg):
        self.logger.critical(msg)

    def log_warning(self, msg):
        self.logger.warning(msg)

    def log_info(self, msg):
        self.logger.info(msg)
