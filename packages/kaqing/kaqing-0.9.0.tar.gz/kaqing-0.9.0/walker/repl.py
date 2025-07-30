import re
import click
from kubernetes import client
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit import PromptSession

from walker.cli_group import cli
from walker.commands.app_id import AppId
from walker.commands.cd import Cd
from walker.commands.check import Check
from walker.commands.command import Command
from walker.commands.command_helpers import ClusterCommandHelper
from walker.commands.cqlsh import Cqlsh
from walker.commands.exit import Exit
from walker.commands.param_get import GetParam
from walker.commands.help import Help
from walker.commands.issues import Issues
from walker.commands.ls import Ls
from walker.commands.nodetool import NodeTool
from walker.commands.reaper import Reaper
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
from walker.commands.report import Report
from walker.commands.restart import Restart
from walker.commands.rolling_restart import RollingRestart
from walker.commands.param_set import SetParam
from walker.commands.params_show import ShowParams
from walker.commands.status import Status
from walker.repl_state import ReplState
from walker.k8s_utils import init_config, init_params
from walker.utils import deep_merge_dicts, log2

def enter_repl(state: ReplState):
    cmd_list: list[Command] = [AppId(), Cd(), Check(), Cqlsh(), GetParam(), Help(), Issues(), Ls(), NodeTool(),
                               ReaperForward(), ReaperSchedules(), ReaperRunAbort(), ReaperRunsAbort(), ReaperRuns(),
                               ReaperScheduleActivate(), ReaperScheduleStop(), ReaperScheduleStart(), ReaperRestart(),
                               ReaperStatus(),
                               Reaper(), Report(), Restart(), RollingRestart(), SetParam(), ShowParams(), Status(), Exit()]
    # head with the Chain of Responsibility pattern
    cmds: Command = Command.chain(cmd_list)
    session = PromptSession()

    def prompt_msg():
        msg = ''
        if state.pod:
            # cs-d0767a536f-cs-d0767a536f-default-sts-0
            group = re.match(r".*?-.*?-(.*)", state.pod)
            msg = group[1]
        elif state.statefulset:
            # cs-d0767a536f-cs-d0767a536f-default-sts
            group = re.match(r".*?-.*?-(.*)", state.statefulset)
            msg = group[1]

        return f"{msg}> "

    apps_v1_api = client.AppsV1Api()
    statefulsets = apps_v1_api.list_stateful_set_for_all_namespaces(label_selector="app.kubernetes.io/name=cassandra")
    ss = [(statefulset.metadata.name, statefulset.metadata.namespace) for statefulset in statefulsets.items]

    if len(ss) == 0:
        raise Exception("no cassandra statefulsets found")

    while True:
        completions = {}
        for cmd in cmd_list:
            completions = deep_merge_dicts(completions, cmd.completion(state))

        completer = NestedCompleter.from_nested_dict(completions)
        cmd = session.prompt(prompt_msg(), completer=completer)

        try:
            if cmd and cmd.strip(' ') and not cmds.run(cmd, state):
                log2(f'* Invalid command: {cmd}')
                log2()
                for l in Help.strings(state, cmd_list):
                    log2(l)
        except Exception as e:
            log2(e)

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterCommandHelper, help="Enter interactive shell.")
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.argument('extra_args', nargs=-1, metavar='[cluster]', type=click.UNPROCESSED)
def repl(kubeconfig: str, config: str, param: list[str], cluster:str, namespace: str, extra_args):
    init_config(kubeconfig)
    if not init_params(config, param):
        return

    state = ReplState(ns_statefulset=cluster, namespace=namespace, in_repl=True)
    state, _ = state.apply_args(extra_args)
    enter_repl(state)