FROM python:3.8-slim

WORKDIR /home/tracker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY tracker.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP tracker.py

#RUN chown -R microblog:microblog ./

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]