from logging import FileHandler
from enum import Enum
from contextlib import contextmanager

from pybrary.func import caller


class Verbosity(Enum):
    quiet = 0
    normal = 1
    verbose = 2


class Logger:
    def __init__(self, logger, verbosity=None):
        self.logger = logger
        self.verbosity = verbosity or Verbosity.normal

    @contextmanager
    def quiet(self):
        back = self.verbosity
        self.verbosity = Verbosity.quiet
        try:
            yield
        finally:
            self.verbosity = back

    def debug(self, *a):
        if len(a)>1:
            self.logger.debug(*a)
        else:
            self.logger.debug(f'{caller()} -> {a[0]}')

    def info(self, *a):
        if self.verbosity.value < Verbosity.normal.value:
            self.debug(*a)
        else:
            self.logger.info(*a)

    def error(self, *a):
        self.logger.error(*a)

    def exception(self, *a):
        self.logger.exception(*a)

    def logs(self, level='info'):
        for h in self.logger.handlers:
            if isinstance(h, FileHandler):
                if h.get_name()==level:
                    return h.baseFilename

