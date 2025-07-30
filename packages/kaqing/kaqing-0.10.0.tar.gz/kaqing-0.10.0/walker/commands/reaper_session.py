from collections.abc import Callable
from kubernetes import client
import portforward
import re
import requests
from typing import List, cast

from walker.config import Config
from walker.repl_state import ReplState
from walker.utils import lines_to_tabular, log2

class ReaperSession:
    def __init__(self, headers: dict[str, str] = None):
        self.headers = headers

    def login(self, state: ReplState, local_addr: str, remote_addr: str) -> str :
        user, pw = state.user_pass(secret_path='reaper.secret')

        response = requests.post(f'http://{local_addr}/login', headers={
            'Accept': '*'
        },data={
            'username':user,
            'password':pw})
        log2(f'POST {remote_addr}/login')
        log2(f'     username={user}&password={pw}')

        if int(response.status_code / 100) != 2:
            log2("login failed")
            return None

        return response.headers['Set-Cookie']

    def port_forwarded(self, state: ReplState, path: str, body: Callable[[str, dict[str, str]], requests.Response], method: str = None):
        local_port = 9001
        target_port = 8080

        with portforward.forward(state.namespace, state.pod, local_port, target_port):
            local_addr = f'localhost:{local_port}'
            remote_addr = f'{state.pod}:{target_port}'
            if not self.headers:
                self.headers = self.cookie_header(state, local_addr, remote_addr)

            if method:
                log2(f'{method} {remote_addr}/{path}')
            response = body(f'http://{local_addr}/{path}', self.headers)
            if response:
                if int(response.status_code / 100) != 2:
                    log2(response.status_code)
                    return response

            log2()

            return response if response else 'no-response'

    def cookie_header(self, state: ReplState, local_addr, remote_addr):
        return {'Cookie': self.login(state, local_addr, remote_addr)}

    def reaper_pod_from_cluster(state: ReplState) -> str:
        pods = ReaperSession.list_reaper_pods(state.statefulset, state.namespace)
        if pods:
            state.pod = pods[0].metadata.name
            return pods[0].metadata.name
        else:
            log2('No reaper found.')
            return None

    def list_reaper_pods(statefulset_name: str, namespace: str) -> List[client.V1Pod]:
        v1 = client.CoreV1Api()

        # k8ssandra.io/reaper: cs-d0767a536f-cs-d0767a536f-reaper
        groups = re.match(Config().get('reaper.pod.cluster-regex', r'(.*?-.*?-.*?-.*?)-.*'), statefulset_name)
        label_selector = Config().get('reaper.pod.label-selector', 'k8ssandra.io/reaper={cluster}-reaper').replace('{cluster}', groups[1])

        return cast(List[client.V1Pod], v1.list_namespaced_pod(namespace, label_selector=label_selector).items)

    def show_schedules(self, state: ReplState, filter: Callable[[list[dict]], dict] = None):
        def body(uri: str, headers: dict[str, str]):
            return requests.get(uri, headers=headers)

        response = self.port_forwarded(state, 'repair_schedule', body, method='GET')
        if not response:
            return

        res = response.json()
        if filter:
            res = filter(res)

        self.show_schedules_tabular(res)

    def show_schedules_tabular(self, schedules: list[dict]):
        log2(lines_to_tabular([f"{schedule['id']} {schedule['state']} {schedule['cluster_name']} {schedule['keyspace_name']}" for schedule in schedules], 'ID STATE CLUSTER KEYSPACE'))

    def show_schedule(self, state: ReplState, schedule_id: str):
        def filter(schedules: list[dict]):
            return [schedule for schedule in schedules if schedule['id'] == schedule_id]

        self.show_schedules(state, filter)