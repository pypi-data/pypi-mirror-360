from walker.commands.command import Command
from walker.repl_state import ReplState, RequiredState
from walker.utils import log2

class RollingRestart(Command):
    COMMAND = 'roll'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(RollingRestart, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return RollingRestart.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        log2("not implemented")

        return state

    def completion(self, state: ReplState):
        if state.pod:
            return {}
        elif state.statefulset:
            return {RollingRestart.COMMAND: None}

        return {}

    def help(self, _: ReplState):
        return f'{RollingRestart.COMMAND}: rolling restart all nodes'