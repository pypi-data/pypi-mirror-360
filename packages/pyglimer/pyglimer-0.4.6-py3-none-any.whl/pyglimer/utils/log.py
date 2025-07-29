'''
:copyright:
   The PyGLImER development team (makus@gfz-potsdam.de).
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
:author:
   Peter Makus (makus@gfz-potsdam.de)

Created: Monday, 13th September 2021 10:38:53 am
Last Modified: Friday, 7th January 2022 11:05:39 am
'''

import logging


def start_logger_if_necessary(
        name: str, logfile: str, loglvl: int) -> logging.Logger:
    """
    Initialise a logger.

    :param name: The logger's name
    :type name: str
    :param logfile: File to log to
    :type logfile: str
    :param loglvl: Log level
    :type loglvl: int
    :return: the logger
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)
    # remove all old handlers: Note that the hasHandlers function can lead
    # to problems if there are several loggers already in the system?
    while 1:
        try:
            logger.removeHandler(logger.handlers[0])
        except IndexError:
            break
    logger.setLevel(loglvl)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)-8s %(message)s"))
    fh = logging.FileHandler(logfile, mode='w')
    fh.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)-8s %(message)s"))
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


def create_mpi_logger(logger: logging.Logger, rank: int) -> logging.Logger:
    """
    Creates a very similar logger to the input logger, but with name and
    filehandler dependent on mpi rank.

    :param logger: The original logger to crete a rank-dependent version on.
    :type logger: logging.Logger
    :return: The rank dependent logger (different name and different file)
    :rtype: logging.Logger
    """
    lvl = logger.level
    rankstr = str(rank).zfill(3)
    name = '%srank%s' % (logger.name, rankstr)
    while not logger.hasHandlers() or not (
            any(hasattr(h, 'baseFilename') for h in logger.handlers)):
        if logger.name == 'root':
            raise ValueError(
                'The logger used as input has to have a configured'
                + 'FileHandler.')
        logger = logger.parent
    for h in logger.handlers:
        if hasattr(h, 'baseFilename'):
            fn = '%srank%s.log' % (h.baseFilename.split('.')[0], rankstr)
    try:
        return start_logger_if_necessary(name, fn, lvl)
    except UnboundLocalError as e:
        print(e)
        raise ValueError(
            'The logger used as input has to have a configured FileHandler.'
        )
