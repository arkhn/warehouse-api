![](https://github.com/arkhn/warehouse-api/workflows/fhir-api/badge.svg)

# fhir-api

Implementation of a FHIR REST server API.

## Usage

### Create a resource

`POST http://localhost:5000/<resource_type>`

`<resource_type>`: eg: Patient, Organization...

`BODY`: resource data in JSON

### Read a resource

`GET http://localhost:5000/<resource_type>/<id>`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

### Update a resource

`PUT http://localhost:5000/<resource_type>/<id>`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

`BODY`: resource data in JSON

### Delete a resource

`DELETE http://localhost:5000/<resource_type>/<id>`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

### Patch a resource (partial update)

`PATCH http://localhost:5000/<resource_type>`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

`BODY`: patch data (partial resource) in JSON

### Search a resource

_Search is a work in progress, compliant to https://www.hl7.org/fhir/search.html_

`GET http://localhost:5000/<resource_type>?[parameter1=value1][&parameter2=value2]...`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

`parameterN`: json path to search in the FHIR resource

`valueN`: exact match of the extracted fhir attribute

## FHIR API SPEC COMPLIANCE

- AND queries: `?name=Sandra&language=french`
- OR queries: `?name=Sandra,Michelle`
- ID search: `?_id=XXXX-YYY-ZZZ-DDDD`

Modifiers :

- String modifiers (`:exact`, `:contains`)
- Prefixes for dates, numbers, and quantity (eq, ne, gt, lt, ge, le)
- `:identifier`, `:in`, `:not`
- tokens `[parameter]=[system]|[code]`<br>

Ability to search on multiple resources:

- `?/_type=MedicalRequest,Observation` query more than one resource type

Search result parameters supported::\*

- `_count=N` display only the first N results,
- `_element=name,birthDate` return only some attributes of the resource queried,
- `_summary=text` return only elements _id, meta, text_ of the bundle,
- `_summary=count` return only the number of resources that matched the query,
- `_summary=false` return all parts of the resource.
- `_sort` by a parameter in ascending or descending order, can be sorted by \_score.
- `_include` include to the result another resource referenced in the search results
- `_revinclude` include to the result all resources referencing the search results
- `_has_` selecting resources based on the properties of resources that refer to them

_Example (gets all patients)_: `GET http://localhost:5000/api/Patient` <br>
_Example (gets a patient by family name)_: `GET http://localhost:5000/api/Patient?name.family=Donald`
_Example (gets name and birthdate of 2 patients named 'Donald' or 'Chalmers')_:`GET http://localhost/api/Patient?name.family=Donald,Chalmers&_count=2&_element=name,birthDate`

## Development

If you wish, you can disabled authentication by setting the env variable `AUTH_DISABLED` to `1`.

### Requirements

First, create a virtual environment using `virtualenv .` and enter it with `. ./bin/activate`

Then install the requirements:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running the stack

This service depends on a mongo database (fhirstore) in order to work properly. We advise you run the services with `docker-compose` [(see usage here)](../README.md). In case you already have your own database running, you should edit the configuration with your db host, username, password [TODO!]. You can then simply run the service using :

```bash
python app.py
# Open your browser to http://localhost:5000
```

### MongoDB management:

```shell
# Disable JSON schema validation:
env $(cat .env.<target>) python scripts/disable_json_validator.py
```

### Elasticsearch management:

```shell
# Rebuild ES index:
env $(cat .env.<target>) python scripts/rebuild_es_index.py
```

### Tests

```bash
pytest -v tests/
```
