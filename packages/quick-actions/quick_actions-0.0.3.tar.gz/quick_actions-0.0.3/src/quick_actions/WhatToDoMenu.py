from typing import Dict

from quick_actions.config_processing.config_classes.Action import Action
from quick_actions.runners.CommandRunner import CommandRunner
from quick_actions.config_processing.ConfigProvider import ConfigProvider


class WhatToDoMenu:
    def __init__(self):
        self.config_provider = ConfigProvider()

        self.actions_by_decorated_label = self.build_labels()

        actions_str = "\n".join(self.actions_by_decorated_label.keys())

        wofi_command = f"echo '{actions_str}' | {self.expand_launcher_command()}"

        wofi_runner = CommandRunner(wofi_command, print_err=False)

        if wofi_runner.returncode != 0:
            print("User cancelled the operation.")
            exit(0)

        self.wofi_output = wofi_runner.output.strip()


    def build_labels(self) -> Dict[str, Action]:
        actions = self.config_provider.actions

        return {f'{x.label} <span color="gray">{x.id}</span> {self.style_prefix(x.prefix)} {self.style_tags(x.tags)} '.strip():x for x in actions.values()}

    
    @staticmethod
    def style_tags(tags):
        tags_decorated = [f'<span color="gray" style="oblique"><sub>{tag}</sub></span>' for tag in tags]
        return " ".join(tags_decorated)

    @staticmethod
    def style_prefix(prefix):
        if prefix is None:
            return ""
        else:
            return f'<sup><b>{prefix}</b><span color="#7a251f">☐☐☐☐</span></sup>'


    def expand_launcher_command(self):
        template = self.config_provider.settings.get("general").get("launcher").get("launcher_command")
        template = template.replace("{prompt}", "Quick Menu")

        return template
