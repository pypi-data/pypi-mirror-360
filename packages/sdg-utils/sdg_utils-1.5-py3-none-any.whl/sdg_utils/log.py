import logging
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
from time import time

FRMT = logging.Formatter('%(relativeCreated)04d %(name)-5s %(levelname)s %(message)s')
__stream_hndlr = None
__stream_level = None
__file_lhndlrs = []
__file_frmt = FRMT


def log_levels(levels={CRITICAL: 'C', ERROR: 'E', WARNING: 'W', INFO: 'I', DEBUG: 'd'}):
    for level, name in levels.items():
        logging.addLevelName(level, name)


def log_init(name=None, level=INFO, frmt_stream=FRMT, frmt_file=None):
    global __stream_hndlr, __stream_level, __file_frmt
    logger = logging.getLogger(name)
    logger.setLevel(level)
    log_levels()
    __stream_hndlr = logging.StreamHandler()
    __stream_hndlr.setLevel(level)
    __stream_hndlr.setFormatter(frmt_stream)
    logger.addHandler(__stream_hndlr)
    __file_frmt = frmt_file or frmt_stream
    __stream_level = level
    return logger


def log_get_stream_handler():
    return __stream_hndlr


def log_file_handlers():
    return __file_lhndlrs


def log_close():
    global __file_lhndlrs
    for hndlr in __file_lhndlrs:
        logger = logging.getLogger()
        logger.removeHandler(hndlr)
        hndlr.close()


def log_file(filename, level=DEBUG, frtm=None, reset_time=True):
    global __file_lhndlrs
    logger = logging.getLogger()
    if logger.getEffectiveLevel() > level:
        logger.setLevel(level)
    hndlr = logging.FileHandler(filename, mode='w')
    hndlr.setLevel(level)
    hndlr.setFormatter(frtm or __file_frmt)
    logger.addHandler(hndlr)
    __file_lhndlrs.append(hndlr)
    if reset_time:
        log_set_starttime(time())
    return logger


def log_set_starttime(starttime):
    try:
        logging._startTime = starttime
    except AttributeError:
        pass


def log_starttime():
    try:
        return logging._startTime
    except AttributeError:
        return time()


def log_stream_disable():
    global __stream_level
    __stream_level = __stream_hndlr.level
    __stream_hndlr.level = CRITICAL


def log_stream_enable():
    __stream_hndlr.level = __stream_level


def log_stream_off(func):
    def wrapper(*args, **kwargs):
        savelevel = __stream_hndlr.level
        __stream_hndlr.level = CRITICAL
        ret = func(*args, **kwargs)
        __stream_hndlr.level = savelevel
        return ret
    return wrapper
