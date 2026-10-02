# LombokCSV — API v1.1.0

Referensi API publik paket npm `lombokcsv` 1.1.0 (TypeScript, ESM + CommonJS). Perilaku normatif ada di [SPEC_](SPEC_LombokCSV_v1.1.0.md); dokumen ini menjelaskan bentuk pemanggilan.

## 1. Ekspor

| Nama | Jenis | Ringkas |
|---|---|---|
| `CSV` | kelas | API utama: parse sekali, lalu `toHTML`, `toJSON`, `aggregate`, getter |
| `CSVParser` | kelas | parser record (SPEC §2) dan header/tipe (SPEC §3) |
| `HTMLGenerator` | kelas | pembuat tabel HTML dari `CSVData` (SPEC §4) |
| `CSVAggregator` | kelas | GROUP BY + SUM/COUNT/AVG dari `CSVData` (SPEC §5) |
| `CSVError` | kelas | error dengan `code: CSVErrorCode` |
| `detectTypes(rows)` | fungsi | tipe per kolom (SPEC §3) |
| `escapeHTML(text)` | fungsi | escaping isi dan atribut HTML (SPEC §4) |
| `isNumber`, `isDate`, `isBoolean` | fungsi | pola SPEC §3.1 |
| `TYPE_SAMPLE_ROWS` | konstanta | `10` |
| `CSVOptions`, `CSVData`, `DataType`, `AggregationOptions`, `AggregationResult`, `HTMLOptions`, `CSVErrorCode` | tipe | lihat §2 |

## 2. Tipe

```ts
type DataType = 'string' | 'number' | 'date' | 'boolean'

interface CSVOptions {
  delimiter?: string   // bawaan ','
  quote?: string       // bawaan '"'
  hasHeader?: boolean  // bawaan true
  trim?: boolean       // bawaan true (baru di 1.1.0)
  escape?: string      // usang, diabaikan
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

## 3. Kelas `CSV`

| Anggota | Hasil | Catatan |
|---|---|---|
| `new CSV(data: string, options?: CSVOptions)` | — | melempar `CSVError('INVALID_OPTION')` untuk opsi tidak sah |
| `getHeaders()` | `string[] \| undefined` | `undefined` bila `hasHeader: false` atau masukan kosong |
| `getRows()` | `string[][]` | baris data tanpa header |
| `getTypes()` | `DataType[]` | satu per kolom |
| `toHTML(options?: HTMLOptions)` | `string` | `className`/`id` di-escape |
| `toJSON()` | `Record<string,string>[] \| string[][]` | objek per baris bila ada header |
| `aggregate(options: AggregationOptions)` | `AggregationResult[]` | melempar `CSVError('UNKNOWN_COLUMN')` |

## 4. Kelas tingkat rendah

```ts
const parser = new CSVParser(text, { delimiter: ';', trim: false })
parser.parseRows()        // string[][] - semua record, termasuk header
parser.parse(true)        // CSVData - header dipisah, tipe terdeteksi

new HTMLGenerator(data).generate({ className: 'tabel' })
new CSVAggregator(data).aggregate({ groupBy: 0, count: true })
```

## 5. Error

```ts
import { CSV, CSVError } from 'lombokcsv'
try {
  new CSV(text).aggregate({ groupBy: 'Wilayah', count: true })
} catch (e) {
  if (e instanceof CSVError && e.code === 'UNKNOWN_COLUMN') { /* ... */ }
}
```

Program MUST memeriksa `code`, bukan teks pesan.

## 6. Kompatibilitas dengan 1.0.0

Tanda tangan semua anggota 1.0.0 tetap ada. Perubahan perilaku (perbaikan bug) dicatat di `CHANGELOG.md` 1.1.0 dan SPEC §9. Tipe `rows` dipersempit dari `any[][]` menjadi `string[][]`.

*Lisensi dokumen: Apache-2.0 · © codinglombok*
