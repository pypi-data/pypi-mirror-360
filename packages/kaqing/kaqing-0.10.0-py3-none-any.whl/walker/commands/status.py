import sys

from walker.commands.command import Command
from walker.commands.nodetool import NodeTool
from walker.config import Config
from walker.repl_state import ReplState, RequiredState
from walker.k8s_utils import get_user_pass, cassandra_pod_exec, pod_names
from walker.utils import lines_to_tabular, log, log2
from walker.checks.status import parse_nodetool_status

class Status(Command):
    COMMAND = 'status'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Status, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Status.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if state.namespace and state.pod:
            NodeTool().run(f'nodetool {cmd}', state)
        elif state.namespace and state.statefulset:
            self.merge_status(pod_names(state.statefulset, state.namespace), state.namespace, Config().get('nodetool.samples', sys.maxsize))

        return state

    def merge_status(self, pod_names: list[str], ns: str, samples: int):
        statuses: list[list[dict]] = []
        for pod_name in pod_names:
            pod_name = pod_name.split('(')[0]
            user, pw = get_user_pass(pod_name, ns)

            try:
                result = cassandra_pod_exec(pod_name, ns, f"nodetool -u {user} -pw {pw} status", show_out=False)
                status = parse_nodetool_status(result.stdout)
                if status: statuses.append(status)
                if samples <= len(statuses) and len(pod_names) != len(statuses):
                    break
            except Exception as e:
                log2(e)
                pass

        return self._merge_status(statuses, len(pod_names))

    def _merge_status(self, statuses: list[list[dict]], pods: int):
        combined = statuses[0]

        status_by_host = {}
        for status in statuses[0]:
            status_by_host[status['host_id']] = status
        for status in statuses[1:]:
            for s in status:
                if s['host_id'] in status_by_host:
                    c = status_by_host[s['host_id']]
                    if c['status'] == 'UN' and s['status'] == 'DN':
                        c['status'] = 'DN*'
                else:
                    combined.append(s)

        log2(f'Showing merged status from {len(statuses)}/{pods} nodes...')
        log(lines_to_tabular([f"{d['status']},{d['address']},{d['load']},{d['tokens']},{d['owns']},{d['host_id']},{d['rack']}" for d in combined],
                         '--,Address,Load,Tokens,Owns,Host ID,Rack', separator=','))

        return combined

    def completion(self, state: ReplState):
        if not state.pod and state.statefulset:
            return {Status.COMMAND: None}

        return {}

    def help(self, _: ReplState):
        return f'{Status.COMMAND}: show nodetool status merged from all nodes'