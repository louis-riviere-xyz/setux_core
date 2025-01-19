from inspect import cleandoc

from pybrary.func import todo

from setux.logger import logger, error, green, yellow, red

# pylint: disable=no-member,not-an-iterable


class Action:
    def __init__(self, target, **context):
        self.target = target
        self.context = context

    def __getattr__(self, attr):
        try:
            return self.context[attr]
        except KeyError:
            try:
                return self.target.context[attr]
            except KeyError:
                # debug(f'{attr} not in context ({self.label})')
                if attr=='local': return self.target.set_local()
                # raise AttributeError

    @property
    def labeler(self):
        return yellow

    @property
    def label(self):
        todo(self)

    def __enter__(self):
        self.backup = dict(self.target.context)
        self.target.context.update(self.context)

    def _call_(self, verbose):
        with logger.quiet():
            try:
                ok = self.check()
            except Exception as x:
                error(x)
                red(f'!! {self.label}')
                return False
            if ok:
                if verbose: green(f'== {self.label}')
                return True

            with self.labeler(f'<> {self.label}'):
                try:
                    ok = self.deploy()
                except Exception as x:
                    error(x)
                    red(f'!! {self.label}')
                    return False

            if ok:
                try:
                    ok = self.check()
                except Exception as x:
                    error(x)
                    red(f'!! {self.label}')
                    return False
                if ok:
                    if verbose: green(f'>> {self.label}')
                    return True

            red(f'XX {self.label}')
            return False

    def __call__(self, verbose=True):
        with self:
            return self._call_(verbose)

    def __exit__(self, typ, val, tb):
        self.target.context = self.backup

    @classmethod
    def help(cls):
        try:
            return cleandoc(cls.__doc__)
        except:
            return '?'


class Runner(Action):
    def _call_(self, verbose):
        with logger.quiet():
            with self.labeler(f'<> {self.label}'):
                try:
                    ok = self.deploy()
                except Exception as x:
                    error(x)
                    ok = False
            if ok:
                if verbose: green(f'.. {self.label}')
                return True
            else:
                if verbose: red(f'!! {self.label}')
                return False


class Actions(Action):
    @property
    def ignore(self):
        return getattr(self, '_continue_', False)

    @ignore.setter
    def ignore(self, val):
        setattr(self, '_continue_', val)

    @property
    def actions(self):
        todo(self)

    def get_action(self, act):
        if isinstance(act, Action):
            action = act
        else:
            action = act(self.target, **self.context)
        return action

    def check_action(self, action):
        if hasattr(action, 'check'):
            try:
                ok = action.check()
            except Exception as x:
                error(x)
                ok =  False
        else:
            try:
                ok = action(verbose=False)
            except Exception as x:
                error(x)
                ok =  False
        return ok

    def deploy_action(self, action):
        err = None
        with yellow(f'<> {action.label}'):
            try:
                ok = action.deploy()
            except Exception as x:
                err = str(x)
                error(err)
                ok =  False
        if err:
            red(f'!! {action.label}')
        return ok

    def check(self):
        all_ok = True
        for dpl in self.actions:
            checker = self.get_action(dpl)
            ok = self.check_action(checker)
            if not ok:
                if self.ignore:
                    all_ok = False
                else:
                    raise RuntimeError
        return all_ok

    def deploy(self):
        all_ok = True
        for dpl in self.actions:
            action = self.get_action(dpl)
            ok = self.deploy_action(action)
            if not ok:
                if self.ignore:
                    all_ok = False
                else:
                    raise RuntimeError
        return all_ok

    def _call_(self, verbose):
        with logger.quiet():
            with yellow(f'<> {self.label}'):
                all_ok = True
                for dpl in self.actions:
                    action = self.get_action(dpl)
                    if isinstance(action, (Actions, Runner)):
                        ok = action()
                    else:
                        ok = self.check_action(action)
                        if ok:
                            green(f'== {action.label}')
                        else:
                            ok = self.deploy_action(action)
                            if ok:
                                ok = self.check_action(action)
                                if ok:
                                    green(f'>> {action.label}')
                                else:
                                    red(f'XX {action.label}')
                    all_ok = all_ok and ok
            if all_ok:
                green(f'.. {self.label}')
                return True
            else:
                red(f'!! {self.label}')
                return False
