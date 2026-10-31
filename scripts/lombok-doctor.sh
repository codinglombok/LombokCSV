#!/usr/bin/env bash
# lombok doctor (v3.7, D-ENV variant) - machine checks for the Lombok Ecosystem
# standards. Logic is byte-equivalent to the upstream LombokVector script; the
# message strings are translated to English per the v3 language rule.
#
# Covers (PRINCIPLES_UNIVERSAL v3.6, MASTERPLAN v3.6 section 5, RELEASE_DIST section 5,
# Masterplan v3.6 -> v3.7 R1-R4):
#   docs     10 public documents exist, file-name version = manifest version, SPEC
#            normative, vector hash matches, vector case count >= 100, vector runner
#            per port
#   claims   no application/framework ownership claims (ADR-019, U1)
#   style    0 emoji in tracked *.md (ADR-025, GP-13)
#   ignore   .gitignore contains the 3 ADR-024 lines, internal documents untracked (GP-13)
#   privacy  0 client terms (ADR-023, GP-12) - list from $LOMBOK_PRIVACY_TERMS
#            or ~/.lombok/client-terms.txt; skipped when the list is unavailable
#   meta     LICENSE, SPDX manifest, README "Mengapa library ini", CHANGELOG top = version,
#            no local path/file: dependencies
#   d-env    D-ENV-1 environment on every registry-publish job (R1, two-way with R3),
#            D-ENV-2 canonical environment names (R2), D-ENV-3 root composer.json for
#            repos with a PHP port
#
# Usage: scripts/lombok-doctor.sh <RepoName> [--internal]
#   --internal  also require the internal documents (masterplan_, architecture_) to
#               exist locally and the U1-U13 evidence table to be complete (run by
#               the owner, not CI).
# Optional variables: LOMBOK_VERSION (force version), LOMBOK_VECTORS (vector file path).
set -u
REPO="${1:?usage: $0 <RepoName> [--internal]}"
INTERNAL=0
[ "${2:-}" = "--internal" ] && INTERNAL=1
PKG="$(echo "$REPO" | tr '[:upper:]' '[:lower:]')"
fail=0
err() { echo "FAIL: $*"; fail=1; }
ok() { echo "ok:   $*"; }

# ---------------------------------------------------------------- manifest version
json_version() { sed -n 's/^  "version": *"\([^"]*\)".*/\1/p' "$1" | head -1; }
VER="${LOMBOK_VERSION:-}"
if [ -z "$VER" ]; then
  for m in package.json typescript/package.json; do
    [ -f "$m" ] && { VER="$(json_version "$m")"; [ -n "$VER" ] && break; }
  done
fi
if [ -z "$VER" ]; then
  for m in rust/Cargo.toml Cargo.toml; do
    [ -f "$m" ] && { VER="$(grep -m1 '^version' "$m" | sed 's/.*"\(.*\)".*/\1/')"; [ -n "$VER" ] && break; }
  done
fi
if [ -z "$VER" ] && [ -f pyproject.toml ]; then
  VER="$(grep -m1 '^version' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')"
fi
[ -z "$VER" ] && [ -f version.txt ] && VER="$(tr -d '[:space:]' < version.txt)"
[ -n "$VER" ] || { err "cannot determine the manifest version"; exit 1; }
echo "repo=$REPO version=$VER"

# every manifest that exists must carry the same version (composer.json has no version field)
for m in package.json typescript/package.json python/pyproject.toml pyproject.toml rust/Cargo.toml version.txt; do
  [ -f "$m" ] || continue
  case "$m" in
    *.json) v="$(json_version "$m")" ;;
    version.txt) v="$(tr -d '[:space:]' < "$m")" ;;
    *) v="$(grep -m1 '^version' "$m" | sed 's/.*"\(.*\)".*/\1/')" ;;
  esac
  [ -z "$v" ] || [ "$v" = "$VER" ] || err "version of $m ($v) != $VER"
done
for c in composer.json php/composer.json; do
  [ -f "$c" ] && grep -q '"version"' "$c" && err "$c contains a version field (Packagist takes the version from the tag)"
