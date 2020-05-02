FROM python:3.7-slim

WORKDIR /home/tracker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY entrypoints entrypoints
COPY tracker.py config.py ./

ENV FLASK_APP tracker.py
ENV SECRET_KEY blah

ENV PGUSER postgres
ENV PGPASSWORD postgres
ENV PGDATABASE postgres
ENV PGHOST db

EXPOSE 5000
CMD entrypoints/app.sh
