import requests

from walker.commands.command import Command
from walker.commands.reaper_session import ReaperSession
from walker.repl_state import ReplState, RequiredState
from walker.utils import log2

class ReaperRunAbort(Command):
    COMMAND = 'reaper abort run'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ReaperRunAbort, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ReaperRunAbort.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if not args:
            if state.in_repl:
                log2('Specify run id to abort.')
            else:
                Command.display_help()

            return state

        if not ReaperSession.reaper_pod_from_cluster(state):
            return state

        self.stop_run(state, args[0])

        return state

    def stop_run(self, state: ReplState, run_id: str):
        def body(uri: str, headers: dict[str, str]):
            return requests.put(uri, headers=headers)

        reaper = ReaperSession()
        # PAUSED, RUNNING, ABORTED
        # PUT /repair_run/{id}/state/{state}
        reaper.port_forwarded(state, f'repair_run/{run_id}/state/ABORTED', body, method='PUT')

    def completion(self, state: ReplState):
        if state.statefulset:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ReaperRunAbort.COMMAND}: abort reaper run'