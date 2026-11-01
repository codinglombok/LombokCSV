# LombokCSV — API v1.1.0

Public API reference for the `lombokcsv` packages 1.1.0 (TypeScript on npm; Python on PyPI; Go module `github.com/codinglombok/lombokcsv/go`; PHP on Packagist). Normative behaviour lives in the [SPEC](SPEC_LombokCSV_v1.1.0.md); this document describes the calling shapes.

## 1. Exports (TypeScript reference)

| Name | Kind | Summary |
|---|---|---|
| `CSV` | class | main API: parse once, then `toHTML`, `toJSON`, `aggregate`, getters |
| `CSVParser` | class | record parser (SPEC §2) and header/type split (SPEC §3) |
| `HTMLGenerator` | class | HTML table builder from `CSVData` (SPEC §4) |
| `CSVAggregator` | class | GROUP BY + SUM/COUNT/AVG over `CSVData` (SPEC §5) |
| `CSVError` | class | error with `code: CSVErrorCode` and the canonical `[CODE] message` |
| `detectTypes(rows)` | function | per-column types (SPEC §3) |
| `escapeHTML(text)` | function | HTML content and attribute escaping (SPEC §4) |
| `isNumber`, `isDate`, `isBoolean` | functions | SPEC §3.1 patterns |
| `TYPE_SAMPLE_ROWS` | constant | `10` |
| `CSVOptions`, `CSVData`, `DataType`, `AggregationOptions`, `AggregationResult`, `HTMLOptions`, `CSVErrorCode` | types | see §2 |

Name mapping per port: Python uses PEP 8 names (`to_json`, `get_headers`, `class_name`, `has_header`); PHP keeps the camelCase method names in the `CodingLombok\LombokCSV` namespace (`Csv`, `CsvParser`, `HtmlGenerator`, `CsvAggregator`, `CsvError`); Go exports `NewCSV`, `CSVParser`, `HTMLGenerator`, `CSVAggregator`, `CSVError`, `DetectTypes`, `EscapeHTML`, `IsNumber`, `IsDate`, `IsBoolean`, `Obj`.

## 2. Types

```ts
type DataType = 'string' | 'number' | 'date' | 'boolean'

interface CSVOptions {
  delimiter?: string   // default ','
  quote?: string       // default '"'
  hasHeader?: boolean  // default true
  trim?: boolean       // default true (new in 1.1.0)
  escape?: string      // deprecated, ignored
}

interface CSVData { headers?: string[]; rows: string[][]; types: DataType[] }

interface AggregationOptions {
  groupBy: number | string
  sum?: (number | string)[]
  avg?: (number | string)[]
  count?: boolean
}

type AggregationResult = { [key: string]: string | number | null }
interface HTMLOptions { className?: string; id?: string }
type CSVErrorCode = 'INVALID_OPTION' | 'UNKNOWN_COLUMN'
```

Go maps optional fields to pointers (`Delimiter *string`, `HasHeader *bool`, ...; `nil` means default; an explicit empty `Delimiter`/`Quote` is invalid) and returns ordered `*Obj` objects where the contract mandates key order.

## 3. Class `CSV`

| Member | Result | Notes |
|---|---|---|
| `new CSV(data: string, options?: CSVOptions)` | — | throws `CSVError('INVALID_OPTION')` for invalid options |
| `getHeaders()` | `string[] \| undefined` | `undefined` when `hasHeader: false` or empty input |
| `getRows()` | `string[][]` | data rows without the header |
| `getTypes()` | `DataType[]` | one per column |
| `toHTML(options?: HTMLOptions)` | `string` | `className`/`id` are escaped |
| `toJSON()` | `Record<string,string>[] \| string[][]` | objects per row when a header exists |
| `aggregate(options: AggregationOptions)` | `AggregationResult[]` | throws `CSVError('UNKNOWN_COLUMN')` |

## 4. Lower-level classes

```ts
const parser = new CSVParser(text, { delimiter: ';', trim: false })
parser.parseRows()        // string[][] - all records, including the header
parser.parse(true)        // CSVData - header split, types detected

new HTMLGenerator(data).generate({ className: 'report' })
new CSVAggregator(data).aggregate({ groupBy: 0, count: true })
```

## 5. Errors

```ts
import { CSV, CSVError } from 'lombokcsv'
try {
  new CSV(text).aggregate({ groupBy: 'Region', count: true })
} catch (e) {
  if (e instanceof CSVError && e.code === 'UNKNOWN_COLUMN') { /* ... */ }
}
```

Programs MUST match on `code`, not on the message text. The message itself is normative and starts with the code in brackets (SPEC §7), e.g. `[UNKNOWN_COLUMN] unknown column: Region`.

## 6. Compatibility with 1.0.0

The signatures of all 1.0.0 members are unchanged. Behaviour changes (bug fixes) are recorded in `CHANGELOG.md` 1.1.0 and SPEC §9. The `rows` type was narrowed from `any[][]` to `string[][]`, and error messages gained the `[CODE] ` prefix.

---

*Document license: Apache-2.0 · © codinglombok*
