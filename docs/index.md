# Documentation

User-facing documentation for the Chores application.

## Contents

- **[User Guide](./user-guide/getting-started.md)** - How to use the app, features, FAQ, troubleshooting
- **[API Documentation](./api/index.md)** - REST API endpoints, request/response formats, examples
- **[Deployment](./deployment/setup.md)** - Deployment instructions and configuration
- **[Blog](./blog/index.md)** - Release announcements

## Quick Start

### For Users

Visit the application in your browser. See [deployment documentation](./deployment/setup.md) for setup.

### For Developers

Development happens across separate repositories; each carries its own
developer documentation:

| Repository | Purpose |
|---|---|
| [chores-web-backend](https://github.com/derekwinters/chores-web-backend) | FastAPI REST API (architecture docs, ADRs, developer guide) |
| [chores-web-frontend](https://github.com/derekwinters/chores-web-frontend) | React SPA |
| [chores-web-android](https://github.com/derekwinters/chores-web-android) | Native Android client |
| [chores-web-ha-plugin](https://github.com/derekwinters/chores-web-ha-plugin) | Home Assistant integration |
| [chores-web-design-tokens](https://github.com/derekwinters/chores-web-design-tokens) | Shared design tokens |
| [chores-web-actions](https://github.com/derekwinters/chores-web-actions) | Shared CI actions and workflows |

## The API Contract

This repository owns the API contract: the golden OpenAPI snapshot at
`docs/api/openapi.json` and the `API_VERSION` file at the repo root.
Backend changes are checked against this contract in CI — breaking changes
require a pull request here first. See [API Documentation](./api/index.md).

## Key Features

- **Household Chore Management** - Create, assign, and track chores
- **Flexible Scheduling** - Weekly, monthly, or interval-based schedules
- **Point System** - Award points for completed chores
- **User Assignments** - Rotating or fixed assignments
- **Audit Logging** - Complete history of all chore actions
- **Customizable Themes** - User-specific theme preferences
- **Multi-user Support** - Admin and regular user roles

## API Base URL

Swagger UI on a running instance: `http://localhost:8000/docs`

## Support

For questions or issues, refer to the relevant documentation or open an
issue in the matching repository.
