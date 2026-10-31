# LombokCSV — Structure Repo v1.1.0

```
LombokCSV/
├── README.md · CHANGELOG.md · CONTRIBUTING.md · SECURITY.md · LICENSE (Apache-2.0)
├── package.json · package-lock.json · tsconfig.json · tsconfig.check.json · vitest.config.ts
├── eslint.config.js · .prettierrc.json · .prettierignore · .gitignore · .dockerignore
├── composer.json        root PHP manifest (no "version" field; Packagist reads it from v* tags)
├── Dockerfile · docker/smoke.mjs
├── .github/workflows/   ci.yml · release.yml · release-npm.yml · release-pypi.yml ·
│                        release-docker.yml · pages.yml
├── src/                 csv.ts (reference implementation) · index.ts (public exports)
├── tests/               csv.test.ts (unit) · vectors.test.ts (vector runner) ·
│                        fuzz/csv.fuzz.ts (lombokfuzzer)
├── vectors/             lombokcsv-vectors-v1.json · SHA256SUMS · build_vectors.py
│                        (case source, expected values hand-written from the SPEC)
├── scripts/             lombok-doctor.sh (v3.7 D-ENV) · bump_version.sh · smoke.mjs
├── python/              pyproject.toml · lombokcsv/{__init__.py, csv.py, py.typed} ·
│                        tests/{test_api.py, vectors_test.py} · README.md · LICENSE
├── go/                  go.mod (module .../lombokcsv/go) · csv.go · obj.go ·
│                        vectors_test.go · csv_test.go · README.md · LICENSE
├── php/                 src/{Csv, CsvParser, CsvAggregator, HtmlGenerator, CsvError,
│                        functions}.php · tests/{run, bootstrap, api, vectors}.php ·
│                        README.md · LICENSE
└── docs/                10 public documents + index.html (GitHub Pages)
                          masterplan_ and architecture_ are internal documents (ADR-024),
                          never committed
```

Rules: the TypeScript reference lives at the repository root (S6 exception for a TS-reference repo); every port lives in its language folder at the root and consumes the same vector file; every behaviour change updates the SPEC + vectors first (SPEC-first); built artifacts (`dist/`, wheels) are not committed; internal documents are never committed.

---

*Document license: Apache-2.0 · © codinglombok*
