FROM python:3.7-slim

WORKDIR /home/tracker

COPY requirements requirements
RUN pip install -r requirements/app.txt

COPY app app
COPY tracker.py config.py ./
COPY seeds seeds

EXPOSE 5000
CMD flask run --host 0.0.0.0
