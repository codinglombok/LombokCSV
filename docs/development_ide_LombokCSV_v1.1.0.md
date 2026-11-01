# LombokCSV — Development IDE v1.1.0

## 1. Environment

| Tool | Version |
|---|---|
| Node.js | 20 LTS or newer (CI: 20, 22, 24) |
| npm | 10+ |
| Editor | VS Code or any IDE with TypeScript support |
| Python | 3.9+ (port and `vectors/build_vectors.py`) |
| Go | 1.22+ (port) |
| PHP | 8.1+ with pcov for the coverage gate (port) |
| Bash | for `scripts/lombok-doctor.sh` and `scripts/bump_version.sh` (Windows: Git Bash or WSL) |

## 2. Commands

| Command | Purpose |
|---|---|
| `npm ci` | install dev dependencies from the lockfile |
| `npm run lint` | `tsc --noEmit` (strict) |
| `npm run lint:eslint` | ESLint flat config |
| `npm run format:check` | Prettier check (generated files are ignored) |
| `npm test` | unit + vector runner |
| `npm run coverage` | tests with the 95/90 coverage threshold |
| `npm run build` | `tsup` into `dist/` (ESM + CJS + d.ts) |
| `npm run smoke` | smoke-test the built `dist/` output |
| `npm run fuzz` | fuzz the parser with lombokfuzzer (`FUZZ_EXECUTIONS` sets the count) |
| `npm run vectors` | rebuild the vector file from `vectors/build_vectors.py` |
| `npm run doctor` | Lombok standards check (v3.7 D-ENV) |
| `npm run check` | lint + eslint + prettier + coverage + build + doctor |
| `python -m coverage run --branch --source=lombokcsv -m pytest -q` | Python port tests (in `python/`) |
| `go test ./...` | Go port tests (in `go/`) |
| `php php/tests/run.php` | PHP port tests (repo root; `--coverage=90` with pcov) |

## 3. Flow for changing behaviour

1. Change the SPEC first.
2. Add or change cases in `vectors/build_vectors.py`; expected values are hand-written from the SPEC, never copied from an implementation's output.
3. `npm run vectors`, then update `vectors/SHA256SUMS` and the hash in the SPEC.
4. Change `src/csv.ts` and every port until all four suites are green.
5. Record the change in `CHANGELOG.md` (newest entries first).

## 4. Development directions

- Streaming API over chunks with results identical to the full parse.
- Locale number options (`decimal: ','`) after their behaviour is specified in the SPEC and vectors.
- Message catalogue `locales/` (see Lang_ §4).

---

*Document license: Apache-2.0 · © codinglombok*
