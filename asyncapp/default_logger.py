"""
   @copyright: 2017 by Pauli Henrikki Rikula
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import logging
import logging.handlers

def get_default_logger(logger_id):
    '''A logging.Logger factory.
    Sets up an logger instance which prints to stdout and then
    logs all events to a rolling log file on the execution folder.
    The logger makes 5 backups of the old log files.
    '''
    logger = logging.getLogger(logger_id)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=logger_id+'.log',
        maxBytes=(2**20)*5,
        backupCount=5
        )
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger

