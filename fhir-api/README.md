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

_Search is a work in progress_

`GET http://localhost:5000/<resource_type>?[parameter1=value1][&parameter2=value2]...`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

`parameterN`: json path to search in the FHIR resource

`valueN`: exact match of the extracted fhir attribute


*Additional features are supported to improve the search:*
`_count=N` search only the first N results,
`_element=name,birthDate` return only some attributes of the resource queried,
`_summary=text` return only elements *id, meta, text* of the bundle,
`_summary=count` return only the number of resources that matched the query,   
`_summary=false` return all parts of the resource.


_Example (gets all patients)_: `GET http://localhost:5000/api/Patient`
_Example (gets a patient by family name)_: `GET http://localhost:5000/api/Patient?name.family=Donald`
_Example (gets name and birthdate of 2 patients named 'Donald' or 'Chalmers')_:`GET http://localhost/api/Patient?name.family=Donald,Chalmers&_count=2&_element=name,birthDate`



## Development

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

### Tests

```bash
pytest -v tests/
```
