import logging

def __get_logger():
    logger=logging.getLogger('logger')

    logger.setLevel(logging.DEBUG)

    formatter=logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s in %(filename)s:%(lineno)d'
    )

    fileHandler = logging.FileHandler('./log/svm_error.log')
    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(logging.DEBUG)
    streamHandler.setFormatter(logging.DEBUG)

    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    if (logger.hasHandlers()):
        logger.handlers.clear()

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    logger.propagate = False

    return logger