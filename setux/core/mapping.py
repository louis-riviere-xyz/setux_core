from . import error, debug


class Mapping: pass


class Packages(Mapping):
    pkg = dict()


class Services(Mapping):
    mapping = dict()
