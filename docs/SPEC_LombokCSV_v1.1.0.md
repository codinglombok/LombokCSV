# LombokCSV — SPEC v1.1.0

This document is the normative cross-language contract. Every language port MUST produce byte-identical output for all specified inputs. Deviations from this specification are bugs.

| Atribut | Nilai |
|---|---|
| Versi SPEC | 1.1.0 (berlaku untuk paket `lombokcsv` 1.1.x) |
| Standar acuan | RFC 4180 (Oktober 2005) untuk format record; WHATWG HTML Living Standard (tinjauan 2026-10-01) untuk escaping keluaran HTML; ISO 8601-1:2019 untuk pola tanggal |
| Vector | `vectors/lombokcsv-vectors-v1.json` — 152 kasus — SHA-256 `be1b3c9fad212348b794be7099a78b02b69440ddf87f6fd498338ca981c7bccd` |
| Referensi | TypeScript (`src/csv.ts`) |
| Tanggal tinjauan | 2026-10-01 |

Kata MUST, MUST NOT, SHOULD, MAY mengikuti RFC 2119.

## 0. Konvensi

1. Masukan adalah string Unicode. Port yang bekerja atas byte MUST mendekode UTF-8 lebih dulu; pemrosesan berikut dinyatakan atas unit karakter. Delimiter, quote, CR, LF, SPACE, TAB semuanya karakter ASCII, sehingga hasil tidak bergantung pada pilihan unit (UTF-16 atau code point).
2. "Whitespace kosong" (blank) = SPACE (U+0020) dan TAB (U+0009).
3. "Strip" = membuang SPACE, TAB, CR (U+000D), LF (U+000A) di kedua ujung. Karakter whitespace Unicode lain (NBSP, U+FEFF, dst.) MUST NOT dibuang.
4. Urutan kunci objek keluaran adalah bagian dari kontrak (§5.4, §6). Vector dibandingkan sebagai JSON kanonik (`JSON.stringify` tanpa spasi; angka mengikuti format angka ECMAScript). Pengecualian: urutan kunci yang berupa indeks bilangan bulat kanonik (mis. header `"0"`, `"12"`) tidak normatif, karena objek ECMAScript selalu menaruhnya di depan; data seperti itu MUST dibandingkan sebagai objek, dan vector tidak memuatnya.

## 1. Opsi

| Opsi | Bawaan | Aturan |
|---|---|---|
| `delimiter` | `,` | MUST tepat satu karakter, bukan CR/LF |
| `quote` | `"` | MUST tepat satu karakter, bukan CR/LF, berbeda dari `delimiter` |
| `hasHeader` | `true` | record pertama menjadi header |
| `trim` | `true` | buang blank di sekitar isi field yang tidak di-quote (§2.3) |
| `escape` | — | usang (deprecated), MUST diabaikan |

Pelanggaran aturan opsi MUST menghasilkan error berkode `INVALID_OPTION` saat parser dibuat.

## 2. Record (`parseRows`)

### 2.1 Pra-proses

Jika karakter pertama masukan adalah U+FEFF (BOM), karakter itu MUST dibuang. U+FEFF di posisi lain adalah data biasa.

### 2.2 Mesin keadaan

Parser memproses masukan dari kiri ke kanan dengan empat keadaan: `START` (awal field), `UNQUOTED`, `QUOTED`, `AFTER_QUOTE`.

| Keadaan | Karakter | Tindakan |
|---|---|---|
| `QUOTED` | quote diikuti quote | tambahkan satu quote ke field, lewati dua karakter |
| `QUOTED` | quote tunggal | pindah ke `AFTER_QUOTE` |
| `QUOTED` | lainnya (termasuk CR, LF, delimiter) | tambahkan ke field |
| selain `QUOTED` | delimiter | akhiri field |
| selain `QUOTED` | CR, LF, atau pasangan CR LF | akhiri field lalu akhiri record |
| `START` | quote | field ditandai *quoted*, pindah ke `QUOTED` |
| `START` | blank dan `trim = true` | abaikan |
| `START` | lainnya | tambahkan ke field, pindah ke `UNQUOTED` |
| `UNQUOTED` | lainnya (termasuk quote) | tambahkan ke field (quote di tengah field adalah literal) |
| `AFTER_QUOTE` | blank dan `trim = true` | abaikan |
| `AFTER_QUOTE` | lainnya | tambahkan ke field secara literal (toleran, bukan error) |

