"""
   @copyright: 2017 by Pauli Henrikki Rikula
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import logging
import logging.handlers

def get_default_logger(logger_id):
    logger = logging.getLogger(logger_id)
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    fh = logging.handlers.RotatingFileHandler(filename=logger_id+'.log',maxBytes = (2**20)*5,backupCount=5)
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    sh.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(sh)
    logger.addHandler(fh)

    return logger