from walker.checks.check import Check
from walker.checks.check_context import CheckContext
from walker.checks.check_result import CheckResult
from walker.checks.issue import Issue
from walker.k8s_utils import cassandra_pod_exec

class Memory(Check):
    def name(self):
        return 'memory'
    
    def check(self, ctx: CheckContext) -> tuple[dict[str, any], list[Issue]]:
        issues: list[Issue] = []

        try:
            result = cassandra_pod_exec(ctx.pod, ctx.namespace, 'cat /c3/cassandra/logs/system.log', show_out=ctx.show_output)
            if issue := self.find_errors(ctx.statefulset, ctx.host_id, ctx.pod, ctx.namespace, result.stdout, 
                                         'Not marking nodes down due to local pause', 
                                         'local pause due to memory pressure'):
                issues.append(issue)
            if issue := self.find_errors(ctx.statefulset, ctx.host_id, ctx.pod, ctx.namespace, result.stdout, 
                                         'java.lang.OutOfMemoryError: Direct buffer memory', 
                                         'direct buffer OOM'):
                issues.append(issue)
        except Exception as e:
            issues.append(self.issue_from_err(statefulset_name=ctx.statefulset, ns=ctx.namespace, pod_name=ctx.pod, exception=e))

        return CheckResult(self.name(), None, issues)
    
    def find_errors(self, statefulset_name: str, host_id: str, pod_name: str, ns: str, stdout: str, keyword: str, issue_desc: str):
        if stdout.find(keyword) > 0:
            for line in reversed(stdout.split('\n')):
                if line.find(keyword) > 0:
                    return Issue(
                        statefulset=statefulset_name,
                        namespace=ns,
                        pod=pod_name,
                        category='memory',
                        desc=f"node: {host_id} reported {issue_desc}",
                        details=line,
                        # kaching admin restart -n gkeops845 -p cs-d0767a536f-cs-d0767a536f-default-sts-0
                        suggestion=f"kaching admin restart {pod_name}@{ns}"
                    )
                
        return None
