#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Load FHIR definitions
flask load-defs /var/data/definitions

uwsgi --ini uwsgi.ini