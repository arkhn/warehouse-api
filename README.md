# `fhir-api` monorepo

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This is a monorepo containing both an api and a dedicated web app.

Each maintain their own (but tied) software versioning, using namespaced tags to mark releases.
| directory     | content                    | versioning                    | tag namespace for release  |
|---------------|----------------------------|-------------------------------|----------------------------|
| `./fhir-api/` | FHIR server implementation | [semver](https://semver.org/) | `api/` (e.g. `api/v1.0.0`) |
| `./front/`    | Web app                    | incrementing sequence         | `app/`  (e.g. `app/v1`)    |


## [Authors](CODEOWNERS)

## [License](LICENSE)
