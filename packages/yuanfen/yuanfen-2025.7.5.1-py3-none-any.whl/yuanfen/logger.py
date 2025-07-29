import logging
import os
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self, name: str = None, level: int = logging.INFO, logger: logging.Logger = None):
        os.makedirs("logs", exist_ok=True)

        self.logger = logger if logger else logging.getLogger()

        if len(self.logger.handlers) == 0:
            log_formatter = logging.Formatter(f"%(asctime)s [%(levelname)-7s] %(message)s")

            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setFormatter(log_formatter)
            self.logger.addHandler(self.stream_handler)

            self.file_handler = TimedRotatingFileHandler("logs/log", when="midnight", backupCount=365, encoding="utf-8")
            self.file_handler.suffix = "%Y-%m-%d.log"
            self.file_handler.setFormatter(log_formatter)
            self.logger.addHandler(self.file_handler)

            self.logger.setLevel(level)

        self.msg_prefix = f"[{name}] " if name else ""

    def debug(self, msg):
        self.logger.debug(f"{self.msg_prefix}{msg}")

    def info(self, msg):
        self.logger.info(f"{self.msg_prefix}{msg}")

    def warning(self, msg):
        self.logger.warning(f"{self.msg_prefix}{msg}")

    def error(self, msg):
        self.logger.error(f"{self.msg_prefix}{msg}")
