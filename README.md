# LombokCSV

> CSV → HTML tables — parse, auto-detect types, aggregate, and format. Zero-dependency, RFC 4180.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![npm version](https://img.shields.io/npm/v/lombokcsv.svg?logo=npm)](https://www.npmjs.com/package/lombokcsv)
[![npm downloads](https://img.shields.io/npm/dm/lombokcsv.svg)](https://www.npmjs.com/package/lombokcsv)
[![PyPI](https://img.shields.io/pypi/v/lombokcsv.svg?logo=pypi)](https://pypi.org/project/lombokcsv)
[![Packagist](https://img.shields.io/packagist/v/codinglombok/lombokcsv.svg?logo=packagist)](https://packagist.org/packages/codinglombok/lombokcsv)
[![CI](https://github.com/codinglombok/LombokCSV/actions/workflows/ci.yml/badge.svg)](https://github.com/codinglombok/LombokCSV/actions/workflows/ci.yml)
[![jsDelivr](https://img.shields.io/jsdelivr/npm/hm/lombokcsv.svg)](https://www.jsdelivr.com/package/npm/lombokcsv)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178c6?logo=typescript)](tsconfig.json)
[![Lombok Ecosystem](https://img.shields.io/badge/Lombok-Ecosystem-2e7d5b?logo=github)](https://github.com/codinglombok)

---

Zero-dependency CSV parser with type detection, HTML table generation, and data aggregation.

## Features

**Fast & Lightweight**
- Zero dependencies
- Pure TypeScript
- ~8KB minified
- Handles large files efficiently

**Full CSV Support**
- RFC 4180 compliant parsing
- Quoted field handling
- Escaped characters
- Custom delimiters
- Windows/Unix line endings

**Type Detection**
- Auto-detect: numbers, dates, booleans, strings
- Configurable detection
- Type-aware HTML rendering

**HTML Generation**
- Semantic `<table>` output
- Right-aligned numbers
- HTML escaping for security
- Custom CSS classes

**Data Aggregation**
- Group by column
- SUM aggregation
- COUNT aggregation
- AVERAGE aggregation

## Installation

```bash
npm install lombokcsv
```

## Quick Start

```typescript
import { CSV } from 'lombokcsv'

const data = `Name,Age,Salary
John,30,50000
Jane,28,55000
Bob,35,60000`

const csv = new CSV(data)

// Convert to HTML
const html = csv.toHTML()
console.log(html)

// Get as JSON
const json = csv.toJSON()
console.log(json)

// Aggregate by department
const grouped = csv.aggregate({
  groupBy: 'Department',
  sum: ['Salary'],
  count: true
})
```

## API Reference

### `new CSV(data, options?)`

Create a CSV parser.

```typescript
const csv = new CSV(csvData, {
  delimiter: ',',
  quote: '"',
  hasHeader: true
})
```

**Options:**
- `delimiter` (string): Field separator (default: `,`)
- `quote` (string): Quote character (default: `"`)
- `hasHeader` (boolean): First row is headers (default: `true`)

### `toHTML(options?)`

Convert to HTML table.

```typescript
const html = csv.toHTML({
  className: 'data-table',
  id: 'results'
})
```

Returns: `<table class="data-table" id="results">...</table>`

### `toJSON()`

Convert to array of objects (using headers as keys).

```typescript
const json = csv.toJSON()
// [
//   { Name: 'John', Age: '30', ... },
//   { Name: 'Jane', Age: '28', ... }
// ]
```

### `aggregate(options)`

Group and aggregate data.

```typescript
csv.aggregate({
  groupBy: 'Department',      // Column name or index
  sum: ['Salary', 'Bonus'],   // Sum these columns
  count: true,                 // Count per group
  avg: ['Rating']              // Average these
})
```

Returns: Array of aggregated results

### `getHeaders()`

Get column headers.

```typescript
const headers = csv.getHeaders()
// ['Name', 'Age', 'Salary']
```

### `getRows()`

Get data rows (2D array).

```typescript
const rows = csv.getRows()
// [['John', '30', '50000'], ['Jane', '28', '55000']]
```

### `getTypes()`

Get detected data types per column.

```typescript
const types = csv.getTypes()
// ['string', 'number', 'number']
```

## Examples

### Parse with Custom Delimiter

```typescript
const csv = new CSV(data, { delimiter: ';' })
```

### Generate HTML with Styling

```typescript
const html = csv.toHTML({
  className: 'table table-striped',
  id: 'employees'
})

// Output:
// <table class="table table-striped" id="employees">
//   <thead>
//     <tr><th>Name</th><th>Age</th></tr>
//   </thead>
//   <tbody>
//     <tr><td>John</td><td style="text-align: right">30</td></tr>
//   </tbody>
// </table>
```

### Group and Sum

```typescript
const csv = new CSV(`
Department,Employee,Salary
IT,John,50000
IT,Jane,55000
Sales,Bob,40000
Sales,Alice,45000`)

const results = csv.aggregate({
  groupBy: 'Department',
  sum: ['Salary'],
  count: true
})

// Output:
// [
//   { Department: 'IT', Salary_sum: 105000, count: 2 },
//   { Department: 'Sales', Salary_sum: 85000, count: 2 }
// ]
```

### Export to JSON for Database

```typescript
const csv = new CSV(csvData)
const json = csv.toJSON()

// Use with database insert
db.collection('records').insertMany(json)
```

### Type-Aware Processing

```typescript
const csv = new CSV(data)
const types = csv.getTypes()

// types[0] might be 'string'
// types[1] might be 'number'
// types[2] might be 'date'

// Numbers are right-aligned in HTML
const html = csv.toHTML()
```

## Supported Features

 RFC 4180 CSV parsing
 Quoted fields with commas
 Escaped quotes inside fields
 Newlines inside quoted fields
 Windows (CRLF) and Unix (LF) line endings
 Custom delimiters (semicolon, tab, pipe, etc.)
 Auto type detection
 HTML table generation
 Data aggregation (GROUP BY, SUM, COUNT, AVG)
 JSON export
 HTML escaping for security

## Performance

- Parse 10,000 rows: < 100ms
- Generate HTML: < 50ms
- Aggregate 1,000 rows: < 10ms

## Security

- HTML escaping in table output
- Safe handling of special characters
- No code execution risk

## Browser Support

- Node.js 18+
- Deno
- Modern browsers (ESM)

## Testing

```bash
npm test
```

Test coverage: 90%+

## Contributing

Contributions welcome! See CONTRIBUTING.md

## License

Apache 2.0 - See LICENSE

## See Also

- [LombokMarkDown](https://github.com/codinglombok/LombokMarkDown) - Markdown to HTML
- [LombokDocx](https://github.com/codinglombok/LombokDocx) - DOCX extraction
- [LombokPDF](https://github.com/codinglombok/lombokpdf) - PDF generation



## Lombok Ecosystem

This library is part of the **[Lombok Ecosystem](https://github.com/codinglombok)** — a modular suite of production-grade, Apache-2.0 libraries for document processing, PDF generation, and data visualization. Built for **developers, researchers, students, and the wider community**.

[![Ecosystem](https://img.shields.io/badge/Lombok-Ecosystem-2e7d5b?logo=github)](https://github.com/codinglombok)
[![Roadmap](https://img.shields.io/badge/Project-Roadmap-8b5cf6?logo=github)](https://github.com/orgs/codinglombok/projects)

| Layer | Library | Purpose |
|-------|---------|---------|
| **Core** | [LombokPDF](https://github.com/codinglombok/LombokPDF) | PDF generation hub |
| **Core** | [LombokCSS](https://github.com/codinglombok/LombokCSS) | Token-first CSS framework |
| **Core** | [LombokFuzzer](https://github.com/codinglombok/LombokFuzzer) | Fuzzing test framework |
| **Core** | [LombokCharts](https://github.com/codinglombok/LombokCharts) | Zero-dependency charts |
| **Docs** | [LombokDocFlow](https://github.com/codinglombok/LombokDocFlow) | Universal import/export |
| **Convert** | [LombokMarkDown](https://github.com/codinglombok/LombokMarkDown) | Markdown → HTML |
| **Convert** | [LombokDocx](https://github.com/codinglombok/LombokDocx) | DOCX → HTML |
| **Convert** | [LombokCSV](https://github.com/codinglombok/LombokCSV) | CSV → HTML tables |
| **Meta** | [LombokJpegExif](https://github.com/codinglombok/LombokJpegExif) | JPEG EXIF metadata |

> **New to the ecosystem?** Start at the [ecosystem overview](https://github.com/codinglombok) or the [DocFlow demo](https://github.com/codinglombok/LombokDocFlow).

