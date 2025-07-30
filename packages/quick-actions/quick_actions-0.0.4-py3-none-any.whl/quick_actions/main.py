#!/usr/bin/env python 

import subprocess

from quick_actions.config_processing.ConfigProvider import ConfigProvider

from quick_actions.config_processing.config_classes.Action import Action
from quick_actions.WhatToDoMenu import WhatToDoMenu
from quick_actions.config_processing.ConfigProvider import ConfigProvider
from quick_actions.ActionDispatcher import ActionDispatcher


def main():
    config_provider = ConfigProvider()
    what_todo_menu = WhatToDoMenu()

    ActionDispatcher(what_todo_menu.wofi_output, what_todo_menu.actions_by_decorated_label)


if __name__=="__main__":
    main()