# LombokCSV — Bahasa & i18n v1.1.0

| Atribut | Nilai |
|---|---|
| Versi | 1.1.0 |
| Tingkat i18n (masterplan §13) | **E** — kode error dan dokumentasi; perilaku parser bebas locale |
| Katalog pesan | belum ada berkas `locales/`; ID pesan dicadangkan di §2 |
| Fallback | teks bahasa Inggris tertanam di kode |
| Cakupan katalog saat ini | en + id (2/20) di tabel §2; Nusantara 0/6 |

## 1. Prinsip

1. Setiap error membawa `code` stabil (SPEC §7). Program MUST memeriksa `code`, bukan teks.
2. Library tidak membaca locale sistem, variabel lingkungan, atau zona waktu.
3. Angka dikenali hanya dalam format titik desimal tanpa pemisah ribuan (SPEC §3.1). `1.000,5` (format Indonesia/Eropa) dikenali sebagai string. Dukungan angka lokal dicatat sebagai gap di `full_summary_`.
4. Pola tanggal memeriksa bentuk saja; `24/07/2026` dan `07/24/2026` sama-sama `date` karena urutan hari/bulan bergantung locale dan tidak ditebak.
5. Teks Unicode apa pun (aksara Latin, Arab, CJK, aksara Nusantara, emoji) dipertahankan apa adanya di field; tidak ada normalisasi NFC/NFKC.

## 2. Katalog ID pesan (dicadangkan)

| ID | Kode | en | id |
|---|---|---|---|
| `lombokcsv.option.invalid` | `INVALID_OPTION` | Invalid option {$name}: {$reason}. | Opsi {$name} tidak valid: {$reason}. |
| `lombokcsv.column.unknown` | `UNKNOWN_COLUMN` | Unknown column: {$column}. | Kolom tidak dikenal: {$column}. |

## 3. RTL

Library tidak menghasilkan UI. Keluaran HTML tidak menetapkan `dir`; pemanggil menetapkan `dir="rtl"` pada elemen induk untuk data berbahasa Arab, Persia, atau Urdu.

## 4. Rencana

- 1.2.0: berkas `locales/en/lombokcsv.json` dan `locales/id/lombokcsv.json`, dimuat lewat LombokLocale bila terpasang (dependensi opsional, bukan wajib).
- Opsi pengenalan angka lokal (`decimal: ','`) setelah perilakunya dispesifikasikan di SPEC dan vector.

*Lisensi dokumen: Apache-2.0 · © codinglombok*
