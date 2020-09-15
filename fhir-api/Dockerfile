FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH "${PYTHONPATH}:/srv"

RUN groupadd api_group && useradd --no-log-init -G api_group api_user

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get -y install build-essential libpoppler-cpp-dev pkg-config bash git \
    && apt-get autoremove --purge -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

COPY requirements.txt  /srv/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt --src /usr/local/src

COPY . .

RUN chmod +x ./start.sh
RUN chown -R api_user:api_group /usr/local/lib

USER api_user

EXPOSE 2000

ENTRYPOINT ["/srv/docker-entrypoint.sh"]