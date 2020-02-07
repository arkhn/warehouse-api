# warehouse-api

** IN PROGRESS **

API of Arkhn's health data warehouse

## Building the services

```bash
 docker-compose build
```

## Running the stack

```bash
docker-compose up
# wait for mongo to be up and running...
env $(cat fhir-api/.env) ./scripts/initiate_rep_set.sh
# Open your browser to http://localhost/api
```

## Usage

### Create a resource

`POST http://localhost/api/<resource_type>`

`<resource_type>`: eg: Patient, Organization...

`BODY`: resource data in JSON

### Read a resource

`GET http://localhost/api/<resource_type>/<id>`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

### Update a resource

`PUT http://localhost/api/<resource_type>/<id>`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

`BODY`: resource data in JSON

### Delete a resource

`DELETE http://localhost/api/<resource_type>/<id>`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

### Patch a resource (partial update)

`PATCH http://localhost/api/<resource_type>`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

`BODY`: patch data (partial resource) in JSON

### Search a resource

_Search is a work in progress, only works with strings right now_

`GET http://localhost/api/<resource_type>?[parameter1=value1][&parameter2=value2]...`

`<resource_type>`: eg: Patient, Organization...

`<id>`: logical id of the resource

`parameterN`: json path to search in the FHIR resource

`valueN`: exact match of the extracted fhir attribute

_Example (gets all patients)_: `GET http://localhost/api/Patient`

_Example (gets a patient by family name)_: `GET http://localhost/api/Patient?name.0.family=Bins636`
