import base64
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import re
import sys
import time
from typing import List, TypeVar, cast
from kubernetes import client, config as kconfig
from kubernetes.stream import stream
from kubernetes.stream.ws_client import ERROR_CHANNEL

from walker.config import Config
from walker.pod_exec_result import PodExecResult
from walker.utils import elapsed_time, log2

T = TypeVar('T')
_TEST_POD_EXEC_OUTS: PodExecResult = None

def set_test_pod_exec_outs(outs: PodExecResult):
    global _TEST_POD_EXEC_OUTS
    _TEST_POD_EXEC_OUTS = outs

    return _TEST_POD_EXEC_OUTS

def list_pods(statefulset_name: str, namespace: str) -> List[client.V1Pod]:
    v1 = client.CoreV1Api()

    # this filters out with labels first -> saves about 1 second
    # cassandra.datastax.com/cluster: cs-9834d85c68
    # cassandra.datastax.com/datacenter: cs-9834d85c68
    # cassandra.datastax.com/rack: default
    # cs-9834d85c68-cs-9834d85c68-default-sts-0
    # cs-d0767a536f-cs-d0767a536f-reaper-946969766-rws92
    groups = re.match(r'(.*?-.*?)-(.*?-.*?)-(.*?)-.*', statefulset_name)
    label_selector = f'cassandra.datastax.com/cluster={groups[1]},cassandra.datastax.com/datacenter={groups[2]},cassandra.datastax.com/rack={groups[3]}'

    pods = cast(List[client.V1Pod], v1.list_namespaced_pod(namespace, label_selector=label_selector).items)
    statefulset_pods = []

    for pod in pods:
        if pod.metadata.owner_references:
            for owner in pod.metadata.owner_references:
                if owner.kind == "StatefulSet" and owner.name == statefulset_name:
                    statefulset_pods.append(pod)
                    break

    return statefulset_pods

def delete_pod(pod_name: str, namespace: str):
    try:
        v1 = client.CoreV1Api()
        api_response = v1.delete_namespaced_pod(pod_name, namespace)
    except Exception as e:
        log2("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

def list_statefulsets() -> List[client.V1StatefulSet]:
    apps_v1_api = client.AppsV1Api()
    statefulsets = apps_v1_api.list_stateful_set_for_all_namespaces(label_selector="app.kubernetes.io/name=cassandra")

    return statefulsets.items

def list_statefulset_names():
    return [f"{statefulset.metadata.name}@{statefulset.metadata.namespace}" for statefulset in list_statefulsets()]

def get_host_id(pod_name, ns):
    try:
        container_name = 'cassandra'
        user, pw = get_user_pass(pod_name, ns)
        command = f'echo "SELECT host_id FROM system.local; exit" | cqlsh --no-color -u {user} -p {pw}'
        result = cassandra_pod_exec(pod_name, ns, command, show_out=False)
        next = False
        for line in result.stdout.splitlines():
            if next:
                return line.strip(' ')
            if line.startswith('----------'):
                next = True
                continue
    except Exception as e:
        return str(e)

    return 'Unknown'

def get_user_pass(ss_name: str, namespace: str, secret_path: str = 'cql.secret'):
    # cs-d0767a536f-cs-d0767a536f-default-sts ->
    # cs-d0767a536f-superuser
    # cs-d0767a536f-reaper-ui
    user = 'superuser'
    if secret_path == 'reaper.secret':
        user = 'reaper-ui'
    groups = re.match(Config().get(f'{secret_path}.cluster-regex', r'(.*?-.*?)-.*'), ss_name)
    secret_name = Config().get(f'{secret_path}.name', '{cluster}-' + user).replace('{cluster}', groups[1], 1)
    v1 = client.CoreV1Api()
    try:
        secret = v1.read_namespaced_secret(secret_name, namespace)
        for key, value in secret.data.items():
            #  username password
            decoded_value = base64.b64decode(value).decode("utf-8")
            if key == Config().get(f'{secret_path}.password-item', 'password'):
                return (secret_name, decoded_value)
    except client.ApiException as e:
        log2(f"Error reading secret: {e}")
        raise e

def cassandra_nodes_exec(statefulset: str, namespace: str, command: str, action: str, max_workers=0):
    pods = pod_names(statefulset, namespace)
    if not max_workers:
        max_workers = Config().action_workers(action, 0)
    if max_workers > 0:
        # if parallel, node sampling is suppressed
        log2(f'Executing on all nodes from statefulset in parallel...')
        start_time = time.time()
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(cassandra_pod_exec, pod, namespace, command, False, False,) for pod in pods]
                if len(futures) == 0:
                    return cast(list[T], [])

            rs = [future.result() for future in as_completed(futures)]
            for result in rs:
                print(result.command)
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    log2(result.stderr, file=sys.stderr)

            return rs
        finally:
            log2(f"Parallel {action} elapsed time: {elapsed_time(start_time)} with {max_workers} workers")
    else:
        samples = Config().action_node_samples(action, sys.maxsize)
        l = min(len(pods), samples)
        adj = 'all'
        if l < len(pods):
            adj = f'{l} sample'
        log2(f'Executing on {adj} nodes from statefulset...')
        for pod_name in pods:
            try:
                result = cassandra_pod_exec(pod_name, namespace, command, throw_err=True)
                if result.exit_code() == 0:
                    l -= 1
                    if not l:
                        break
            except Exception as e:
                log2(e)

