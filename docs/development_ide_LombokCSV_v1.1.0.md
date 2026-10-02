# LombokCSV — Development IDE v1.1.0

## 1. Lingkungan

| Alat | Versi |
|---|---|
| Node.js | 20 LTS atau lebih baru (CI: 20, 22, 24) |
| npm | 10+ |
| Editor | VS Code atau IDE apa pun dengan dukungan TypeScript |
| Python | 3.10+ (hanya untuk `vectors/build_vectors.py`) |
| Bash | untuk `scripts/lombok-doctor.sh` (Windows: Git Bash atau WSL) |

## 2. Perintah

| Perintah | Fungsi |
|---|---|
| `npm ci` | pasang dependensi dev sesuai lockfile |
| `npm run lint` | `tsc --noEmit` (strict) |
| `npm test` | unit + runner vector |
| `npm run coverage` | test dengan ambang coverage 90% |
| `npm run build` | `tsup` ke `dist/` (ESM + CJS + d.ts) |
| `npm run fuzz` | fuzz parser dengan lombokfuzzer (`FUZZ_EXECUTIONS` mengatur jumlah) |
| `npm run vectors` | bangun ulang berkas vector dari `vectors/build_vectors.py` |
| `npm run doctor` | pemeriksaan standar Lombok v3.6 |
| `npm run check` | lint + coverage + build + doctor |

## 3. Alur mengubah perilaku

1. Ubah SPEC lebih dulu.
2. Tambah atau ubah kasus di `vectors/build_vectors.py`; nilai harapan ditulis tangan dari SPEC, bukan disalin dari keluaran kode.
3. `npm run vectors`, lalu perbarui `vectors/SHA256SUMS` dan hash di SPEC.
4. Ubah `src/csv.ts` sampai `npm test` hijau.
5. Catat di `CHANGELOG.md` (entri terbaru di depan).

## 4. Arah pengembangan

- Port Python sebagai pemeriksa referensi kedua (GP-11), lalu Go dan PHP.
- API streaming berbasis potongan (chunk) dengan hasil identik dengan parse penuh.
- Opsi angka lokal dan katalog pesan `locales/`.

*Lisensi dokumen: Apache-2.0 · © codinglombok*
