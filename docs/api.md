# API Reference

## Interactive Documentation

The application automatically generates interactive API documentation from the OpenAPI specification.

| Type | URL | Description |
|------|-----|-------------|
| **Swagger UI** | `/schema/swagger` | Interactive API explorer |
| **ReDoc** | `/schema/redoc` | Alternative API documentation |
| **OpenAPI JSON** | `/schema/openapi.json` | Raw OpenAPI 3.x specification |

> Start the application with `uv run app run`, then visit `http://localhost:8000/schema/swagger` to explore the API.

## Authentication

- **Method**: JWT Bearer Token
- **Header**: `Authorization: Bearer <token>`
- **Token Refresh**: Refresh tokens are supported for long-lived sessions
- **MFA**: Optional TOTP-based multi-factor authentication
- **OAuth**: Third-party OAuth provider support via `httpx-oauth`

## Request / Response Conventions

- **Content-Type**: `application/json`
- **Pagination**: Offset-based pagination with `limit` and `offset` query parameters
- **Error Format**:

```json
{
  "status_code": 400,
  "detail": "Validation error message",
  "extra": {}
}
```

## Type Generation

After backend schema changes, regenerate the TypeScript client:

```bash
make types
```

This exports the OpenAPI schema and generates TypeScript types and an API client for the frontend.