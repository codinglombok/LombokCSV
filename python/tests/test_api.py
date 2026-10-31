"""Unit tests for the Python port (mirrors the TypeScript unit suite)."""

from __future__ import annotations

import pytest

import lombokcsv
from lombokcsv import CSV, CSVError, CSVOptions, CSVParser, AggregationOptions


def test_version() -> None:
    assert lombokcsv.__version__ == "1.1.0"


def test_parses_simple_csv() -> None:
    csv = CSV("a,b,c\n1,2,3")
    assert csv.get_rows() == [["1", "2", "3"]]


def test_parses_with_headers() -> None:
    csv = CSV("Name,Age,City\nJohn,30,NYC")
    assert csv.get_headers() == ["Name", "Age", "City"]
    assert len(csv.get_rows()) == 1


def test_handles_quoted_fields() -> None:
    csv = CSV('"Name","Age"\n"John Smith",30')
    assert csv.get_headers() == ["Name", "Age"]
    assert csv.get_rows()[0][0] == "John Smith"


def test_handles_commas_inside_quotes() -> None:
    csv = CSV('Name,Address\n"Smith, John","123 Main, Apt 4"')
    assert csv.get_rows()[0][0] == "Smith, John"
    assert csv.get_rows()[0][1] == "123 Main, Apt 4"


def test_handles_newlines_inside_quotes() -> None:
    csv = CSV('Name,Description\n"John","Line 1\nLine 2"')
    assert len(csv.get_rows()) == 1


def test_parses_multiple_rows() -> None:
    csv = CSV("A,B\n1,2\n3,4\n5,6")
    assert len(csv.get_rows()) == 3


def test_detects_types() -> None:
    csv = CSV("Name,Value,Date,Active\nTest,123,2026-01-01,true")
    types = csv.get_types()
    assert types == ["string", "number", "date", "boolean"]


def test_boolean_detection() -> None:
    csv = CSV("b\ntrue\nFALSE\nYes\nno")
    assert csv.get_types() == ["boolean"]


def test_mixed_column_falls_back_to_string() -> None:
    csv = CSV("m\n1\nabc")
    assert csv.get_types() == ["string"]


def test_generates_html() -> None:
    csv = CSV("Name,Age\nJohn,30")
    html = csv.to_html()
    assert "<table>" in html
    assert "<thead>" in html
    assert "<th>Name</th>" in html
    assert '<td style="text-align: right">30</td>' in html


def test_escapes_html_in_content() -> None:
    csv = CSV("Name\n<script>alert(\"xss\")</script>")
    html = csv.to_html()
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_escapes_class_and_id_attributes() -> None:
    csv = CSV("A\n1")
    html = csv.to_html(lombokcsv.HTMLOptions(class_name='data-table', id='t1'))
    assert 'class="data-table"' in html
    assert 'id="t1"' in html
    evil = CSV("A\nx").to_html(lombokcsv.HTMLOptions(class_name='" onclick="alert(1)'))
    assert 'onclick="alert(1)"' not in evil


def test_aggregation_group_by() -> None:
    data = "Department,Employee,Salary\nIT,John,50000\nIT,Jane,55000\nSales,Bob,40000\nSales,Alice,45000"
    csv = CSV(data)
    result = csv.aggregate(AggregationOptions(group_by="Department", sum=["Salary"], count=True))
    by_dept = {r["Department"]: r for r in result}
    assert by_dept["IT"]["Salary_sum"] == 105000
    assert by_dept["Sales"]["Salary_sum"] == 85000
    assert by_dept["IT"]["count"] == 2


def test_aggregation_avg_ignores_non_numeric() -> None:
    csv = CSV("g,v\nx,1\nx,abc\nx,\nx,2")
    result = csv.aggregate(AggregationOptions(group_by="g", sum=["v"], avg=["v"], count=True))
    assert result == [{"g": "x", "v_sum": 3.0, "v_avg": 1.5, "count": 4}]


def test_avg_null_without_numbers() -> None:
    csv = CSV("g,v\nx,abc")
    result = csv.aggregate(AggregationOptions(group_by="g", sum=["v"], avg=["v"]))
    assert result == [{"g": "x", "v_sum": 0, "v_avg": None}]


