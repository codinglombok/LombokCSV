# LombokCSV — Map v1.1.0

## 1. Posisi di ekosistem

```
Cluster 03 Format, Parser & Serialisasi · tingkat L0 (tanpa dependensi Lombok wajib)

L0  LombokCSV
     dependensi wajib : (tidak ada)
     dependensi opsional : (tidak ada saat ini; rencana: LombokLocale untuk katalog pesan)
     dependensi dev   : lombokfuzzer (fuzz harness)
```

## 2. Contoh pemakai di ekosistem

Library ini mandiri dan dapat dipakai siapa pun. Aplikasi dan library Lombok yang dapat memakainya (arah dependensi selalu pemakai ke library):

| Pemakai | Pemakaian |
|---|---|
| LombokPDF (aplikasi) | memasukkan tabel CSV ke dokumen |
| LombokRAGFrameworks (aplikasi) | loader CSV |
| LombokClarion (framework, opsional) | pratinjau impor data |

## 3. Peta fitur x port

| Fitur | TypeScript | Python | Go | PHP |
|---|---|---|---|---|
| parseRows / parse / tipe | YA (lulus vector) | stub | stub | stub |
| toHTML | YA (lulus vector) | stub | stub | stub |
| toJSON | YA (lulus vector) | stub | stub | stub |
| aggregate | YA (lulus vector) | stub | stub | stub |

YA = runner vector lulus 100%. stub = hanya README rencana, belum ada kode (GP-11).

*Lisensi dokumen: Apache-2.0 · © codinglombok*
