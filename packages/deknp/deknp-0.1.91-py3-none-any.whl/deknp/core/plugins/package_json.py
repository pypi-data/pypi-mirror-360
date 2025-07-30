from dektools.dict import assign
from .base import Plugin


class PluginPackageJson(Plugin):
    def run(self):
        for data in self.dek_info_list_final:
            package_json = data.get(self.package_standard_name) or {}
            if package_json:
                d = self.load_package_standard()
                d = assign(d, package_json)
                d.pop(self.dek_key_root, None)
                self.save_json(self.package_standard_filepath, d)
