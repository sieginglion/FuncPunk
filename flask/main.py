import func
import flask

app = flask.Flask(__name__)

@app.route('/')
def main():
    return func.func(flask.request)

