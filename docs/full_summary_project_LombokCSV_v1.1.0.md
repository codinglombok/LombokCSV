# LombokCSV — Full Summary Project v1.1.0

| Item | Value |
|---|---|
| Description | RFC 4180 CSV parser with type detection, safe HTML tables, JSON export and GROUP BY aggregation; no runtime dependencies |
| Cluster · level | 03.06 Format, Parser & Serialisation · L0 |
| Reference | TypeScript (`src/csv.ts`, ~390 lines) |
| Ports | Python, Go, PHP: implemented, all 152 shared vectors pass |
| Vectors | 152 cases (parseRows 56, parse 39, aggregate 20, toHTML 15, error 13, toJSON 9) · SHA-256 `83c208af...24c1b420` |
| Tests | TypeScript 187 (35 unit + 152 vectors), Python 187, Go 152 vectors + 15 units, PHP 854 vector checks + 51 api checks · branch coverage TS 97.9%, Python 99%, Go 93.1%, PHP gated in CI at 90% |
| Fuzz | lombokfuzzer, mutation mode, 20,000 local executions without crash/hang; 200,000 in CI |
| Registries | npm `lombokcsv` · PyPI `lombokcsv` · Go `github.com/codinglombok/lombokcsv/go` · Packagist `codinglombok/lombokcsv` · GHCR `ghcr.io/codinglombok/lombokcsv` (all pending the `v1.1.0` tag) |
| License | Apache-2.0 |

## 1. Honest gap table vs comparators

| Capability | LombokCSV 1.1.0 | Papa Parse | rust-csv | qsv |
|---|---|---|---|---|
| RFC 4180 (quotes, doubled quotes, newlines in fields) | YES | YES | YES | YES |
| Custom delimiter/quote | YES | YES | YES | YES |
| Automatic delimiter detection | NO | YES | NO | YES (sniff) |
| Streaming / staged large files | NO (whole string in memory) | YES | YES | YES |
| Column type detection | YES (10-row sample) | partial (dynamicTyping) | NO | YES (stats) |
| Safe HTML table | YES | NO | NO | NO |
| GROUP BY + SUM/COUNT/AVG | YES | NO | NO | YES |
| Cross-language contract (SPEC + vectors) | YES (4 ports) | NO | NO | NO |
| Locale number formats (comma decimal) | NO | NO | NO | partial |
| CSV writing/serialisation | NO | YES (unparse) | YES | YES |

Position proven by tests: parse + escaped HTML table + aggregation in one dependency-free package, with a SPEC + vector contract that lets three other languages prove byte-identical behaviour.

## 2. Known limitations

1. The whole input is read as one string; there is no streaming API. The "streaming" and "pivot" claims in CHANGELOG 1.0.0 were never implemented and were corrected in 1.1.0.
2. Type detection only looks at the first 10 rows; a column that changes type after row 10 keeps the sampled type.
3. Numbers are only recognised with a dot decimal separator and no thousands separator.
4. There is no automatic delimiter detection and no CSV writer.
5. There is no protection against CSV (formula) injection when data is exported back to a spreadsheet (SPEC §8).
6. Object key order for integer-index-like names follows the ECMAScript rule (SPEC §0.5).
7. The performance figures once shown in the old README ("10,000 rows < 100 ms") were never measured with a tracked benchmark; they were removed from the README until a benchmark exists.
8. The Go option struct uses pointer fields to distinguish "unset" from an explicitly invalid empty string; other ports use language-native optionals.

## 3. Universal principles (public summary)

| Principle | Status | Evidence |
|---|---|---|
| U1 Standalone | YES | README without ownership claims; neutral scenarios in guide_ §6 |
| U2 Modern | YES | SPEC: RFC 4180, WHATWG HTML, ISO 8601 + review dates |
| U3 Multi-platform | YES | CI matrix: linux/windows/macos for all four ports; TypeScript also runs in Deno/Bun/browsers (pure functions, no Node APIs) |
| U4 Multi-language | YES | 4 ports, all passing the 152 shared vectors in CI |
| U5 Scale range | PARTIAL | no dependencies; no streaming |
| U6 Complete & unique | PARTIAL | gap table above |
| U7 Safe & tested | YES | SPEC §8; fuzz; 152 vectors; coverage 90-99% per port |
| U8 No-coupling ecosystem | YES | 0 mandatory dependencies; no path/file: dependencies |
| U9 International | PARTIAL | Lang_: level E, en + id reserved catalogue |
| U10 License | YES | Apache-2.0, full LICENSE |
| U11 Registry-ready | YES | staged release workflows; tag version gate; dry-run publish |
| U12 Documentation | YES | 10 public documents + 2 internal |
| U13 Confidentiality & clean documents | YES | `lombok-doctor.sh`: 0 emoji, ADR-024 ignore block, privacy scan |

---

*Document license: Apache-2.0 · © codinglombok*
