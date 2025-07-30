import click

from walker.checks.check_result import CheckResult
from walker.checks.check_utils import all_checks, run_checks
from walker.commands.command import Command
from walker.commands.command_helpers import ClusterOrPodCommandHelper
from walker.commands.issues import Issues
from walker.repl_state import ReplState
from walker.utils import log

class Check(Issues):
    COMMAND = 'check'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Check, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Check.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        if not args:
            if state.in_repl:
                log('Specify a check name.')
            else:
                log('* Check name is missing.')
                Command.display_help()
            return 'arg missing'

        check = args[0]

        results = run_checks(state.statefulset, state.namespace, state.pod, check=check)
        issues = CheckResult.issues(results)
        self.show_issues(issues)

        return issues

    def completion(self, _: ReplState):
        return {Check.COMMAND: {check.name(): None for check in all_checks()}}

    def help(self, _: ReplState):
        return f'{Check.COMMAND}: run a single check'

class CheckCommandHelper(click.Command):
    def get_help(self, ctx: click.Context):
        log(super().get_help(ctx))
        log()
        log('Check-names:')

        for check in all_checks():
            log(f'  {check.name()}')
        log()

        ClusterOrPodCommandHelper.cluter_or_pod_help()