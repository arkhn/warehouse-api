# Contributing to the `fhir-api`

## Deploy the stack

### Prerequisites

- `docker`
- `docker-compose >= 3.7`

### Deployment

1.  Copy the `.template.env`, edit it and save it as a `.env` file in the root directory. `.template.env` contains the minimal configuration required to deploy the stack locally. Your `.env` should be the preferred place to override the default settings used in `docker-compose.yml` and should not be committed. The variables defined in `.env` are only used by `docker-compose.yml`.

        # Minimal configuration in .env
        MONGO_PASSWORD=whatever
        ES_PASSWORD=whatever

2.  Deploy stateful services (mongo, elasticsearch) and the bootstrap task

        # In the root directory of this repo
        docker-compose up -d mongo elasticsearch monstache api-bootstrap

3.  Once the bootstrap task completed (a few seconds, up to 1 minute), deploy the remaining services

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

## Builds

Each push (commits and/or tags) will publish a single image to the DockerHub registry.

Each image will have one or more docker tags, depending on the context:

- on every branch (including `master`), images have following tags:
  - the first 8 chars of the targetted commit hash,
  - the branch name, with `/` replaced by `-`. For instance the branch `jd/fix/1` will have the `jd-fix-1` tag on DockerHub.
- on `master`, images have **additional** tags:
  - the version, only if the push is a tag (i.e. `git push --tags api/vX.Y.Z`),
  - the `latest` tag, for the most recent pushed tag.

## Versioning of `fhir-api`

The api must follow a [**semantic versioning**](https://semver.org/).

## Publishing a new release of `fhir-api`

### 1. Tag the target commit (on `master`)

        git tags api/vX.Y.Z [<commit-sha>]

Tags for the `fhir-api` should be prefixed with `api/v`. For instance, use `api/v1.1.0` if you want to publish the `1.1.0` version of the `fhir-api` on DockerHub.

### 2. Push the tag

        git push --tags api/vX.Y.Z

Providing that the CI workflow is successful (which should always be the case on `master`...), a new image will soon be available on DockerHub with the specified tag.

### 3. Pull the tagged image

        docker pull arkhn/fhir-api:vX.Y.Z
