# Architecture

## System Overview

```mermaid
graph TB
    Client["Browser Client<br/>(React)"]
    Frontend["Frontend<br/>(React SPA)"]
    API["REST API<br/>(FastAPI)"]
    DB["Database<br/>(SQLite)"]
    Scheduler["Scheduler<br/>(APScheduler)"]
    
    Client -->|HTTP| Frontend
    Frontend -->|HTTP/REST| API
    API -->|SQL| DB
    Scheduler -->|Async Tasks| API
    API -->|Update| DB
```

## Frontend Architecture

```mermaid
graph TB
    App["App<br/>(auth context)"]
    
    Pages["Pages"]
    Dashboard["Dashboard"]
    Manage["Manage"]
    UserDetail["UserDetail"]
    Settings["Settings"]
    
    Components["Components"]
    UserCard["UserCard"]
    ChoreList["ChoreList"]
    ChoreForm["ChoreForm"]
    ThemeSettings["ThemeSettings"]
    Log["Log"]
    
    Utils["Utils"]
    Auth["auth.ts"]
    Theme["theme.ts"]
    PersonColors["personColors.ts"]
    
    API["API Client"]
    RQ["React Query"]
    
    App --> Pages
    App --> Components
    Pages --> Dashboard
    Pages --> Manage
    Pages --> UserDetail
    Pages --> Settings
    
    Dashboard --> UserCard
    Dashboard --> ChoreList
    Manage --> ChoreForm
    Settings --> ThemeSettings
    Settings --> Log
    
    Components --> API
    Pages --> API
    API --> RQ
    RQ -->|HTTP| Backend["Backend API"]
    
    Components --> Utils
    Pages --> Utils
```

## Backend Architecture

```mermaid
graph TB
    API["FastAPI App"]
    
    Routers["Routers"]
    AuthRouter["auth.py"]
    ChoresRouter["chores.py"]
    PeopleRouter["people.py"]
    PointsRouter["points.py"]
    LogRouter["log.py"]
    ThemeRouter["theme.py"]
    ConfigRouter["config.py"]
    
    Services["Services"]
    ChoreService["chore_service.py"]
    Scheduler["scheduler.py"]
    
    Models["Models"]
    Person["Person"]
    Chore["Chore"]
    PointsLog["PointsLog"]
    ChoreLog["ChoreLog"]
    TokenBlacklist["TokenBlacklist"]
    
    Database["SQLite Database"]
    
    API --> Routers
    
    AuthRouter --> ChoreService
    ChoresRouter --> ChoreService
    Routers --> Services
    Scheduler --> ChoreService
    
    ChoreService --> Models
    Routers --> Models
    
    Models --> Database
    Scheduler -->|async| Database
```

## Data Model

```mermaid
erDiagram
    PERSON ||--o{ CHORE : assigns
    PERSON ||--o{ POINTSLOG : earns
    PERSON ||--o{ CHORELOG : acts_on
    CHORE ||--o{ POINTSLOG : awards
    CHORE ||--o{ CHORELOG : logs
    PERSON ||--o{ TOKENBLACKLIST : invalidates

    PERSON {
        int id PK
        string name UK
        string username UK
        string password_hash
        bool is_admin
        string color
        int goal_7d
        int goal_30d
        string preferred_theme
    }

    CHORE {
        int id PK
        string unique_id UK
        string name
        string schedule_type
        json schedule_config
        string assignment_type
        json eligible_people
        string assignee
        int points
        string state
        bool disabled
        date next_due
        string current_assignee
        int rotation_index
        timestamp last_changed_at
        string last_changed_by
        string last_change_type
        timestamp last_completed_at
        string last_completed_by
    }

    POINTSLOG {
        int id PK
        string person FK
        int points
        string chore_id FK
        timestamp completed_at
    }

    CHORELOG {
        int id PK
        string chore_id FK
        string chore_name
        string person FK
        string action
        timestamp timestamp
        string reassigned_to
    }

    TOKENBLACKLIST {
        int id PK
        string token_jti UK
        timestamp invalidated_at
        timestamp expires_at
    }
```

## Request/Response Flow

### Authentication

```mermaid
sequenceDiagram
    Client->>API: POST /auth/login (username, password)
    API->>Database: Query person by username
    Database-->>API: Person object
    API->>API: Hash password, compare
    API-->>Client: {access_token, user_info}
    Client->>Client: Store token in localStorage
    Note over Client: Add to Authorization header
```

### Chore Completion

```mermaid
sequenceDiagram
    Client->>API: POST /chores/{id}/complete
    API->>Database: Get chore
    API->>ChoreService: complete_chore()
    ChoreService->>Database: Add PointsLog
    ChoreService->>Database: Add ChoreLog (action=completed)
    ChoreService->>ChoreService: Calculate next_due
    ChoreService->>Database: Update chore state
    Database-->>ChoreService: Refresh chore
    ChoreService-->>API: Updated chore
    API-->>Client: ChoreOut (200)
    Client->>Client: Invalidate React Query cache
    Client->>Client: Refetch chores
```

