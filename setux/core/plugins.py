from importlib import import_module
from pkgutil import iter_modules

from . import debug
import setux.core
from .distro import Distro


def get_modules(ns):
    path, name = ns.__path__, ns.__name__ + '.'
    debug(f'{path} {name}')
    for finder, name, _ispkg in iter_modules(path, name):
        yield name, import_module(name)


def get_raw_plugins(ns, cls):
    for mod, module in get_modules(ns):
        for plg, plugin in module.__dict__.items():
            try:
                if issubclass(plugin, cls):
                    yield mod, plg, plugin
            except TypeError: pass


def get_plugins(ns, cls):
    get_core = get_raw_plugins(setux.core, cls)
    core = set(cls for _m, _p, cls in get_core)
    return [
        (mod, plg, plugin)
        for mod, plg, plugin in get_raw_plugins(ns, cls)
        if plugin not in core
    ]


class Plugins:
    def __init__(self, target, Base, ns):
        self.target = target
        self.Base = Base
        self.ns = ns
        self.items = dict()
        self.collect()

    def parse(self, mod, plg, plugin):
        return plg, plugin

    def sort(self):
        ''' sort self.items in place
        '''

    def collect(self):
        plugins = get_plugins(self.ns, self.Base)
        for mod, plg, plugin in plugins:
            key, val = self.parse(mod, plg, plugin)
            if key and val:
                debug(f'{val.__module__}.{val.__name__} collected')
                self.items[key] = val
        self.sort()


class Managers(Plugins):
    pass


class Distros(Plugins):
    def sort(self):
        def sort_key(item):
            name, cls = item
            return len(Distro.distro_lineage(cls))

        self.items = dict(
            item
            for item in reversed(sorted(
                self.items.items(),
                key = sort_key
            ))
        )


class Modules(Plugins):
    def parse(self, mod, plg, plugin):
        lineage = self.target.distro.lineage
        if plg in lineage:
            name = '.'.join(mod.split('.')[2:])
            old = self.items.get(mod)
            if old:
                idx = lineage.index(plg)
                old_idx = lineage.index(old.__name__)
                if idx > old_idx:
                    return name, plugin
            else:
                return name, plugin
        return None, None
