FROM python:3.7-slim

WORKDIR /home/prices

COPY requirements requirements
RUN pip install -r requirements/prices.txt

COPY tasks tasks

CMD python3 -m tasks.prices_cli
