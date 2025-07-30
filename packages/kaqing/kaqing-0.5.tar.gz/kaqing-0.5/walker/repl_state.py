import copy
from enum import Enum

from walker.k8s_utils import get_user_pass, is_pod_name, is_statefulset_name
from walker.utils import display_help, log2

class RequiredState(Enum):
    CLUSTER = 'cluster'
    POD = 'pod'
    CLUSTER_OR_POD = 'cluster_or_pod'

class ReplState:
    def __init__(self, statefulset: str = None, pod: str = None, namespace: str = None, ns_statefulset: str = None, in_repl = False):
        self.statefulset = statefulset
        self.pod = pod
        self.namespace = namespace
        self.in_repl = in_repl

        if ns_statefulset:
            nn = ns_statefulset.split('@')
            self.statefulset = nn[0]
            if len(nn) > 1:
                self.namespace = nn[1]

    def apply_args(self, args: list[str], cmd: list[str] = None) -> tuple['ReplState', list[str]]:
        state = self

        new_args = []
        for index, arg in enumerate(args):
            if index < 5:
                state = copy.copy(state)

                s, n = is_statefulset_name(arg)
                if s:
                    if not state.statefulset:
                        state.statefulset = s
                    if n and not state.namespace:
                        state.namespace = n

                p, n = is_pod_name(arg)
                if p:
                    if not state.pod:
                        state.pod = p
                    if n and not state.namespace:
                        state.namespace = n

                if not s and not p:
                    new_args.append(arg)
            else:
                new_args.append(arg)

        if cmd:
            new_args = new_args[len(cmd):]

        return (state, new_args)

    def validate(self, required: RequiredState = None):
        if required == RequiredState.CLUSTER:
            if not self.namespace or not self.statefulset:
                if self.in_repl:
                    log2('cd to a cluster first.')
                else:
                    log2('* cluster is missing.')
                    log2()
                    display_help()

                return False
        elif required == RequiredState.POD:
            if not self.namespace or not self.pod:
                if self.in_repl:
                    log2('cd to a pod first.')
                else:
                    log2('* Pod is missing.')
                    log2()
                    display_help()

                return False
        elif required == RequiredState.CLUSTER_OR_POD:
            if not self.namespace or not self.statefulset and not self.pod:
                if self.in_repl:
                    log2('cd to a cluster first.')
                else:
                    log2('* cluster or pod is missing.')
                    log2()
                    display_help()

                return False

        return True

    def user_pass(self, secret_path = 'cql.secret'):
        return get_user_pass(self.pod if self.pod else self.statefulset, self.namespace, secret_path=secret_path)