from flask import Blueprint
from subsearch.search import parse_params, parse_comma, process_params, sort_params, include_params

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
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"_summary": ["count"]})
        assert parsed_params == {}
        assert result_size == 100
        assert elements is None
        assert is_summary_count is True
        assert sort is None
        assert include is None

    def test_text_summary(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"_summary": ["text"]})
        assert parsed_params == {}
        assert result_size == 100
        assert elements == ["text", "id", "meta"]
        assert is_summary_count is False
        assert sort is None
        assert include is None

    def test_element(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"_element": ["birthDate"]})
        assert parsed_params == {}
        assert result_size == 100
        assert elements == ["birthDate"]
        assert is_summary_count is False
        assert sort is None
        assert include is None

    def test_elements(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"_element": ["birthDate", "gender"]})
        assert parsed_params == {}
        assert result_size == 100
        assert elements == ["birthDate", "gender"]
        assert is_summary_count is False
        assert offset == 0
        assert sort is None
        assert include is None

    def test_display_size(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"_count": ["2"]})
        assert parsed_params == {}
        assert result_size == 2
        assert elements is None
        assert is_summary_count is False
        assert offset == 0
        assert sort is None
        assert include is None

    def test_result_parameters(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"_count": ["2"], "_summary": ["False"], "_element": ["birthDate,name"]})
        assert parsed_params == {}
        assert result_size == 2
        assert elements == ["birthDate", "name"]
        assert is_summary_count is False
        assert offset == 0
        assert sort is None
        assert include is None

    def test_mix_parameters(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params(
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
        assert result_size == 200
        assert elements == ["text", "id", "meta"]
        assert is_summary_count is False
        assert offset == 0
        assert sort is None
        assert include is None

    def test_mix_params_count(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"language": ["FR", "EN,NL"], "_summary": ["count"]})
        assert parsed_params == {
            "language": ["FR"],
            "multiple": {"language": ["EN", "NL"]},
        }
        assert result_size == 100
        assert elements is None
        assert is_summary_count is True
        assert offset == 0
        assert sort is None
        assert include is None

    def test_mix_params_sort(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"language": ["FR", "EN,NL"], "_sort": ["birthDate"]})
        assert parsed_params == {
            "language": ["FR"],
            "multiple": {"language": ["EN", "NL"]},
        }
        assert result_size == 100
        assert elements is None
        assert is_summary_count is False
        assert offset == 0
        assert sort == ["birthDate"]
        assert include is None

    def test_mix_params_include(self):
        (
            parsed_params,
            result_size,
            elements,
            is_summary_count,
            offset,
            sort,
            include,
        ) = process_params({"language": ["FR", "EN,NL"], "_include": ["medicationrequest:patient"]})
        assert parsed_params == {
            "language": ["FR"],
            "multiple": {"language": ["EN", "NL"]},
        }
        assert result_size == 100
        assert elements is None
        assert is_summary_count is False
        assert offset == 0
        assert sort is None
        assert include == ["patient"]

    def test_sort_param(self):
        sort = sort_params({"_sort": ["birthDate"]})
        assert sort == ["birthDate"]

    def test_sort_param_desc(self):
        sort = sort_params({"_sort": ["-birthDate"]})
        assert sort == [{"birthDate": {"order": "desc"}}]

    def test_sort_param_score(self):
        sort = sort_params({"_sort": ["_score"]})
        assert sort == ["_score"]

    def test_sort_param_score_asc(self):
        sort = sort_params({"_sort": ["-_score"]})
        assert sort == [{"_score": {"order": "asc"}}]

    def test_sort_params(self):
        sort = sort_params({"multiple": {"_sort": ["birthDate", "active"]}})
        assert sort == ["birthDate", "active"]

    def test_sort_params_and_score(self):
        sort = sort_params({"multiple": {"_sort": ["birthDate", "_score"]}})
        assert sort == ["birthDate", "_score"]

    def test_sort_params_desc_and_score(self):
        sort = sort_params({"multiple": {"_sort": ["-birthDate", "_score"]}})
        assert sort == [{"birthDate": {"order": "desc"}}, "_score"]

    def test_sort_params_desc_and_score_asc(self):
        sort = sort_params({"multiple": {"_sort": ["-birthDate", "-_score"]}})
        assert sort == [{"birthDate": {"order": "desc"}}, {"_score": {"order": "asc"}}]

    def test_include_param(self):
        included = include_params({"_include": ["medicationrequest:patient"]})
        assert included == ["patient"]

    def test_include_params(self):
        included = include_params(
            {
                "multiple": {
                    "_include": ["medicationrequest:patient", "medicationrequest:organization"]
                }
            }
        )
        assert included == ["patient", "organization"]
