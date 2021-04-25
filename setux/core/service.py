from time import sleep

from pybrary.func import todo

from . import info
from .manage import Manager


# pylint: disable=assignment-from-no-return


class Service(Manager):
    def __init__(self, distro):
        super().__init__(distro)
        self.svcmap = distro.svcmap

    def status(self, name):
        svc = self.svcmap.get(name, name)
        up = self.do_status(svc)
        info(f'\tservice {name} {"." if up else "X"}')
        return up

    def wait(self, name, up=True):
        sleep(1)
        for _ in range(3):
            if self.status(name) is up: break
            sleep(3)

    def enable(self, name):
        svc = self.svcmap.get(name, name)
        if not self.do_enabled(svc):
            info(f'\tenable {name}')
            self.do_enable(svc)
            enabled = self.do_enabled(svc)
            info(f'\t{name} enabled {"." if enabled else "X"}')

    def disable(self, name):
        svc = self.svcmap.get(name, name)
        if self.do_enabled(svc):
            info(f'\tdisable {name}')
            self.do_disable(svc)
            enabled = self.do_enabled(svc)
            info(f'\t{name} disabled {"." if not enabled else "X"}')

    def start(self, name):
        svc = self.svcmap.get(name, name)
        if not self.status(name):
            info(f'\tstart {name}')
            self.do_start(svc)
            self.wait(name)

    def stop(self, name):
        svc = self.svcmap.get(name, name)
        if self.status(name):
            info(f'\tstop {name}')
            self.do_stop(svc)
            self.wait(name, up=False)

    def restart(self, name):
        svc = self.svcmap.get(name, name)
        if self.status(name):
            info(f'\trestart {name}')
            self.do_restart(svc)
            self.wait(name)
        else:
            self.start(name)

    def do_enabled(self, svc): todo(self)
    def do_status(self, svc): todo(self)
    def do_enable(self, svc): todo(self)
    def do_disable(self, svc): todo(self)
    def do_start(self, svc): todo(self)
    def do_stop(self, svc): todo(self)
    def do_restart(self, svc): todo(self)
