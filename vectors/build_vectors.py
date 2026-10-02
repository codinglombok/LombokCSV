#!/usr/bin/env python3
"""Builds vectors/lombokcsv-vectors-v1.json from hand-written cases.

Every expected value below is written by hand from SPEC_LombokCSV, never produced
by running an implementation (GP-11). After editing, run:

    python3 vectors/build_vectors.py
    sha256sum vectors/lombokcsv-vectors-v1.json > vectors/SHA256SUMS

and update the hash in docs/SPEC_LombokCSV_v<version>.md.
"""
import json
import pathlib

cases = []


def add(fn, input, expected, options=None, **extra):
    case = {"id": f"{fn}-{sum(1 for c in cases if c['fn'] == fn) + 1:03d}", "fn": fn, "input": input}
    if options:
        case["options"] = options
    case.update(extra)
    case["expected"] = expected
    cases.append(case)


# --- §2 records: parseRows(input, options) -> string[][] ---------------------
R = "parseRows"
add(R, "", [])
add(R, "a", [["a"]])
add(R, "a,b,c", [["a", "b", "c"]])
add(R, "a,b\n1,2", [["a", "b"], ["1", "2"]])
add(R, "a,b\r\n1,2\r\n", [["a", "b"], ["1", "2"]])
add(R, "a,b\r1,2", [["a", "b"], ["1", "2"]])
add(R, "a,b\n\n1,2", [["a", "b"], ["1", "2"]])
add(R, "a,b\n\n\n", [["a", "b"]])
add(R, "\n\na", [["a"]])
add(R, "a,b\n", [["a", "b"]])
add(R, "a,,c", [["a", "", "c"]])
add(R, ",", [["", ""]])
add(R, ",,\n,,", [["", "", ""], ["", "", ""]])
add(R, "a,b,", [["a", "b", ""]])
add(R, '"a"', [["a"]])
add(R, '""', [[""]])
add(R, '"",""', [["", ""]])
add(R, 'a\n""\nb', [["a"], [""], ["b"]])
add(R, '"a,b",c', [["a,b", "c"]])
add(R, '"line1\nline2",x', [["line1\nline2", "x"]])
add(R, '"line1\r\nline2"', [["line1\r\nline2"]])
add(R, '"say ""hi"""', [['say "hi"']])
add(R, '""""', [['"']])
add(R, '"a""b",c', [['a"b', "c"]])
add(R, 'ab"c,d', [['ab"c', "d"]])
add(R, 'a"b"c', [['a"b"c']])
add(R, '"ab"c,d', [["abc", "d"]])
add(R, '"unterminated,x\ny', [["unterminated,x\ny"]])
add(R, '"a",', [["a", ""]])
add(R, '"a"\n', [["a"]])
add(R, "﻿a,b\n1,2", [["a", "b"], ["1", "2"]])
add(R, "a,﻿b", [["a", "﻿b"]])
add(R, "  a  ,  b  ", [["a", "b"]])
add(R, "\ta\t,\tb", [["a", "b"]])
add(R, "  a  ,  b  ", [["  a  ", "  b  "]], {"trim": False})
add(R, '  "a"  ,b', [["a", "b"]])
add(R, '" a ",b', [[" a ", "b"]])
add(R, '" a ",b', [[" a ", "b"]], {"trim": False})
add(R, '  "a"  ,b', [['  "a"  ', "b"]], {"trim": False})
add(R, "a b,c  d", [["a b", "c  d"]])
add(R, "   \n a", [["a"]])
add(R, "   \n a", [["   "], [" a"]], {"trim": False})
add(R, "a;b;c\n1;2;3", [["a", "b", "c"], ["1", "2", "3"]], {"delimiter": ";"})
add(R, "a,b;c", [["a,b", "c"]], {"delimiter": ";"})
add(R, "a\tb\n1\t2", [["a", "b"], ["1", "2"]], {"delimiter": "\t"})
add(R, "a\t\tb", [["a", "", "b"]], {"delimiter": "\t"})
add(R, "a|b|c", [["a", "b", "c"]], {"delimiter": "|"})
add(R, "'a,b',c", [["a,b", "c"]], {"quote": "'"})
add(R, "'it''s',x", [["it's", "x"]], {"quote": "'"})
add(R, '"a,b",c', [['"a', 'b"', "c"]], {"quote": "'"})
add(R, "é,ü\n日本,語", [["é", "ü"], ["日本", "語"]])
add(R, "😀,x", [["😀", "x"]])
add(R, "a,b\n1", [["a", "b"], ["1"]])
add(R, "a\n1,2,3", [["a"], ["1", "2", "3"]])
add(R, "\r\n\r\n", [])
add(R, "x\r\r\ny", [["x"], ["y"]])

