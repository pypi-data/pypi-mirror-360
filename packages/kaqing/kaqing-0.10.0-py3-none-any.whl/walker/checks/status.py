import re

from walker.checks.check import Check
from walker.checks.check_context import CheckContext
from walker.checks.check_result import CheckResult
from walker.checks.issue import Issue
from walker.k8s_utils import cassandra_pod_exec

class Status(Check):
    def name(self):
        return 'status'
    
    def check(self, ctx: CheckContext) -> tuple[dict[str, any], list[Issue]]:
        issues: list[Issue] = []

        try:
            result = cassandra_pod_exec(ctx.pod, ctx.namespace, f"nodetool -u {ctx.user} -pw {ctx.pw} status", show_out=ctx.show_output)
            status = parse_nodetool_status(result.stdout)
            pod_details = {
                'name': ctx.pod,
                'namespace': ctx.namespace,
                'statefulset': ctx.statefulset,
                'status': status
            }
            if result.stderr: pod_details['stderr'] = result.stderr

            for pod in pod_details['status']:
                if pod['status'] != 'UN':
                    issues.append(Issue(
                        statefulset=ctx.statefulset,
                        namespace=ctx.namespace,
                        pod=ctx.pod,
                        category='status',
                        desc=f"node: {ctx.host_id} reported DOWN"
                    ))                    

            return CheckResult(self.name(), pod_details, issues)
        except Exception as e:
            pod_details = {
                'err': str(e)
            }

            return CheckResult(self.name(), pod_details, issues)
        
def parse_nodetool_status(stdout: str):
    nodes: list[dict] = []
    for line in stdout.splitlines():
        groups = re.match(r"(\S*)\s+(\S*)\s+(.*B)\s+(\S*)\s+(\S*)\s+(\S*)\s+(\S*)", line)
        if groups:
            nodes.append({
                'status': groups[1],
                'address': groups[2],
                'load': groups[3],
                'tokens': groups[4],
                'owns': groups[5],
                'host_id': groups[6],
                'rack': groups[7]
            })

    return nodes