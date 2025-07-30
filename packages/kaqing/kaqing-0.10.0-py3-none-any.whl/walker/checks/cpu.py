from kubernetes import client
from kubernetes.utils import parse_quantity

from walker.checks.check import Check
from walker.checks.check_context import CheckContext
from walker.checks.check_result import CheckResult
from walker.checks.issue import Issue
from walker.config import Config

class Cpu(Check):
    def name(self):
        return 'cpu'

    def check(self, ctx: CheckContext) -> tuple[dict[str, any], list[Issue]]:
        issues: list[Issue] = []
        cpu_usage = "Unknown"

        group = "metrics.k8s.io"
        version = "v1beta1"
        plural = "pods"

        try:
            api = client.CustomObjectsApi()
            resource = api.list_namespaced_custom_object(group=group, version=version, namespace=ctx.namespace, plural=plural)
            for pod in resource["items"]:
                p_name = pod["metadata"]["name"]
                if p_name != ctx.pod:
                    continue

                for container in pod["containers"]:
                    if container["name"] == 'cassandra':
                        usage = container["usage"]
                        cpu_usage = usage["cpu"]
                        break
                break

            cpu_threshold = Config().get('checks.cpu-threshold', 1.0)
            if cpu_usage != "Unknown" and parse_quantity(cpu_usage) > cpu_threshold:
                issues.append(Issue(
                    statefulset=ctx.statefulset,
                    namespace=ctx.namespace,
                    pod=ctx.pod,
                    category='cpu',
                    desc=f'CPU is too busy: {cpu_usage}',
                    suggestion=f"kaching admin restart {ctx.pod}@{ctx.namespace}"
                ))
        except Exception as e:
            issues.append(self.issue_from_err(statefulset_name=ctx.statefulset, ns=ctx.namespace, pod_name=ctx.pod, exception=e))

        return CheckResult(self.name(), cpu_usage, issues)