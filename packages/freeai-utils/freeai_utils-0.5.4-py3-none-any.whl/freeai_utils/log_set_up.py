import logging

def setup_logging(name: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent logs from bubbling up to root

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger
