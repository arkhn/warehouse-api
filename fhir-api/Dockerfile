FROM python:3.8-slim

RUN apt-get update \
    && apt-get -y install build-essential libpoppler-cpp-dev pkg-config bash git

RUN groupadd api_group
RUN useradd -G api_group api_user

WORKDIR /srv/flask_app
ENV PYTHONPATH "${PYTHONPATH}:/srv/flask_app"

COPY requirements.txt  /srv/flask_app/requirements.txt
RUN pip3 install -r requirements.txt --src /usr/local/src

COPY . /srv/flask_app

RUN chmod +x ./start.sh

RUN chown -R api_user:api_group /usr/local/lib

USER api_user

CMD ["./start.sh"]