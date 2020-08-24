from shlex import split
from subprocess import (
    PIPE,
    CalledProcessError,
    run,
)

from pybrary.func import todo

from .errors import (
    MissingModuleError,
    ModuleTypeError,
    UnsupportedDistroError,
)
from . import debug, info, error
from .distro import Distro
from .manage import Manager
from .module import Module
from . import plugins
import setux.distros
import setux.managers.common
import setux.modules


# pylint: disable= filter-builtin-not-iterating


class Target:
    def __init__(self, *,
        name = None,
        distro = None,
        sudo = None,
        outdir = None,
        exclude = None,
    ):
        self.name = name or 'target'
        self.outdir = outdir
        self.sudo = sudo
        self.chk_cnx()
        self.distros = plugins.Distros(self,
            Distro, setux.distros
        )
        self.managers = plugins.Managers(self,
            Manager, setux.managers.common
        )
        self.probe_distro()
        self.modules = plugins.Modules(self,
            Module, setux.modules
        )
        self.sudo = self.distro.Login.id != 0
        self.exclude = exclude

    @property
    def outdir(self):
        return getattr(self, '_outdir_', None)

    @outdir.setter
    def outdir(self, path):
        self._outdir_ = path
        if path:
            run(f'mkdir -p {path}', shell=True)
            self.set_trace()

    def chk_cnx(self):
        ''' to be overwriten
        '''

    def probe_distro(self):
        Distros = self.distros.items.values()
        infos = Distro.release_default(self)
        for Dist in Distros:
            if Dist.release_check(self, infos):
                self.distro = Dist(self)
                debug(f'{self.distro.Host.name} : {self.distro.name}')
                break
        else:
            raise UnsupportedDistroError(self)

    def set_trace(self):
        self.outrun = f'{self.outdir}/{self.name}.run'
        self.outlog = f'{self.outdir}/{self.name}.log'
        try:
            with open(self.outrun, 'w') as log:
                debug(f'outrun : {log.name}')
            with open(self.outlog, 'w') as log:
                debug(f'outlog : {log.name}')
        except Exception as x:
            error(x)
            self.outdir = None

    def trace(self, cmd, ret, out, err, **kw):
        if self.outdir:
            with open(self.outrun, 'a') as log:
                log.write(f'{cmd}\n')

            with open(self.outlog, 'a') as log:
                log.write(f'\n[{ret:^3}] {cmd}\n')
                if out:
                    if kw.get('report')=='quiet':
                        log.write(f'[out] ... ({len(out)})\n')
                    else:
                        if len(out)==1:
                            out = out[0]
                        else:
                            out = '\n'+'\n'.join(out)
                        log.write(f'[out] {out}\n')
                if err:
                    if len(err)==1:
                        err = err[0]
                    else:
                        err = '\n'+'\n'.join(err)
                    log.write(f'[err] {err}\n')

    def __getattr__(self, attr):
        return getattr(self.distro, attr)

    def parse(self, *arg, **kw):
        shell = kw.get('shell')
        if shell is None and len(arg)==1:
            shell = any(x in arg[0] for x in '*|>?<')
            kw['shell'] = shell

        args = []

        if kw.pop('sudo', True) and self.sudo:
            args.append('sudo')

        if not shell and len(arg)==1:
            arg = filter(None,
                (i.strip() for i in split(arg[0]))
            )
        args.extend(arg)
        return args, kw

    def run(self, *arg, report='normal', critical=True, raw=False, skip=None, **kw):
        def log(*msg):
            if report=='verbose':
                debug(*msg)

        cmd = arg
        command = ' '.join(cmd)
        if kw.get('shell'):
            cmd = command

        try:
            log('running "%s" ...', command)
            try:
                proc = run(cmd, stdout=PIPE, stderr=PIPE, **kw)
            except OSError:
                kw['shell'] = True
                proc = run(cmd, stdout=PIPE, stderr=PIPE, **kw)

            out = proc.stdout.decode("utf-8").strip()
            if out:
                if report!='quiet':
                    debug("%s [out]:\n%s", command, out)
                if not raw:
                    out = [i.strip() for i in out.split('\n')]
                    if skip:
                        out = [i for i in out if not skip(i)]

            err = proc.stderr.decode("utf-8").strip()
            if err:
                log("%s [err]:\n%s", command, err)
                if not raw:
                    err = [i.strip() for i in err.split('\n')]
                    if skip:
                        err = [i for i in err if not skip(i)]

            ret = proc.returncode
            log('"%s" [ret]: %s', command, ret)

            return ret, out, err

        except CalledProcessError as exc:
            if critical:
                error(
                    "\n%s > %s\n%s\n%s",
                    " ".join(exc.cmd),
                    exc.returncode,
                    exc.stdout.decode("utf-8"),
                    exc.stderr.decode("utf-8"),
                )
            return -1, "ERROR", str(exc)

        except Exception as exc:
            error("%s raised: %s", cmd, exc)
            raise

    def deploy(self, module, **kw):
        if isinstance(module, str):
            try:
                cls = self.modules.items[module]
            except KeyError:
                raise MissingModuleError(module, self.distro)
        else:
            cls = module

        try:
            if not issubclass(cls, Module):
                raise ModuleTypeError(cls)
        except TypeError:
            raise ModuleTypeError(cls)

        ret = cls(self.distro).deploy(self, **kw)

        params = ', '.join(f'{k}={v}' for k, v in kw.items()) if kw else ''
        status = '.' if ret else 'X'
        info(f'\tdeploy {module} {params} {status}')
        return ret

    def rsync_opt(self):
        ''' additional rsync opts
        '''

    def rsync(self, *arg, **kw):
        self.Package.install('rsync')
        kw['sudo'] = False
        arg, kw = self.parse(*arg, **kw)
        cmd = 'rsync -qcr -zz --delete'.split()
        if self.exclude:
            cmd.extend(['--exclude-from', self.exclude, '--delete-excluded'])
        opt = self.rsync_opt()
        if opt:
            cmd.append(opt)
        cmd.extend(arg)
        kw['report'] = 'verbose'
        ret, out, err =  Target.run(self, *cmd, **kw)
        self.trace('rsync '+' '.join(arg), ret, out, err, **kw)
        return ret, out, err

    def script(self, content, path=None, name=None, remove=True, report='quiet'):
        path = path or '/tmp/setux'
        self.run(f'mkdir -p {path}')
        self.run(f'chmod 777 {path}')
        name = name or 'script'
        full = '/'.join((path, name))
        self.write(full, content, report='quiet')
        self.run(f'chmod +x {full}')
        ret, out, err = self.run(full)
        if remove: self.run(f'rm {full}', report='quiet')
        return ret, out, err

    def read(self, path, mode='rt', report='normal'): todo(self)
    def write(self, path, content, mode='wt', report='normal'): todo(self)
    def send(self, local, remote): todo(self)
    def fetch(self, remote, local): todo(self)
    def sync(self, src, dst=None): todo(self)
    def export(self, path): todo(self)
    def remote(self, module, export_path=None, **kw): todo(self)

