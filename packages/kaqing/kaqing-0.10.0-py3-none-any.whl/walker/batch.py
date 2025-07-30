import click

from walker.commands.app_id import AppId
from walker.commands.check import Check, CheckCommandHelper
from walker.commands.command import Command
from walker.commands.command_helpers import ClusterCommandHelper, ClusterOrPodCommandHelper, PodCommandHelper
from walker.commands.cqlsh import CqlCommandHelper, Cqlsh
from walker.commands.issues import Issues
from walker.commands.logs import Logs
from walker.commands.ls import Ls
from walker.commands.nodetool import NodeTool, NodeToolCommandHelper
from walker.commands.reaper import Reaper, ReaperCommandHelper
from walker.commands.report import Report
from walker.commands.restart import Restart
from walker.commands.rolling_restart import RollingRestart
from walker.commands.status import Status as StatusCmd
from walker.repl_state import ReplState
from walker.k8s_utils import init_config, init_params
from walker.cli_group import cli

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterCommandHelper, help='Show c3 app id.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.argument('extra_args', nargs=-1, metavar='<cluster|pod>', type=click.UNPROCESSED)
def appid(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, pod: str, extra_args):
    run_command(AppId(), kubeconfig, config, param, cluster, namespace, pod, extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=CheckCommandHelper, help='Run a single check.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.argument('extra_args', nargs=-1, metavar='<check-name> [cluster|pod]', type=click.UNPROCESSED)
def check(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, pod: str, extra_args):
    run_command(Check(), kubeconfig, config, param, cluster, namespace, pod, extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=CqlCommandHelper, help='Execute CQL statements.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.argument('extra_args', nargs=-1, metavar='<CQL-statements> <cluster|pod>', type=click.UNPROCESSED)
def cql(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, pod: str, extra_args):
    run_command(Cqlsh(), kubeconfig, config, param, cluster, namespace, pod, extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterOrPodCommandHelper, help="Print Qing's issues.")
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.option('--show', '-s', is_flag=True, help='show output from Cassandra nodes')
@click.argument('extra_args', nargs=-1, metavar='[cluster|pod]', type=click.UNPROCESSED)
def issues(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, pod: str, show: bool, extra_args):
    run_command(Issues(), kubeconfig, config, param, cluster, namespace, pod, ('-s',) + extra_args if show else extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=PodCommandHelper, help='Get cassandra log.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.argument('extra_args', nargs=-1, metavar='<pod>', type=click.UNPROCESSED)
def logs(kubeconfig: str, config: str, param: list[str], namespace: str, pod: str, extra_args):
    run_command(Logs(), kubeconfig, config, param, None, namespace, pod, extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterCommandHelper, help='List statefulset or pods.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.argument('extra_args', nargs=-1, metavar='[cluster|..]', type=click.UNPROCESSED)
def ls(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, extra_args):
    run_command(Ls(), kubeconfig, config, param, cluster, namespace, None, extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=NodeToolCommandHelper, help='Nodetool operations.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.argument('extra_args', nargs=-1, metavar='sub-command <cluster|pod>', type=click.UNPROCESSED)
def nodetool(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, pod: str, extra_args):
    run_command(NodeTool(), kubeconfig, config, param, cluster, namespace, pod, extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ReaperCommandHelper, help='Execute reaper operations.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.argument('extra_args', nargs=-1, metavar='COMMAND <cluster>', type=click.UNPROCESSED)
def reaper(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, extra_args):
    run_command(Reaper(), kubeconfig, config, param, cluster, namespace, None, extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterOrPodCommandHelper, help="Generate Qing's report.")
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.option('--show', '-s', is_flag=True, help='show output from Cassandra nodes')
@click.argument('extra_args', nargs=-1, metavar='[cluster|pod]', type=click.UNPROCESSED)
def report(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, pod: str, show: bool, extra_args):
    run_command(Report(), kubeconfig, config, param, cluster, namespace, pod, ('-s',) + extra_args if show else extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterOrPodCommandHelper, help='Restart Cassandra Cluster or Node')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.option('--force', is_flag=True, help='need for restarting the whole cluster')
@click.argument('extra_args', nargs=-1, metavar='<cluster|pod>', type=click.UNPROCESSED)
def restart(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, pod: str, force: bool, extra_args):
    run_command(Restart(), kubeconfig, config, param, cluster, namespace, pod, ('--force',) + extra_args if force else extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterOrPodCommandHelper, help='Rolling restart Cassandra Cluster.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.argument('extra_args', nargs=-1, metavar='<cluster>', type=click.UNPROCESSED)
def rolling_restart(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, extra_args):
    run_command(RollingRestart(), kubeconfig, config, param, cluster, namespace, None, extra_args)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterOrPodCommandHelper, help='Show combined nodetool status from Cassandra nodes.')
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaching parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.option('--pod', '-c', required=False, metavar='pod', help='Kubernetes pod name')
@click.argument('extra_args', nargs=-1, metavar='<cluster|pod>', type=click.UNPROCESSED)
def status(kubeconfig: str, config: str, param: list[str], cluster: str, namespace: str, pod: str, extra_args):
    run_command(StatusCmd(), kubeconfig, config, param, cluster, namespace, pod, extra_args)


def run_command(cmd: Command, kubeconfig: str, config: str, params: list[str], cluster:str, namespace: str, pod: str, extra_args):
    init_config(kubeconfig)
    if not init_params(config, params):
        return

    state = ReplState(ns_statefulset=cluster, pod=pod, namespace=namespace)
    cmd.run(build_cmd(cmd.command(), extra_args), state)

def build_cmd(cmd, extra_args):
    path = ' '.join(list(extra_args))
    if path:
        cmd = f'{cmd} {path}'

    return cmd.strip(' ')