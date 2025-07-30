import importlib
import os
import shutil
from typing import TypeVar, cast
import importlib.resources as pkg_resources
import yaml
from pathlib import Path

from walker.utils import get_deep_keys, log2

T = TypeVar('T')

class Config:
    EMBEDDED_PARAMS = {}

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Config, cls).__new__(cls)

        return cls.instance

    def __init__(self, path: str = None):
        if path:
            try:
                with open(path) as f:
                    self.params = cast(dict[str, any], yaml.safe_load(f))
            except:
                # /git/ops/kaching/walker/params.yaml -> ~/.kaqing/params.yaml
                # log2(f'Config file: {path} does not exist; using ~/.kaqing/params.yaml.')
                self.copy_config_file()
        elif not hasattr(self, 'params'):
            self.copy_config_file()

    def copy_config_file(self):
        dir = f'{Path.home()}/.kaqing'
        path = f'{dir}/params.yaml'
        if not os.path.exists(path):
            os.makedirs(dir, exist_ok=True)
            my_module = importlib.import_module('walker.embedded_params')
            with open(path, 'w') as f:
                yaml.dump(my_module.params(), f, default_flow_style=False)
            log2(f'Default params.yaml has been written to {path}.')

        with open(path) as f:
            self.params = cast(dict[str, any], yaml.safe_load(f))

        return path

    def action_node_samples(self, action: str, default: T):
        return self.get(f'{action}.samples', default)

    def action_workers(self, action: str, default: T):
        return self.get(f'{action}.workers', default)

    def keys(self) -> list[str]:
        return get_deep_keys(self.params)

    def get(self, key: str, default: T) -> T:
        # params['nodetool']['status']['max-nodes']
        d = self.params
        for p in key.split("."):
            if p in d:
                d = d[p]
            else:
                return default

        return d

    def set(self, key: str, v: str):
        d = Config().params
        ps = key.split('.')
        for p in ps[:len(ps) - 1]:
            if p in d:
                d = d[p]
            else:
                log2(f'incorrect path: {key}')
                return None

        try:
            v = int(v)
        except:
            pass

        p = ps[len(ps) - 1]
        if p in d:
            d[p] = v
        else:
            log2(f'incorrect path: {key}')
            return None

        return v