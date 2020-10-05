# Contributing to the `fhir-api`

## Deploy the stack

### Prerequisites

- `docker`
- `docker-compose >= 3.7`

### Deployment

1.  Copy the `.template.env`, edit it and save it as a `.env` file in the root directory. `.template.env` contains the minimal configuration required to deploy the stack locally. Your `.env` should be the preferred place to override the default settings used in `docker-compose.yml` and should not be committed. The variables defined in `.env` are only used by `docker-compose.yml`.

        # Minimal configuration in .env
        MONGO_PASSWORD=whatever
        ELASTIC_PASSWORD=whatever

2.  Deploy mongo

        # In the root directory of this repo
        docker-compose up -d mongo

3.  Once mongo's up (a few seconds), initiate the replica set

        docker-compose exec mongo mongo -u ${MONGO_USER:-arkhn} -p ${MONGO_PASSWORD:-whatever} --eval "rs.initiate()"

4.  Deploy the remaining of the stack

        docker-compose up -d

## Local development

### Local prerequisites

1.  Install OS dependencies (for `pdftotext` notably)

        sudo apt-get update -y
        sudo apt-get install build-essential libpoppler-cpp-dev pkg-config

2.  Create an environment with the project requirements

        mkvirtualenv fhir-api --python python3.8 -r requirements/dev.txt
        workon fhir-api

3.  Run the development server

        flask run

## Code quality

Code quality is enforced with `pre-commit` hooks: `black`, `isort`, `flake8`

1.  Install the hooks

        precommit install

## Tests

1.  Run tests in dedicated virtual env.

        tox
