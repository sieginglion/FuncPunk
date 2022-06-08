FROM python:3.10-slim
RUN mkdir /flask/
COPY * /flask/
WORKDIR /flask/
RUN pip install flask
CMD FLASK_APP=main flask run --host 0.0.0.0 || true
