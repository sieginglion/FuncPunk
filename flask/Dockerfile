FROM python:latest
COPY * ./
CMD pip install -r requirements.txt && \
    export FLASK_APP=main && flask run --host 0.0.0.0

