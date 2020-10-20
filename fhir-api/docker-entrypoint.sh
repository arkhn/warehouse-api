#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Load FHIR definitions
flask load-defs /var/data/definitions

export UWSGI_PROCESSES=${UWSGI_PROCESSES:-5}
export UWSGI_THREADS=${UWSGI_THREADS:-4}

uwsgi --ini uwsgi.ini