# Changelog

All notable changes to **LombokCSV** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [1.1.0] — 2026-10-01

Brings the library in line with the Lombok Ecosystem v3.7 standards: a normative
specification, executed shared vectors, identical behaviour in four languages,
and claims that match the code.

### Added
- Python, Go and PHP ports, all consuming the shared vectors and passing all
  152 cases with byte-identical results before any release tag (`python/`,
  `go/`, `php/` language folders at the repository root; root `composer.json`
  without a version field for Packagist).
- `docs/SPEC_LombokCSV_v1.1.0.md`: normative contract for parsing, type
  detection, HTML, JSON and aggregation, now with the normative vector
  comparison semantics and the canonical error messages.
- `vectors/lombokcsv-vectors-v1.json`: 152 hand-written cases, executed by a
  runner in every port; error cases pin both the stable `code` and the
  canonical `[CODE] message` text.
- Canonical error messages prefixed with the error code (S3): e.g.
  `[UNKNOWN_COLUMN] unknown column: Missing`.
- Exported helpers `detectTypes`, `escapeHTML`, `isNumber`, `isDate`,
  `isBoolean` and `TYPE_SAMPLE_ROWS` (PEP 8 names in Python, namespaced
  functions in PHP, exported functions in Go).
- Go port ships an insertion-ordered `Obj` map so object key order is
  preserved where the contract mandates it.
- Ten standard documents under `docs/` (in English) and
  `scripts/lombok-doctor.sh` (v3.7 D-ENV variant, English messages) plus
  `scripts/bump_version.sh`.
- CI (LombokVector pattern): one job per language folder with OS x runtime
  matrices, `hashFiles` guards, concurrency cancellation, per-port coverage
  gates (TypeScript 95% statements / 90% branches; ports 90%), deterministic
  vector regeneration, doctor, npm audit and fuzzing.
- Release flows: `release.yml` on `v*` tags (npm, PyPI trusted publishing,
  GHCR/Docker Hub image, `go/v*` module tag, GitHub Release bundle with
  SHA256SUMS) and staged `release-npm/pypi/docker.yml` workflow dispatch runs
  with `dry_run=true` default.
- Coverage threshold raised to 95% statements / 90% branches for the reference
  implementation; `npm pack --dry-run` and the fuzz harness run in CI.
- ESLint flat config and Prettier (clean), `.prettierignore` covering the
  generated vector file; container image (`Dockerfile`) whose entrypoint is a
  self-verifying smoke test.
- `scripts/smoke.mjs`: smoke test against the built `dist/` output.

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
- The README no longer advertises unmeasured performance figures; registry statuses are shown as pending until the first tag is published.

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
