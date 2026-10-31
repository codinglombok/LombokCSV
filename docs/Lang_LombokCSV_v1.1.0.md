# LombokCSV — Language & i18n v1.1.0

| Attribute | Value |
|---|---|
| Version | 1.1.0 |
| i18n level (masterplan §13) | **E** — error codes and documentation; parser behaviour is locale-free |
| Message catalogue | no `locales/` files yet; message IDs reserved in §2 |
| Fallback | English text embedded in code |
| Current catalogue coverage | en + id (2/20) in the §2 table; Nusantara 0/6 |

## 1. Principles

1. Every error carries a stable `code` (SPEC §7). Programs MUST match on `code`, not on message text. The canonical message text is `[CODE] human message` and is byte-identical across ports.
2. The library never reads the system locale, environment variables, or time zones.
3. Numbers are only recognised in dot-decimal format without thousands separators (SPEC §3.1). `1.000,5` (Indonesian/European format) is recognised as a string. Locale-aware numbers are recorded as a gap in `full_summary_`.
4. Date patterns check shape only; both `24/07/2026` and `07/24/2026` are `date` because the day/month order depends on the locale and cannot be inferred.
5. Any Unicode text (Latin, Arabic, CJK, Nusantara scripts, emoji) is preserved as-is in fields; there is no NFC/NFKC normalisation.

## 2. Message ID catalogue (reserved)

| ID | Code | en | id |
|---|---|---|---|
| `lombokcsv.option.invalid` | `INVALID_OPTION` | [INVALID_OPTION] {$name} must be a single character other than CR/LF / delimiter and quote must differ | {$name} harus satu karakter selain CR/LF / delimiter dan quote harus berbeda |
| `lombokcsv.column.unknown` | `UNKNOWN_COLUMN` | [UNKNOWN_COLUMN] unknown column: {$column} / column index out of range: {$index} | Kolom tidak dikenal: {$column} / indeks kolom di luar jangkauan: {$index} |

## 3. RTL

The library produces no UI. The HTML output does not set `dir`; callers set `dir="rtl"` on a parent element for Arabic, Persian, or Urdu data.

## 4. Plans

- 1.2.0: `locales/en/lombokcsv.json` and `locales/id/lombokcsv.json`, loaded through LombokLocale when installed (optional dependency, never mandatory).
- Locale-aware number options (`decimal: ','`) after their behaviour is specified in the SPEC and vectors.

---

*Document license: Apache-2.0 · © codinglombok*
