FROM python:3.7-slim

RUN apt-get clean \
    && apt-get -y update
    
RUN apt-get -y install python3-dev \
    && apt-get -y install build-essential \
    && apt-get -y install postgresql python-psycopg2 libpq-dev

WORKDIR /srv/flask_app

COPY requirements.txt  /srv/flask_app/requirements.txt
RUN pip install -r requirements.txt --src /usr/local/src

COPY . /srv/flask_app

RUN chmod +x ./start.sh
CMD ["./start.sh"]