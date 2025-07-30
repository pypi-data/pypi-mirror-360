from abc import abstractmethod

from walker.checks.check_context import CheckContext
from walker.checks.check_result import CheckResult
from walker.checks.issue import Issue

class Check:
    """Abstract base class for checks"""
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def check(self, context: CheckContext) -> CheckResult:
        pass

    def issue_from_err(statefulset_name: str, ns: str, pod_name: str, exception: Exception):
        return Issue(
            statefulset=statefulset_name,
            namespace=ns,
            pod=pod_name,
            category='kaching',
            desc=f"{exception}"
        )