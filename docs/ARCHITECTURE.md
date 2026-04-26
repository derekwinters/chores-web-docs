# Architecture

## System Overview

```mermaid
graph TB
    Client["Browser Client<br/>(React)"]
    Frontend["Frontend<br/>(React SPA)"]
    API["REST API<br/>(FastAPI)"]
    DB["Database<br/>(PostgreSQL)"]
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
    App["App.jsx<br/>(auth context)"]
    
    Pages["Pages/"]
    Dashboard["Dashboard.jsx"]
    Chores["Chores.jsx"]
    UserDetail["UserDetail.jsx"]
    Settings["Settings.jsx"]
    
    Components["Components/"]
    UserCard["UserCard.jsx"]
    ChoreList["ChoreList.jsx"]
    ChoreForm["ChoreForm.jsx"]
    ThemeSettings["ThemeSettings.jsx"]
    Log["Log.jsx"]
    
    Utils["Utils/"]
    Auth["auth.ts"]
    Theme["theme.ts"]
    PersonColors["personColors.ts"]
    
    API["API Client"]
    RQ["React Query"]
    
    App --> Pages
    App --> Components
    Pages --> Dashboard
    Pages --> Chores
    Pages --> UserDetail
    Pages --> Settings
    
    Dashboard --> UserCard
    Dashboard --> ChoreList
    Chores --> ChoreForm
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
    API["FastAPI App<br/>(main.py)"]
    
    Routers["Routers/"]
    AuthRouter["auth.py"]
    ChoresRouter["chores.py"]
    PeopleRouter["people.py"]
    PointsRouter["points.py"]
    LogRouter["log.py"]
    ThemeRouter["theme.py"]
    ConfigRouter["config.py"]
    ExportRouter["export.py"]
    ImportRouter["data_import.py"]
    
    Services["Services/"]
    ChoreService["chore_service.py"]
    Scheduler["scheduler.py"]
    ExportService["export_service.py"]
    ImportService["import_service.py"]
    
    Models["Models/"]
    Person["Person"]
    Chore["Chore"]
    PointsLog["PointsLog"]
    ChoreLog["ChoreLog"]
    TokenBlacklist["TokenBlacklist"]
    Settings["Settings"]
    
    Database["PostgreSQL Database"]
    
    API --> Routers
    
    AuthRouter --> ChoreService
    ChoresRouter --> ChoreService
    ExportRouter --> ExportService
    ImportRouter --> ImportService
    Routers --> Services
    Scheduler --> ChoreService
    
    ChoreService --> Models
    ExportService --> Models
    ImportService --> Models
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
    Defaults["DEFAULT_THEMES<br/>(hardcoded)"]
    Memory["Custom Themes<br/>(in-memory)"]
    Database["Database<br/>(Person.preferred_theme)"]
    CSS["CSS Variables<br/>(--bg, --surface, etc)"]
    
    Frontend -->|GET /theme/list| API
    API -->|fetch| Defaults
    API -->|fetch| Memory
    API -->|themes list| Frontend
    
    Frontend -->|POST /theme/save| API
    API -->|store| Memory
    
    Frontend -->|POST /theme/set/{id}| API
    API -->|save| Database
    Database -->|update| Frontend
    
    Frontend -->|DELETE /theme/delete/{id}| API
    API -->|remove| Memory
    
    Frontend -->|apply| CSS
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

## Points & Scoring System

Points are awarded when users complete chores, with goal tracking over 7-day and 30-day rolling windows.

```mermaid
graph TB
    Completion["User Completes<br/>Chore"]
    ChoreService["ChoreService<br/>complete_chore()"]
    PointsLog["PointsLog Entry<br/>(+points)"]
    PersonAggregate["Person.points<br/>(sum)"]
    GoalCheck["Check Goals<br/>(7d, 30d)"]
    
    Completion -->|call| ChoreService
    ChoreService -->|create| PointsLog
    PointsLog -->|aggregate| PersonAggregate
    PersonAggregate -->|evaluate| GoalCheck
    GoalCheck -->|display| UI["Dashboard<br/>Points Card"]
