#!/bin/sh
#source venv/bin/activate
#flask db upgrade
#flask translate compile
#exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app
echo $FLASK_APP
pwd
ls
flask run