# --- §2.4 option errors ------------------------------------------------------
E = "error"
add(E, "a,b", {"code": "INVALID_OPTION"}, {"delimiter": ""}, call="parseRows")
add(E, "a,b", {"code": "INVALID_OPTION"}, {"delimiter": ";;"}, call="parseRows")
add(E, "a,b", {"code": "INVALID_OPTION"}, {"delimiter": "\n"}, call="parseRows")
add(E, "a,b", {"code": "INVALID_OPTION"}, {"quote": "\r"}, call="parseRows")
add(E, "a,b", {"code": "INVALID_OPTION"}, {"delimiter": '"'}, call="parseRows")
add(E, "a,b", {"code": "INVALID_OPTION"}, {"quote": ""}, call="parseRows")

# --- §3 types: parse(input, options) -> {headers, rows, types} ---------------
P = "parse"
add(P, "", {"headers": None, "rows": [], "types": []})
add(P, "Name,Age\nJohn,30", {"headers": ["Name", "Age"], "rows": [["John", "30"]], "types": ["string", "number"]})
add(P, "Name,Age", {"headers": ["Name", "Age"], "rows": [], "types": []})
add(P, "1,2\n3,4", {"headers": None, "rows": [["1", "2"], ["3", "4"]], "types": ["number", "number"]}, {"hasHeader": False})
add(P, "h\n-1\n2.5\n.5\n3.\n1e10\n-2E-3", {"headers": ["h"], "rows": [["-1"], ["2.5"], [".5"], ["3."], ["1e10"], ["-2E-3"]], "types": ["number"]})
add(P, "h\n+1", {"headers": ["h"], "rows": [["+1"]], "types": ["string"]})
add(P, "h\n1,5", {"headers": ["h"], "rows": [["1", "5"]], "types": ["number", "number"]})
add(P, "h\n1.000,5", {"headers": ["h"], "rows": [["1.000", "5"]], "types": ["number", "number"]})
add(P, "h\n0x1F", {"headers": ["h"], "rows": [["0x1F"]], "types": ["string"]})
add(P, "h\nInfinity", {"headers": ["h"], "rows": [["Infinity"]], "types": ["string"]})
add(P, "h\nNaN", {"headers": ["h"], "rows": [["NaN"]], "types": ["string"]})
add(P, "h\n-", {"headers": ["h"], "rows": [["-"]], "types": ["string"]})
add(P, "h\n.", {"headers": ["h"], "rows": [["."]], "types": ["string"]})
add(P, "h\n1e", {"headers": ["h"], "rows": [["1e"]], "types": ["string"]})
add(P, "d\n2026-07-24", {"headers": ["d"], "rows": [["2026-07-24"]], "types": ["date"]})
add(P, "d\n2026-07-24T10:30", {"headers": ["d"], "rows": [["2026-07-24T10:30"]], "types": ["date"]})
add(P, "d\n2026-07-24 10:30:15.250Z", {"headers": ["d"], "rows": [["2026-07-24 10:30:15.250Z"]], "types": ["date"]})
add(P, "d\n2026-07-24T10:30:00+07:00", {"headers": ["d"], "rows": [["2026-07-24T10:30:00+07:00"]], "types": ["date"]})
add(P, "d\n24/07/2026\n7/4/2026", {"headers": ["d"], "rows": [["24/07/2026"], ["7/4/2026"]], "types": ["date"]})
add(P, "d\n24-07-2026", {"headers": ["d"], "rows": [["24-07-2026"]], "types": ["date"]})
add(P, "d\n2026-07-24x", {"headers": ["d"], "rows": [["2026-07-24x"]], "types": ["string"]})
add(P, "d\n2026-7-24", {"headers": ["d"], "rows": [["2026-7-24"]], "types": ["string"]})
add(P, "d\n2026-07-24\n2026-07-25T08:00", {"headers": ["d"], "rows": [["2026-07-24"], ["2026-07-25T08:00"]], "types": ["date"]})
add(P, "b\ntrue\nFALSE\nYes\nno", {"headers": ["b"], "rows": [["true"], ["FALSE"], ["Yes"], ["no"]], "types": ["boolean"]})
add(P, "b\n1\n0", {"headers": ["b"], "rows": [["1"], ["0"]], "types": ["number"]})
add(P, "b\n1\nyes", {"headers": ["b"], "rows": [["1"], ["yes"]], "types": ["boolean"]})
add(P, "b\ny\nn", {"headers": ["b"], "rows": [["y"], ["n"]], "types": ["string"]})
add(P, "m\n1\nabc", {"headers": ["m"], "rows": [["1"], ["abc"]], "types": ["string"]})
add(P, "m\n1\n2026-01-01", {"headers": ["m"], "rows": [["1"], ["2026-01-01"]], "types": ["string"]})
add(P, "e\n\n", {"headers": ["e"], "rows": [], "types": []})
add(P, "a,b\n,1\n,2", {"headers": ["a", "b"], "rows": [["", "1"], ["", "2"]], "types": ["string", "number"]})
add(P, 'a\n" 7 "', {"headers": ["a"], "rows": [[" 7 "]], "types": ["number"]})
add(P, "a\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\nx",
    {"headers": ["a"], "rows": [[str(i)] for i in range(1, 11)] + [["x"]], "types": ["number"]})
