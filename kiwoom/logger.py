import logging
import logging.handlers
from singleton_decorator import singleton


@singleton
class KWlog():
    def __init__(self):
        self.logger_name = "KW"
        self.logger = logging.getLogger(self.logger_name)
        formatter = logging.Formatter('[%(asctime)s|%(levelname)s|%(funcName)s:%(lineno)s] %(message)s')
        file_max_byte = 1024 * 1024 * 10  # 10MB
        log_path = "D:/work/TopTrader_log/{}.log".format(self.logger_name)
        file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=file_max_byte, backupCount=1000)
        stream_handler = logging.StreamHandler()
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.DEBUG)

    def debug(self, m):
        self.logger.debug(m)

    def info(self, m):
        self.logger.info(m)

    def warning(self, m):
        self.logger.warning(m)

    def error(self, m):
        self.logger.error(m)

    def critical(self, m):
        self.logger.critical(m)
