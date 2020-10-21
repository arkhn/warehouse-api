import os
import re

from flask import jsonify

from fhirstore.search import Bundle
from pysin import search as document_search

from fhir_api.db import get_store
from fhir_api.models.base import BaseResource


class DocumentReference(BaseResource):
    resource = None

    def search(self, query_string=None, params=None):
        """Searchs a resource by calling fhirstore search function"""
        # FIXME cleanup
        if params.get("$search"):
            bundle = Bundle()
            key_word = params.get("$search")
            results, count_dict = document_search(key_word, os.environ.get("DOCUMENTS_PATH"))
            document_names = []
            contexts = []
            for result in results[1:]:  # remove the header
                path, _, context = result
                document_name = re.search(r"\d+\.pdf", path).group(0)
                document_names.append(document_name)
                contexts.append(context)

            store = get_store()
            document_references = store.db[self.resource_type].find(
                {"content.attachment.url": {"$in": document_names}}
            )

            entries = []
            for document_reference, context in zip(document_references, contexts):
                del document_reference["_id"]
                document_reference["description"] = context
                entries.append({"resource": document_reference, "search": {"mode": "match"}})
            bundle.content["entry"] = entries
            bundle.content["total"] = count_dict["nb"]

            return jsonify(bundle.content)
        else:
            return super().search(query_string=query_string, params=params)
