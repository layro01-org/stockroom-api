# Intentional Security Findings — stockroom-api

> **DEMO ENVIRONMENT ONLY.** This document describes security vulnerabilities that have been deliberately introduced into this codebase to demonstrate Veracode Trust Authority Phase 1. This repository is a sandboxed sample application and is never deployed to production.

---

## Purpose

These findings exist to make the Trust Authority demo realistic. When the Veracode GitHub App runs a SAST Policy Scan and SCA scan against `stockroom-api`, it should surface one Critical static finding and one SCA vulnerability, causing the associated Asset Snapshot to **fail policy evaluation** and the Trust Engine to return `Unsafe to Ship`.

---

## Finding 1 — SQL Injection (SAST)

| Attribute | Value |
| --------- | ----- |
| **Type** | Static Analysis (SAST) |
| **CWE** | CWE-89: Improper Neutralization of Special Elements used in an SQL Command |
| **Severity** | Critical |
| **File** | `app/routers/search.py` |
| **Function** | `search_products` |

### What flaw was introduced

A new `/api/v1/search` endpoint was added that constructs a SQL query by directly interpolating the user-supplied `q` parameter into an f-string passed to SQLAlchemy's `text()`:

```python
query = (
    f"SELECT id, sku, name, description, unit_price, quantity_in_stock "
    f"FROM products "
    f"WHERE name ILIKE '%{q}%' "
    f"OR sku ILIKE '%{q}%' "
    f"OR description ILIKE '%{q}%' "
    f"ORDER BY name"
)
result = await db.execute(text(query))
```

### Why the flaw is a finding

The search term `q` arrives from an HTTP query parameter and is interpolated directly into the SQL string without sanitisation or parameterisation. An attacker can inject arbitrary SQL — for example:

```rest
GET /api/v1/search?q='; DROP TABLE products; --
```

Veracode SAST traces the taint flow from the HTTP input (`Query(...)`) through the f-string into the `text()` call, classifying this as CWE-89 SQL Injection at Critical severity.

### The secure fix for the flaw (not applied — intentional)

Use SQLAlchemy's parameterised `text()` with `bindparams`:

```python
from sqlalchemy import text

query = text(
    "SELECT id, sku, name, description, unit_price, quantity_in_stock "
    "FROM products "
    "WHERE name ILIKE :term OR sku ILIKE :term OR description ILIKE :term "
    "ORDER BY name"
)
result = await db.execute(query, {"term": f"%{q}%"})
```

---

## Finding 2 — Vulnerable Dependency: requests 2.25.1 (SCA)

| Attribute | Value |
| --------- | ----- |
| **Type** | Software Composition Analysis (SCA) |
| **Package** | `requests` |
| **Pinned version** | `2.25.1` |
| **CVE** | CVE-2023-32681 |
| **CVSS** | 6.1 (Medium) |
| **File** | `pyproject.toml` |

### What SCA vulnerability was introduced

`requests==2.25.1` was added as a pinned dependency in `pyproject.toml`. The pin is intentionally below the patched version.

### Why the vulnerability is a finding

CVE-2023-32681 affects `requests < 2.31.0`. When a redirect crosses from HTTPS to HTTP, the `Proxy-Authorization` header is leaked to the unintended destination host. In a backend service that proxies user-initiated requests (e.g. fetching product data from a third-party supplier API), this could allow a network-positioned attacker to intercept proxy credentials.

Patched in `requests==2.31.0`.

### The secure fix for the vulnerability (not applied — intentional)

Upgrade the constraint:

```toml
"requests>=2.31.0",
```

---

## Demo Script Notes

- **Policy that fires:** The "Stockroom Deployment Policy" is configured with the rule: *block on any Critical SAST finding OR any High SCA vulnerability*. Finding 1 (CWE-89, Critical SAST) is sufficient on its own to trigger a `Block Deployment` action.
- **Which scan type surfaces which finding:**
  - SAST Policy Scan → Finding 1 (SQL Injection)
  - SCA scan → Finding 2 (requests CVE)
- **Expected platform verdict:** Asset Snapshot for `stockroom-api` → **Policy Failed** → Trust Engine returns `Unsafe to Ship`.
- **Reset path (approved demo):** Remove `app/routers/search.py`, revert to parameterised queries, and upgrade `requests` to `>=2.31.0`. The next scan will produce a clean snapshot, and the Trust Engine will return `Safe to Ship`.
