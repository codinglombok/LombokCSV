# LombokCSV — Guide How to Use v1.1.0

## 1. Pemasangan

```bash
npm install lombokcsv
```

Paket belum terbit di npm saat dokumen ini ditulis (lihat [how_to_dist_](how_to_dist_LombokCSV_v1.1.0.md)). Sementara itu dapat dipasang dari GitHub: `npm install github:codinglombok/LombokCSV`.

## 2. Membaca CSV

```ts
import { CSV } from 'lombokcsv'

const csv = new CSV('Kota,Penduduk\nMataram,429651\nBima,155140')
csv.getHeaders()  // ['Kota', 'Penduduk']
csv.getRows()     // [['Mataram', '429651'], ['Bima', '155140']]
csv.getTypes()    // ['string', 'number']
```

Delimiter lain dan berkas tanpa header:

```ts
new CSV('a;b\n1;2', { delimiter: ';' })
new CSV('1\t2\n3\t4', { delimiter: '\t', hasHeader: false })
```

Spasi di sekitar field tak-ber-quote dibuang secara bawaan; matikan dengan `trim: false` untuk perilaku RFC 4180 murni. Isi field yang di-quote tidak pernah diubah.

## 3. Tabel HTML

```ts
const html = csv.toHTML({ className: 'tabel tabel-garis', id: 'penduduk' })
```

Semua teks di-escape, termasuk nilai `className` dan `id`. Kolom bertipe `number` diberi `style="text-align: right"`.

## 4. JSON

```ts
csv.toJSON() // [{ Kota: 'Mataram', Penduduk: '429651' }, ...]
```

Nilai tetap string; konversi tipe dilakukan pemanggil (gunakan `getTypes()` sebagai petunjuk).

## 5. Agregasi

```ts
const data = new CSV(`Wilayah,Produk,Jumlah
Barat,Beras,120
Barat,Jagung,80
Timur,Beras,95`)

data.aggregate({ groupBy: 'Wilayah', sum: ['Jumlah'], avg: ['Jumlah'], count: true })
// [
//   { Wilayah: 'Barat', Jumlah_sum: 200, Jumlah_avg: 100, count: 2 },
//   { Wilayah: 'Timur', Jumlah_sum: 95,  Jumlah_avg: 95,  count: 1 }
// ]
```

Sel yang bukan angka (kosong, `n/a`, `12abc`) diabaikan untuk `sum` dan `avg`; `avg` bernilai `null` bila grup tidak punya angka sama sekali.

## 6. Skenario pemakaian

| Skenario | Contoh |
|---|---|
| Pratinjau unggahan berkas di aplikasi web | tampilkan 50 baris pertama sebagai tabel HTML yang aman dari XSS |
| Laporan statis | ubah ekspor CSV dari basis data menjadi tabel HTML di generator situs |
| Ringkasan data sensor/IoT | kelompokkan log CSV per perangkat lalu hitung rata-rata |
| Alat baris perintah | konversi CSV ke JSON dalam skrip Node.js tanpa dependensi |

## 7. Batasan

Lihat [full_summary_](full_summary_project_LombokCSV_v1.1.0.md) bagian "Batasan yang Diketahui".

*Lisensi dokumen: Apache-2.0 · © codinglombok*
