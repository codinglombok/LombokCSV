# LombokCSV — Guide How to Use v1.1.0

## 1. Installation

```bash
npm install lombokcsv        # TypeScript / JavaScript
pip install lombokcsv        # Python
go get github.com/codinglombok/lombokcsv/go
composer require codinglombok/lombokcsv
```

The packages are published by the `v*` tag flow; until the first tag is pushed, install from source (`npm install github:codinglombok/LombokCSV`, `pip install ./python`, Go/PHP `replace` to a local checkout). See [how_to_dist_](how_to_dist_LombokCSV_v1.1.0.md).

## 2. Reading CSV

```ts
import { CSV } from 'lombokcsv'

const csv = new CSV('City,Population\nMataram,429651\nBima,155140')
csv.getHeaders()  // ['City', 'Population']
csv.getRows()     // [['Mataram', '429651'], ['Bima', '155140']]
csv.getTypes()    // ['string', 'number']
```

Other delimiters and headerless files:

```ts
new CSV('a;b\n1;2', { delimiter: ';' })
new CSV('1\t2\n3\t4', { delimiter: '\t', hasHeader: false })
```

Spaces around unquoted fields are stripped by default; switch to strict RFC 4180 with `trim: false`. Quoted field content is never modified. The same call shapes exist in Python (`CSV(data, CSVOptions(...))`), Go (`NewCSV(data, &CSVOptions{...})`) and PHP (`new Csv($data, [...])`) with identical results (SPEC §0.5).

## 3. HTML tables

```ts
const html = csv.toHTML({ className: 'report striped', id: 'population' })
```

All text is escaped, including the `className` and `id` values. Columns typed `number` get `style="text-align: right"`.

## 4. JSON

```ts
csv.toJSON() // [{ City: 'Mataram', Population: '429651' }, ...]
```

Values stay strings; the caller converts types (use `getTypes()` as the hint). Without a header row the raw rows are returned.

## 5. Aggregation

```ts
const data = new CSV(`Region,Product,Qty
West,Rice,120
West,Corn,80
East,Rice,95`)

data.aggregate({ groupBy: 'Region', sum: ['Qty'], avg: ['Qty'], count: true })
// [
//   { Region: 'West', Qty_sum: 200, Qty_avg: 100, count: 2 },
//   { Region: 'East', Qty_sum: 95,  Qty_avg: 95,  count: 1 }
// ]
```

Cells that are not numbers (empty, `n/a`, `12abc`) are ignored for `sum` and `avg`; `avg` is `null` when a group has no numbers at all. Result objects keep the key order `<groupKey>`, `<col>_sum`, `<col>_avg`, `count` (SPEC §5.4) in every port.

## 6. Usage scenarios

| Scenario | Example |
|---|---|
| Previewing an uploaded file in a web app | render the first 50 rows as an XSS-safe HTML table |
| Static reports | turn a database CSV export into an HTML table in a site generator |
| Sensor / IoT summaries | group CSV logs per device and compute averages |
| Command-line tooling | convert CSV to JSON in a dependency-free script |

## 7. Errors

```ts
try {
  new CSV(text).aggregate({ groupBy: 'Missing' })
} catch (e) {
  e.code     // 'UNKNOWN_COLUMN'  <- match on this
  e.message  // '[UNKNOWN_COLUMN] unknown column: Missing' (identical in every port)
}
```

## 8. Limitations

See [full_summary_](full_summary_project_LombokCSV_v1.1.0.md), section "Known limitations".

---

*Document license: Apache-2.0 · © codinglombok*
