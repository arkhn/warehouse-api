import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DB_NAME = os.getenv("MONGO_DB", "fhirstore")
DB_HOST = os.getenv("MONGO_HOST", "localhost")
DB_PORT = int(os.getenv("MONGO_PORT", 27017))
DB_USER = os.getenv("MONGO_USER")
DB_PASSWORD = os.getenv("MONGO_PASSWORD")

ES_USERNAME = os.getenv("ES_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD")
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = os.getenv("ES_PORT", 9200)
ES_URL = f"http://{ES_USERNAME}{':'+ES_PASSWORD if ES_PASSWORD else ''}@{ES_HOST}:{ES_PORT}"

AUTH_DISABLED = os.getenv("AUTH_DISABLED", "").lower() in ["1", "true", "yes"]

TOKEN_INTROSPECTION_URL = os.getenv("TOKEN_INTROSPECTION_URL")
