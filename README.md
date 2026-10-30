# Bilingual Hreflang Configuration Linter for MENA Domains

> Catch hreflang return errors, wrong regional ISO codes, and currency mismatches across your Arabic and English domains.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Format: CLI_SCRIPT](https://img.shields.io/badge/Format-CLI--SCRIPT-green.svg)](#)
[![Tier: 2](https://img.shields.io/badge/Tier-2-orange.svg)](#)
[![Region: MENA](https://img.shields.io/badge/Region-Egypt%20%7C%20GCC%20%7C%20Saudi-purple.svg)](#)
[![Tests: Passing](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#)
[![Owner: mahmoudabdelnaby1](https://img.shields.io/badge/Owner-mahmoudabdelnaby1-blue.svg)](https://github.com/mahmoudabdelnaby1)

---

## 📌 Problem Statement & Target Persona

### Target Persona
**PRO** operating in high-growth e-commerce, digital publishing, and direct-response marketing across Saudi Arabia, UAE, and Egypt.

### Core Problem
Build a Python CLI (`hreflang_validator.py`) that audits bilingual Arabic/English XML sitemaps: 1) Validates language and country codes against official ISO 639-1 and ISO 3166-1 registries (strictly rejecting non-existent codes like `zz-xx`), 2) Enforces reciprocal bidirectional return links across URLs, 3) Treats `x-default` as an optional fallback in full alignment with official Google Search Central guidelines, 4) Generates structured JSON audit reports.

---

## 🛠️ Repository Architecture & Deliverables

This repository provides self-contained, documented implementations and specifications:

- `data/mena_iso_locales.json`
- `examples/audit_output.json`
- `examples/sample_sitemap.xml`
- `LICENSE`
- `README.md`
- `src/hreflang_validator.py`
- `tests/test_validator.py`


---

## 🚀 Quick Start & How to Run Locally

### Run Test Suite Locally
```bash
# Ensure no bytecode generation
export PYTHONDONTWRITEBYTECODE=1  # Linux / macOS
$env:PYTHONDONTWRITEBYTECODE="1"  # Windows PowerShell

# Run Python unittest discovery
python -m unittest discover -s tests
```

### Run CLI Script
```bash
# Validate sitemap against ISO registries and reciprocal linking rules
python src/hreflang_validator.py --sitemap examples/sample_sitemap.xml
```

---

## 📊 Sample Input & Output Fixtures

> **Data Disclosure:** Any included sample data is illustrative and may be synthetic; it is not a measured customer result or market benchmark unless a source and collection method are stated alongside it. These files run offline with standard libraries and require no paid third-party API credentials.

```json
{
  "sitemap_path": "examples/sample_sitemap.xml",
  "pages_audited": 2,
  "total_issues_found": 0,
  "issues": [],
  "status": "PASS",
  "official_spec_reference": "https://developers.google.com/search/docs/specialty/international/localized-versions"
}
```

---

## ⚠️ Known Technical & Domain Constraints

- **Official ISO Code Verification:** Codes must strictly exist in the official ISO 639-1 (language) and ISO 3166-1 alpha-2 (country) registries. Formats matching regex ^[a-z]{2}-[a-z]{2}$ but with fake entries (e.g. zz-xx) are flagged as fatal errors.
- **Hreflang Reciprocal Confirmation:** If Page A links to Page B via an alternate hreflang annotation, Page B must link back to Page A; missing return links cause search engines to disregard annotations.
- **Optional x-default:** In accordance with Google Search Central guidelines, x-default is recommended for unmatched landing pages, but its absence is never flagged as an error.

---

## 📚 Primary Documentation & Verifiable References

- [Google Search Central: Localized Versions (hreflang)](https://developers.google.com/search/docs/specialty/international/localized-versions) - Official multi-language SEO specification and reciprocal tagging rules.
- [ISO 639-1 Language Code Standards](https://www.iso.org/iso-639-language-codes.html) - International standard for official 2-letter language identifiers.
- [ISO 3166-1 Country Code Standards](https://www.iso.org/iso-3166-country-codes.html) - Official 2-letter country and territory codes.

---


## 👤 Maintainer & License

- **Author & Maintainer:** [Mahmoud Abdelnaby](https://github.com/mahmoudabdelnaby1) (`@mahmoudabdelnaby1`)
- **License:** [MIT License](LICENSE) - Open-source, auditable, and freely adaptable for internal enterprise or commercial use.
