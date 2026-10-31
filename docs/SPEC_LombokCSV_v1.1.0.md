# LombokCSV — SPEC v1.1.0

This document is the normative cross-language contract. Every language port MUST produce byte-identical output for all specified inputs. Deviations from this specification are bugs.

| Attribute | Value |
|---|---|
| SPEC version | 1.1.0 (applies to the `lombokcsv` package 1.1.x) |
| Reference standards | RFC 4180 (October 2005) for the record format; WHATWG HTML Living Standard (reviewed 2026-10-01) for HTML output escaping; ISO 8601-1:2019 for date patterns |
| Vectors | `vectors/lombokcsv-vectors-v1.json` — 152 cases — SHA-256 `83c208af06e530592ff721735dbc6f0ef9814d40d87643679f687a7424c1b420` |
| Reference implementation | TypeScript (`src/csv.ts`) |
| Ports | TypeScript (root), Python (`python/`), Go (`go/`), PHP (`php/`) — all consume the vector file above |
| Review date | 2026-10-01 |

The key words MUST, MUST NOT, SHOULD, MAY are to be interpreted as described in RFC 2119.

## 0. Conventions

1. Input is Unicode text. Ports that operate on bytes MUST decode UTF-8 first; all further processing is specified over characters. Delimiter, quote, CR, LF, SPACE and TAB are ASCII, so results do not depend on the unit chosen (UTF-16 code unit or code point).
2. "Blank" means SPACE (U+0020) and TAB (U+0009) only.
3. "Strip" means removing SPACE, TAB, CR (U+000D) and LF (U+000A) from both ends. Other Unicode whitespace (NBSP, U+FEFF, ...) MUST NOT be removed.
4. Option `delimiter` and `quote` MUST be exactly one UTF-16 code unit in the reference implementation (a single code point no greater than U+FFFF). Ports MUST reject surrogate-pair characters the same way.
5. Vector comparison semantics (normative for every port runner): values are compared structurally — strings byte-exact; numbers by IEEE 754 binary64 equality (an integral-valued double and the corresponding integer are equal; `1001.0 == 1001`); booleans and null by identity; arrays element-wise in order; objects by key sequence (insertion order) and then values, so object key order is part of the contract. The TypeScript runner implements this via `JSON.stringify` canonical form (ECMAScript number formatting, no spaces). Exception: the order of keys that are canonical integer indices (e.g. headers `"0"`, `"12"`) is not normative, because ECMAScript objects always move them to the front; such data MUST be compared as objects and the vectors do not contain it.

## 1. Options

| Option | Default | Rule |
|---|---|---|
| `delimiter` | `,` | MUST be exactly one character, not CR/LF |
| `quote` | `"` | MUST be exactly one character, not CR/LF, and different from `delimiter` |
| `hasHeader` | `true` | first record is the header row |
| `trim` | `true` | remove blanks around unquoted field content (§2.3) |
| `escape` | — | deprecated, MUST be ignored |

Violating an option rule MUST produce an error with code `INVALID_OPTION` when the parser is constructed.

## 2. Records (`parseRows`)

### 2.1 Preprocessing

If the first character of the input is U+FEFF (BOM), that character MUST be removed. U+FEFF anywhere else is ordinary data.

### 2.2 State machine

The parser processes input left to right with four states: `START` (field start), `UNQUOTED`, `QUOTED`, `AFTER_QUOTE`.

| State | Character | Action |
|---|---|---|
| `QUOTED` | quote followed by quote | append one quote to the field, skip two characters |
| `QUOTED` | single quote | move to `AFTER_QUOTE` |
| `QUOTED` | anything else (including CR, LF, delimiter) | append to the field |
| other than `QUOTED` | delimiter | end the field |
| other than `QUOTED` | CR, LF, or the CR LF pair | end the field, then end the record |
| `START` | quote | mark the field *quoted*, move to `QUOTED` |
| `START` | blank and `trim = true` | ignore |
| `START` | anything else | append to the field, move to `UNQUOTED` |
| `UNQUOTED` | anything else (including a quote) | append to the field (a quote inside an unquoted field is literal) |
| `AFTER_QUOTE` | blank and `trim = true` | ignore |
| `AFTER_QUOTE` | anything else | append to the field literally (lenient, not an error) |

