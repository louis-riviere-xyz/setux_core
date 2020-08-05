from .distro import Distro
from .plugin import Plugins


class Managers(Plugins):
    pass


class Distros(Plugins):
    def sort(self):
        def sort_key(item):
            name, cls = item
            return len(Distro.distro_lineage(cls))

        self.items = dict(
            item
            for item in reversed(sorted(
                self.items.items(),
                key = sort_key
            ))
        )


class Modules(Plugins):
    def parse(self, mod, plg, plugin):
        lineage = self.target.distro.lineage
        if plg in lineage:
            old = self.items.get(mod)
            if old:
                idx = lineage.index(plg)
                old_idx = lineage.index(old.__name__)
                if idx > old_idx:
                    return mod, plugin
            else:
                return mod, plugin
        return None, None
