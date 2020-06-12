FROM python:3.7-slim

WORKDIR /home/tracker

COPY requirements requirements
RUN pip install -r requirements/app_dev.txt

COPY app app
COPY tracker.py config.py pytest.ini ./
COPY tests_app tests_app
COPY seeds seeds

CMD pytest tests_app/
