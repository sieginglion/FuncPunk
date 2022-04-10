import os
import dotenv
from kubernetes import client
from flask import Flask, request, Response

if not os.getenv('KUBE_BASE_URL'):
    dotenv.load_dotenv()

KUBE_BASE_URL = os.getenv('KUBE_BASE_URL')
KUBE_AUTH = os.getenv('KUBE_AUTH')

config = client.Configuration(host=KUBE_BASE_URL, api_key={'authorization': KUBE_AUTH})
config.verify_ssl = False
v1 = client.CoreV1Api(client.ApiClient(config))

app = Flask(__name__)

@app.route('/func/<name>', methods=['GET', 'PUT'])
def func(name):
    if request.method == 'GET':
        try:
            cm = v1.read_namespaced_config_map(name, 'funcpunk')
            return cm.data['code']
        except:
            return Response(status=404)
    elif request.method == 'PUT':
        cm = client.V1ConfigMap(
            data={'code': request.data.decode()},
            metadata=client.V1ObjectMeta(name=name)
        )
        try:
            v1.replace_namespaced_config_map(name, 'funcpunk', cm)
        except:
            v1.create_namespaced_config_map('funcpunk', cm)
        return Response(status=201)

app.run(host='0.0.0.0')
