from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from kubernetes import client

from walker.checks.check import Check
from walker.checks.check_context import CheckContext
from walker.checks.check_result import CheckResult
from walker.checks.compactionstats import CompactionStats
from walker.checks.cpu import Cpu
from walker.checks.gossip import Gossip
from walker.checks.issue import Issue
from walker.checks.memory import Memory
from walker.checks.status import Status
from walker.k8s_utils import get_host_id, get_user_pass, list_pods
from walker.config import Config
from walker.utils import elapsed_time, log2

def all_checks() -> list[Check]:
    return [CompactionStats(), Cpu(), Gossip(), Memory(), Status()]

def run_checks(cluster: str = None, namespace: str = None, pod: str = None, check: str = None, show_output=True):
    checks: list[Check] = all_checks()

    if check:
        checks = [c for c in checks if c.name() == check]

    apps_v1_api = client.AppsV1Api()
    statefulsets = apps_v1_api.list_stateful_set_for_all_namespaces(label_selector="app.kubernetes.io/name=cassandra")
    sss: tuple[str, str] = [(statefulset.metadata.name, statefulset.metadata.namespace) for statefulset in statefulsets.items]

    action = 'issues'
    crs: list[CheckResult] = []

    def on_clusters(f: Callable[[any, list[str]], any]):
        for ss, ns in sss:
            if (not cluster or cluster == ss) and (not namespace or namespace == ns):
                pods = list_pods(ss, ns)
                for pod_name in [pod.metadata.name for pod in pods]:
                    if not pod or pod == pod_name:
                        f(ss, ns, pod_name, show_output)

    max_workers = Config().action_workers(action, 30)
    if max_workers < 2:
        def serial(ss, ns, pod_name, show_output):
            if not pod or pod == pod_name:
                crs.append(run_checks_on_pod(checks, ss[0], ns, pod_name, show_output))

        on_clusters(serial)
    else:
        log2(f'Executing on all nodes from statefulset with {max_workers} workers...')
        start_time = time.time()
        try:
            futures = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                def submit(ss, ns, pod_name, show_output):
                    f = executor.submit(run_checks_on_pod, checks, ss, ns, pod_name, show_output,)
                    if f: futures.append(f)

                on_clusters(submit)

            crs = [future.result() for future in as_completed(futures)]
        finally:
            log2(f"Parallel {action} elapsed time: {elapsed_time(start_time)} with {max_workers} workers")

    return crs

def run_checks_on_pod(checks: list[Check], cluster: str = None, namespace: str = None, pod: str = None, show_output=True):
    host_id = get_host_id(pod, namespace)
    user, pw = get_user_pass(pod, namespace)
    results = {}
    issues: list[Issue] = []
    for c in checks:
        check_results = c.check(CheckContext(cluster, host_id, pod, namespace, user, pw, show_output=show_output))
        if check_results.details:
            results = results | {check_results.name: check_results.details}
        if check_results.issues:
            issues.extend(check_results.issues)

    return CheckResult(None, results, issues)