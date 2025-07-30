from walker.checks.issue import Issue

class CheckResult:
    def __init__(self, name: str, details: any = None, issues: list[Issue] = None):
        self.name = name
        self.details = details
        self.issues = issues

    def details(results: list['CheckResult']):
        return [r.details for r in results]
    
    def issues(results: list['CheckResult']):
        return sum([r.issues for r in results], [])
    
    def report(results: list['CheckResult']):
        return {
            'checks': CheckResult.details(results),
            'issues': [issue.to_dict() for issue in CheckResult.issues(results)]
        }