done
# the PHP manifest must be single at the root (Packagist only reads the root composer.json)
[ -f php/composer.json ] && err "php/composer.json still exists - the PHP manifest moved to the root composer.json"
# documents of other versions must not be committed (relapse: *_v<old>.md copies come back)
for f in docs/*_"${REPO}"_v*.md; do
  [ -e "$f" ] || continue
  case "$f" in
    *_v${VER}.md) ;;
    *) err "document of another version is committed: $f (must be *_v${VER}.md)" ;;
  esac
done

# ---------------------------------------------------------------- docs
PUBLIC="changelog map structure_repo full_summary_project guide_how_to_use how_to_dist development_ide API Lang SPEC"
count=0
for d in $PUBLIC; do
  f="docs/${d}_${REPO}_v${VER}.md"
  if [ -f "$f" ]; then count=$((count+1)); else err "missing public document: $f"; fi
done
echo "public documents: $count/10"
if [ "$INTERNAL" -eq 1 ]; then
  for d in masterplan architecture; do
    f="docs/${d}_${REPO}_v${VER}.md"
    [ -f "$f" ] || err "missing internal document (local): $f"
  done
  MP="docs/masterplan_${REPO}_v${VER}.md"
  if [ -f "$MP" ]; then
    grep -q '^## 2\. Prinsip Universal' "$MP" || err "masterplan without the '## 2. Prinsip Universal' section"
    n="$(grep -c -E '^\| U(1[0-3]|[1-9]) \|' "$MP")"
    [ "$n" -eq 13 ] || err "U1-U13 evidence table holds $n/13 rows"
  fi
fi

SPEC="docs/SPEC_${REPO}_v${VER}.md"
S="This document is the normative cross-language contract. Every language port MUST produce byte-identical output for all specified inputs. Deviations from this specification are bugs."
VEC="${LOMBOK_VECTORS:-vectors/${PKG}-vectors-v1.json}"
if [ -f "$SPEC" ]; then
  grep -qF "$S" "$SPEC" || err "SPEC is missing the mandatory normative sentence"
  if [ -f "$VEC" ]; then
    ACTUAL="$(sha256sum "$VEC" | cut -d' ' -f1)"
    grep -q "$ACTUAL" "$SPEC" || err "vector SHA-256 in SPEC does not match $VEC (actual $ACTUAL)"
    n="$(grep -o '"id": *"' "$VEC" | wc -l)"
    [ "$n" -ge 100 ] || err "vector file has only $n cases (<100, GP-11)"
    echo "vector: $n cases"
  else
    err "missing vector file: $VEC"
  fi
fi

# vector runner for every port that has a manifest (GP-11)
has_runner() { ls $1 >/dev/null 2>&1; }
if [ -f package.json ] && [ -d src ]; then has_runner "tests/*vectors*" || err "TS vector runner (tests/*vectors*) missing"; fi
if [ -f typescript/package.json ]; then has_runner "typescript/test*/*vectors*" || err "TS vector runner missing"; fi
if [ -f rust/Cargo.toml ]; then has_runner "rust/tests/*vectors*" || has_runner "rust/*/tests/*vectors*" || has_runner "rust/*-vectors" || err "Rust vector runner missing"; fi
if [ -f python/pyproject.toml ]; then has_runner "python/tests/*vectors*" || err "Python vector runner missing"; fi
if [ -f go/go.mod ]; then has_runner "go/*vectors*_test.go" || err "Go vector runner missing"; fi
if [ -d php/src ]; then has_runner "php/tests/*ectors*" || err "PHP vector runner missing"; fi

