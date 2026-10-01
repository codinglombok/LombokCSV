# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 1.1.x | Yes |
| 1.0.x and older | No (upgrade to 1.1.x; 1.0.0 did not escape the `class` / `id` attributes of `toHTML`) |

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub Security Advisories:
<https://github.com/codinglombok/LombokCSV/security/advisories/new>.
Do not open a public issue. You should receive an acknowledgement within 3 working days and a fix or mitigation plan within 30 days.

## Scope and threat model

LombokCSV parses untrusted text and renders it as HTML. The guarantees are normative and listed in [SPEC section 8](docs/SPEC_LombokCSV_v1.1.0.md#8-keamanan-normatif):

- parsing runs in linear time and never throws on any input;
- every piece of text written by `toHTML`, including the `class` and `id` options, is escaped for element content and double-quoted attributes;
- the library performs no I/O and evaluates nothing.

Out of scope: CSV (formula) injection when data is exported back to a spreadsheet, and inserting the generated HTML inside `<script>`, `<style>`, or unquoted attributes.
