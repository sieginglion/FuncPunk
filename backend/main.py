import flask
from kubernetes import client, config

config.load_kube_config('/config')
v1 = client.CoreV1Api()

app = flask.Flask(__name__)

@app.route('/func/<name>', methods=['GET', 'POST'])
def func(name):
    if flask.request.method == 'GET':
        v1.read_namespaced_config_map(name)