End of input: if the state is not `START`, or the running record already has fields, the field and record are ended. An unterminated quote (input ends in `QUOTED`) is not an error: the content gathered so far becomes the field value.

### 2.3 Field values

When a field ends: if `trim = true` and the field is not *quoted*, trailing blanks MUST be removed (leading blanks were already ignored in `START`). Quoted field content MUST be preserved exactly as-is.

### 2.4 Empty lines

A record consisting of exactly one empty unquoted field MUST be dropped (an empty line, including a line holding only blanks when `trim = true`). The line `""` yields a record with one empty field. The line `,` yields two empty fields.

### 2.5 Record length

Records MAY differ in length; the parser MUST NOT pad or truncate fields.

## 3. Header and types (`parse`)

1. With no records: the result is `{headers: absent, rows: [], types: []}` (written as `null` in the vectors).
2. With `hasHeader = true`: the first record becomes `headers`, the rest become `rows`.
3. The number of type columns equals the length of the longest record in `rows` (the header is not counted). With empty `rows`, `types = []`.
4. For each column, inspect the values in the first `TYPE_SAMPLE_ROWS = 10` rows after stripping (§0.3); empty values are skipped.
5. Column type: `number` if all values match the number pattern; otherwise `date` if all match a date pattern; otherwise `boolean` if all match the boolean pattern; otherwise (including a column with no values) `string`.

### 3.1 Patterns (regular expressions; every value must match)

| Type | Pattern |
|---|---|
| number | `^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$` (no `+` sign, no thousands separator, no `NaN`/`Infinity`/hexadecimal) |
| date | `^\d{4}-\d{2}-\d{2}$` · `^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$` · `^\d{1,2}/\d{1,2}/\d{4}$` · `^\d{1,2}-\d{1,2}-\d{4}$` |
| boolean | `^(true|false|yes|no|1|0)$`, case-insensitive |

`\d` means ASCII 0-9 only. Date patterns check shape, not calendar validity.

## 4. HTML (`toHTML`)

The output MUST exactly follow this template (`\n` = LF), with no extra spaces:

```
<table{class}{id}>\n
[<thead>\n<tr>\n(<th>{h}</th>\n)*</tr>\n</thead>\n]     -- only when headers exist and are non-empty
<tbody>\n
(<tr>\n(<td{align}>{v}</td>\n)*</tr>\n)*                -- one <td> per field present in the record
</tbody>\n</table>                                     -- no trailing LF
```

- `{class}` = ` class="<esc(className)>"` when `className` is non-empty; `{id}` = ` id="<esc(id)>"` when `id` is non-empty.
- `{align}` = ` style="text-align: right"` when that column's type is `number`.
- `esc` replaces, in order: `&` with `&amp;`, `<` with `&lt;`, `>` with `&gt;`, `"` with `&quot;`, `'` with `&#39;`. The same function is used for cell content and attribute values.

## 5. Aggregation (`aggregate`)

### 5.1 Column resolution

A column is either a name (string) or an index (number). Names are looked up by exact string comparison in `headers` (first occurrence). An index MUST be an integer with `0 <= i < width`, where width = maximum of the `headers` length and the lengths of the records in `rows`. A missing name, a name when there is no header row, or an index outside that rule MUST produce an `UNKNOWN_COLUMN` error. All columns (`groupBy`, `sum`, `avg`) are resolved before any row is processed.

### 5.2 Output column names

Name of column `i` = `headers[i]` when present, otherwise `col_<i>`.

### 5.3 Grouping and values

