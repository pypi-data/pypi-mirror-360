from walker.commands.command import Command
from walker.repl_state import ReplState, RequiredState
from walker.k8s_utils import delete_pod, pod_names
from walker.utils import log2

class Restart(Command):
    COMMAND = 'restart'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Restart, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Restart.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        args, forced = Command.extract_options(args, '--force')
        if len(args) == 0:
            if state.pod:
                log2(f'Restarting {state.pod}...')
                delete_pod(state.pod, state.namespace)
            else:
                if not forced:
                    log2('Please add --force for restarting all nodes in a cluster.')
                    return

                log2(f'Restarting all pods from {state.statefulset}...')
                for pod_name in pod_names(state.statefulset, state.namespace):
                    delete_pod(pod_name, state.namespace)
        else:
            for arg in args:
                delete_pod(arg, state.namespace)

        return state

    def completion(self, state: ReplState):
        if state.pod:
            return {Restart.COMMAND: None}
        elif state.statefulset:
            return {Restart.COMMAND: {p: None for p in pod_names(state.statefulset, state.namespace)}}

        return {}

    def help(self, _: ReplState):
        return f"{Restart.COMMAND} [<host-id>]: restart the node you're in or all the nodes in the cluster"