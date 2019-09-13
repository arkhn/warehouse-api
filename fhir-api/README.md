# fhir-api

Implementation of a FHIR REST server API.

## Development

### Requirements

First, create a virtual environment using `virtualenv .` and enter it with `. ./bin/activate`

Then install the requirements:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running the stack

This service depends on a postgres database (fhirbase) in order to work properly. We advise you run the services with `docker-compose` [(see usage here)](../README.md). In case you already have your own database running, you should edit the configuration with your db host, username, password [TODO!]. You can then simply run the service using :
```bash
python app.py
# Open your browser to http://localhost:5000/api
```

### Tests

```bash
pytest -v tests/
```