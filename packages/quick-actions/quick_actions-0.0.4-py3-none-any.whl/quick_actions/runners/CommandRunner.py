import subprocess
from typing import Dict
import os


class CommandRunner:
    def __init__(self, command: str, envs: Dict = None, print_err: bool = True):
        if envs is not None:
            default_env = os.environ.copy()

            envs={name:os.path.expandvars(value) for name,value in envs.items() }
            envs.update(**default_env)

        self.process = subprocess.run(command, shell=True, encoding='utf-8', env=envs,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
            # capture_output = True
            )

        print(self.output)

        if print_err:
            print(f"{command}: {self.error}")

    @property
    def returncode(self):
        return self.process.returncode

    @property
    def output(self):
        return self.process.stdout

    @property
    def error(self):
        return self.process.stderr
