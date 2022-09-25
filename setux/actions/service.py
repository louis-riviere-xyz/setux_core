from setux.core.action import Runner, Action


class Enabler(Action):
    '''Enable a Service '''

    @property
    def label(self):
        return f'enable {self.name}'

    def check(self):
        return self.servicer.do_enabled(self.name)

    def deploy(self):
        return self.servicer.do_enable(self.name)


class Disabler(Action):
    '''Disable a Service '''

    @property
    def label(self):
        return f'disable {self.name}'

    def check(self):
        return not self.servicer.do_enabled(self.name)

    def deploy(self):
        return self.servicer.do_disable(self.name)


class Starter(Action):
    '''Start a Service '''

    @property
    def label(self):
        return f'start {self.name}'

    def check(self):
        return self.servicer.status(self.name)

    def deploy(self):
        ok = self.servicer.do_start(self.name)
        if ok: self.servicer.wait(self.name)
        return ok


class Stoper(Action):
    '''Stop a Service '''

    @property
    def label(self):
        return f'stop {self.name}'

    def check(self):
        return not self.servicer.status(self.name)

    def deploy(self):
        ok = self.servicer.do_stop(self.name)
        if ok: self.servicer.wait(self.name, up=False)
        return ok


class Restarter(Runner):
    '''Restart a Service '''

    @property
    def label(self):
        return f'restart {self.name}'

    def deploy(self):
        ok = True
        if self.servicer.status(self.name):
            ok = self.servicer.do_stop(self.name)
            if ok: self.servicer.wait(self.name, up=False)
        if ok:
            ok = self.servicer.do_start(self.name)
            if ok: self.servicer.wait(self.name)
        return ok

