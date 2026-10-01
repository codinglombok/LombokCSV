# Changelog

All notable changes to **LombokCSV** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [1.1.0] — 2026-10-01

Brings the library in line with the Lombok Ecosystem v3.6 standards: a normative
specification, executed shared vectors, and claims that match the code.

### Added
- `docs/SPEC_LombokCSV_v1.1.0.md`: normative contract for parsing, type detection, HTML, JSON and aggregation.
- `vectors/lombokcsv-vectors-v1.json`: 152 hand-written cases, executed by `tests/vectors.test.ts`.
- `trim` option (default `true`, the previous behaviour) to switch to strict RFC 4180 whitespace handling.
- `CSVError` with stable `code` values `INVALID_OPTION` and `UNKNOWN_COLUMN`.
- Exported helpers `detectTypes`, `escapeHTML`, `isNumber`, `isDate`, `isBoolean` and `TYPE_SAMPLE_ROWS`.
- Ten standard documents under `docs/` and `scripts/lombok-doctor.sh`.
- Coverage threshold (90%) and `npm pack --dry-run` in CI; GitHub Actions pinned to commit SHAs.

### Fixed
- Security: `className` and `id` passed to `toHTML` were written into attributes without escaping, allowing attribute injection. They are now escaped, and `'` is escaped as `&#39;` everywhere.
- Quoted field content is no longer trimmed (`" a "` keeps its spaces).
- A quote inside an unquoted field is now literal instead of toggling quote mode.
- A leading byte order mark (U+FEFF) is removed instead of becoming part of the first header.
- Date detection patterns are anchored, so values such as `2026-07-24x` are no longer typed as `date`.
- `aggregate` with an unknown column name used index `-1` and produced `undefined` keys; it now throws `UNKNOWN_COLUMN`. Out-of-range or non-integer indexes throw the same error.
- `aggregate` no longer leaks the internal `<column>_count` key next to `<column>_avg`.
- `sum` and `avg` ignore non-numeric cells instead of reading prefixes (`parseFloat('12abc')` was 12); `avg` is `null` for a group without numbers and is computed as sum / count.
- Without a header row, the group key is named `col_<i>`, matching the names used for `sum` and `avg`.
- `toJSON` fills missing cells with `""` instead of `undefined`.
- Invalid `delimiter` / `quote` options (empty, multi-character, CR/LF, or equal to each other) now throw `INVALID_OPTION`.
- `package-lock.json` was out of sync with `package.json`; development tooling upgraded (vitest 5) so that `npm audit` reports no critical or high findings.

### Corrected claims
- The 1.0.0 entry below listed pivot tables, per-locale number and date formatting, column type overrides, a streaming API, and encoding handling. None of these were implemented. They are kept below for history but marked as not implemented; see the known limitations in `docs/full_summary_project_LombokCSV_v1.1.0.md`.
- The README no longer advertises PyPI, Packagist, or Go packages or unmeasured performance figures.

## [1.0.0] — 2026-08-24

First **stable** release. API is now considered stable under SemVer.

### Added
- Pivot table generation (skill module) — not implemented (corrected in 1.1.0)
- Number & date formatting per locale — not implemented (corrected in 1.1.0)
- Custom column type overrides — not implemented (corrected in 1.1.0)
- Streaming API for multi-million-row files — not implemented (corrected in 1.1.0)
- BOM & encoding handling (UTF-8 / UTF-8-BOM) — not implemented; BOM removal added in 1.1.0
- 90%+ test coverage

### Changed
- Promoted from alpha to stable; public API frozen
- Full CI matrix (Node 18 / 20 / 22)
- GitHub Pages documentation site
- npm provenance publishing

### Fixed
- Edge cases in nested structures surfaced during alpha testing

---

## [0.9.0-alpha] — 2026-07-24

Initial alpha release.

### Added
- RFC 4180-compliant CSV parser (quoting, escaping, delimiters)
- Automatic data-type detection (string, number, date, boolean)
- Semantic HTML table generation
- Basic aggregation (groupBy + sum/count/avg)
- Auto delimiter detection
- ESM + CommonJS builds

### Known limitations (resolved in 1.0.0)
- Alpha API subject to change
- Multi-language ports not yet available

---

[Unreleased]: https://github.com/codinglombok/LombokCSV/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/codinglombok/LombokCSV/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/codinglombok/LombokCSV/releases/tag/v1.0.0
[0.9.0-alpha]: https://github.com/codinglombok/LombokCSV/releases/tag/v0.9.0-alpha
