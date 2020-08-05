from importlib import import_module
from os import walk
from os.path import join, commonpath
from sys import path as syspath

from setux.main.logger import debug


def filter_py(name):
    if name.startswith('_'): return False
    if not name.endswith('.py'): return False
    return True


def walk_py(path):
    for path, _dirs, files in walk(path):
        for name in files:
            if filter_py(name):
                yield join(path, name)


def get_modules(path):
    try:
        package = import_module(path)
    except ModuleNotFoundError as x:
        raise Exception(f'not found : {path}')
    try:
        packpath = package.__path__[0]
    except AttributeError as x:
        raise Exception('not a package')

    paths = [p for p in syspath if packpath.startswith(p)]
    com = max(len(commonpath([p, packpath])) for p in paths) + 1

    for path in walk_py(packpath):
        mod = path[com:-3].replace('/', '.')
        yield mod, import_module(mod)


def get_raw_plugins(path, cls):
    for mod, module in get_modules(path):
        for plg, plugin in module.__dict__.items():
            try:
                if issubclass(plugin, cls):
                    yield mod, plg, plugin
            except TypeError: pass


def get_plugins(path, cls):
    get_core = get_raw_plugins('setux.core', cls)
    core = set(cls for _m, _p, cls in get_core)
    return [
        (mod, plg, plugin)
        for mod, plg, plugin in get_raw_plugins(path, cls)
        if plugin not in core
    ]


class Plugins:
    def __init__(self, target, Base, paths=''):
        self.target = target
        self.Base = Base
        self.paths = [p.strip() for p in paths.split(':')]
        self.items = dict()
        self.collect()

    def parse(self, mod, plg, plugin):
        return plg, plugin

    def sort(self):
        ''' sort self.items in place
        '''

    def collect(self):
        for path in self.paths:
            try:
                plugins = get_plugins(path, self.Base)
            except Exception:
                self.paths.remove(path)
                raise
            for mod, plg, plugin in plugins:
                key, val = self.parse(mod, plg, plugin)
                if key and val:
                    debug(f'{val.__module__}.{val.__name__} collected')
                    self.items[key] = val
        self.sort()

    def add(self, path):
        if isinstance(path, list):
            self.paths.extend(path)
        else:
            self.paths.append(path)
        self.collect()
