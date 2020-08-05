from logging import getLogger

__version__ = '0.0.1'


logger = getLogger('setux_core')

debug = logger.debug
info = logger.info
error = logger.error
exception = logger.exception
