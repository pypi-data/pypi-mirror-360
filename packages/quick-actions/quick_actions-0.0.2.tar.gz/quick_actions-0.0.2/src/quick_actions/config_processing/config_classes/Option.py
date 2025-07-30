from dataclasses import dataclass
from typing import Dict
from pathlib import Path
from quick_actions import constants
import copy


@dataclass
class Option:
    id: str
    label: str
    exec: str | None = None
    script: Path | str | None = None
    sleep_before: float | int | None = None
    search_tags: str | None = None
    prefix: str | None = None

    @staticmethod
    def is_option(option_candidate: Dict):
        # print(option_candidate)
        if option_candidate.get("label") == None:
            return False
        if option_candidate.get(constants.INLINE_SCRIPT_PREFIX) == None and \
            option_candidate.get(constants.SCRIPT_PREFIX) == None:
            # TODO: use proper warning log
            print(f"[WARNING]: Option '{option_candidate["label"]}' has no command")
        return True

    @property
    def tags(self):
        if self.search_tags is None:
            return []
        return self.search_tags.strip().split(",")

    def with_arguments(self, arguments):
        new_option = copy.copy(self)

        if self.script is not None:
            new_option.script = None
            new_option.exec = str(self.script) + " " + arguments
        elif self.exec is not None:
            new_option.exec += " " + arguments
        return new_option
