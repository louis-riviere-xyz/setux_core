from pybrary.func import memo

from . import debug


# pylint: disable=bad-staticmethod-argument


class Distro:
    Package = None
    pkgmap = dict()
    Service = None
    svcmap = dict()

    def __init__(self, target):
        self.name = self.__class__.__name__
        self.target = target
        self.set_managers()
        self.Package = self.Package(self)
        self.Service = self.Service(self)

    def __str__(self):
        return f'Distro : {self.name}'

    def set_managers(self):
        todo = list(self.target.managers.items.values())
        while todo:
            for manager in list(todo):
                todo.remove(manager)
                try:
                    setattr(self, manager.__name__, manager(self))
                    debug('%s %s %s', self.name, manager.__name__, '.')
                except AttributeError:
                    debug('%s %s %s', self.name, manager.__name__, 'X')
                    todo.append(manager)

    @classmethod
    def release_default(cls, target):
        ret, out, err = target.run('cat /etc/*-release', report='quiet', shell=True)
        infos = dict(l.split('=') for l in out if '=' in l)
        debug('%s %s', target, infos)
        return infos

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
