FROM python:3.7-slim

WORKDIR /home/tracker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY entrypoints entrypoints
COPY tracker.py config.py pytest.ini ./
COPY tests tests

ENV FLASK_APP tracker.py
ENV SECRET_KEY blah

CMD entrypoints/test_suite.sh