# ---------------------------------------------------------------- claims (ADR-019)
APPS='RAG[A-Za-z]*|Clarion|DocFlow|PDF|AgenticAuto|Miner|DNSProxy|Proxy'
for f in README.md docs/*.md; do
  [ -f "$f" ] || continue
  case "$f" in docs/map_*) continue ;; esac
  hits="$(grep -n -i -E "(peran di rag|role in rag|purpose in rag|library *#[0-9]+|(part of|bagian dari|modul dari|komponen dari)[^.]{0,20}Lombok(${APPS})\\b|khusus (untuk )?(rag|Lombok[A-Za-z]+))" "$f" \
    | grep -v -i -E "bukan|tidak|not |never|jangan|salah|diperiksa|ditolak|dilarang" || true)"
  [ -z "$hits" ] || err "ownership claim in $f (ADR-019): $(echo "$hits" | head -1 | cut -c1-120)"
done

# ---------------------------------------------------------------- style (ADR-025)
EMOJI_RE='[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B05}-\x{2B55}\x{FE0F}\x{1F1E6}-\x{1F1FF}]'
emoji="$(git ls-files -z -- '*.md' 2>/dev/null | xargs -0 -r perl -CSD -ne "print \"\$ARGV:\$.\\n\" if /$EMOJI_RE/; close ARGV if eof" 2>/dev/null)"
if [ -n "$emoji" ]; then err "emoji in *.md: $(echo "$emoji" | head -5 | tr '\n' ' ')"; else ok "0 emoji in *.md"; fi

# ---------------------------------------------------------------- ignore (ADR-024)
for rule in '/map' '/docs/*architecture*.*' '/docs/*masterplan*.*'; do
  grep -qxF "$rule" .gitignore 2>/dev/null || err ".gitignore lacks the line '$rule' (ADR-024)"
done
tracked="$(git ls-files 2>/dev/null | grep -E '^map/|^docs/[^/]*architecture[^/]*\.|^docs/[^/]*masterplan[^/]*\.' || true)"
[ -z "$tracked" ] || err "internal documents tracked by git: $(echo "$tracked" | tr '\n' ' ')"

# ---------------------------------------------------------------- privacy (ADR-023)
TERMS_FILE=""
if [ -n "${LOMBOK_PRIVACY_TERMS:-}" ]; then
  TERMS_FILE="$(mktemp)"; printf '%s\n' "$LOMBOK_PRIVACY_TERMS" | sed '/^[[:space:]]*$/d' > "$TERMS_FILE"
elif [ -f "$HOME/.lombok/client-terms.txt" ]; then
  TERMS_FILE="$(mktemp)"; sed '/^[[:space:]]*$/d' "$HOME/.lombok/client-terms.txt" > "$TERMS_FILE"
fi
if [ -n "$TERMS_FILE" ] && [ -s "$TERMS_FILE" ]; then
  # the output never prints the terms themselves so CI logs cannot leak the list
  n1="$(git grep -I -i -F -c -f "$TERMS_FILE" -- . ':!*.lock' ':!package-lock.json' 2>/dev/null | wc -l)"
  n2="$(git log --format='%s%n%b' 2>/dev/null | grep -i -F -c -f "$TERMS_FILE" || true)"
  [ "$n1" -eq 0 ] || err "client references found in $n1 files (ADR-023)"
  [ "${n2:-0}" -eq 0 ] || err "client references found in $n2 commit message lines (ADR-023)"
  [ "$n1" -eq 0 ] && [ "${n2:-0}" -eq 0 ] && ok "privacy: 0 findings"
  rm -f "$TERMS_FILE"
else
  echo "skip: privacy (LOMBOK_PRIVACY_TERMS / ~/.lombok/client-terms.txt unavailable)"
fi

# ---------------------------------------------------------------- meta
SPDX=""
[ -f package.json ] && SPDX="$(sed -n 's/^  "license": *"\([^"]*\)".*/\1/p' package.json | head -1)"
[ -z "$SPDX" ] && [ -f rust/Cargo.toml ] && SPDX="$(grep -m1 '^license' rust/Cargo.toml | sed 's/.*"\(.*\)".*/\1/')"
case "$SPDX" in
  *"OR MIT"*) for f in LICENSE-APACHE LICENSE-MIT; do [ -f "$f" ] || err "license $SPDX but $f is missing"; done ;;
  "") err "no SPDX license found in the manifests" ;;
  *) [ -f LICENSE ] || err "LICENSE is missing" ;;
esac
for f in LICENSE LICENSE-APACHE LICENSE-MIT; do
  [ -f "$f" ] && [ "$(wc -c < "$f")" -lt 1000 ] && err "$f is too short (<1000 bytes)"
done
grep -q -i 'Mengapa library ini' README.md 2>/dev/null || err "README lacks the 'Mengapa library ini?' section"
if [ -f CHANGELOG.md ]; then
  first="$(grep -m1 -E '^## \[[0-9]' CHANGELOG.md | sed 's/^## \[\([^]]*\)\].*/\1/')"
  [ "$first" = "$VER" ] || err "top CHANGELOG.md entry ($first) != version $VER"
else
  err "CHANGELOG.md is missing"
fi
for m in package.json typescript/package.json; do
  [ -f "$m" ] && grep -q -E '"(file|link):' "$m" && err "$m uses local file:/link: dependencies"