### Automatic Schedule Transition

```mermaid
sequenceDiagram
    Scheduler->>Scheduler: Every minute, check overdue chores
    Scheduler->>Database: Query state=complete AND next_due <= today
    Database-->>Scheduler: List of chores
    Scheduler->>ChoreService: transition_overdue_chores()
    ChoreService->>Database: Add ChoreLog (action=marked_due_by_schedule)
    ChoreService->>Database: Update chore state to 'due'
    Note over ChoreService: Runs automatically, person=system
```

## Frontend Data Flow

```mermaid
graph TB
    QueryClient["React Query<br/>Client"]
    Cache["Query Cache"]
    
    Pages["Pages/Components"]
    useQuery["useQuery()"]
    useMutation["useMutation()"]
    
    API["API Client<br/>(client.js)"]
    HTTP["HTTP"]
    Backend["Backend"]
    
    Pages -->|fetch| useQuery
    useQuery -->|cache hit?| Cache
    useQuery -->|cache miss| API
    Pages -->|mutate| useMutation
    useMutation --> API
    API -->|REST| HTTP
    HTTP --> Backend
    Backend -->|response| HTTP
    HTTP --> API
    API -->|invalidate| Cache
    Cache -->|refetch| useQuery
    useQuery -->|state| Pages
```

## Authentication Flow

```mermaid
graph TB
    Setup["System Setup?"]
    Login["Login Page"]
    Auth["Auth Context"]
    Protected["Protected Pages"]
    
    Setup -->|No| Login
    Login -->|username/password| Auth
    Auth -->|validate| Backend["Backend JWT"]
    Backend -->|token| Auth
    Auth -->|store token| Storage["localStorage"]
    Auth -->|in state| Protected
    Protected -->|token in header| Backend
    Backend -->|verify| Auth
    Auth -->|invalid| Login
```

## Chore State Machine

```mermaid
stateDiagram-v2
    [*] --> Complete: Created
    
    Complete --> Due: schedule triggered<br/>or manual mark-due
    Due --> Complete: completed or skipped
    
    Complete --> Disabled: chore disabled
    Due --> Disabled: chore disabled
    Disabled --> Complete: chore enabled
    Disabled --> Due: chore enabled
    
    Complete --> [*]: deleted
    Due --> [*]: deleted
    Disabled --> [*]: deleted
```

## Theme System

```mermaid
graph TB
    Frontend["Frontend<br/>(ThemeSettings)"]
    API["Theme API"]
    Memory["In-Memory<br/>Custom Themes"]
    Database["Database<br/>(Person.preferred_theme)"]
    
    Frontend -->|GET /theme/list| API
    API -->|DEFAULT_THEMES| API
    API -->|_custom_themes| Memory
    
    Frontend -->|POST /theme/save| API
    API -->|save| Memory
    
    Frontend -->|POST /theme/set/{id}| API
    API -->|save to| Database
    Database -->|return| Frontend
    
    Frontend -->|DELETE /theme/delete/{id}| API
    API -->|remove| Memory
    
    Frontend -->|CSS Variables| CSS["Styles<br/>--bg, --surface, etc"]
```

## Scheduler Architecture

```mermaid
graph TB
    Init["App Startup"]
    Scheduler["APScheduler"]
    Queue["Job Queue"]
    
    Task1["Every Minute:<br/>transition_overdue_chores()"]
    
    Init -->|start| Scheduler
    Scheduler -->|enqueue| Queue
    Queue -->|execute| Task1
    Task1 -->|mark due| Database["Database"]
    Database -->|log action| ChoreLog["ChoreLog<br/>person=system"]
```

## Deployment Architecture

### Development

```
Frontend (npm dev)     -->  Backend (uvicorn)  -->  SQLite DB
http://localhost:5173     http://localhost:8000
```

### Production

```
Docker Compose:
  - frontend:3000 (Nginx)    -->  backend:8000 (FastAPI)  -->  SQLite
  - Backend initializes DB on startup
  - Scheduler runs inside backend container
```

## Security Considerations

1. **Authentication:** JWT tokens with 365-day expiration
2. **Password:** SHA256 pre-hash before bcrypt
3. **Token Blacklist:** InvalidTokenList in DB for logout
4. **CORS:** Configured for frontend origin
5. **Input Validation:** Pydantic schemas validate all inputs
6. **Admin Actions:** is_admin flag protects sensitive operations

## Performance Optimizations

1. **React Query:** Client-side caching of queries
2. **Query Invalidation:** Precise cache invalidation after mutations
3. **Async Database:** AsyncSession for non-blocking I/O
4. **Scheduler:** Single background process for system events
5. **Database Indexes:** unique_id, username, state, next_due (implicit)

## Future Scalability

- **Multi-user:** Already supports multiple Person records
- **Custom Themes:** In-memory store, could migrate to database
- **Logging:** ChoreLog ready, system events populated
- **API Clients:** Can be extended beyond React frontend
- **Real-time Updates:** WebSocket support could be added