def cassandra_pod_exec(pod_name: str, namespace: str, command: str, show_out = True, throw_err = False):
    return pod_exec(pod_name, "cassandra", namespace, command, show_out, throw_err)

def pod_exec(pod_name: str, container: str, namespace: str, command: str, show_out = True, throw_err = False, interaction: Callable[[any, list[str]], any] = None):
    if _TEST_POD_EXEC_OUTS:
        return _TEST_POD_EXEC_OUTS

    api = client.CoreV1Api()

    exec_command = ["/bin/sh", "-c", command]
    k_command = f'kubectl exec -it {pod_name} -c {container} -n {namespace} -- {command}'
    if show_out:
        print(k_command)

    resp = stream(
        api.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=exec_command,
        container=container,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=True,
        _preload_content=False,
    )

    stdout = []
    stderr = []
    error_output = None
    try:
        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                frag = resp.read_stdout()
                stdout.append(frag)
                if show_out: print(frag, end="")

                if interaction:
                    interaction(resp, stdout)
            if resp.peek_stderr():
                frag = resp.read_stderr()
                stderr.append(frag)
                if show_out: print(frag, end="")

        try:
            # get the exit code from server
            error_output = resp.read_channel(ERROR_CHANNEL)
        except Exception:
            pass
    except Exception as e:
        if throw_err:
            raise e
        else:
            log2(e)
    finally:
        resp.close()

    return PodExecResult("".join(stdout), "".join(stderr), k_command, error_output)

def pod_names(ss: str, ns: str):
    pods = list_pods(ss, ns)

    return [pod.metadata.name for pod in pods]

def pod_names_by_host_id(ss: str, ns: str):
    pods = list_pods(ss, ns)
    return {get_host_id(pod.metadata.name, ns): pod.metadata.name for pod in pods}

def get_app_ids():
    app_ids_by_ss: dict[str, str] = {}

    group = Config().get('app.cr.group', 'ops.c3.ai')
    v = Config().get('app.cr.v', 'v2')
    plural = Config().get('app.cr.plural', 'c3cassandras')
    label = Config().get('app.label', 'c3__app_id-0')
    strip = Config().get('app.strip', '0')

    v1 = client.CustomObjectsApi()
    try:
        c3cassandras = v1.list_cluster_custom_object(group=group, version=v, plural=plural)
        for c in c3cassandras.items():
            if c[0] == 'items':
                for item in c[1]:
                    app_ids_by_ss[f"{item['metadata']['name']}@{item['metadata']['namespace']}"] = item['metadata']['labels'][label].strip(strip)
    except Exception:
        pass

    return app_ids_by_ss

def get_cr_name(cluster: str, namespace: str = None):
    nn = cluster.split('@')
    # cs-9834d85c68-cs-9834d85c68-default-sts
    if not namespace and len(nn) > 0:
        namespace = nn[1]
    groups = re.match(Config().get('app.cr.cluster-regex', r"(.*?-.*?)-.*"), nn[0])
    return f"{groups[1]}@{namespace}"

def init_config(config: str = None):
    if not config:
        config = os.getenv('KUBECONFIG')
        if not config:
            log2('Use --config or set KUBECONFIG env variable to path to your config file.')
            exit(1)

    try:
        kconfig.load_kube_config(config_file=config)
    except:
        log2(f'Kubernetes config file: {config} does not exist or is not valid.')
        exit(1)

def init_params(params_file: str, param_ovrs: list[str]):
    Config(params_file)
    for p in param_ovrs:
        tokens = p.split('=')
        if len(tokens) == 2:
            if m := Config().set(tokens[0], tokens[1]):
                log2(f'set {tokens[0]} {tokens[1]}')
                log2(m)
            else:
                return None
        else:
            log2('Use -k <key>=<value> format.')
            return None

    return Config().params

def is_pod_name(name: str):
    namespace = None
    # cs-d0767a536f-cs-d0767a536f-default-sts-0
    nn = name.split('@')
    if len(nn) > 1:
        namespace = nn[1]
    groups = re.match(r"^cs-.*-sts-\d+$", nn[0])
    if groups:
        return (nn[0], namespace)

    return (None, None)

def is_statefulset_name(name: str):
    namespace = None
    # cs-d0767a536f-cs-d0767a536f-default-sts
    nn = name.split('@')
    if len(nn) > 1:
        namespace = nn[1]
    groups = re.match(r"^cs-.*-sts$", nn[0])
    if groups:
        return (nn[0], namespace)

    return (None, None)