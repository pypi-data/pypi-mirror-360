from walker.commands.command import Command
from walker.commands.reaper_session import ReaperSession
from walker.repl_state import ReplState, RequiredState

class ReaperSchedules(Command):
    COMMAND = 'reaper schedules'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ReaperSchedules, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ReaperSchedules.COMMAND

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

        ReaperSession().show_schedules(state)

        return state

    def completion(self, state: ReplState):
        if state.statefulset:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ReaperSchedules.COMMAND}: show reaper schedules'