add(P, "a\nx\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10",
    {"headers": ["a"], "rows": [["x"]] + [[str(i)] for i in range(1, 11)], "types": ["string"]})
add(P, "a,b,c\n1\n2,x", {"headers": ["a", "b", "c"], "rows": [["1"], ["2", "x"]], "types": ["number", "string"]})
add(P, "a\n1,2,3", {"headers": ["a"], "rows": [["1", "2", "3"]], "types": ["number", "number", "number"]})
add(P, "Name,Value,Date,Active\nTest,123,2026-01-01,true",
    {"headers": ["Name", "Value", "Date", "Active"], "rows": [["Test", "123", "2026-01-01", "true"]],
     "types": ["string", "number", "date", "boolean"]})
add(P, "x;y\n1;a", {"headers": ["x", "y"], "rows": [["1", "a"]], "types": ["number", "string"]}, {"delimiter": ";"})
add(P, "x\n  42  ", {"headers": ["x"], "rows": [["  42  "]], "types": ["number"]}, {"trim": False})

# --- §4 HTML: toHTML(input, options, html) -> string -------------------------
H = "toHTML"
add(H, "A\n1", "<table>\n<thead>\n<tr>\n<th>A</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style=\"text-align: right\">1</td>\n</tr>\n</tbody>\n</table>")
add(H, "Name,Age\nJohn,30",
    "<table>\n<thead>\n<tr>\n<th>Name</th>\n<th>Age</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>John</td>\n"
    "<td style=\"text-align: right\">30</td>\n</tr>\n</tbody>\n</table>")
add(H, "", "<table>\n<tbody>\n</tbody>\n</table>")
add(H, "A,B", "<table>\n<thead>\n<tr>\n<th>A</th>\n<th>B</th>\n</tr>\n</thead>\n<tbody>\n</tbody>\n</table>")
add(H, "1,x", "<table>\n<tbody>\n<tr>\n<td style=\"text-align: right\">1</td>\n<td>x</td>\n</tr>\n</tbody>\n</table>",
    {"hasHeader": False})
add(H, "A\n<script>alert(\"x\")</script>",
    "<table>\n<thead>\n<tr>\n<th>A</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n"
    "<td>&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;</td>\n</tr>\n</tbody>\n</table>")
add(H, "<b>&amp;'\nv",
    "<table>\n<thead>\n<tr>\n<th>&lt;b&gt;&amp;amp;&#39;</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>v</td>\n</tr>\n</tbody>\n</table>")