Akhir masukan: bila keadaan bukan `START` atau record berjalan sudah memiliki field, field dan record diakhiri. Quote yang tidak ditutup (masukan berakhir di `QUOTED`) bukan error: isi yang terkumpul menjadi nilai field.

### 2.3 Nilai field

Saat field diakhiri: bila `trim = true` dan field tidak *quoted*, blank di ujung kanan MUST dibuang (blank di kiri sudah diabaikan di `START`). Isi field yang di-quote MUST dipertahankan apa adanya.

### 2.4 Baris kosong

Record yang terdiri atas tepat satu field kosong yang tidak di-quote MUST dibuang (baris kosong, termasuk baris yang hanya berisi blank bila `trim = true`). Baris `""` menghasilkan record berisi satu field kosong. Baris `,` menghasilkan dua field kosong.

### 2.5 Panjang record

Record MAY berbeda panjang; parser MUST NOT menambah atau memotong field.

## 3. Header dan tipe (`parse`)

1. Bila tidak ada record: hasil `{headers: tidak ada, rows: [], types: []}` (di vector ditulis `null`).
2. Bila `hasHeader = true`: record pertama menjadi `headers`, sisanya `rows`.
3. Jumlah kolom tipe = panjang record terpanjang di `rows` (header tidak ikut dihitung). Bila `rows` kosong, `types = []`.
4. Untuk setiap kolom, periksa nilai di `TYPE_SAMPLE_ROWS = 10` baris pertama setelah di-strip (§0.3); nilai kosong dilewati.
5. Tipe kolom: `number` bila semua nilai cocok pola angka; jika tidak, `date` bila semua cocok pola tanggal; jika tidak, `boolean` bila semua cocok pola boolean; selain itu (termasuk kolom tanpa nilai) `string`.

### 3.1 Pola (ekspresi reguler, seluruh nilai harus cocok)

| Tipe | Pola |
|---|---|
| number | `^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$` (tanpa `+`, tanpa pemisah ribuan, tanpa `NaN`/`Infinity`/heksadesimal) |
| date | `^\d{4}-\d{2}-\d{2}$` · `^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$` · `^\d{1,2}/\d{1,2}/\d{4}$` · `^\d{1,2}-\d{1,2}-\d{4}$` |
| boolean | `^(true|false|yes|no|1|0)$`, tidak peka huruf besar |

`\d` berarti ASCII 0-9 saja. Pola tanggal memeriksa bentuk, bukan validitas kalender.

## 4. HTML (`toHTML`)

Keluaran MUST tepat mengikuti templat berikut (`\n` = LF), tanpa spasi tambahan:

```
<table{class}{id}>\n
[<thead>\n<tr>\n(<th>{h}</th>\n)*</tr>\n</thead>\n]     -- hanya bila headers ada dan tidak kosong
<tbody>\n
(<tr>\n(<td{align}>{v}</td>\n)*</tr>\n)*                -- satu <td> per field yang ada di record
</tbody>\n</table>                                     -- tanpa LF penutup
```

- `{class}` = ` class="<esc(className)>"` bila `className` tidak kosong; `{id}` = ` id="<esc(id)>"` bila `id` tidak kosong.
- `{align}` = ` style="text-align: right"` bila tipe kolom itu `number`.
- `esc` mengganti, berurutan: `&` menjadi `&amp;`, `<` menjadi `&lt;`, `>` menjadi `&gt;`, `"` menjadi `&quot;`, `'` menjadi `&#39;`. Fungsi yang sama dipakai untuk isi sel dan nilai atribut.

## 5. Agregasi (`aggregate`)

