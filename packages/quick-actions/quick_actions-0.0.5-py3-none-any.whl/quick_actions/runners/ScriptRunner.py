import subprocess
from typing import Dict
import os


class ScriptRunner:
    def __init__(self, command: str, envs: Dict = None):
        if envs is not None:
            default_env = os.environ.copy()

            envs={name:os.path.expandvars(value) for name,value in envs.items() }
            envs.update(**default_env)

            envs.update(**default_env)

        self.process = subprocess.run(command, env=envs, encoding='utf-8')

    @property
    def returncode(self):
        return self.process.returncode

    @property
    def output(self):
        return self.process.stdout
