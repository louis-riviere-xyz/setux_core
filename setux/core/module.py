from inspect import cleandoc

from pybrary.func import todo

from . import error


def inst(installer, installables):
    if installables:
        installables = installables.strip()
        if ' ' in installables:
            installables = installables.split()
        else:
            installables = [installables]
        for installable in installables:
            installer(installable)


class Module:
    def __init__(self, distro):
        self.distro = distro

    def deploy(self, target, **kw):
        for mod in (
            c
            for c in reversed(self.__class__.mro())
            if issubclass(c, Module)
        ):
            try:
                ret = mod.do_deploy(self, target, **kw)
            except Exception as x:
                error(x)
                return False
            if not ret: return False
        return True

    def do_deploy(self, target, **kw):
        '''to be overridden
        '''
        return True

    def install(self, target, *, dep=None, pre=None, pkg=None, pip=None):
        inst(target.Package.install, pre)
        inst(target.deploy, dep)
        inst(target.Package.install, pkg)
        inst(target.Pip.install, pip)
        return True

    @classmethod
    def help(cls):
        for mod in (
            c
            for c in cls.mro()
            if issubclass(c, Module)
        ):
            try:
                return cleandoc(mod.__doc__)
            except: pass
        return '?'