add(H, "A\n1", "<table class=\"data-table\" id=\"t1\">\n<thead>\n<tr>\n<th>A</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n"
    "<td style=\"text-align: right\">1</td>\n</tr>\n</tbody>\n</table>", html={"className": "data-table", "id": "t1"})
add(H, "A\nx", "<table class=\"&quot; onclick=&quot;alert(1)\">\n<thead>\n<tr>\n<th>A</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n"
    "<td>x</td>\n</tr>\n</tbody>\n</table>", html={"className": "\" onclick=\"alert(1)"})
add(H, "A\nx", "<table id=\"a&#39;b&lt;\">\n<thead>\n<tr>\n<th>A</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n"
    "<td>x</td>\n</tr>\n</tbody>\n</table>", html={"id": "a'b<"})
add(H, "A\nx", "<table>\n<thead>\n<tr>\n<th>A</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>x</td>\n</tr>\n</tbody>\n</table>",
    html={"className": "", "id": ""})
add(H, "A,B\n1\n2,3",
    "<table>\n<thead>\n<tr>\n<th>A</th>\n<th>B</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style=\"text-align: right\">1</td>\n</tr>\n"
    "<tr>\n<td style=\"text-align: right\">2</td>\n<td style=\"text-align: right\">3</td>\n</tr>\n</tbody>\n</table>")
add(H, "A,B\n,x",
    "<table>\n<thead>\n<tr>\n<th>A</th>\n<th>B</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td></td>\n<td>x</td>\n</tr>\n</tbody>\n</table>")
add(H, 'A\n"l1\nl2"',
    "<table>\n<thead>\n<tr>\n<th>A</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>l1\nl2</td>\n</tr>\n</tbody>\n</table>")
add(H, "D\n2026-01-01",
    "<table>\n<thead>\n<tr>\n<th>D</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>2026-01-01</td>\n</tr>\n</tbody>\n</table>")

# --- §6 JSON: toJSON(input, options) -> object[] | string[][] ----------------
J = "toJSON"
add(J, "Name,Age\nJohn,30\nJane,25", [{"Name": "John", "Age": "30"}, {"Name": "Jane", "Age": "25"}])
add(J, "1,2\n3,4", [["1", "2"], ["3", "4"]], {"hasHeader": False})
add(J, "a,b\n1", [{"a": "1", "b": ""}])
add(J, "a\n1,2", [{"a": "1"}])
add(J, "a,a\n1,2", [{"a": "2"}])
add(J, "a,b", [])
add(J, "", [])
add(J, "k\n\"x,y\"", [{"k": "x,y"}])
add(J, ",b\n1,2", [{"": "1", "b": "2"}])

# --- §5 aggregation: aggregate(input, options, agg) -> object[] --------------
A = "aggregate"
D = "Department,Employee,Salary\nIT,John,50000\nIT,Jane,55000\nSales,Bob,40000\nSales,Alice,45000"
add(A, D, [{"Department": "IT", "count": 2}, {"Department": "Sales", "count": 2}], agg={"groupBy": 0, "count": True})
add(A, D, [{"Department": "IT", "Salary_sum": 105000}, {"Department": "Sales", "Salary_sum": 85000}],
    agg={"groupBy": "Department", "sum": ["Salary"]})
add(A, D, [{"Department": "IT", "Salary_avg": 52500}, {"Department": "Sales", "Salary_avg": 42500}],
    agg={"groupBy": "Department", "avg": ["Salary"]})
add(A, D, [{"Department": "IT", "Salary_sum": 105000, "Salary_avg": 52500, "count": 2},
           {"Department": "Sales", "Salary_sum": 85000, "Salary_avg": 42500, "count": 2}],
    agg={"groupBy": "Department", "sum": ["Salary"], "avg": [2], "count": True})
add(A, D, [{"Department": "IT"}, {"Department": "Sales"}], agg={"groupBy": "Department"})
add(A, "g,v\nb,1\na,2\nb,3", [{"g": "b", "v_sum": 4}, {"g": "a", "v_sum": 2}], agg={"groupBy": "g", "sum": ["v"]})
add(A, "g,v\nx,1\nx,abc\nx,\nx,2", [{"g": "x", "v_sum": 3, "v_avg": 1.5, "count": 4}],
    agg={"groupBy": "g", "sum": ["v"], "avg": ["v"], "count": True})
