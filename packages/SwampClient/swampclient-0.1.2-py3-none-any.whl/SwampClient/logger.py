# swamp_mqtt_client/logger.py

import logging

def setup_logger(name: str, level: str = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(level)

        formatter = logging.Formatter('[%(asctime)s] '      # timestamp
                                        '[%(levelname)s] '  # log level
                                        '[%(name)s] '       # logger name
                                        '[%(filename)s '    # source
                                        '%(funcName)s() '
                                        '%(lineno)d]'
                                        ': %(message)s')    # message

        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    logger.propagate = False
    return logger
