import requests

from walker.commands.command import Command
from walker.commands.reaper_session import ReaperSession
from walker.repl_state import ReplState, RequiredState
from walker.utils import log2

class ReaperScheduleStart(Command):
    COMMAND = 'reaper start schedule'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ReaperScheduleStart, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ReaperScheduleStart.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if not args:
            log2('Specify schedule to activate.')

            return state

        schedule_id = args[0]
        if not ReaperSession.reaper_pod_from_cluster(state):
            return schedule_id

        self.activate_schedule(state, schedule_id)

        return schedule_id

    def activate_schedule(self, state: ReplState, schedule_id: str):
        def body(uri: str, headers: dict[str, str]):
            return requests.post(uri, headers=headers)

        reaper = ReaperSession()
        reaper.port_forwarded(state, f'repair_schedule/start/{schedule_id}', body, method='POST')
        reaper.show_schedule(state, schedule_id)

    def completion(self, state: ReplState):
        if state.statefulset:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ReaperScheduleStart.COMMAND}: start reaper schedule'