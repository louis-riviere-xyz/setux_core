from setux.logger import logger, green, yellow, red


class Deployer:
    def __init__(self, **conf):
        for k, v in conf.items():
            setattr(self, k, v)

    def __call__(self):
        with logger.quiet():
            try:
                status = self.check()
            except Exception as x:
                red(f'!! {self.label}')
                return False
            if status:
                green(f'== {self.label}')
                return True

            with yellow(f'<> {self.label}'):
                try:
                    status = self.deploy()
                except Exception as x:
                    red(f'!! {self.label}')
                    return False

            if status:
                try:
                    status = self.check()
                except Exception as x:
                    red(f'!! {self.label}')
                    return False
                if status:
                    green(f'>> {self.label}')
                    return True

            red(f'XX {self.label}')
            return False

