from inspect import cleandoc

from pybrary.func import todo


class Module:
    def __init__(self, distro):
        self.distro = distro

    def deploy(self, target, **kw):
        todo(self)

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
