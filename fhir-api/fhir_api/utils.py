import datetime
import json
from os import path

from fhirstore.search_engine import ElasticSearchEngine


def write_es_mappings(fhir_release, dest_dir):
    engine = ElasticSearchEngine(fhir_release, None, None)
    mappings = engine.generate_mappings(engine.es_reference_analyzer, engine.es_token_normalizer)
    for resource, mapping in mappings.items():
        data = {
            "resourceType": resource,
            "meta": {
                "lastUpdated": datetime.datetime.now().isoformat(),
                "versionId": fhir_release.name,
            },
            "mapping": mapping,
        }
        path_ = path.join(dest_dir, f"{resource}.mapping.json")
        with open(path_, "w") as fp:
            text = json.dumps(data, indent=2)
            fp.write(text)

    return mappings
