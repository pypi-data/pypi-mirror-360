from kubernetes import client
from typing import List

from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.k8s_utils import get_app_ids, get_cr_name, list_pods, list_statefulset_names, get_host_id
from walker.utils import lines_to_tabular, log, log2

class Ls(Command):
    COMMAND = 'ls'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Ls, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Ls.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        if state.pod:
            pass
        elif state.statefulset:
            self.show_pods(list_pods(state.statefulset, state.namespace), state.namespace)
        else:
            self.show_statefulsets()

        return state

    def show_statefulsets(self):
        ss = list_statefulset_names()
        if len(ss) == 0:
            log2('No cassandra statefulsets found.')
            return

        app_ids = get_app_ids()
        list = []
        for s in ss:
            cr_name = get_cr_name(s)
            app_id = 'Unknown'
            if cr_name in app_ids:
                app_id = app_ids[cr_name]
            list.append(f"{s} {app_id}")

        log(lines_to_tabular(list, 'STATEFULSET_NAME@NAMESPACE APP_ID'))

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

            return f"{get_host_id(pod.metadata.name, ns)} {pod.metadata.name}@{ns} {ready}/{pods} {status}"

        pod_names = [line(pod) for pod in pods]

        log(lines_to_tabular(pod_names, 'HOST_ID POD_NAME READY POD_STATUS'))

    def completion(self, state: ReplState):
        if state.pod:
            return {}

        if not state.statefulset:
            return {Ls.COMMAND: {n: None for n in list_statefulset_names()}}

        return {Ls.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Ls.COMMAND}: list clusters|nodes'