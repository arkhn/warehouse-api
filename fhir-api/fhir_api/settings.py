import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DB_NAME = os.getenv("MONGO_DB", "fhirstore")
DB_HOST = os.getenv("MONGO_HOST", "localhost")
DB_PORT = int(os.getenv("MONGO_PORT", 27017))
DB_USER = os.getenv("MONGO_USER")
DB_PASSWORD = os.getenv("MONGO_PASSWORD")

ES_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")

AUTH_DISABLED = os.getenv("AUTH_DISABLED", "").lower() in ["1", "true", "yes"]
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY", "").replace("\\n", "\n")