done
for m in rust/Cargo.toml $(ls rust/*/Cargo.toml 2>/dev/null); do
  [ -f "$m" ] && grep -E '^[a-z].*path *= *"\.\./\.\.' "$m" >/dev/null && err "$m uses a path dependency to another repo"
done

# ---------------------------------------------------------------- D-ENV (v3.7, R1-R4)
# D-ENV-1  every registry-publish job MUST declare `environment:` at job level
#          (R1); jobs other than registry-publish MUST NOT have an environment (R3).
# D-ENV-2  the environment name must be canonical (R2).
# Registry-publish classification (dual ecosystem pattern):
#   (a) job id/name contains publish|mirror|gpr|packagist  -> publish_*.yml
#       and release-github.yml pattern (LombokEncryptDecrypt);
#   (b) job id = canonical registry name in release*.yml -> release.yml
#       SimHash/Vector/Locale pattern (crates, npm, pypi, docker, github-release).
# Non-upload automation jobs are deliberately OUTSIDE R1: release-please,
# go-tag, check-version - none of them uploads to a registry; environments
# there would only flood the Deployments tab with no-op records.
CANON_RE='^(npm|pypi|crates|packagist|docker|github-release|maven|nuget|cpan|pgxn)$'
PUBLISH_RE='publish|mirror|gpr|packagist'
if [ ! -d .github/workflows ]; then
  err "D-ENV-1: .github/workflows not found"
else
  shopt -s nullglob
  found=0
  for wf in .github/workflows/*.yml .github/workflows/*.yaml; do
    [ -f "$wf" ] || continue
    case "$wf" in */release*.yml|*/release*.yaml) relfile=1 ;; *) relfile=0 ;; esac
    # job-level key = indent 2 directly below `jobs:`; job body = indent >= 4.
    # Per-job output: <job-id>\001<environment>\001<name>
    # (delimiter \001 = SOH, not tab: tab is IFS whitespace so empty fields
    # would merge and shift - a bug that already happened. \001 never occurs
    # in YAML text.)
    records="$(awk '
      /^[[:space:]]*#/ { next }
      /^jobs:/ { inj=1; next }
      inj && /^[^ #]/ { inj=0 }
      inj && /^  [A-Za-z0-9_-]+:[[:space:]]*$/ {
        if (job != "") print job "\001" envv "\001" jname
        job=$0; sub(/^  /,"",job); sub(/:[[:space:]]*$/,"",job)
        envv=""; jname=""
        next
      }
      inj && job != "" {
        if (jname == "" && /^    name:/) { jname=$0; sub(/^ *name:[[:space:]]*/,"",jname) }
        if (/^    environment:/) { envv=$0; sub(/^ *environment:[[:space:]]*/,"",envv) }
      }
      END { if (job != "") print job "\001" envv "\001" jname }
    ' "$wf")"
    [ -z "$records" ] && continue
    while IFS=$'\001' read -r job envv jname; do
      [ -n "$job" ] || continue
      envv="$(printf '%s' "$envv" | tr -d '"')"
      label="${jname:-$job}"
      if printf '%s %s' "$job" "$jname" | grep -qiE "$PUBLISH_RE" \
         || { [ "$relfile" -eq 1 ] && printf '%s' "$job" | grep -qE "$CANON_RE"; }; then
        found=$((found+1))
        if [ -z "$envv" ]; then
          err "D-ENV-1: $wf :: $job ('$label') is a registry-publish job without environment: (R1)"
        elif printf '%s' "$envv" | grep -qE "$CANON_RE"; then
          ok "D-ENV: $wf :: $job -> environment: $envv"
        else
          err "D-ENV-2: $wf :: $job environment '$envv' is not a canonical name (R2)"
        fi
      else
        if [ -n "$envv" ]; then
          err "D-ENV-1/R3: $wf :: $job ('$label') is not a publish job but has environment: $envv"
        fi
      fi
    done <<< "$records"
  done
  if [ "$found" -gt 0 ]; then
    echo "registry-publish jobs detected: $found"
  else
    err "D-ENV-1: no registry-publish job detected (misclassification?)"
  fi
fi

# ---------------------------------------------------------------- D-ENV-3
if [ -d ports/php ] || [ -d php/src ]; then
  if [ -f composer.json ]; then
    ok "D-ENV-3: PHP port detected and root composer.json exists"
  else
    err "D-ENV-3: repo has a PHP port but the root composer.json is missing"
  fi
else
  echo "skip: D-ENV-3 (not a repo with a PHP port)"
fi

[ $fail -eq 0 ] && echo "OK: lombok doctor (v3.7 D-ENV) passed" || { echo "lombok doctor FAILED"; exit 1; }
