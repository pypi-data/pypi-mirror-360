from walker.checks.check_result import CheckResult
from walker.checks.check_utils import run_checks
from walker.checks.issue import Issue
from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.utils import lines_to_tabular, log, log2

class Issues(Command):
    COMMAND = 'issues'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Issues, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Issues.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        args, show = Command.extract_options(args, ['-s', '--show'])

        results = run_checks(state.statefulset, state.namespace, state.pod, show_output=show)
        issues = CheckResult.issues(results)
        self.show_issues(issues)

        return issues

    def show_issues(self, issues: list[Issue]):
        if not issues:
            log2('No issues found.')
        else:
            log2(f'* {len(issues)} issues found.')
            lines = []
            for i, issue in enumerate(issues, start=1):
                lines.append(f"{i}||{issue.category}||{issue.desc}")
                lines.append(f"||statefulset||{issue.statefulset}@{issue.namespace}")
                lines.append(f"||pod||{issue.pod}@{issue.namespace}")
                if issue.details:
                    lines.append(f"||details||{issue.details}")

                if issue.suggestion:
                    lines.append(f'||suggestion||{issue.suggestion}')
            log(lines_to_tabular(lines, separator='||'))

    def completion(self, _: ReplState):
        return {Issues.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Issues.COMMAND}: find all issues'