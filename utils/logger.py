import logging


def get_logger(name, level='INFO'):
    logger = logging.getLogger(name)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    logger.setLevel(getattr(logging, level if isinstance(level, str) else 'INFO'))
    return logger
