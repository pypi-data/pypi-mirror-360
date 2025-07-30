import logging
import sys

# # TODO - TO SAVE FILES WITH TIME ROTATION + UNIQUE FILE NAME
# # fh = logging.FileHandler('DocGen' + '.log', mode='w')
# from datetime import datetime
# from logging.handlers import TimedRotatingFileHandler
#
# log_file_name = f"myapp-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

# fh = logging.FileHandler('DocGen' + '.log', mode='w')


class LoggerFakeWriter:
    """
    Fake file-like stream object that redirects writes to a logger instance.
    due to docx2pdf https://stackoverflow.com/questions/74787311/error-with-docx2pdf-after-compiling-using-pyinstaller
    """
    def __init__(self, logfct):
        self.logfct = logfct
        self.buf = []

    def write(self, msg):
        pass
        # if msg.endswith('\n'):
        #     self.buf.append(msg.rstrip('\n'))
        #     self.logfct(''.join(self.buf))
        #     self.buf = []
        # else:
        #     self.buf.append(msg)

    def flush(self):
        pass


class LoggerWriter:
    """
    Fake file-like stream object that redirects writes to a logger instance.
    due to docx2pdf https://stackoverflow.com/questions/74787311/error-with-docx2pdf-after-compiling-using-pyinstaller
    """
    def __init__(self, logfct):
        self.logfct = logfct
        self.buf = []

    def write(self, msg):
        # print(msg)
        red_start = "\033[91m"
        reset = "\033[0m"
        print(f"{red_start}{msg}{reset}", file=sys.stdout)

        # pass
        # if msg.endswith('\n'):
        #     self.buf.append(msg.rstrip('\n'))
        #     self.logfct(''.join(self.buf))
        #     self.buf = []
        # else:
        #     self.buf.append(msg)

    def flush(self):
        pass


def parse_logging_level(verbosity: str):
    # Check if input is a string:
    if type(verbosity) != str:
        # When not a string, print warning message and choose the default INFO
        error_message: str = f"[WARNING]: Invalid input! Parameter <logging_verbosity> '{verbosity}' is: " \
                             f"{type(verbosity)}. Should be of class 'string'.\nUsing the default verbosity 'INFO'."
        print(error_message)
        return logging.INFO

    verbosity_upper = verbosity.upper()
    if verbosity_upper == 'FATAL':
        return logging.FATAL
    elif verbosity_upper == 'ERROR':
        return logging.ERROR
    elif verbosity_upper == 'WARNING':
        return logging.WARNING
    elif verbosity_upper == 'INFO':
        return logging.INFO
    elif verbosity_upper == 'DEBUG':
        return logging.DEBUG
    elif verbosity_upper == 'TRACE':
        return logging.DEBUG
    else:
        error_message = f"[WARNING]: Invalid input! Parameter <verbosity_level> is {verbosity}. Should be either " \
                        f"'FATAL','ERROR','WARNING','INFO' or 'DEBUG'. \nUsing the default verbosity 'INFO'."
        raise  Exception(error_message)


def init_logger(module_name, verbosity):
    # Start by setting the root logger:
    verbosity_level = parse_logging_level(verbosity)
    logger = logging.getLogger(module_name)
    # create console handler with a higher log level
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(verbosity_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(verbosity_level)
    # add the handlers to the root logger
    # root_logger.addHandler(ch)
    # TODO Removed file handler untill we come up with a solution that allows running multiple exe
    # create file handler which logs even debug messages
    # fh = logging.FileHandler('DocGen' + '.log', mode='w')
    # TODO - TO SAVE FILES WITH TIME ROTATION + UNIQUE FILE NAME (instead of previous line)
    # fh = TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=7)
    # fh.setLevel(logging.DEBUG)
    # fh.setFormatter(formatter)
    # root_logger.addHandler(fh)
	# prevent propagting to stderr
    # root_logger.propagate = False

    # Then create the current module's logger (that will use the root logger's configuration):
    logger = logging.getLogger(module_name)
    return logger


def add_logger(module_name = None):
    if module_name:
        return logging.getLogger(module_name)
    else:
        # root logger
        return logging.getLogger()