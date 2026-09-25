#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p docs/superpowers/plans docs/adr
cat > docs/superpowers/plans/2026-09-19-feature.md <<'MD'
# Plan: export invoices as CSV

## Context
Finance downloads invoices one by one from the admin screen. They asked for a
monthly CSV export.

## Decision
Add `GET /invoices/export?month=YYYY-MM` streaming CSV from the read replica.
Reuse the existing `InvoiceQuery`; no new table.

## Steps
1. Add the endpoint behind the `finance` role.
2. Stream rows with a cursor, 500 at a time.
3. Add an integration test with 3 invoices across two months.
4. Document the column order in the API reference.

## Risks
- Large months (50k+ rows) could hold a replica connection for minutes.
- Column order is a contract once finance builds spreadsheets on it.
MD
cat > docs/adr/0002-new-database.md <<'MD'
# ADR 0002: move the reporting store from MySQL to PostgreSQL

Status: proposed

## Context
Reporting queries use window functions and JSON aggregation that MySQL 5.7 does
not support well. The reporting store is read-only for the app and refreshed
nightly by an ETL job.

## Decision
Create a PostgreSQL 16 instance for reporting; the ETL writes to it instead of
MySQL. The transactional database stays on MySQL.

## Consequences
- Two engines to operate and back up.
- The ETL needs a new writer; the app's reporting DAO changes its driver.
- Rollback: point the ETL and the DAO back at MySQL; data is rebuilt nightly.

## Alternatives
- Upgrade MySQL to 8.0 (window functions available).
- Keep MySQL and precompute aggregates in the ETL.
MD
git add -A
git commit -q -m "chore: initial import"
