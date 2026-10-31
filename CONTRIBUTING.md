# Contributing to LombokCSV

Thank you for your interest in contributing. LombokCSV is part of the
[Lombok Ecosystem](https://github.com/codinglombok).

## Ways to contribute

- **Report bugs** — open an issue with a minimal reproduction
- **Request features** — describe the use case
- **Port to another language** — the shared vectors make new ports verifiable
- **Improve docs** — typos, examples, tutorials
- **Add tests** — the reference implementation holds 95% statement / 90% branch coverage; ports hold 90%

## Development setup

```bash
git clone https://github.com/codinglombok/LombokCSV.git
cd LombokCSV
npm ci
npm run check
```

## Pull request process

1. Fork and create a feature branch (`git checkout -b feature/my-feature`)
2. Behaviour changes start in the specification: update `docs/SPEC_LombokCSV_v<version>.md`,
   add cases to `vectors/build_vectors.py` with hand-written expected values, run `npm run vectors`,
   and update `vectors/SHA256SUMS` and the hash in the SPEC
3. Port the change to every language port (`python/`, `go/`, `php/`) — all ports must pass the
   same vectors before the change can land
4. Ensure `npm run check` passes (tsc, eslint, prettier, tests with coverage, build,
   `scripts/lombok-doctor.sh`) plus the per-port suites (`python -m pytest`, `go test ./...`,
   `php php/tests/run.php`)
5. Update `CHANGELOG.md` under `[Unreleased]` (newest entries first)
6. Open a PR against `main`

## Code style

- TypeScript strict mode; `gofmt`/`go vet` clean for Go; `php -l` clean for PHP
- Zero runtime dependencies in every port
- No emoji in Markdown files; no client, organisation, or customer names in code, tests, docs, or commit messages
- Conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`)

## Adding a language port

Ports live in their language folder at the repository root (`python/`, `go/`, `php/`). Each port must:
- Implement the identical public API and the canonical `[CODE]` error messages
- Ship a runner that executes every case in `vectors/lombokcsv-vectors-v1.json`
  (comparison semantics: SPEC section 0.5)
- Hold at least 90% coverage in its CI job
- Include its own README with install instructions

## License

By contributing you agree your work is licensed under Apache-2.0.
