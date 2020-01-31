from flask import Blueprint
from subsearch.search import sub_search, parse_comma

api = Blueprint("api", __name__)


class TestSearch:
    def test_parse_comma_simple(self):
        key_result, element_result = parse_comma("gender", "male")
        assert key_result == "gender"
        assert element_result == ["male"]

    def test_parse_comma_multiple(self):
        key_result, element_result = parse_comma("gender", "female,male")
        assert key_result == "multiple"
        assert element_result == {"gender": ["female", "male"]}

    def test_no_params(self):
        resp = sub_search({})
        assert resp == {}

    def test_one_param_no_comma(self):
        resp = sub_search({"gender": ["female"]})
        assert resp == {"gender": ["female"]}

    def test_one_param_one_comma(self):
        resp = sub_search({"gender": ["female,male"]})
        assert resp == {"multiple": {"gender": ["female", "male"]}}

    def test_one_param_two_entry_no_comma(self):
        resp = sub_search({"name": ["John", "Lena"]})
        assert resp == {"name": ["John", "Lena"]}

    def test_one_param_two_entries_one_comma(self):
        resp = sub_search({"language": ["FR", "EN,NL"]})
        assert resp == {"language": ["FR"], "multiple": {"language": ["EN", "NL"]}}
