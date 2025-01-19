import logging
from logging import Logger

def get_logger(name: str) -> Logger:

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(filename=f"logs/{name}.log", mode="a")
    file_handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    formater = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formater)
    stream_handler.setFormatter(formater)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger