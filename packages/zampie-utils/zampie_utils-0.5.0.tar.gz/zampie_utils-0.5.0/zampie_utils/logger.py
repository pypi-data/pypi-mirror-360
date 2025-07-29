import logging
from colorlog import ColoredFormatter
from .singleton import Singleton


class Logger(metaclass=Singleton):
    """"""

    def __init__(
        self, log_level=logging.INFO, logfile="log.txt", enable_file_handler=False
    ):
        """
        description: 初始化日志记录器
        param:
            log_level: 日志级别
            logfile: 日志文件路径
            enable_file_handler: 是否启用文件处理器
        return:
        """
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)

        # 控制台处理器
        self.console_handler_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
            secondary_log_colors={},
            style="%",
        )

        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.console_handler_formatter)
        self.logger.addHandler(self.console_handler)

        # 文件处理器
        self.file_handler = None
        if enable_file_handler:
            self.enable_file_handler(logfile)

    def enable_file_handler(self, logfile="log.txt"):
        """
        description: 启用文件处理器
        param:
            logfile: 日志文件路径
        return:
        """
        if self.file_handler is None:
            self.file_handler_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            self.file_handler = logging.FileHandler(logfile)
            self.file_handler.setFormatter(self.file_handler_formatter)
            self.logger.addHandler(self.file_handler)

    def disable_file_handler(self):
        """
        description: 禁用文件处理器
        param:
        return:
        """
        if self.file_handler is not None:
            self.logger.removeHandler(self.file_handler)
            self.file_handler = None

    def log(self, level, message):
        """
        description:
        param:
        return:
        """
        self.logger.log(level, message)

    def info(self, message):
        """
        description:
        param:
        return:
        """
        self.logger.info(message)

    def warning(self, message):
        """
        description:
        param:
        return:
        """
        self.logger.warning(message)

    def error(self, message):
        """
        description:
        param:
        return:
        """
        self.logger.error(message)

    def critical(self, message):
        """
        description:
        param:
        return:
        """
        self.logger.critical(message)

    def debug(self, message):
        """
        description:
        param:
        return:
        """
        self.logger.debug(message)


if __name__ == "__main__":
    # 默认不启用文件处理器
    logger = Logger()
    logger.info("this is a log message")
    logger.warning("this is a warning message")
    logger.error("this is an error message")
    logger.debug("this is a debug message")

    # 启用文件处理器
    logger.enable_file_handler("test.log")
    logger.info("this will be written to file")

    # 禁用文件处理器
    logger.disable_file_handler()
    logger.info("this will not be written to file")

    print(f"They are same instance? {id(logger) == id(Logger())}")
