from quick_actions.config_processing.config_classes.Action import Action 
from queue import Queue
from pathlib import Path
from typing import Dict


class ActionProcessor:

    @classmethod
    def get_prefixes(cls, actions):
        prefixes = {}
        # TODO: pirorized prefixes
        for action in actions.values():
            if action.prefix is not None:
                prefixes[action.prefix] = action
        return prefixes

    @classmethod
    def flat_actions(cls, actions):
        queue = Queue()
        queue.put(("", actions))
        flattened = {}
        envs = {}
        while not queue.empty():
            prefix, subactions = queue.get()
            if subactions.get("env"):
                envs[prefix] = subactions["env"]
                del subactions["env"]

            for name, action in subactions.items():
                if prefix: 
                    new_prefix = f"{prefix}.{name}"
                else:
                    new_prefix = name
                # print(new_prefix)
                if Action.is_action(action):
                    flattened[new_prefix] = Action(id=new_prefix, **action)
                elif isinstance(action, dict):
                    queue.put(
                        (new_prefix, action)
                    )
                else:
                    # TODO: custom exceptions
                    raise Exception("Invalid Config")
        return flattened, envs

    @staticmethod
    def expand_file_paths(base: Path, config_part: Dict):
        queue = Queue()
        queue.put(config_part)

        while not queue.empty():
            current = queue.get()

            if current.get("label") is not None:
                if (sc := current.get("script")) is not None:
                    sc_path = Path(sc)
                    if not sc_path.is_absolute():
                        current["script"] = (base / sc_path).resolve()
            else:
                for value in current.values():
                    if isinstance(value, dict):
                        queue.put(value)