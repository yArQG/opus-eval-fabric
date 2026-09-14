# Security

Do not put secrets, tokens, private source material, or production credentials in issues, fixtures, examples, or receipts.

The core package is intentionally non-effectful. Adapters that can mutate external systems must implement explicit authority checks and fail closed when authorization cannot be verified.
