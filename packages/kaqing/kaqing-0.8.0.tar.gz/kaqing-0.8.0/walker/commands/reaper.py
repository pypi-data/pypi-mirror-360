import click

from walker.commands.command import Command
from walker.commands.command_helpers import ClusterCommandHelper
from walker.commands.help import Help
from walker.commands.reaper_forward import ReaperForward
from walker.commands.reaper_restart import ReaperRestart
from walker.commands.reaper_run_abort import ReaperRunAbort
from walker.commands.reaper_runs import ReaperRuns
from walker.commands.reaper_runs_abort import ReaperRunsAbort
from walker.commands.reaper_schedule_activate import ReaperScheduleActivate
from walker.commands.reaper_schedule_start import ReaperScheduleStart
from walker.commands.reaper_schedule_stop import ReaperScheduleStop
from walker.commands.reaper_schedules import ReaperSchedules
from walker.commands.reaper_status import ReaperStatus
from walker.repl_state import ReplState, RequiredState
from walker.utils import log, log2

class Reaper(Command):
    COMMAND = 'reaper'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Reaper, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Reaper.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        # head with the Chain of Responsibility pattern
        cmds = Command.chain(Reaper.cmd_list())
        if not cmds.run(cmd, state):
            if state.in_repl:
                for l in Help.strings(ReplState(), Reaper.cmd_list()):
                    log2(l)
            else:
                log2('* Command is missing.')
                Command.display_help()

    def cmd_list():
        return [ReaperSchedules(), ReaperScheduleStop(), ReaperScheduleActivate(), ReaperScheduleStart(),
                ReaperForward(), ReaperRunAbort(), ReaperRunsAbort(), ReaperRestart(), ReaperRuns(), ReaperStatus()]

    def completion(self, state: ReplState):
        if state.statefulset:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return None

class ReaperCommandHelper(click.Command):
    def get_help(self, ctx: click.Context):
        log(super().get_help(ctx))
        log()
        log('Commands:')

        for l in Help.strings(ReplState(), Reaper.cmd_list()):
            log(l.replace(f'{Reaper.COMMAND} ', '  ', 1))
        log()
        ClusterCommandHelper.cluster_help()