from pathlib import Path

from pybrary.func import todo

from setux.logger import error, info
from setux.actions.package import Installer, Remover

from .errors import PackagerError
from .manage import Manager


class _Packager(Manager):
    def __init__(self, distro):
        super().__init__(distro)
        self.done = set()
        self.ready = False
        self._installed = None

    def _get_ready_(self):
        if self.ready: return
        try:
            self.do_init()
        except Exception as x:
            raise PackagerError(self, 'Init', x)
        self.mapkg = {v:k for k,v in self.pkgmap.items()}
        self.ready = True

    def filter(self, do_fetch, pattern=None):
        self._get_ready_()
        chk_name = self.mapkg.get
        try:
            for name, ver in do_fetch(pattern):
                name = chk_name(name, name)
                if pattern:
                    if pattern in name.lower():
                        yield name, ver
                else:
                    yield name, ver
        except Exception as x:
            raise PackagerError(self, f'Packager Filter({do_fetch.__name__}, {pattern})', x)


    def installed(self, pattern=None):
        if not self._installed:
            try:
                self._installed = list(self.do_installed())
            except Exception as x:
                raise PackagerError(self, 'Installed', x)

        def do_installed(_pattern):
            yield from self._installed

        yield from self.filter(do_installed, pattern)

    def installable(self, pattern=None):
        yield from self.filter(self.do_installable, pattern)

    def bigs(self):
        self._get_ready_()
        info('\tbigs')
        try:
            for line in self.do_bigs():
                size, pkg = line.split()
                size = int(size)
                while size>1000:
                    size = size//1000
                yield size, pkg
        except Exception as x:
            raise PackagerError(self, 'Bigs', x)

    def upgradable(self):
        self._get_ready_()
        info('\tupgradable')
        try:
            yield from self.do_upgradable()
        except Exception as x:
            raise PackagerError(self, 'Upgradable', x)

    def update(self):
        self._get_ready_()
        info('\tupdate')
        try:
            self.do_update()
        except Exception as x:
            raise PackagerError(self, 'Update', x)
        for name, _ver in self.upgradable():
            info(f'\t\t{name}')

    def upgrade(self):
        self._get_ready_()
        info('\tupgrade')
        try:
            self.do_upgrade()
        except Exception as x:
            raise PackagerError(self, 'Upgrade', x)
        self._installed = None

    def install_pkg(self, name, ver=None):
        if name in self.done: return
        self._get_ready_()
        info('\t--> %s', name)
        self.done.add(name)
        pkg = self.pkgmap.get(name, name)
        self._installed = None
        try:
            ok = self.do_install(pkg, ver)
        except Exception as x:
            raise PackagerError(self, f'Install({name}, {ver})', x)
        return ok

    def install(self, name, ver=None, verbose=True):
        try:
            Installer(self.target, packager=self, name=name, ver=ver)(verbose)
        except Exception as x:
            raise PackagerError(self, f'Installer({name}, {ver})', x)
        return True

    def remove_pkg(self, name):
        self._get_ready_()
        info('\t<-- %s', name)
        self.done.discard(name)
        pkg = self.pkgmap.get(name, name)
        self._installed = None
        try:
            ok = self.do_remove(pkg)
        except Exception as x:
            raise PackagerError(self, f'Remove({name}', x)
        return ok

    def remove(self, name, verbose=True):
        try:
            Remover(self.target, packager=self, name=name)(verbose)
        except Exception as x:
            raise PackagerError(self, f'Remover({name}', x)
        return True

    def cleanup(self):
        self._get_ready_()
        info('\tcleanup')
        try:
            self.do_cleanup()
        except Exception as x:
            raise PackagerError(self, 'Cleanup', x)
        self._installed = None

    def do_init(self): todo(self)
    def do_update(self): todo(self)
    def do_upgradable(self): todo(self)
    def do_upgrade(self): todo(self)
    def do_install(self, pkg, ver=None): todo(self)
    def do_bigs(self): todo(self)
    def do_remove(self, pkg): todo(self)
    def do_cleanup(self): todo(self)
    def do_installed(self): todo(self)
    def do_installable(self, pattern=None): todo(self)


class SystemPackager(_Packager):
    def __init__(self, distro):
        super().__init__(distro)
        self.pkgmap = distro.pkgmap


class CommonPackager(_Packager):
    def __init__(self, distro):
        super().__init__(distro)
        self.cache_dir = Path('/tmp/setux/cache')
        self.cache_file = self.cache_dir / str(self.manager)
        self.cache_days = 10

    def do_installable(self, pattern=None):
        from setux.targets import Local
        local = Local(outdir=self.cache_dir)
        cache = local.file(self.cache_file)
        if cache.age is None or cache.size==0 or cache.age > self.cache_days:
            try:
                self.do_installable_cache()
            except Exception as x:
                raise PackagerError(self, 'Cache', x)

        for line in open(self.cache_file):
            yield line.strip().split(maxsplit=1)

    def do_installable_cache(self): todo(self)

