#!/usr/bin/env bash
until psql postgres://postgres@fhirbase:5432/fhirbase -c '\q'; do \
    >&2 echo "Postgres is starting up..."; \
    sleep 1; \
done

uwsgi --ini uwsgi.ini --py-autoreload 1