1. The group key is the cell value of the `groupBy` column as-is (no stripping, case-sensitive); a missing cell is treated as `""`.
2. Groups appear in first-occurrence order.
3. The numeric value of a cell = the cell stripped and, when it matches the number pattern (§3.1), converted to IEEE 754 binary64 (round to nearest). Cells that do not match are ignored.
4. `<name>_sum` = the sum of the numeric values, added left-to-right in row order, starting from 0.
5. `<name>_avg` = (the sum as in item 4) divided by the count of numeric values; `null` when there are none.
6. `count` = the number of rows in the group (including rows with empty cells).

### 5.4 Output shape

One object per group with keys in order: `<groupBy name>`, then `<name>_sum` for every `sum` column (option order), then `<name>_avg` for every `avg` column, then `count` when `count = true`. When two keys collide, the value written last wins and the key keeps the position of its first write.

## 6. JSON (`toJSON`)

Without a header row: return `rows`. With a header row: one object per row; keys follow the `headers` order; missing cells become `""`; cells beyond the number of headers are dropped; for duplicate header names the last column wins (the key keeps the position of its first occurrence).

## 7. Errors

| Code | When |
|---|---|
| `INVALID_OPTION` | §1 |
| `UNKNOWN_COLUMN` | §5.1 |

Ports MUST expose `code` as the exact string above. The message text is also normative and MUST be byte-identical in every port; it is prefixed with the code in brackets:

| Situation | Canonical message |
|---|---|
| `delimiter` invalid | `[INVALID_OPTION] delimiter must be a single character other than CR/LF` |
| `quote` invalid | `[INVALID_OPTION] quote must be a single character other than CR/LF` |
| `delimiter` equals `quote` | `[INVALID_OPTION] delimiter and quote must differ` |
| unknown column name `<x>` | `[UNKNOWN_COLUMN] unknown column: <x>` |
| column index `<n>` out of range | `[UNKNOWN_COLUMN] column index out of range: <n>` |

In the index message, `<n>` is formatted with the shortest round-trip decimal representation of the binary64 value (`3`, `-1`, `1.5`); programs MUST match on `code`, not on message text.

## 8. Security (normative)

1. The parser MUST run in time linear in the input length and MUST NOT throw for any input (only options can trigger errors).
2. `toHTML` MUST escape every piece of text derived from input or options (§4). The output is safe to insert as element content; it is not designed to be inserted inside `<script>`/`<style>` or unquoted attributes.
3. The library performs no I/O, evaluates nothing, and does not protect against CSV (formula) injection (cells starting with `=`, `+`, `-`, `@`) when data is exported back to a spreadsheet; that is the caller's responsibility.

## 9. Changes from 1.0.0

See `CHANGELOG.md`, section 1.1.0. In short: quoted field content is no longer trimmed; a quote inside an unquoted field is literal; the BOM is removed; date patterns are fully anchored; the `class`/`id` attributes are escaped; unknown columns are errors; `_avg` no longer emits a helper `_count` key and ignores non-numeric cells; group names without a header use `col_<i>`; error messages gained the canonical `[CODE] ` prefix.

## 10. Vectors

- File: `vectors/lombokcsv-vectors-v1.json` — 152 cases (`parseRows` 56, `parse` 39, `aggregate` 20, `toHTML` 15, `error` 13, `toJSON` 9).
- SHA-256: `83c208af06e530592ff721735dbc6f0ef9814d40d87643679f687a7424c1b420` (also pinned in `vectors/SHA256SUMS`).
- Source: `vectors/build_vectors.py` — expected values are hand-written from this SPEC, never copied from an implementation's output; error cases pin the canonical messages of §7.
- Regenerate with `python3 vectors/build_vectors.py`, then `sha256sum vectors/lombokcsv-vectors-v1.json > vectors/SHA256SUMS` and update the hash in this document. CI fails when the file, its source, and `SHA256SUMS` disagree.
- Every port MUST ship a runner that executes every case and compares results with the semantics of §0.5.

---

*Document license: Apache-2.0 · © codinglombok*
