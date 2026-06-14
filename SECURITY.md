# Security Policy

Main Street Capital Access Atlas is a static public-data project. It does not collect user data, operate user accounts, process payments, or require secrets for the default build.

Security still matters because the project includes data pipelines, generated public files, GitHub Actions workflows, and optional credentials for source adapters.

## Supported Versions

The current `main` branch is the supported version. Public releases should be made from reviewed commits after tests pass and generated data has been inspected.

## Report A Vulnerability

Do not open a public issue for a suspected vulnerability, exposed secret, or accidental private-data disclosure.

Use GitHub private vulnerability reporting if it is enabled on the hosted repository. If it is not enabled, contact the repository owner or maintainers through their preferred private channel and include:

- A short description of the issue.
- Affected files, workflows, generated artifacts, or pages.
- Steps to reproduce or verify the issue.
- Whether any private, sensitive, or credential-like data may be exposed.

Maintainers should acknowledge credible reports promptly, preserve evidence, remove exposed sensitive material from public artifacts when possible, rotate any affected credentials, and document the remediation in release notes or a public issue after sensitive details are no longer exposed.

## Sensitive Data Rules

Do not contribute:

- Private, personally identifiable, household-level, applicant-level, or account-level data.
- Business names, owner names, addresses, phone numbers, emails, application IDs, or bank account details.
- API keys, tokens, cookies, access logs, or credentials.
- Proprietary datasets or data that cannot be redistributed in a public open-source repository.

Manual data imports must be aggregated to county level and follow `data/manual/README.md`.

## Dependency And Workflow Hygiene

- Keep dependencies minimal and pinned through `pyproject.toml` constraints where practical.
- Keep the default build free of required secrets.
- Store optional API keys only in local environment variables or GitHub Actions secrets.
- Review GitHub Actions changes carefully because workflows can access generated artifacts and optional repository secrets.
- Run `python -m pytest` and `python -m ruff check .` before publishing a release.

## Data Integrity Incidents

If a public source changes format, a generated file appears corrupted, or county values look materially wrong, open a data issue rather than a security report unless sensitive data or credentials are involved.
