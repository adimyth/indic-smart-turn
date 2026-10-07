# Project conventions

## Commits

- Every commit message follows [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/): `<type>(<optional scope>): <description>`, optional body separated by a blank line, optional footers. Types used here: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `build`, `ci`. Breaking changes use `!` after the type/scope or a `BREAKING CHANGE:` footer.
- Commit in logical, reviewable sections, never one dump of everything.
- Never add a `Co-Authored-By` line or any other AI attribution to commits or pull requests.

## Spending and approvals

- Ask before any step that spends money (LLM APIs, GPU time) or creates an external resource. State the estimated cost first.
- Plan first, implement after review: `PLAN.md` is the source of truth for stages and gates.

## Data handling

- `data/private/` is operator-only: never committed, synced to a pod, or sent to a third-party API.
- Secrets live in `.env` only; `.env.example` lists the keys.
