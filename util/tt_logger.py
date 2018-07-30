import logging
import logging.handlers
from singleton_decorator import singleton


@singleton
class TTlog():
    def __init__(self, logger_name="TT"):
        self.logger = logging.getLogger(logger_name)
        format = '[%(asctime)s|{}|%(levelname)s|%(filename)s:%(funcName)s:%(lineno)s] %(message)s'. \
            format(logger_name)
        formatter = logging.Formatter(format)
        file_max_byte = 1024 * 1024 * 10  # 10MB
        log_path = "D:/work/TopTrader_log/app_{}.log".format(logger_name)
        file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=file_max_byte, backupCount=1000)
        stream_handler = logging.StreamHandler()
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.DEBUG)
