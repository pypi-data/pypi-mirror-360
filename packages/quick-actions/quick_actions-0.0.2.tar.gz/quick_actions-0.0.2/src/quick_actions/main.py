#!/usr/bin/env python 

import subprocess

from quick_actions.config_processing.ConfigProvider import ConfigProvider
from quick_actions.runners.CommandRunner import CommandRunner
from quick_actions.runners.ScriptRunner import ScriptRunner
from quick_actions import constants
from quick_actions.config_processing.config_classes.Option import Option
from time import sleep

config_provider = ConfigProvider()
options = config_provider.options

def style_tags(tags):
    tags_decorated = [f'<span color="gray" style="oblique"><sub>{tag}</sub></span>' for tag in tags]
    return " ".join(tags_decorated)

options_by_label = {f'{x.label} <span color="gray">{x.id}</span> {style_tags(x.tags)}':x for x in options.values()}


options_str = "\n".join(options_by_label.keys())

wofi_command = f"echo '{options_str}' | wofi --prompt='Quick Menu' --dmenu --width=70% --height=60%"

wofi_runner = CommandRunner(wofi_command, print_err=False)

if wofi_runner.returncode != 0:
    print("User cancelled the operation.")
    exit(0)

wofi_output = wofi_runner.output.strip()

chosen_option: Option = options_by_label.get(wofi_output)

for prefix, option in config_provider.option_prefixes.items():
    if wofi_output.startswith(prefix):
        arguments = wofi_output.removeprefix(prefix)
        chosen_option = option.with_arguments(arguments)





if chosen_option is not None:
    envs = {}
    for id_prefix, env_dict in config_provider.envs.items():
        if chosen_option.id.startswith(id_prefix):
            envs.update(env_dict)
    
    if chosen_option.sleep_before is not None:
        sleep(chosen_option.sleep_before)

    if chosen_option.exec is not None:
        CommandRunner(chosen_option.exec, envs)
    if chosen_option.script is not None:
        ScriptRunner(chosen_option.script, envs)
else:
    print("Unkown action: ", wofi_output)