import logging
import os

LOG_PATH = os.path.dirname(os.path.abspath(__file__)) + "/log/"


def configure_logging(
    log_path: str = LOG_PATH,
    filename: str = "temp.log",
    level: int = logging.ERROR,
) -> logging.Logger:
    logger = logging.getLogger(filename)
    logger.setLevel(level)
    fh_formatter = logging.Formatter(
        "%(levelname)s [%(filename)s(%(lineno)s):%(funcName)s] %(message)s"
    )
    if len(filename) == 0:
        sh = logging.StreamHandler()
        sh.setFormatter(fh_formatter)
        logger.addHandler(sh)
        return logger
    else:
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        fh = logging.FileHandler(log_path + filename, mode="w")
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)
        return logger
