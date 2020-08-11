from pybrary.func import todo

from . import info
from .manage import Manager


class Packager(Manager):
    system = True

    def __init__(self, distro):
        super().__init__(distro)
        self.host = distro.Host.name
        self.pkgmap = distro.pkgmaps
        self.done = set()
        self.ready = False

    def _get_ready_(self):
        if self.ready: return
        self.do_init()
        self.ready = True

    def installed(self, pattern=None):
        if pattern:
            for name, ver in self.do_installed():
                if pattern in name:
                    yield name, ver
        else:
            yield from self.do_installed()

    def available(self, pattern=None):
        if pattern:
            for name, ver in self.do_available():
                if pattern in name:
                    yield name, ver
        else:
            yield from self.do_available()

    def bigs(self):
        info('\tbigs')
        for line in self.do_bigs():
            size, pkg = line.split()
            yield f'{size:>9} {pkg}'

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
        info('\t--> %s %s', name, ver or '')
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
    def do_available(self): todo(self)

