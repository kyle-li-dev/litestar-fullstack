# Litestar Fullstack Reference Application

A production-ready fullstack web application built on [Litestar](https://litestar.dev), React 19, and [Vite](https://vitejs.dev/).

## Features

- **SPA Frontend** — React 19 + Vite + TailwindCSS (SPA mode via [litestar-vite](https://github.com/cofin/litestar-vite))
- **JWT Auth** — Refresh tokens, MFA (TOTP), OAuth, and admin tooling
- **Service/Repository Pattern** — UUIDv7 primary keys with [Advanced Alchemy](https://docs.advanced-alchemy.litestar.dev)
- **Background Jobs** — [SAQ](https://saq-py.readthedocs.io) workers with structured logging via [structlog](https://www.structlog.org)
- **Docker Ready** — Dockerized development and production workflows (distroless)

## Quick Start

```bash
make install
cp .env.local.example .env
make start-infra
uv run app database upgrade
uv run app run
```

Or run everything in Docker:

```bash
docker compose up
```

## Documentation

| Document | Description |
|---|---|
| [API Reference](api.md) | OpenAPI endpoints & conventions |
| [Contributing](contributing.md) | Dev setup, Git strategy, versioning, testing |
| [Changelog](changelog.md) | Release history |
| [Roadmap](roadmap.md) | Product planning |

## License

This is a proprietary project. See [Third-Party Licenses](license.md) for open-source dependencies.