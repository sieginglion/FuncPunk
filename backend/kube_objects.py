from __future__ import annotations

import os
from typing import Any, List

import dotenv
import requests
import yaml

if not os.getenv('KUBE_BASE_URL'):
    dotenv.load_dotenv()

KUBE_BASE_URL = os.getenv('KUBE_BASE_URL')
KUBE_AUTH = os.getenv('KUBE_AUTH')
KUBE_NAMESPACE = os.getenv('KUBE_NAMESPACE')


class DotDict(dict):
    def __setattr__(self, k: str, v: Any) -> None:
        return super().__setitem__(k, v)

    def __getattr__(self, k: str) -> Any:
        return super().__getitem__(k)

    def __init__(self, d: dict = {}):
        for k, v in d.items():
            self[k] = DotDict(v) if isinstance(v, dict) else v

    def to_dict(self) -> dict:
        return {
            k: v.to_dict() if isinstance(v, DotDict) else v for k, v in self.items()
        }


class BaseObject(object):
    def __init__(self, new: bool = True) -> None:
        self.body = DotDict({'metadata': {'name': ''}})
        self.new = new
        self.s = requests.Session()
        self.s.headers = {'Authorization': 'Bearer ' + KUBE_AUTH}
        self.s.verify = False
        self.url_class = 's'

    def put(self) -> None:
        self.s.request(
            'POST' if self.new else 'PUT',
            f'{ KUBE_BASE_URL }/api/v1/namespaces/{ KUBE_NAMESPACE }/{ self.url_class }/{ "" if self.new else self.body.metadata.name }',
            json=self.body.to_dict(),
        )

    def _get(self, name: str) -> dict:
        resp = self.s.get(
            f'{ KUBE_BASE_URL }/api/v1/namespaces/{ KUBE_NAMESPACE }/{ self.url_class }/{ name }'
        )
        return resp.json()

    def _get_all(self) -> List[dict]:
        resp = self.s.get(
            f'{ KUBE_BASE_URL }/api/v1/namespaces/{ KUBE_NAMESPACE }/{ self.url_class }'
        )
        return resp.json()['items']

    def delete(self, name: str) -> None:
        self.s.delete(
            f'{ KUBE_BASE_URL }/api/v1/namespaces/{ KUBE_NAMESPACE }/{ self.url_class }/{ name }'
        )

    def __del__(self) -> None:
        self.s.close()
        print('destructed')


configmap_template = DotDict(
    yaml.safe_load(
        '''
apiVersion: v1
data: {}
kind: ConfigMap
metadata:
  labels: {}
  name: ""
'''
    )
)


class ConfigMap(BaseObject):
    def __init__(
        self, name: str = '', labels: dict = {}, data: dict = {}, new: bool = True
    ) -> None:
        super().__init__(new)
        self.body = configmap_template
        self.body.metadata.name = name
        self.body.metadata.labels = DotDict(labels)
        self.body.data = DotDict(data)
        self.url_class = type(self).__name__.lower() + 's'

    def get(self, name: str) -> ConfigMap:
        d = self._get(name)
        return ConfigMap(
            d['metadata']['name'], d['metadata']['labels'], d['data'], False
        )

    def get_all(self) -> List[ConfigMap]:
        return [
            ConfigMap(d['metadata']['name'], d['metadata']['labels'], d['data'], False)
            for d in self._get_all()
            if 'labels' in d['metadata'] and 'data' in d
        ]
