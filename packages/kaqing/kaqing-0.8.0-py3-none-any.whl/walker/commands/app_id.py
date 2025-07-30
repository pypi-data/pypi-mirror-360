from walker.commands.command import Command
from walker.repl_state import ReplState, RequiredState
from walker.k8s_utils import get_app_ids, get_cr_name
from walker.utils import log

class AppId(Command):
    COMMAND = 'appid'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(AppId, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return AppId.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, _ = state.apply_args(args)
        if not self.validate_state(state):
            return state

        c3_app_id = 'Unknown'

        apps = get_app_ids()
        cr_name = get_cr_name(state.statefulset if state.statefulset else state.pod, namespace=state.namespace)
        if cr_name in apps:
            c3_app_id = (apps[cr_name])

        log(c3_app_id)

        return c3_app_id

    def completion(self, state: ReplState):
        if state.statefulset:
            return {AppId.COMMAND: None}

        return {}

    def help(self, _: ReplState):
        return f'{AppId.COMMAND}: show app id for the cassandra cluster'