```

### Point Calculation

- **Award:** Chore completion = Chore.points awarded to person
- **Tracking:** PointsLog record created with (person, points, chore_id, completed_at)
- **Aggregation:** Person.points = sum of all PointsLog entries for that person
- **Goals:** Rolling 7-day and 30-day windows calculated from PointsLog timestamps
- **Reset:** Goals reset automatically at week/month boundaries based on completed_at timestamps

### Models

- **Person.points** – Total lifetime points (sum of all PointsLog)
- **Person.goal_7d** – Target points for 7-day rolling window
- **Person.goal_30d** – Target points for 30-day rolling window
- **PointsLog** – Transaction log: (id, person, points, chore_id, completed_at)

## Deployment Architecture

### Development

```
Frontend (npm dev)     -->  Backend (uvicorn)  -->  PostgreSQL
http://localhost:5173     http://localhost:8000
```

### Production

```
Docker Compose:
  - frontend:3000 (Nginx)    -->  backend:8000 (FastAPI)  -->  PostgreSQL
  - Backend initializes schema on startup
  - Scheduler runs inside backend container
  - Database persists in volume /var/lib/postgresql/data
```

### Development

```
Frontend (npm dev)     -->  Backend (uvicorn)  -->  PostgreSQL
http://localhost:5173     http://localhost:8000
```

### Production

```
Docker Compose:
  - frontend:3000 (Nginx)    -->  backend:8000 (FastAPI)  -->  PostgreSQL
  - Backend initializes schema on startup
  - Scheduler runs inside backend container
```

## Roles & Permissions

Two user roles with distinct capabilities:

### Admin Role
- Create/delete users
- Create/modify/delete chores
- Modify other users' settings and goals
- Export and import system data
- Access admin panel
- Perform all regular user operations

### Regular User Role
- View all chores and assignments
- Complete/skip assigned chores
- View personal points and progress
- Modify own settings and goals
- View audit log of actions
- Cannot create or modify chores
- Cannot manage other users

### Access Control

- **is_admin flag** in Person model determines role
- **Dependency injection** enforces auth checks via `get_current_user`
- **Route protection** via FastAPI `Depends(get_current_user)` on all protected endpoints
- **Admin-only routes** explicitly check `current_user.is_admin`

## Design Decisions & Rationale

### Database: PostgreSQL

**Why:** 
- Reliability and data integrity for multi-user households
- ACID compliance ensures consistency in point tracking and chore state
- Production-ready with replication options
- Scales better than SQLite for concurrent requests

**Trade-off:** Requires database server vs. file-based SQLite

### Scheduler: APScheduler

**Why:**
- Embedded scheduler (no external service required)
- Simple Python integration
- Automatic chore state transitions without manual intervention
- Runs in-process, no deployment complexity

**Trade-off:** Single-process scheduler, not distributed (sufficient for household use)

### Authentication: JWT with 365-Day Expiration

**Why:**
- Stateless authentication reduces server memory usage
- 365-day expiration provides convenience (no frequent re-login)
- Simple to implement in single-page application

**Trade-off:** Long expiration reduces security window; longer refresh token required for truly secure deployments

### Points System: Sum-Based Aggregation

**Why:**
- Simple, transparent scoring (points = effort)
- Historical tracking via PointsLog for audit
- Supports rolling window goals (7-day, 30-day)

**Trade-off:** No decay or weighting; old points count equally to recent points

### Frontend: React Query for State Management

**Why:**
- Client-side caching reduces API calls
- Automatic cache invalidation on mutations
- Optimistic updates improve perceived performance
- Handles loading and error states cleanly

**Trade-off:** Server-side state not shared across browser tabs (acceptable for household app)

### Architecture: Layered (Router → Service → Model → Database)

**Why:**
- Clean separation of concerns
- Testable business logic in services
- API contracts defined in schemas
- Easy to extend with new endpoints

**Trade-off:** More files/structure than monolithic approach

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
