# LombokCSV — Full Summary Project v1.1.0

| Item | Nilai |
|---|---|
| Deskripsi | Parser CSV RFC 4180 dengan deteksi tipe, tabel HTML aman, ekspor JSON, dan agregasi GROUP BY; tanpa dependensi runtime |
| Cluster · tingkat | 03.06 Format, Parser & Serialisasi · L0 |
| Referensi | TypeScript (`src/csv.ts`, sekitar 360 baris) |
| Port | Python, Go, PHP: stub (belum ada kode) |
| Vector | 152 kasus (parseRows 56, parse 39, aggregate 20, toHTML 15, error 13, toJSON 9) · SHA-256 `be1b3c9f...c7bccd` |
| Test | 182 (29 unit + 153 vector) · coverage baris 100%, cabang 97,9% |
| Fuzz | lombokfuzzer, mode mutasi, 20.000 eksekusi lokal tanpa crash/hang |
| Registry | npm `lombokcsv` (belum terbit) |
| Lisensi | Apache-2.0 |

## 1. Tabel gap vs pembanding (jujur)

| Kemampuan | LombokCSV 1.1.0 | Papa Parse | rust-csv | qsv |
|---|---|---|---|---|
| RFC 4180 (quote, quote ganda, newline di field) | YA | YA | YA | YA |
| Delimiter/quote kustom | YA | YA | YA | YA |
| Deteksi delimiter otomatis | TIDAK | YA | TIDAK | YA (sniff) |
| Streaming / berkas besar bertahap | TIDAK (seluruh string di memori) | YA | YA | YA |
| Deteksi tipe kolom | YA (10 baris sampel) | parsial (dynamicTyping) | TIDAK | YA (stats) |
| Tabel HTML aman | YA | TIDAK | TIDAK | TIDAK |
| GROUP BY + SUM/COUNT/AVG | YA | TIDAK | TIDAK | YA |
| Kontrak lintas bahasa (SPEC + vector) | YA (port lain belum ada) | TIDAK | TIDAK | TIDAK |
| Angka format lokal (koma desimal) | TIDAK | TIDAK | TIDAK | parsial |
| Penulisan/serialisasi CSV | TIDAK | YA (unparse) | YA | YA |

Posisi unik yang dibuktikan test: parse + tabel HTML ter-escape + agregasi dalam satu paket tanpa dependensi, dengan kontrak SPEC + vector sehingga port lain dapat dibuktikan identik.

## 2. Batasan yang Diketahui

1. Hanya port TypeScript yang ada. Port Python/Go/PHP baru README rencana.
2. Seluruh masukan dibaca sebagai satu string; tidak ada API streaming. Klaim "streaming" dan "pivot" di CHANGELOG 1.0.0 tidak pernah diimplementasikan dan dikoreksi di 1.1.0.
3. Deteksi tipe hanya melihat 10 baris pertama; kolom yang berubah tipe setelah baris ke-10 tetap memakai tipe hasil sampel.
4. Angka hanya dikenali dengan titik desimal tanpa pemisah ribuan.
5. Tidak ada deteksi delimiter otomatis dan tidak ada fungsi menulis CSV.
6. Tidak ada perlindungan *CSV injection* saat data diekspor kembali ke spreadsheet (SPEC §8).
7. Urutan kunci objek ber-nama indeks bilangan bulat mengikuti aturan ECMAScript (SPEC §0.4).
8. Angka kinerja di README lama ("10.000 baris < 100 ms") belum diukur dengan benchmark yang terlacak; sudah dihapus dari README sampai benchmark tersedia.

## 3. Prinsip Universal (ringkas, untuk publik)

| Prinsip | Status | Bukti |
|---|---|---|
| U1 Mandiri | YA | README tanpa klaim kepemilikan; 4 skenario netral di guide_ §6 |
| U2 Modern | YA | SPEC: RFC 4180, WHATWG HTML, ISO 8601 + tanggal tinjauan |
| U3 Multi-platform | SEBAGIAN | TS murni (Node/Deno/browser); CI baru Linux, matriks Node 20/22/24 |
| U4 Multi-bahasa | SEBAGIAN | runner vector TS saja; port lain stub |
| U5 Rentang skala | SEBAGIAN | tanpa dependensi; tanpa streaming |
| U6 Lengkap & unik | SEBAGIAN | tabel gap di atas |
| U7 Aman & teruji | YA | SPEC §8; coverage 100% baris; fuzz; vector 152 kasus |
| U8 Ekosistem tanpa kopling | YA | 0 dependensi wajib |
| U9 Internasional | SEBAGIAN | Lang_: tingkat E, 2/20 |
| U10 Lisensi | YA | Apache-2.0, LICENSE lengkap |
| U11 Siap registri | YA | `npm pack` di CI; gate versi tag di publish |
| U12 Dokumentasi | YA | 10 dokumen publik + 2 internal |
| U13 Kerahasiaan & dokumen bersih | YA | `lombok-doctor.sh`: 0 emoji, `.gitignore` ADR-024 |

*Lisensi dokumen: Apache-2.0 · © codinglombok*
