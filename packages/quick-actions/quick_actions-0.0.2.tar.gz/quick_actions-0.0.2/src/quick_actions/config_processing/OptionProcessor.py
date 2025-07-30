from quick_actions.config_processing.config_classes.Option import Option 
from queue import Queue
from pathlib import Path
from typing import Dict


class OptionProcessor:

    @classmethod
    def get_prefixes(cls, options):
        prefixes = {}
        # TODO: pirorized prefixes
        for option in options.values():
            if option.prefix is not None:
                prefixes[option.prefix] = option
        return prefixes

    @classmethod
    def flat_options(cls, options):
        queue = Queue()
        queue.put(("", options))
        flattened = {}
        envs = {}
        while not queue.empty():
            prefix, suboptions = queue.get()
            if suboptions.get("env"):
                envs[prefix] = suboptions["env"]
                del suboptions["env"]

            for name, option in suboptions.items():
                if prefix: 
                    new_prefix = f"{prefix}.{name}"
                else:
                    new_prefix = name
                # print(new_prefix)
                if Option.is_option(option):
                    flattened[new_prefix] = Option(id=new_prefix, **option)
                elif isinstance(option, dict):
                    queue.put(
                        (new_prefix, option)
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