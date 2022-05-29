FROM python:3.10-slim
RUN mkdir backend/
COPY *.py requirements.txt backend/
RUN pip install -r backend/requirements.txt
CMD python main.py
