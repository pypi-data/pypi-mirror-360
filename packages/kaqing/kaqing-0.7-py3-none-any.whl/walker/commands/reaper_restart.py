from walker.commands.command import Command
from walker.commands.reaper_session import ReaperSession
from walker.k8s_utils import delete_pod
from walker.repl_state import ReplState, RequiredState

class ReaperRestart(Command):
    COMMAND = 'reaper restart'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ReaperRestart, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ReaperRestart.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if not ReaperSession.reaper_pod_from_cluster(state):
            return

        delete_pod(state.pod, state.namespace)

        return state

    def completion(self, state: ReplState):
        if state.statefulset:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ReaperRestart.COMMAND}: restart reaper'