import tomllib
from pathlib import Path
from typing import List, Dict
from benedict import benedict

from pprint import pprint

from quick_actions.config_processing.OptionProcessor import OptionProcessor

class ConfigProvider:
    def __init__(self):
        self.CONFIG_DIR = Path("./config").resolve()

        self.settings = self.collect()
        self.settings["options"], self.envs = OptionProcessor.flat_options(self.settings["options"])

    @property
    def options(self):
        return self.settings["options"]

    @property
    def option_prefixes(self):
        return OptionProcessor.get_prefixes(self.settings["options"])

    @property
    def options_by_label(self):
        return { x.label: x for key, x in self.options.items()}


    def folder_generator(self):
        return self.CONFIG_DIR.rglob('*.toml')


    def collect_toml(self):
        settings = benedict(keypath_separator=None)
        for path in self.folder_generator():
            relative_dirs = path.parent.relative_to(self.CONFIG_DIR).parts

            with open(path, "rb") as f:
                new_values = tomllib.load(f)

                OptionProcessor.expand_file_paths(path.parent, new_values)


                for part in reversed(relative_dirs):
                    new_values = { part: new_values }

                # print("--->",new_values, end="\n\n\n")
                settings.merge(new_values)
                # print(settings)

            
        return settings


    def collect(self):
        return self.collect_toml()



    

if __name__ == "__main__":
    cp = ConfigProvider()
    # print(cp.envs)

    # print(cp.options["hyprland.group.togglelock"])
    # .collect_toml()

    # print(opts)
    # opts["options"]= OptionProcessor.flat_options(opts["options"])
    # pprint (
    #     dict(opts["options"])
    # )