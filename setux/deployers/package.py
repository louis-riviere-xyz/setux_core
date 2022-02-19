from setux.core.deploy import Deployer


class Installer(Deployer):
    @property
    def label(self):
        return f'install {self.name}'

    def check(self):
        return self.name in [n.lower() for n,v in self.packager.installed(self.name)]

    def deploy(self):
        return self.packager.install_pkg(self.name, self.ver)


class Remover(Deployer):
    @property
    def label(self):
        return f'remove {self.name}'

    def check(self):
        return self.name not in [n.lower() for n,v in self.packager.installed(self.name)]

    def deploy(self):
        return self.packager.remove_pkg(self.name)
