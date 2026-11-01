"""Vector runner (GP-11): executes every case in vectors/lombokcsv-vectors-v1.json
against the Python port. Comparison follows SPEC section 0.5: strings byte-exact,
numbers by IEEE 754 binary64 equality (integral doubles equal integers), booleans
and null by identity, arrays element-wise in order, objects by key sequence.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Callable, Dict, List, Optional

import pytest

from lombokcsv import CSV, CSVError, CSVOptions, CSVParser, AggregationOptions, HTMLOptions

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = json.loads((ROOT / "vectors" / "lombokcsv-vectors-v1.json").read_text(encoding="utf-8"))


def compare(got: Any, want: Any, path: str = "$") -> None:
    if isinstance(want, bool) or isinstance(got, bool):
        assert isinstance(got, bool) and isinstance(want, bool), f"{path}: {got!r} != {want!r}"
        assert got is want, f"{path}: {got!r} != {want!r}"
    elif want is None or got is None:
        assert got is None and want is None, f"{path}: {got!r} != {want!r}"
    elif isinstance(want, (int, float)) and isinstance(got, (int, float)):
        assert float(got) == float(want), f"{path}: {got!r} != {want!r}"
    elif isinstance(want, str) and isinstance(got, str):
        assert got == want, f"{path}: {got!r} != {want!r}"
    elif isinstance(want, list) and isinstance(got, list):
        assert len(got) == len(want), f"{path}: length {len(got)} != {len(want)}"
        for i, (g, w) in enumerate(zip(got, want)):
            compare(g, w, f"{path}[{i}]")
    elif isinstance(want, dict) and isinstance(got, dict):
        assert list(got.keys()) == list(want.keys()), (
            f"{path}: key order {list(got.keys())} != {list(want.keys())}"
        )
        for k, w in want.items():
            compare(got[k], w, f"{path}.{k}")
    else:
        raise AssertionError(f"{path}: type mismatch {type(got).__name__} vs {type(want).__name__}")


def build_options(d: Dict[str, Any]) -> CSVOptions:
    kwargs: Dict[str, Any] = {}
    if "delimiter" in d:
        kwargs["delimiter"] = d["delimiter"]
    if "quote" in d:
        kwargs["quote"] = d["quote"]
    if "hasHeader" in d:
        kwargs["has_header"] = d["hasHeader"]
    if "trim" in d:
        kwargs["trim"] = d["trim"]
    return CSVOptions(**kwargs)


def run(fn: str, c: Dict[str, Any]) -> Any:
    opts = build_options(c.get("options") or {})
    if fn == "parseRows":
        return CSVParser(c["input"], opts).parse_rows()
    if fn == "parse":
        r = CSVParser(c["input"], opts).parse(opts.has_header if opts.has_header is not None else True)
        return {"headers": r.headers, "rows": r.rows, "types": r.types}
    if fn == "toHTML":
        h = c.get("html") or {}
        return CSV(c["input"], opts).to_html(HTMLOptions(class_name=h.get("className", ""), id=h.get("id", "")))
    if fn == "toJSON":
        return CSV(c["input"], opts).to_json()
    if fn == "aggregate":
        agg = c["agg"]
        return CSV(c["input"], opts).aggregate(
            AggregationOptions(
                group_by=agg["groupBy"],
                sum=agg.get("sum"),
                avg=agg.get("avg"),
                count=agg.get("count", False),
            )
        )
    raise ValueError(f"unknown fn {fn}")


def test_at_least_100_cases() -> None:
    assert len(DOC["cases"]) >= 100


CASES: List[Dict[str, Any]] = DOC["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_vector(case: Dict[str, Any]) -> None:
    if case["fn"] == "error":
        with pytest.raises(CSVError) as excinfo:
            run(case["call"], case)
        assert excinfo.value.code == case["expected"]["code"]
        assert str(excinfo.value) == case["expected"]["message"]
        return
    compare(run(case["fn"], case), case["expected"])
