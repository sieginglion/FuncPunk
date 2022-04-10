import flask
from code import func

app = flask.Flask(__name__)

@app.route('/')
def main():
    return func(flask.request)
