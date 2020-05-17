FROM python:3.7-slim

WORKDIR /home/tracker

COPY requirements requirements
RUN pip install -r requirements/app.txt

COPY app app
COPY entrypoints entrypoints
COPY tracker.py config.py pytest.ini ./
COPY tests_app tests_app
COPY seeds seeds

ENV FLASK_APP tracker.py
ENV SECRET_KEY blah

CMD entrypoints/test.sh
