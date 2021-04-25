from pybrary.func import memo

from . import debug
from .manage import Manager
from .module import Module
from .package import SystemPackager
from .service import Service
from . import plugins
import setux.managers
import setux.modules


# pylint: disable=bad-staticmethod-argument


class Distro:
    Package = None
    pkgmap = dict()
    Service = None
    svcmap = dict()

    def __init__(self, target):
        self.name = self.__class__.__name__
        self.target = target
        self.managers = plugins.Managers(self,
            Manager, setux.managers
        )
        self.modules = plugins.Modules(self,
            Module, setux.modules
        )
        self.set_managers()
        self.reg_modules()

    def __str__(self):
        return f'Distro : {self.name}'

    def reg_modules(self):
        for module in self.modules.items.values():
            attr = getattr(module, 'register', None)
            if attr:
                self.target.register(module, attr)

    def set_managers(self):
        todo = list(self.managers.items.values())
        while todo:
            for manager in list(todo):
                todo.remove(manager)
                if issubclass(manager,SystemPackager):
                    if manager.manager==self.Package:
                        self.Package = manager(self)
                        debug('%s Package %s', self.name, manager.manager)
                elif issubclass(manager, Service):
                    if manager.manager==self.Service:
                        self.Service = manager(self)
                        debug('%s Service %s', self.name, manager.manager)
                else:
                    setattr(self, manager.manager, manager(self))
                    debug('%s %s', self.name, manager.manager)

    @classmethod
    def release_default(cls, target):
        if target.release_infos is None:
            ret, out, err = target.run('cat /etc/*-release', report='quiet', shell=True)
            target.release_infos = dict(l.split('=') for l in out if '=' in l)
            debug('%s %s', target, target.release_infos)
        return target.release_infos

    @classmethod
    def release_name(cls, infos):
        did = infos['ID'].strip()
        ver = infos['VERSION_ID'].strip()
        return f'{did}_{ver}'

    @classmethod
    def release_check(cls, target, infos=None):
        if hasattr(cls, 'release_infos'):
            try:
                infos = cls.release_infos(target)
            except: pass
        if not infos:
            infos = cls.release_default(target)
        try:
            return cls.release_name(infos) == cls.__name__
        except: return False

    @staticmethod
    def distro_bases(cls):
        return list(reversed([
            base
            for base in cls.__mro__
            if issubclass(cls, Distro)
        ]))[1:]

    @memo
    def bases(self):
        return Distro.distro_bases(self.__class__)

    @staticmethod
    def distro_lineage(cls):
        return [b.__name__ for b in Distro.distro_bases(cls)]

    @memo
    def lineage(self):
        return [b.__name__ for b in self.bases]

    @memo
    def pkgmaps(self):
        pkgs = dict()
        for distro in self.bases:
            pkgs.update(distro.pkgmap)
        return pkgs

    @memo
    def svcmaps(self):
        svcs = dict()
        for distro in self.bases:
            svcs.update(distro.svcmap)
        return svcs
