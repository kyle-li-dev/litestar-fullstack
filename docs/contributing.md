# Contributing

## Setting up the Environment

1. Install [Astral's UV](https://docs.astral.sh/uv/) if you don't have it: `make install-uv`
2. Run `uv sync --all-groups` to create a virtual environment and install all dependencies
3. Install [pre-commit](https://pre-commit.com/)
4. Run `pre-commit install` to install pre-commit hooks

!!! tip "Quick Setup"
    Run `make install` to do everything above in one step (installs UV, creates venv, installs deps, and sets up pre-commit).

## Code Contributions

### Workflow

1. [Fork](https://github.com/kyle-li-dev/litestar-fullstack/fork) the repository
2. Clone your fork locally with git
3. [Set up the environment](#setting-up-the-environment)
4. Make your changes
5. (Optional) Run `pre-commit run --all-files` to run linters and formatters
6. Commit your changes to git
7. Push the changes to your fork
8. Open a [pull request](https://docs.github.com/en/pull-requests) with a descriptive title

!!! tip "Conventional Commits"
    All pull requests and commits must follow the [Conventional Commit format](https://www.conventionalcommits.org).
    Example: `fix: Make needles easier to find by applying fire to haystack`

## Git Branching Strategy

### Branch Hierarchy

```
feature/* --> dev --> main
```

| Branch | Purpose |
|---|---|
| **main** | Production-stable release branch |
| **dev** | Development integration branch |
| **feature/*** | Individual feature branches |

### Workflow

```
feature/*  -->  Local Testing
                   |
                   v
   dev     -->  Dev Environment (Integration Testing)
                   |
                   v
  main     -->  Staging (Pre-release Verification)
                   |
                   v
   tag     -->  Production (Official Release)
```

1. **Create** a `feature/*` branch from `dev`.
2. **Develop & test** locally on the feature branch.
3. **Rebase** the feature branch onto `dev` and push.
4. **Verify** on the dev environment (integration testing).
5. **Rebase** `dev` onto `main` for staging verification.
6. **Tag** a release on `main` and deploy to production.

### Rules

> **Linear history is mandatory. Merge commits are forbidden.**

- Always use `git rebase` instead of `git merge`.
- Before pushing a feature branch, rebase it onto the latest `dev`:
  ```bash
  git checkout feature/my-feature
  git fetch origin
  git rebase origin/dev
  ```
- Use `--force-with-lease` when pushing rebased branches:
  ```bash
  git push --force-with-lease
  ```
- Never use `git merge`. If a merge commit is accidentally created, use interactive rebase to remove it.
- Keep commits atomic and meaningful — squash WIP commits before rebasing onto `dev`.

## Version Management

This project uses [bump-my-version](https://github.com/callowayproject/bump-my-version) with [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).

### Version Sources

The version is kept in sync across two files:

| File | Field |
|---|---|
| `pyproject.toml` | `version` |
| `src/js/web/package.json` | `version` |

Both are updated automatically by `bump-my-version`.

### Bump Version

```bash
make release bump=patch   # 0.1.0 → 0.1.1  (bug fixes)
make release bump=minor   # 0.1.0 → 0.2.0  (new features)
make release bump=major   # 0.1.0 → 1.0.0  (breaking changes)
```

This command will:

1. Clean the workspace (`make clean`).
2. Update the version in `pyproject.toml` and `src/js/web/package.json`.
3. Auto-commit with message: `Bump version: {old} → {new}` (skips pre-commit hooks).
4. Auto-create git tag `vX.X.X`.
5. Build the project (`make build`).

!!! warning
    `allow_dirty = false` — your working tree must be clean before running `make release`.

### Release Workflow

```
feature/* → dev (integration testing)
                ↓
             main (staging verification)
                ↓
        make release bump=patch/minor/major
                ↓
          git push (push the bump commit)
                ↓
     Release + Tag vX.X.X → Production
```

1. Ensure all features are merged into `main` via rebase and staging is verified.
2. Run `make release bump=<patch|minor|major>` on the `main` branch.
3. Push the commit and tag: `git push && git push --tags`.
4. Create a Release linked to the auto-generated tag `vX.X.X`.

## Development

### Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install dev environment from scratch |
| `make upgrade` | Upgrade all dependencies |
| `make lint` | Run all linters (ruff, mypy, pyright, slotscheck, biome, codespell) |
| `make test` | Run test suite |
| `make test-all` | Run all tests |
| `make coverage` | Run tests with coverage report |
| `make types` | Export OpenAPI schema and generate TypeScript types |
| `make docs-serve` | Serve documentation locally |
| `make docs` | Build documentation |

### Database Migrations

```bash
# Create a new migration
uv run app database make-migrations

# Apply migrations
uv run app database upgrade
```

### Starting the Server

**Development** (with Vite hot-reload):

```bash
cp .env.local.example .env
uv run app run
```

Set `VITE_DEV_MODE=true` to enable the Vite dev server.

**Production**:

```bash
uv run app assets build
uv run app run
```

### Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Application secret key (generate with `openssl rand -base64 32`) |
| `DATABASE_URL` | PostgreSQL connection string |
| `APP_URL` | Application base URL |
| `ALLOWED_CORS_ORIGINS` | Allowed CORS origins |
| `VITE_DEV_MODE` | Enable Vite dev server (`true`/`false`) |
| `VITE_PORT` | Vite dev server port (default: `3006`) |
| `SAQ_USE_SERVER_LIFESPAN` | Auto start/stop SAQ workers with the app |

## Documentation

The documentation is located in `/docs` and is built with [MkDocs](https://www.mkdocs.org/) using the [Material](https://squidfundinglab.github.io/mkdocs-material/) theme.

To run the docs locally:

```bash
uv sync --group docs
make docs-serve
```

Guidelines for writing docs:

- Write in clear, simple language
- Keep examples self-contained
- Provide links where applicable
- Use [Mermaid](https://mermaid.js.org/) diagrams where helpful