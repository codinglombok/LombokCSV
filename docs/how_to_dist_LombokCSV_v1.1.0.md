# LombokCSV — How to Dist v1.1.0

## 1. Registries

| Registry | Name | Status | Mechanism |
|---|---|---|---|
| npm | `lombokcsv` | pending tag | `release.yml` job `npm` on a `v*` tag: `npm publish --provenance --access public`, secret `NPM_TOKEN`, environment `npm` |
| PyPI | `lombokcsv` | pending tag | `release.yml` job `pypi`: `pypa/gh-action-pypi-publish`, trusted publishing, environment `pypi` |
| Go module proxy | `github.com/codinglombok/lombokcsv/go` | pending tag | `release.yml` job `go-tag` pushes `go/v<version>`; pkg.go.dev picks it up automatically |
| Packagist | `codinglombok/lombokcsv` | pending listing | register once at packagist.org/packages/submit; afterwards auto-synced from `v*` tags (root `composer.json` has no `version` field) |
| GHCR | `ghcr.io/codinglombok/lombokcsv` | pending tag | `release.yml` job `docker`: multi-arch image, environment `docker`; Docker Hub only when `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` exist |
| jsDelivr / unpkg | `lombokcsv` | automatic after npm | `https://cdn.jsdelivr.net/npm/lombokcsv@1.1.0/dist/index.js` |

## 2. Staged rehearsal (per registry)

1. Run `.github/workflows/release-<registry>.yml` via `workflow_dispatch` with `dry_run=true` (default): it builds, tests and (for Docker) smoke-tests the artefact without publishing.
2. Run it again with `dry_run=false` **and** the `tag` input matching the manifest version; the job refuses a mismatch.

## 3. Full release flow

1. All changes reach `main` through PRs with green CI (lint, tests + coverage, build, `npm pack --dry-run`, `scripts/lombok-doctor.sh`).
2. The version in `package.json`, `python/pyproject.toml`, `python/lombokcsv/__init__.py`, the `docs/*_v<version>.md` file names and the top `CHANGELOG.md` entry must be identical (the doctor checks this; `scripts/bump_version.sh` performs the mechanical part).
3. Tag `v<version>` on `main` and push it. `release.yml` then runs `check-version` (tag == manifests == changelog == docs names + doctor) and publishes npm, PyPI, the container image, the `go/v*` tag, and the GitHub Release bundle (git archive zip + SHA256SUMS).

```bash
git switch main && git pull
npm ci && npm run check
bash scripts/bump_version.sh 1.2.0   # when bumping; skip when already at the target version
# ... human steps printed by the script (CHANGELOG, SPEC, verification) ...
git tag -a v1.2.0 -m "LombokCSV 1.2.0"
git push origin v1.2.0
```

One-time setup: `NPM_TOKEN` secret, PyPI trusted publisher (environment `pypi`), environment reviewers for `npm`/`pypi`/`docker`/`github-release` so every release is staged.

## 4. Post-release verification

```bash
npm view lombokcsv@1.1.0 version
npm i lombokcsv@1.1.0 && node -e "console.log(new (require('lombokcsv').CSV)('a\n1').getRows())"
pip index versions lombokcsv
go list -m -versions github.com/codinglombok/lombokcsv/go
docker run --rm ghcr.io/codinglombok/lombokcsv:1.1.0   # container smoke prints OK
```

Rollback: `npm deprecate lombokcsv@1.1.0 "use 1.1.1"` (unpublish only within 72 hours and without dependents); tags are never moved or deleted — a faulty release is fixed by a new version.

---

*Document license: Apache-2.0 · © codinglombok*
