from __future__ import annotations

import json
import os
import string
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
    def __init__(self) -> None:
        self.body = DotDict({'metadata': {'name': ''}})
        self.s = requests.Session()
        self.s.headers = {'Authorization': 'Bearer ' + KUBE_AUTH}
        self.s.verify = False
        self.url_class = type(self).__name__.lower() + 's'

    def put(self) -> None:
        api_type = 'apis/apps' if self.url_class == 'deployments' else 'api'
        resp = self.s.request(
            'POST',
            f'{ KUBE_BASE_URL }/{ api_type }/v1/namespaces/{ KUBE_NAMESPACE }/{ self.url_class }/',
            json=self.body.to_dict(),
        )
        if resp.status_code != 201:
            resp = self.s.request(
                'PUT',
                f'{ KUBE_BASE_URL }/{ api_type }/v1/namespaces/{ KUBE_NAMESPACE }/{ self.url_class }/{ self.body.metadata.name }',
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
        return resp.json().get('items', [])

    def delete(self, name: str) -> None:
        api_type = 'apis/apps' if self.url_class == 'deployments' else 'api'
        self.s.delete(
            f'{ KUBE_BASE_URL }/{ api_type }/v1/namespaces/{ KUBE_NAMESPACE }/{ self.url_class }/{ name }'
        )

    def __del__(self) -> None:
        self.s.close()
        print('destructed')


configmap_template = string.Template(
    '''
apiVersion: v1
data: ${data}
kind: ConfigMap
metadata:
  name: ${name}
'''
)


class ConfigMap(BaseObject):
    def __init__(self, name: str = '', data: dict = {}) -> None:
        super().__init__()
        self.body = DotDict(
            yaml.safe_load(
                configmap_template.substitute({'name': name, 'data': json.dumps(data)})
            )
        )

    def get(self, name: str) -> ConfigMap:
        d = self._get(name)
        return ConfigMap(d['metadata']['name'], d['data'])

    def get_all(self) -> List[ConfigMap]:
        return [
            ConfigMap(d['metadata']['name'], d['data'])
            for d in self._get_all()
            if 'data' in d
        ]


deployment_template = string.Template(
    '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${name}
  template:
    metadata:
      labels:
        app: ${name}
    spec:
      containers:
      - image: funcpunk/flask
        name: ${name}
        volumeMounts:
        - mountPath: /flask/code.py
          name: ${name}
          subPath: code
      volumes:
      - configMap:
          name: ${name}
        name: ${name}
'''
)


class Deployment(BaseObject):
    def __init__(self, name: str = '') -> None:
        super().__init__()
        self.body = DotDict(
            yaml.safe_load(deployment_template.substitute({'name': name}))
        )

    def get(self, name: str) -> Deployment:
        d = self._get(name)
        return Deployment(d['metadata']['name'])

    def get_all(self) -> List[Deployment]:
        return [Deployment(d['metadata']['name']) for d in self._get_all()]


service_template = string.Template(
    '''
apiVersion: v1
kind: Service
metadata:
  name: ${name}
spec:
  ports:
  - port: 5000
    targetPort: 5000
  selector:
    app: ${name}
'''
)


class Service(BaseObject):
    def __init__(self, name: str = '') -> None:
        super().__init__()
        self.body = DotDict(yaml.safe_load(service_template.substitute({'name': name})))

    def get(self, name: str) -> Service:
        d = self._get(name)
        return Service(d['metadata']['name'])

    def get_all(self) -> List[Service]:
        return [Service(d['metadata']['name']) for d in self._get_all()]
