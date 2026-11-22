---
paths:
  - "**/migrations/**"
  - "**/*.sql"
  - "code/**/database/**"
---

# Database rules

- Schema changes only through migrations; never edit an applied migration.
- Every migration is reversible or says why not.
- Personal data columns are classified in a comment or the data catalogue.
- Audit tables are append-only: no update or delete path, ever.
- Dumps, backups and real customer data never enter git; restored production data stays local and is deleted when the work ends.
- Local database servers bind to 127.0.0.1; passwords come from a gitignored `.env`.
