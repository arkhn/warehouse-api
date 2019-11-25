FROM alpine:3.10

RUN apk update

RUN apk add --no-cache \
    uwsgi-python3 \
    python3-dev \
    bash

RUN addgroup -S api_group && adduser -S api_user -G api_group

WORKDIR /srv/flask_app

COPY requirements.txt  /srv/flask_app/requirements.txt
RUN pip3 install -r requirements.txt --src /usr/local/src

COPY . /srv/flask_app

RUN chmod +x ./start.sh

USER api_user

CMD ["./start.sh"]