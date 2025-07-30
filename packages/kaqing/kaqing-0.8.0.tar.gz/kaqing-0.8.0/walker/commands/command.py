from abc import abstractmethod
import copy
import subprocess
import sys

from walker.repl_state import ReplState, RequiredState

cmd_list: list['Command'] = []

class Command:
    """Abstract base class for commands"""
    def __init__(self, successor: 'Command'=None):
        self._successor = successor

    @abstractmethod
    def command(self) -> str:
        pass

    # The chain of responsibility pattern
    # Do not do child of child!!!
    @abstractmethod
    def run(self, cmd: str, state: ReplState):
        if self._successor:
            return self._successor.run(cmd, state)

        return None

    def completion(self, _: ReplState) -> dict[str, any]:
        # COMMAND = 'reaper activate schedule'
        d = None
        for t in reversed(self.command().split(' ')):
            d = {t: d}

        return d

    def required(self) -> RequiredState:
        return None

    def validate_state(self, state: ReplState):
        return state.validate(self.required())

    @abstractmethod
    def help(self, state: ReplState) -> str:
        pass

    def args(self, cmd: str):
        a = list(filter(None, cmd.split(' ')))
        spec = self.command_tokens()
        if spec != a[:len(spec)]:
            return None

        return a

    def apply_state(self, args: list[str], state: ReplState) -> tuple[ReplState, list[str]]:
        return state.apply_args(args, self.command_tokens())

    def command_tokens(self):
        return self.command().split(' ')

    # build a chain-of-responsibility chain
    def chain(cl: list['Command']):
        global cmd_list
        cmd_list.extend(cl)

        cmds = cl[0]
        cmd = cmds
        for successor in cl[1:]:
            cmd._successor = successor
            cmd = successor

        return cmds

    def command_to_completion(self):
        # COMMAND = 'reaper activate schedule'
        d = None
        for t in reversed(self.command().split(' ')):
            d = {t: d}

        return d

    def display_help():
        args = copy.copy(sys.argv)
        args.extend(['--help'])
        subprocess.run(args)

    def extract_options(args: list[str], names: list[str]):
        found: list[str] = []

        new_args: list[str] = []
        for arg in args:
            if arg in names:
                found.append(arg)
            else:
                new_args.append(arg)

        return new_args, found