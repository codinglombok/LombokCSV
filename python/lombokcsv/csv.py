"""LombokCSV - RFC 4180 CSV parser, type detector, HTML table generator, aggregator.

Zero runtime dependencies. Normative behaviour: docs/SPEC_LombokCSV_v<version>.md.
The Python port consumes the same shared vector file as every other port
(vectors/lombokcsv-vectors-v1.json) and must produce byte-identical results.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union

__all__ = [
    "TYPE_SAMPLE_ROWS",
    "CSV",
    "CSVAggregator",
    "CSVData",
    "CSVError",
    "CSVOptions",
    "CSVParser",
    "HTMLOptions",
    "HTMLGenerator",
    "AggregationOptions",
    "detect_types",
    "escape_html",
    "is_boolean",
    "is_date",
    "is_number",
]

TYPE_SAMPLE_ROWS = 10

NUMBER_RE = re.compile(r"^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$", re.ASCII)
DATE_RES = [
    re.compile(r"^\d{4}-\d{2}-\d{2}$", re.ASCII),
    re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$", re.ASCII),
    re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$", re.ASCII),
    re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$", re.ASCII),
]
BOOLEAN_RE = re.compile(r"^(true|false|yes|no|1|0)$", re.ASCII | re.IGNORECASE)

DataType = str

TRAILING_BLANKS = re.compile(r"[ \t]+$")


class CSVError(Exception):
    """Error with a stable, language-neutral `code` (SPEC section 7)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.name = "CSVError"


@dataclass
class CSVOptions:
    """Parser options (SPEC section 1)."""

    delimiter: str = ","
    quote: str = '"'
    has_header: Optional[bool] = None  # default True
    trim: bool = True
    escape: Optional[str] = None  # deprecated, ignored


@dataclass
class CSVData:
    headers: Optional[List[str]] = None
    rows: List[List[str]] = field(default_factory=list)
    types: List[DataType] = field(default_factory=list)


@dataclass
class AggregationOptions:
    group_by: Union[str, int, float]
    sum: Optional[List[Union[str, int, float]]] = None
    avg: Optional[List[Union[str, int, float]]] = None
    count: bool = False


@dataclass
class HTMLOptions:
    class_name: str = ""
    id: str = ""


def is_number(val: str) -> bool:
    return NUMBER_RE.match(val) is not None


def is_date(val: str) -> bool:
    return any(pattern.match(val) is not None for pattern in DATE_RES)


def is_boolean(val: str) -> bool:
    return BOOLEAN_RE.match(val) is not None


def _strip(val: str) -> str:
    """Strips SPACE, TAB, CR and LF from both ends (SPEC section 0.3)."""
    return val.strip(" \t\r\n")


def _single_char(name: str, value: str) -> str:
    # SPEC section 0.4: exactly one UTF-16 code unit, i.e. one code point
    # no greater than U+FFFF, and not CR/LF.
    if len(value) != 1 or ord(value) > 0xFFFF or value in ("\n", "\r"):
        raise CSVError("INVALID_OPTION", f"[INVALID_OPTION] {name} must be a single character other than CR/LF")
    return value


def detect_types(rows: Sequence[Sequence[str]]) -> List[DataType]:
    """Detects one type per column from the first TYPE_SAMPLE_ROWS rows (SPEC section 3)."""
    num_cols = 0
    for r in rows:
        if len(r) > num_cols:
            num_cols = len(r)
    types: List[DataType] = []
    sample = list(rows)[:TYPE_SAMPLE_ROWS]
    for col in range(num_cols):
        any_value = False
        num = date = boolean = True
        for row in sample:
            val = _strip(row[col] if col < len(row) else "")
            if val == "":
                continue
            any_value = True
            if num and not is_number(val):
                num = False
            if date and not is_date(val):
                date = False
            if boolean and not is_boolean(val):
                boolean = False
        if not any_value:
            types.append("string")
        elif num:
            types.append("number")
        elif date:
            types.append("date")
        elif boolean:
            types.append("boolean")
        else:
            types.append("string")
    return types


