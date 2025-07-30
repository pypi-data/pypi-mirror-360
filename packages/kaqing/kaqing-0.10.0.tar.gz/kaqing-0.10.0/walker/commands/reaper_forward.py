import time

from walker.commands.command import Command
from walker.commands.reaper_session import ReaperSession
from walker.config import Config
from walker.repl_state import ReplState, RequiredState
from walker.utils import log2

class ReaperForward(Command):
    COMMAND = 'reaper forward'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ReaperForward, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ReaperForward.COMMAND

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

        def body(uri: str, _: dict[str, str]):
            try:
                user, pw = state.user_pass(secret_path='reaper.secret')
                log2(f"Click: {uri}")
                log2(f'username: {user}')
                log2(f'password: {pw}')
                log2()
                log2(f"Press Ctrl+C to break.")

                time.sleep(Config().get('reaper.port-forward-timeout', 3600 * 24))
            except KeyboardInterrupt:
                pass

        return ReaperSession().port_forwarded(state, 'webui', body)

    def completion(self, state: ReplState):
        if state.statefulset:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ReaperForward.COMMAND}: port-forward to reaper'