add(A, "g,v\nx,abc", [{"g": "x", "v_sum": 0, "v_avg": None}], agg={"groupBy": "g", "sum": ["v"], "avg": ["v"]})
add(A, "g,v\nx,12abc", [{"g": "x", "v_sum": 0}], agg={"groupBy": "g", "sum": ["v"]})
add(A, "g,v\nx,1.5\nx,-0.5\nx,1e3", [{"g": "x", "v_sum": 1001}], agg={"groupBy": "g", "sum": ["v"]})
add(A, "g,v\nx,1\nx,2\nx,2", [{"g": "x", "v_avg": 1.6666666666666667}], agg={"groupBy": "g", "avg": ["v"]})
add(A, "g,v\nx,0.1\nx,0.2", [{"g": "x", "v_sum": 0.30000000000000004}], agg={"groupBy": "g", "sum": ["v"]})
add(A, "g,v\n,1\na,2\n,3", [{"g": "", "count": 2}, {"g": "a", "count": 1}], agg={"groupBy": "g", "count": True})
add(A, "g,v\na\na,5", [{"g": "a", "v_sum": 5, "count": 2}], agg={"groupBy": 0, "sum": [1], "count": True})
add(A, "a,1\nb,2\na,3", [{"col_0": "a", "col_1_sum": 4}, {"col_0": "b", "col_1_sum": 2}],
    {"hasHeader": False}, agg={"groupBy": 0, "sum": [1]})
add(A, "g,v\nA,1\na,2", [{"g": "A", "count": 1}, {"g": "a", "count": 1}], agg={"groupBy": "g", "count": True})
add(A, "g,v\n\" a\",1\na,2", [{"g": " a", "count": 1}, {"g": "a", "count": 1}], agg={"groupBy": "g", "count": True})
add(A, "g,v\nx, 7 ", [{"g": "x", "v_sum": 7}], {"trim": False}, agg={"groupBy": "g", "sum": ["v"]})
add(A, "g,v", [], agg={"groupBy": "g", "count": True})
add(A, "g,v\nx,1", [{"g": "x", "v_sum": 1}], agg={"groupBy": "g", "sum": ["v"], "count": False})

add(E, D, {"code": "UNKNOWN_COLUMN"}, call="aggregate", agg={"groupBy": "Missing", "count": True})
add(E, D, {"code": "UNKNOWN_COLUMN"}, call="aggregate", agg={"groupBy": 0, "sum": ["Missing"]})
add(E, D, {"code": "UNKNOWN_COLUMN"}, call="aggregate", agg={"groupBy": 0, "avg": ["Missing"]})
add(E, D, {"code": "UNKNOWN_COLUMN"}, call="aggregate", agg={"groupBy": 3})
add(E, D, {"code": "UNKNOWN_COLUMN"}, call="aggregate", agg={"groupBy": -1})
add(E, D, {"code": "UNKNOWN_COLUMN"}, call="aggregate", agg={"groupBy": 1.5})
add(E, "1,2", {"code": "UNKNOWN_COLUMN"}, {"hasHeader": False}, call="aggregate", agg={"groupBy": "1"})

doc = {
    "name": "lombokcsv-vectors",
    "version": 1,
    "spec": "docs/SPEC_LombokCSV (sections 2-6)",
    "functions": {
        "parseRows": "CSVParser(input, options).parseRows() -> string[][]",
        "parse": "CSVParser(input, options).parse(options.hasHeader ?? true) -> {headers|null, rows, types}",
        "toHTML": "CSV(input, options).toHTML(case.html) -> string",
        "toJSON": "CSV(input, options).toJSON()",
        "aggregate": "CSV(input, options).aggregate(case.agg)",
        "error": "case.call raises an error whose code equals expected.code",
    },
    "cases": cases,
}
out = pathlib.Path(__file__).with_name("lombokcsv-vectors-v1.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"{len(cases)} cases -> {out}")
