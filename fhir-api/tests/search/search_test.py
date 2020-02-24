from flask import Blueprint
from subsearch.search import parse_params, parse_comma, process_params

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
        resp = parse_params({})
        assert resp == {}

    def test_one_param_no_comma(self):
        resp = parse_params({"gender": ["female"]})
        assert resp == {"gender": ["female"]}

    def test_one_param_one_comma(self):
        resp = parse_params({"gender": ["female,male"]})
        assert resp == {"multiple": {"gender": ["female", "male"]}}

    def test_one_param_two_entry_no_comma(self):
        resp = parse_params({"name": ["John", "Lena"]})
        assert resp == {"name": ["John", "Lena"]}

    def test_one_param_two_entries_one_comma(self):
        resp = parse_params({"language": ["FR", "EN,NL"]})
        assert resp == {"language": ["FR"], "multiple": {"language": ["EN", "NL"]}}

    def test_count_summary(self):
        parsed_params, total, elements, count, offset = process_params(
            {"_summary": ["count"]}
        )
        assert parsed_params == {}
        assert total == 100
        assert elements is None
        assert count is True

    def test_text_summary(self):
        parsed_params, total, elements, count, offset = process_params(
            {"_summary": ["text"]}
        )
        assert parsed_params == {}
        assert total == 100
        assert elements == ["text", "id", "meta"]
        assert count is False

    def test_element(self):
        parsed_params, total, elements, count, offset = process_params(
            {"_element": ["birthDate"]}
        )
        assert parsed_params == {}
        assert total == 100
        assert elements == ["birthDate"]
        assert count is False

    def test_elements(self):
        parsed_params, total, elements, count, offset = process_params(
            {"_element": ["birthDate", "gender"]}
        )
        assert parsed_params == {}
        assert total == 100
        assert elements == ["birthDate", "gender"]
        assert count is False
        assert offset == 0

    def test_display_size(self):
        parsed_params, total, elements, count, offset = process_params(
            {"_count": ["2"]}
        )
        assert parsed_params == {}
        assert total == 2
        assert elements is None
        assert count is False
        assert offset == 0

    def test_result_parameters(self):
        parsed_params, total, elements, count, offset = process_params(
            {"_count": ["2"], "_summary": ["False"], "_element": ["birthDate,name"]}
        )
        assert parsed_params == {}
        assert total == 2
        assert elements == ["birthDate", "name"]
        assert count is False
        assert offset == 0

    def test_mix_parameters(self):
        parsed_params, total, elements, count, offset = process_params(
            {
                "language": ["FR", "EN,NL"],
                "_element": ["birthDate", "name"],
                "_count": ["200"],
                "_summary": ["text"],
            }
        )
        assert parsed_params == {
            "language": ["FR"],
            "multiple": {"language": ["EN", "NL"]},
        }
        assert total == 200
        assert elements == ["text", "id", "meta"]
        assert count is False
        assert offset == 0

    def test_mix_params_count(self):
        parsed_params, total, elements, count, offset = process_params(
            {"language": ["FR", "EN,NL"], "_summary": ["count"]}
        )
        assert parsed_params == {
            "language": ["FR"],
            "multiple": {"language": ["EN", "NL"]},
        }
        assert total == 100
        assert elements is None
        assert count is True
        assert offset == 0
