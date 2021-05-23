from pybrary.func import todo

from . import info
from .manage import Manager


class _Packager(Manager):
    def __init__(self, distro):
        super().__init__(distro)
        self.done = set()
        self.ready = False

    def _get_ready_(self):
        if self.ready: return
        self.do_init()
        self.ready = True

    def installed(self, pattern=None):
        self._get_ready_()
        if pattern:
            for name, ver in self.do_installed():
                if pattern in name:
                    yield name, ver
        else:
            yield from self.do_installed()

    def installable(self, pattern=None):
        self._get_ready_()
        if pattern:
            for name, ver in self.do_installable():
                if pattern in name.lower():
                    yield name, ver
        else:
            yield from self.do_installable()

    def bigs(self):
        self._get_ready_()
        info('\tbigs')
        for line in self.do_bigs():
            size, pkg = line.split()
            size = int(size)
            while size>1000:
                size = size//1000
            yield f'{size:>7} {pkg}'

    def upgradable(self):
        info('\tupgradable')
        yield from self.do_upgradable()

    def update(self):
        info('\tupdate')
        self.do_update()
        for name, ver in self.upgradable():
            info(f'\t\t{name}')

    def upgrade(self):
        info('\tupgrade')
        self.do_upgrade()

    def install(self, name, ver=None):
        if name in self.done: return
        self._get_ready_()
        self.done.add(name)
        pkg = self.pkgmap.get(name, name)
        self.do_install(pkg, ver)

    def remove(self, name):
        info('\t<-- %s', name)
        pkg = self.pkgmap.get(name, name)
        self.do_remove(pkg)

    def cleanup(self):
        info('\tcleanup')
        self.do_cleanup()

    def do_init(self): todo(self)
    def do_update(self): todo(self)
    def do_upgradable(self): todo(self)
    def do_upgrade(self): todo(self)
    def do_install(self, pkg, ver=None): todo(self)
    def do_bigs(self): todo(self)
    def do_remove(self, pkg): todo(self)
    def do_cleanup(self): todo(self)
    def do_installed(self): todo(self)
    def do_installable(self): todo(self)


class SystemPackager(_Packager):
    def __init__(self, distro):
        super().__init__(distro)
        self.pkgmap = distro.pkgmaps


class CommonPackager(_Packager):
    pkgmap = dict()

