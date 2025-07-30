import re
from typing import List, cast
from kubernetes import client

from walker.commands.command import Command
from walker.commands.reaper_session import ReaperSession
from walker.repl_state import ReplState, RequiredState
from walker.utils import lines_to_tabular, log, log2

class ReaperStatus(Command):
    COMMAND = 'reaper status'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ReaperStatus, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ReaperStatus.COMMAND

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

        self.show_pods(self.list_pods(state.statefulset, state.namespace), state.namespace)

        return state

    def list_pods(self, statefulset_name: str, namespace: str) -> List[client.V1Pod]:
        v1 = client.CoreV1Api()

        # cs-9834d85c68-cs-9834d85c68-default-sts-0
        # k8ssandra.io/reaper: cs-d0767a536f-cs-d0767a536f-reaper
        groups = re.match(r'(.*?-.*?-.*?-.*?)-.*', statefulset_name)
        label_selector = f'k8ssandra.io/reaper={groups[1]}-reaper'

        return cast(List[client.V1Pod], v1.list_namespaced_pod(namespace, label_selector=label_selector).items)

    def show_pods(self, pods: List[client.V1Pod], ns: str):
        if len(pods) == 0:
            log2('No pods found.')
            return

        def line(pod: client.V1Pod):
            pods = len(pod.status.container_statuses)
            ready = 0
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    if container_status.ready:
                        ready += 1

            status = pod.status.phase
            if pod.metadata.deletion_timestamp:
                status = 'Terminating'

            return f"{pod.metadata.name}@{ns} {ready}/{pods} {status}"

        pod_names = [line(pod) for pod in pods]

        log(lines_to_tabular(pod_names, 'POD_NAME READY POD_STATUS'))

    def completion(self, state: ReplState):
        if state.statefulset:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ReaperStatus.COMMAND}: restart reaper'