def escape_html(text: str) -> str:
    """Escapes text for HTML element content and double-quoted attribute values."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


class CSVParser:
    """CSV parser - RFC 4180 records with configurable delimiter and quote."""

    def __init__(self, data: str, options: Optional[CSVOptions] = None) -> None:
        options = options or CSVOptions()
        self.data = data[1:] if data[:1] == "﻿" else data
        self.delimiter = _single_char("delimiter", options.delimiter)
        self.quote = _single_char("quote", options.quote)
        if self.delimiter == self.quote:
            raise CSVError("INVALID_OPTION", "[INVALID_OPTION] delimiter and quote must differ")
        self.trim = options.trim

    def parse(self, has_header: bool = True) -> CSVData:
        rows = self.parse_rows()
        if not rows:
            return CSVData()
        headers = rows.pop(0) if has_header else None
        return CSVData(headers=headers, rows=rows, types=detect_types(rows))

    def parse_rows(self) -> List[List[str]]:
        """Splits the input into records (SPEC section 2)."""
        data, delimiter, quote, trim = self.data, self.delimiter, self.quote, self.trim
        rows: List[List[str]] = []
        row: List[str] = []
        chars: List[str] = []
        quoted = False
        row_quoted = False
        # 0 = field start, 1 = unquoted, 2 = inside quotes, 3 = after closing quote
        state = 0

        def end_field() -> None:
            nonlocal chars, quoted, row_quoted, state
            f = "".join(chars)
            if trim and not quoted:
                f = TRAILING_BLANKS.sub("", f)
            row.append(f)
            row_quoted = row_quoted or quoted
            chars = []
            quoted = False
            state = 0

        def end_record() -> None:
            nonlocal row, row_quoted
            end_field()
            # A line holding a single empty unquoted field is blank and skipped.
            if len(row) > 1 or row[0] != "" or row_quoted:
                rows.append(row)
            row = []
            row_quoted = False

        i = 0
        n = len(data)
        while i < n:
            c = data[i]
            if state == 2:
                if c == quote:
                    if i + 1 < n and data[i + 1] == quote:
                        chars.append(quote)
                        i += 2
                        continue
                    state = 3
                else:
                    chars.append(c)
                i += 1
                continue
            if c == delimiter:
                end_field()
            elif c == "\n" or c == "\r":
                end_record()
                if c == "\r" and i + 1 < n and data[i + 1] == "\n":
                    i += 1
            elif state == 0:
                if c == quote:
                    quoted = True
                    state = 2
                elif not (trim and (c == " " or c == "\t")):
                    chars.append(c)
                    state = 1
            elif state == 3:
                # Lenient: text after a closing quote is appended literally.
                if not (trim and (c == " " or c == "\t")):
                    chars.append(c)
            else:
                chars.append(c)
            i += 1
        if state != 0 or len(row) > 0:
            end_record()
        return rows


class HTMLGenerator:
    """HTML generator - semantic table markup (SPEC section 4)."""

    def __init__(self, data: CSVData) -> None:
        self.data = data

    def generate(self, options: Optional[HTMLOptions] = None) -> str:
        class_attr = f' class="{escape_html(options.class_name)}"' if options and options.class_name else ""
        id_attr = f' id="{escape_html(options.id)}"' if options and options.id else ""

        parts: List[str] = [f"<table{class_attr}{id_attr}>\n"]
        if self.data.headers:
            parts.append("<thead>\n<tr>\n")
            for header in self.data.headers:
                parts.append(f"<th>{escape_html(header)}</th>\n")
            parts.append("</tr>\n</thead>\n")
        parts.append("<tbody>\n")
        for row in self.data.rows:
            parts.append("<tr>\n")
            for i, cell in enumerate(row):
                align = ' style="text-align: right"' if i < len(self.data.types) and self.data.types[i] == "number" else ""
                parts.append(f"<td{align}>{escape_html(cell)}</td>\n")
            parts.append("</tr>\n")
        parts.append("</tbody>\n</table>")
        return "".join(parts)


class CSVAggregator:
    """Aggregator - GROUP BY with SUM / COUNT / AVG (SPEC section 5)."""

    def __init__(self, data: CSVData) -> None:
        self.data = data

    def _width(self) -> int:
        w = len(self.data.headers) if self.data.headers is not None else 0
        for r in self.data.rows:
            if len(r) > w:
                w = len(r)
        return w

    def _resolve(self, col: Union[str, int, float]) -> int:
        if isinstance(col, bool):
            raise CSVError("UNKNOWN_COLUMN", f"[UNKNOWN_COLUMN] column index out of range: {col}")
        if isinstance(col, str):
            idx = -1
            if self.data.headers is not None:
                try:
                    idx = self.data.headers.index(col)
                except ValueError:
                    idx = -1
            if idx < 0:
                raise CSVError("UNKNOWN_COLUMN", f"[UNKNOWN_COLUMN] unknown column: {col}")
            return idx
        if isinstance(col, float):
            if not col.is_integer():
                raise CSVError("UNKNOWN_COLUMN", f"[UNKNOWN_COLUMN] column index out of range: {col}")
            col = int(col)
        if col < 0 or col >= self._width():
            raise CSVError("UNKNOWN_COLUMN", f"[UNKNOWN_COLUMN] column index out of range: {col}")
        return int(col)

    def _name(self, idx: int) -> str:
        if self.data.headers is not None and idx < len(self.data.headers):
            return self.data.headers[idx]
        return f"col_{idx}"

    def aggregate(self, options: AggregationOptions) -> List[Dict[str, Any]]:
        g = self._resolve(options.group_by)
        sums = [self._resolve(c) for c in (options.sum or [])]
        avgs = [self._resolve(c) for c in (options.avg or [])]
        group_name = self._name(g)

        groups: Dict[str, Dict[str, Any]] = {}
        for row in self.data.rows:
            key = row[g] if g < len(row) else ""
            acc = groups.get(key)
            if acc is None:
                acc = {"key": key, "count": 0, "sum": [0.0] * len(sums), "avg_sum": [0.0] * len(avgs), "avg_n": [0] * len(avgs)}
                groups[key] = acc
            acc["count"] += 1
            for k, c in enumerate(sums):
                v = _strip(row[c] if c < len(row) else "")
                if is_number(v):
                    acc["sum"][k] += float(v)
            for k, c in enumerate(avgs):
                v = _strip(row[c] if c < len(row) else "")
                if is_number(v):
                    acc["avg_sum"][k] += float(v)
                    acc["avg_n"][k] += 1

        out: List[Dict[str, Any]] = []
        for acc in groups.values():
            r: Dict[str, Any] = {group_name: acc["key"]}
            for k, c in enumerate(sums):
                r[f"{self._name(c)}_sum"] = acc["sum"][k]
            for k, c in enumerate(avgs):
                r[f"{self._name(c)}_avg"] = None if acc["avg_n"][k] == 0 else acc["avg_sum"][k] / acc["avg_n"][k]
            if options.count:
                r["count"] = acc["count"]
            out.append(r)
        return out


class CSV:
    """Main API combining parser, generator and aggregator."""

    def __init__(self, data: str, options: Optional[CSVOptions] = None) -> None:
        parser = CSVParser(data, options)
        has_header = options.has_header if options is not None and options.has_header is not None else True
        self._data = parser.parse(has_header)

    def to_html(self, options: Optional[HTMLOptions] = None) -> str:
        return HTMLGenerator(self._data).generate(options)

    def aggregate(self, options: AggregationOptions) -> List[Dict[str, Any]]:
        return CSVAggregator(self._data).aggregate(options)

    def get_headers(self) -> Optional[List[str]]:
        return self._data.headers

    def get_rows(self) -> List[List[str]]:
        return self._data.rows

    def get_types(self) -> List[DataType]:
        return self._data.types

    def to_json(self) -> Union[List[Dict[str, str]], List[List[str]]]:
        """Rows as objects keyed by header (SPEC section 6). Missing cells become
        "", extra cells are dropped, and for duplicate header names the last
        column wins. Without a header row the raw rows are returned."""
        headers = self._data.headers
        if headers is None:
            return self._data.rows
        out: List[Dict[str, str]] = []
        for row in self._data.rows:
            obj: Dict[str, str] = {}
            for i, h in enumerate(headers):
                obj[h] = row[i] if i < len(row) else ""
            out.append(obj)
        return out
