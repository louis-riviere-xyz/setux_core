from setux.core.action import Action


class Installer(Action):
    '''Install a Package '''

    @property
    def label(self):
        return f'install {self.name}'

    def check(self):
        return self.name in [n.lower() for n,v in self.packager.installed(self.name)]

    def deploy(self):
        return self.packager.install_pkg(self.name, self.ver)


class Remover(Action):
    '''Remove a Package '''

    @property
    def label(self):
        return f'remove {self.name}'

    def check(self):
        return self.name not in [n.lower() for n,v in self.packager.installed(self.name)]

    def deploy(self):
        return self.packager.remove_pkg(self.name)
