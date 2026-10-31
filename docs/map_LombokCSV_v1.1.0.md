# LombokCSV — Map v1.1.0

## 1. Position in the ecosystem

```
Cluster 03 Format, Parser & Serialisation · level L0 (no mandatory Lombok dependencies)

L0  LombokCSV
     mandatory dependencies : (none)
     optional dependencies  : (none today; planned: LombokLocale for message catalogues)
     dev dependencies       : lombokfuzzer (fuzz harness)
```

## 2. Example consumers in the ecosystem

The library is standalone and usable by anyone. Lombok applications and libraries that can use it (the dependency direction is always consumer -> library):

| Consumer | Usage |
|---|---|
| LombokPDF (application) | embedding CSV tables into documents |
| LombokRAGFrameworks (application) | CSV loader |
| LombokClarion (framework, optional) | data-import preview |

## 3. Feature x port map

| Feature | TypeScript | Python | Go | PHP |
|---|---|---|---|---|
| parseRows / parse / types | YES (vectors pass) | YES (vectors pass) | YES (vectors pass) | YES (vectors pass) |
| toHTML | YES | YES | YES | YES |
| toJSON | YES | YES | YES | YES |
| aggregate | YES | YES | YES | YES |

All four ports run the same 152 shared cases (`vectors/lombokcsv-vectors-v1.json`) in CI on three operating systems; a port is listed only when its runner passes every case (GP-11).

## 4. Cross-repo dependency graph

```
                  LombokVector (senior reference repo, structure + CI/release pattern)
                        |  pattern only (no code dependency)
                        v
LombokCSV  <-------- consumers (LombokPDF, LombokRAGFrameworks, LombokClarion, ...)
     |
     +-- dev: lombokfuzzer (npm)
```

LombokCSV has no file:, path:, or version dependency on any other ecosystem repository; the only ecosystem coupling is the shared doctor/CI convention.

---

*Document license: Apache-2.0 · © codinglombok*