### 5.1 Resolusi kolom

Kolom dapat berupa nama (string) atau indeks (bilangan). Nama dicari dengan kesamaan string persis pada `headers` (kemunculan pertama). Indeks MUST bilangan bulat `0 <= i < lebar`, dengan lebar = maksimum panjang `headers` dan panjang record di `rows`. Nama yang tidak ada, nama ketika tidak ada header, atau indeks di luar aturan MUST menghasilkan error `UNKNOWN_COLUMN`. Semua kolom (`groupBy`, `sum`, `avg`) diresolusi sebelum baris diproses.

### 5.2 Nama kolom keluaran

Nama kolom `i` = `headers[i]` bila ada, selain itu `col_<i>`.

### 5.3 Pengelompokan dan nilai

1. Kunci grup = nilai sel kolom `groupBy` apa adanya (tanpa strip, peka huruf besar); sel yang tidak ada dianggap `""`.
2. Grup muncul dalam urutan kemunculan pertama.
3. Nilai numerik sebuah sel = sel di-strip lalu, bila cocok pola angka §3.1, dikonversi ke IEEE 754 binary64 (pembulatan terdekat). Sel yang tidak cocok diabaikan.
4. `<nama>_sum` = jumlah nilai numerik, dijumlahkan kiri-ke-kanan menurut urutan baris, mulai dari 0.
5. `<nama>_avg` = (jumlah seperti butir 4) dibagi banyak nilai numerik; `null` bila tidak ada nilai numerik.
6. `count` = banyak baris dalam grup (termasuk baris dengan sel kosong).

### 5.4 Bentuk keluaran

Satu objek per grup dengan kunci berurutan: `<nama groupBy>`, lalu `<nama>_sum` untuk setiap kolom `sum` (urutan opsi), lalu `<nama>_avg` untuk setiap kolom `avg`, lalu `count` bila `count = true`. Bila dua kunci bertabrakan, nilai yang ditulis terakhir menang dan posisi kunci mengikuti penulisan pertama.

## 6. JSON (`toJSON`)

Tanpa header: kembalikan `rows`. Dengan header: satu objek per baris; kunci mengikuti urutan `headers`; sel yang tidak ada menjadi `""`; sel melebihi jumlah header dibuang; untuk nama header ganda, kolom terakhir menang (posisi kunci mengikuti kemunculan pertama).

## 7. Error

| Kode | Kapan |
|---|---|
| `INVALID_OPTION` | §1 |
| `UNKNOWN_COLUMN` | §5.1 |

Port MUST mengekspos `code` sebagai string persis di atas. Teks pesan informatif dan MAY berbeda antar port.

## 8. Keamanan (normatif)

1. Parser MUST berjalan dalam waktu linier terhadap panjang masukan dan MUST NOT melempar error untuk masukan apa pun (hanya opsi yang dapat memicu error).
2. `toHTML` MUST meng-escape setiap teks yang berasal dari masukan atau opsi (§4). Keluaran aman disisipkan sebagai isi elemen; tidak dirancang untuk disisipkan di dalam `<script>`/`<style>` atau atribut tanpa tanda kutip.
3. Library tidak melakukan I/O, tidak mengevaluasi rumus, dan tidak melindungi dari *CSV injection* (sel yang diawali `=`, `+`, `-`, `@`) ketika data diekspor kembali ke spreadsheet; itu tanggung jawab pemanggil.

## 9. Perubahan dari 1.0.0

Lihat `CHANGELOG.md` bagian 1.1.0. Ringkasnya: isi field yang di-quote tidak lagi di-trim; quote di tengah field tak-ber-quote menjadi literal; BOM dibuang; pola tanggal dijangkar penuh; atribut `class`/`id` di-escape; kolom tak dikenal menjadi error; `_avg` tidak lagi menyertakan kunci bantu `_count` dan mengabaikan sel non-angka; nama grup tanpa header memakai `col_<i>`.

*Lisensi dokumen: Apache-2.0 · © codinglombok*
