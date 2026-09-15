# Changelog

All notable changes to **LombokCSV** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Python port (`lombokcsv` on PyPI)
- PHP port (`codinglombok/csv` on Packagist)
- Go port
- Performance benchmarks published to `benchmarks/`

---

## [1.0.0] — 2026-08-24

First **stable** release. API is now considered stable under SemVer.

### Added
- Pivot table generation (skill module)
- Number & date formatting per locale
- Custom column type overrides
- Streaming API for multi-million-row files
- BOM & encoding handling (UTF-8 / UTF-8-BOM)
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

[Unreleased]: https://github.com/codinglombok/LombokCSV/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/codinglombok/LombokCSV/releases/tag/v1.0.0
[0.9.0-alpha]: https://github.com/codinglombok/LombokCSV/releases/tag/v0.9.0-alpha