def test_unknown_column_error() -> None:
    csv = CSV("a,b\n1,2")
    with pytest.raises(CSVError) as excinfo:
        csv.aggregate(AggregationOptions(group_by="Missing", count=True))
    assert excinfo.value.code == "UNKNOWN_COLUMN"
    assert str(excinfo.value) == "[UNKNOWN_COLUMN] unknown column: Missing"


def test_index_out_of_range_error() -> None:
    csv = CSV("a,b\n1,2")
    with pytest.raises(CSVError) as excinfo:
        csv.aggregate(AggregationOptions(group_by=3))
    assert excinfo.value.code == "UNKNOWN_COLUMN"
    assert str(excinfo.value) == "[UNKNOWN_COLUMN] column index out of range: 3"


def test_invalid_option_error() -> None:
    with pytest.raises(CSVError) as excinfo:
        CSV("a,b", CSVOptions(delimiter=""))
    assert excinfo.value.code == "INVALID_OPTION"
    assert str(excinfo.value) == "[INVALID_OPTION] delimiter must be a single character other than CR/LF"


def test_delimiter_equals_quote_error() -> None:
    with pytest.raises(CSVError) as excinfo:
        CSV("a,b", CSVOptions(delimiter='"'))
    assert excinfo.value.code == "INVALID_OPTION"
    assert str(excinfo.value) == "[INVALID_OPTION] delimiter and quote must differ"


def test_json_export() -> None:
    csv = CSV("Name,Age\nJohn,30\nJane,25")
    assert csv.to_json() == [{"Name": "John", "Age": "30"}, {"Name": "Jane", "Age": "25"}]


def test_json_without_header() -> None:
    csv = CSV("1,2\n3,4", lombokcsv.CSVOptions(has_header=False))
    assert csv.to_json() == [["1", "2"], ["3", "4"]]


def test_duplicate_headers_last_wins() -> None:
    csv = CSV("a,a\n1,2")
    assert csv.to_json() == [{"a": "2"}]


def test_missing_cells_fill_empty_string() -> None:
    csv = CSV("a,b\n1")
    assert csv.to_json() == [{"a": "1", "b": ""}]


def test_empty_csv() -> None:
    csv = CSV("")
    assert csv.get_rows() == []
    assert csv.get_headers() is None


def test_windows_line_endings() -> None:
    csv = CSV("A,B\r\n1,2\r\n3,4")
    assert len(csv.get_rows()) == 2


def test_bom_is_removed() -> None:
    csv = CSV("﻿a,b\n1,2")
    assert csv.get_headers() == ["a", "b"]


def test_blank_lines_are_skipped() -> None:
    csv = CSV("a,b\n\n1,2")
    assert csv.get_rows() == [["1", "2"]]


def test_unterminated_quote_is_lenient() -> None:
    parser = CSVParser('"unterminated,x\ny')
    assert parser.parse_rows() == [["unterminated,x\ny"]]


def test_parser_parse_rows_includes_header_row() -> None:
    parser = CSVParser("a,b\n1,2")
    assert parser.parse_rows() == [["a", "b"], ["1", "2"]]


def test_trim_false_keeps_blanks() -> None:
    parser = CSVParser("  a  ,  b  ", CSVOptions(trim=False))
    assert parser.parse_rows() == [["  a  ", "  b  "]]


def test_quoted_content_is_never_trimmed() -> None:
    parser = CSVParser('" a ",b')
    assert parser.parse_rows() == [[" a ", "b"]]


def test_custom_delimiter_and_quote() -> None:
    parser = CSVParser("'a,b',c", CSVOptions(quote="'"))
    assert parser.parse_rows() == [["a,b", "c"]]
    parser2 = CSVParser("a;b;c\n1;2;3", CSVOptions(delimiter=";"))
    assert parser2.parse_rows() == [["a", "b", "c"], ["1", "2", "3"]]


def test_large_csv() -> None:
    rows = "\n".join(f"{i},value_{i}" for i in range(1000))
    csv = CSV(f"ID,Value\n{rows}")
    assert len(csv.get_rows()) == 1000
