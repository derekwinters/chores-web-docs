# Documentation

Complete documentation for the Chores application.

## Contents

- **[API Documentation](./API.md)** - REST API endpoints, request/response formats, examples
- **[Architecture](./ARCHITECTURE.md)** - System design, data model, component diagrams
- **[Developer Guide](./DEVELOPER.md)** - Setup, development workflow, testing
- **[Deployment](./DEPLOYMENT.md)** - Deployment instructions and configuration

## Quick Start

### For Users

Visit the application in your browser. See deployment documentation for setup.

### For Developers

1. Read [Developer Guide](./DEVELOPER.md) for local setup
2. Review [Architecture](./ARCHITECTURE.md) to understand system design
3. Reference [API Documentation](./API.md) when building features

## Project Structure

```
chores-web/
├── frontend/              # React SPA
│   ├── src/
│   │   ├── pages/        # Route pages
│   │   ├── components/   # Reusable components
│   │   ├── api/          # API client
│   │   └── utils/        # Utilities
│   └── package.json
├── backend/               # FastAPI REST API
│   ├── app/
│   │   ├── routers/      # API route handlers
│   │   ├── services/     # Business logic
│   │   ├── models.py     # Database models
│   │   └── schemas.py    # Data schemas
│   └── requirements.txt
└── docs/                 # This documentation
```

## Key Features

- **Household Chore Management** - Create, assign, and track chores
- **Flexible Scheduling** - Weekly, monthly, or interval-based schedules
- **Point System** - Award points for completed chores
- **User Assignments** - Rotating or fixed assignments
- **Audit Logging** - Complete history of all chore actions
- **Customizable Themes** - User-specific theme preferences
- **Multi-user Support** - Admin and regular user roles

## Technology Stack

**Frontend:**
- React 18
- React Query (Tanstack Query)
- Vitest + React Testing Library
- Vite

**Backend:**
- FastAPI
- SQLAlchemy ORM
- SQLite
- APScheduler
- Pydantic

**DevOps:**
- Docker & Docker Compose
- GitHub Actions (future)

## API Base URL

Swagger UI: `http://localhost:8000/docs`

## Contributing

1. Follow the architecture patterns in [Architecture](./ARCHITECTURE.md)
2. Write tests for new features
3. Update API documentation when adding/changing endpoints
4. Ensure 100% test passing before committing

## Support

For questions or issues, refer to the relevant documentation or examine the codebase.
