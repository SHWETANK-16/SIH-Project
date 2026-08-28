# Contributing

Use focused feature branches and small pull requests. Keep routes thin, schemas typed, services testable, and external systems behind interfaces. Never commit real financial or personal data, credentials, `.env` files, virtual environments, build output, or `node_modules`.

Before a pull request:

1. Run `pytest` from `backend/`.
2. Run `npm run build` from `frontend/`.
3. Confirm mock values remain visibly labeled.
4. Update API types on both sides when a contract changes.
5. Document new dependency wiring in `ARCHITECTURE.md`.

Do not add a database or real intelligence model without an agreed architecture change. Preserve the distinction between risk signals and guilt.
