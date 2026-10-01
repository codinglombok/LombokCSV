# LombokCSV

> RFC 4180 CSV parser with column type detection, safe HTML tables, JSON export, and GROUP BY aggregation. Zero runtime dependencies.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/codinglombok/LombokCSV/actions/workflows/ci.yml/badge.svg)](https://github.com/codinglombok/LombokCSV/actions/workflows/ci.yml)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178c6?logo=typescript)](tsconfig.json)
[![Lombok Ecosystem](https://img.shields.io/badge/Lombok-Ecosystem-2e7d5b?logo=github)](https://github.com/codinglombok)

Part of the [Lombok Ecosystem](https://github.com/codinglombok).

## Mengapa library ini? (Why this library?)

- One small package covers the common path from a CSV file to something people can read: parse, detect column types, render an HTML table that is safe against injected markup, export JSON, and summarise with GROUP BY / SUM / COUNT / AVG.
- Behaviour is written down as a normative specification ([SPEC](docs/SPEC_LombokCSV_v1.1.0.md)) and pinned by 152 shared test vectors, so every future language port can be checked for byte-identical results.
- No runtime dependencies, no I/O, no `eval`: it runs the same in Node.js, Deno, Bun, browsers, and edge runtimes.

Typical uses: previewing uploaded files in a web app, turning database exports into static report tables, summarising sensor or device logs, and small command-line conversions.

## Installation

```bash
npm install lombokcsv
```

The package has not been published to npm yet; until then install from GitHub with `npm install github:codinglombok/LombokCSV`.

## Quick start

```ts
import { CSV } from 'lombokcsv'

const csv = new CSV(`Region,Product,Qty
West,Rice,120
West,Corn,80
East,Rice,95`)

csv.getHeaders() // ['Region', 'Product', 'Qty']
csv.getTypes()   // ['string', 'string', 'number']
csv.toJSON()     // [{ Region: 'West', Product: 'Rice', Qty: '120' }, ...]
csv.toHTML({ className: 'report' })

csv.aggregate({ groupBy: 'Region', sum: ['Qty'], avg: ['Qty'], count: true })
// [ { Region: 'West', Qty_sum: 200, Qty_avg: 100, count: 2 },
//   { Region: 'East', Qty_sum: 95,  Qty_avg: 95,  count: 1 } ]
```

## Features

| Feature | Details |
|---|---|
| Parsing | RFC 4180 quoting and doubled quotes, newlines inside quoted fields, CRLF / LF / CR line endings, leading BOM removed, custom delimiter and quote |
| Whitespace | `trim: true` (default) strips spaces and tabs around unquoted fields; quoted content is never changed; `trim: false` gives strict RFC 4180 |
| Type detection | `number`, `date`, `boolean`, `string` per column from the first 10 data rows |
| HTML | `<table>` with `<thead>` / `<tbody>`, numeric columns right-aligned, all text and the `class` / `id` attributes escaped |
| JSON | array of objects keyed by header, or raw rows when there is no header |
| Aggregation | GROUP BY a column name or index with SUM, AVG, COUNT; non-numeric cells are ignored |
| Errors | `CSVError` with a stable `code` (`INVALID_OPTION`, `UNKNOWN_COLUMN`) |

Full API: [docs/API_LombokCSV_v1.1.0.md](docs/API_LombokCSV_v1.1.0.md). Usage guide: [docs/guide_how_to_use_LombokCSV_v1.1.0.md](docs/guide_how_to_use_LombokCSV_v1.1.0.md).

## Language ports

| Language | Status |
|---|---|
| TypeScript / JavaScript | Reference implementation, passes all 152 vectors |
| Python, Go, PHP | Planned (stub README only, no code yet) |

## Known limitations

The whole input is held in memory (no streaming), type detection samples only the first 10 rows, numbers are recognised only with a dot decimal separator, and there is no CSV writer. See [Known limitations](docs/full_summary_project_LombokCSV_v1.1.0.md#2-batasan-yang-diketahui).

## Security

Output escaping and the parser's guarantees are specified in [SPEC section 8](docs/SPEC_LombokCSV_v1.1.0.md#8-keamanan-normatif). Report vulnerabilities as described in [SECURITY.md](SECURITY.md).

## Development

```bash
npm ci
npm run check   # lint, tests with coverage, build, standards check
npm run fuzz    # fuzz the parser
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/development_ide_LombokCSV_v1.1.0.md](docs/development_ide_LombokCSV_v1.1.0.md).

## Related libraries

- [LombokMarkDown](https://github.com/codinglombok/LombokMarkDown) — Markdown to HTML
- [LombokDocx](https://github.com/codinglombok/LombokDocx) — DOCX extraction
- [LombokHTML](https://github.com/codinglombok/LombokHTML) — HTML parsing and sanitising

## License

Apache-2.0. See [LICENSE](LICENSE).
