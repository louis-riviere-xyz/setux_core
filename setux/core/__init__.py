from logging import getLogger

__version__ = '0.0.2'


logger = getLogger('setux')

debug = logger.debug
info = logger.info
error = logger.error
exception = logger.exception
