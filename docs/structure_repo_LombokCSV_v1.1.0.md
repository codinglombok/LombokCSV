# LombokCSV — Structure Repo v1.1.0

```
LombokCSV/
├── README.md · CHANGELOG.md · CONTRIBUTING.md · SECURITY.md · LICENSE (Apache-2.0)
├── package.json · package-lock.json · tsconfig.json · vitest.config.ts
├── .github/workflows/   ci.yml (lint, test+coverage, build, pack, doctor, fuzz, publish pada tag v*) · pages.yml
├── src/                 csv.ts (implementasi referensi) · index.ts (ekspor publik)
├── tests/               csv.test.ts (unit) · vectors.test.ts (runner vector) · fuzz/csv.fuzz.ts (lombokfuzzer)
├── vectors/             lombokcsv-vectors-v1.json · SHA256SUMS · build_vectors.py (sumber kasus, nilai harapan ditulis tangan)
├── scripts/             lombok-doctor.sh (pemeriksaan standar v3.6)
├── ports/               go/ · php/ · python/ - README rencana (stub)
└── docs/                10 dokumen publik + index.html (GitHub Pages)
                         masterplan_ dan architecture_ adalah dokumen internal (ADR-024), tidak di-commit
```

Aturan: kode sumber hanya di `src/`; setiap perubahan perilaku mengubah SPEC + vector lebih dulu (test-first); dist hasil build tidak di-commit.

*Lisensi dokumen: Apache-2.0 · © codinglombok*
