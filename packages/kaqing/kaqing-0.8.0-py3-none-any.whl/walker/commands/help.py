from walker.commands.command import Command, cmd_list
from walker.repl_state import ReplState
from walker.utils import log

class Help(Command):
    COMMAND = 'help'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Help, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Help.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not self.args(cmd):
            return super().run(cmd, state)

        lines = Help.strings(state, cmd_list)
        for l in lines:
            log(l)

        return lines

    def strings(state: ReplState, cmd_list: list[Command]):
        strs = []

        lines = [cmd.help(state) for cmd in cmd_list]
        paddings = 0
        for line in lines:
            if line == None: continue

            p = len(line.split(":")[0])
            if paddings < p: paddings = p
        for line in lines:
            if line == None: continue

            kv = line.strip('\n').split(":")
            strs.append(f"{kv[0].ljust(paddings)} {kv[1]}")

        return strs

    def strings(state: ReplState, cmd_list: list[Command]):
        strs = []

        lines = [cmd.help(state) for cmd in cmd_list]
        paddings = 0
        for line in lines:
            if line == None: continue

            p = len(line.split(":")[0])
            if paddings < p: paddings = p
        for line in lines:
            if line == None: continue

            kv = line.strip('\n').split(":")
            strs.append(f"{kv[0].ljust(paddings)} {kv[1]}")

        return strs

    def completion(self, _: ReplState):
        return {Help.COMMAND: None}

    def help(self, _: ReplState):
        return None