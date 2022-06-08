import code

from flask import Flask, request


app = Flask(__name__)


@app.route('/')
def main():
    return code.main(request)
