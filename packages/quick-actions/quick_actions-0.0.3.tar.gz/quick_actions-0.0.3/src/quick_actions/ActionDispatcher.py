from typing import Dict
from time import sleep

from quick_actions.config_processing.config_classes.Action import Action
from quick_actions.config_processing.ConfigProvider import ConfigProvider
from quick_actions.runners.CommandRunner import CommandRunner
from quick_actions.runners.ScriptRunner import ScriptRunner
from quick_actions.MenuLoader import MenuLoader


class ActionDispatcher:
    def __init__(self, what_todo_output: str, actions_by_decorated_label: Dict[str, Action]):
        self.actions_by_decorated_label = actions_by_decorated_label
        self.what_todo_output = what_todo_output

        self.config_provider = ConfigProvider()

        self.find_action()

        self.run()

    
    def find_action(self):
        self.chosen_action: Action | None = self.actions_by_decorated_label.get(self.what_todo_output)
        self.prefix_matching(self.what_todo_output)


    def match_envs(self):
        envs = {}
        for id_prefix, env_dict in self.config_provider.envs.items():
            if self.chosen_action.id.startswith(id_prefix):
                envs.update(env_dict)
        return envs


    def run(self):
        if self.chosen_action is not None:
            envs = self.match_envs()
            
            self.sleep_before_run()

            runner = None

            if self.chosen_action.exec is not None:
                runner = CommandRunner(self.chosen_action.exec, envs)
            if self.chosen_action.script is not None:
                runner = ScriptRunner(self.chosen_action.script, envs)
            
            if runner is not None and self.chosen_action.show_response:
                MenuLoader(runner.output, "Result:")

        else:
            print("Unkown action: ", f"|{self.what_todo_output}|")

    
    def prefix_prompt(self):
        if self.chosen_action.prefix is not None:
            # FIXME: refactor this
            menu = MenuLoader("", f"Provide arguments for action {self.chosen_action.id}")
            arguments = menu.menu_output
            self.chosen_action = self.chosen_action.with_arguments(arguments)

    
    def sleep_before_run(self):
        if self.chosen_action.sleep_before is not None:
            sleep(self.chosen_action.sleep_before)


    def prefix_matching(self, what_todo_output: str):
        found_match = False
        for prefix, action in self.config_provider.action_prefixes.items():
            if self.what_todo_output.startswith(prefix):
                arguments = what_todo_output.removeprefix(prefix)
                self.chosen_action = action.with_arguments(arguments)
                found_match = True
        if not found_match and self.chosen_action is not None:
            self.prefix_prompt()
