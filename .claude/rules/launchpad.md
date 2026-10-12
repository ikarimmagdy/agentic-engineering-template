---
paths:
  - "**/docker-compose*.yml"
  - "**/compose*.yaml"
  - "**/package.json"
  - "**/.env.example"
  - "**/Procfile"
  - "**/vite.config.*"
  - "**/next.config.*"
  - "**/k8s/**"
  - "**/kustomization.yaml"
---

# Launchpad rules

- A new app, service, port, database, seed/demo login, or deployed URL is
  recorded in the stream's `launchpad.json` (two levels up from `code/<repo>/`)
  in the same change. Run `/register-app`.
- Passwords and tokens go in only as `password_env: {file, key}` pointing at
  this repo's gitignored `.env`, never as values.
- Keep dev ports stable and distinct from other workspaces; check
  <http://127.0.0.1:8899> before picking one.
