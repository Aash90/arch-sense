# Server Scaffold File Structure

## Full File Tree

```
server/
├── src/
│   ├── index.ts                          (184 lines) - Application entry point
│   │   ├── Imports middleware & services
│   │   ├── Database initialization
│   │   ├── AI service initialization
│   │   ├── Express app configuration
│   │   ├── Graceful shutdown handlers
│   │   └── Server startup on port 3000
│   │
│   ├── types.ts                          (113 lines) - Shared type definitions
│   │   ├── enum ComponentType (11 types)
│   │   ├── interface SystemNode
│   │   ├── interface SystemEdge
│   │   ├── interface SimulationState
│   │   ├── interface Message
│   │   ├── interface Evaluation
│   │   ├── type DesignSignal (5 types)
│   │   ├── interface SessionData
│   │   ├── interface UpdateSessionRequest
│   │   ├── interface ArchitectFeedbackRequest
│   │   ├── interface FinalEvaluationRequest
│   │   ├── interface ApiResponse<T>
│   │   └── interface PaginationParams
│   │
│   ├── config/
│   │   └── index.ts                      (51 lines) - Configuration management
│   │       ├── Load .env file
│   │       ├── Export config object
│   │       ├── validateConfig() function
│   │       └── Support for custom paths
│   │
│   ├── db/
│   │   └── index.ts                      (268 lines) - Database layer
│   │       ├── initializeDatabase() - Setup & schema creation
│   │       ├── getDatabase() - Accessor
│   │       ├── createTables() - Schema definition
│   │       ├── closeDatabase() - Cleanup
│   │       └── sessionDb object with methods:
│   │           ├── create(id, initialData) → SessionData
│   │           ├── get(id) → SessionData | null
│   │           ├── update(id, updates) → SessionData | null
│   │           ├── delete(id) → boolean
│   │           └── listAll(limit, offset) → SessionData[]
│   │
│   ├── middleware/
│   │   ├── errorHandler.ts               (50 lines) - Error handling
│   │   │   ├── AppError class
│   │   │   ├── errorHandler middleware
│   │   │   └── notFoundHandler middleware
│   │   │
│   │   └── logger.ts                     (60 lines) - Request logging
│   │       ├── createLogger() - Logger factory
│   │       ├── logger singleton
│   │       ├── log(level, message, data)
│   │       ├── error/warn/info/debug methods
│   │       └── requestLogger middleware
│   │
│   ├── services/
│   │   ├── sessionService.ts             (152 lines) - Session business logic
│   │   │   ├── SessionService class
│   │   │   ├── createSession(scenario)
│   │   │   ├── getSession(id)
│   │   │   ├── updateSession(id, updates)
│   │   │   ├── deleteSession(id)
│   │   │   ├── listSessions(limit, offset)
│   │   │   ├── getSessionSummary(session)
│   │   │   ├── analyzeArchitectureSignals(nodes, edges)
│   │   │   └── validateSessionData(data)
│   │   │
│   │   └── aiService.ts                  (174 lines) - Gemini AI integration
│   │       ├── AIService class
│   │       ├── initialize() - Setup Gemini client
│   │       ├── getArchitectFeedback() - Real-time feedback
│   │       ├── getFinalEvaluation() - Scoring & assessment
│   │       └── getArchitectMessage() - Conversational AI
│   │
│   ├── controllers/
│   │   ├── sessionController.ts          (155 lines) - Session handlers
│   │   │   ├── SessionController class
│   │   │   ├── getSessions() - GET /api/sessions
│   │   │   ├── createSession() - POST /api/sessions
│   │   │   ├── getSession() - GET /api/sessions/:id
│   │   │   ├── updateSession() - POST /api/sessions/:id (auto-signals)
│   │   │   ├── deleteSession() - DELETE /api/sessions/:id
│   │   │   └── getSessionSummary() - GET /api/sessions/:id/summary
│   │   │
│   │   └── aiController.ts               (162 lines) - AI feedback handlers
│   │       ├── AIController class
│   │       ├── getArchitectFeedback() - POST /api/ai/feedback
│   │       ├── evaluateDesign() - POST /api/ai/evaluate
│   │       └── sendMessage() - POST /api/ai/message
│   │
│   └── routes/
│       ├── index.ts                      (12 lines) - Route aggregation
│       │   └── Combines all route modules
│       │
│       ├── health.ts                     (14 lines) - Health check
│       │   └── GET /api/health
│       │
│       ├── sessions.ts                   (19 lines) - Session routes
│       │   ├── GET /api/sessions
│       │   ├── POST /api/sessions
│       │   ├── GET /api/sessions/:id
│       │   ├── POST /api/sessions/:id
│       │   ├── GET /api/sessions/:id/summary
│       │   └── DELETE /api/sessions/:id
│       │
│       └── ai.ts                         (16 lines) - AI routes
│           ├── POST /api/ai/feedback
│           ├── POST /api/ai/evaluate
│           └── POST /api/ai/message
│
├── .env.example                          - Environment template
├── package.json                          - Dependencies & scripts
├── tsconfig.json                         - TypeScript configuration
└── README.md                             - Comprehensive documentation

Total: 17 files, ~1,500 lines of production code
```

## File Dependencies

```
index.ts (Entry)
├─ config/index.ts → environment setup
├─ db/index.ts → database initialization
├─ services/aiService.ts → AI integration
├─ services/sessionService.ts
├─ middleware/logger.ts
├─ middleware/errorHandler.ts
└─ routes/index.ts
   ├─ routes/health.ts
   ├─ routes/sessions.ts
   │  └─ controllers/sessionController.ts
   │     └─ services/sessionService.ts
   │        └─ db/index.ts
   └─ routes/ai.ts
      └─ controllers/aiController.ts
         ├─ services/aiService.ts
         │  └─ config/index.ts
         └─ services/sessionService.ts
```

## Module Breakdown

### Core Modules (4)
- **index.ts** - Express app creation & startup
- **types.ts** - Type definitions (shared with webapp)
- **config** - Environment & configuration
- **db** - Database operations

### Business Logic (2)
- **sessionService** - Session CRUD & analysis
- **aiService** - Gemini AI integration

### HTTP Layer (3)
- **controllers** - Request handlers
- **routes** - Express routes
- **middleware** - Error, logging, CORS

## Data Flow Architecture

```
HTTP Request
    ↓
[Route Handler]
    ↓
[Middleware] → [Logger], [Error Handler], [CORS]
    ↓
[Controller] → Validation
    ↓
[Service Layer] → Business Logic
    ↓
[Database/AI] → Persistence/External API
    ↓
[Response] → JSON with ApiResponse<T>
    ↓
Error Path → [AppError] → [Error Handler] → 400/500 response
```

## Configuration Hierarchy

```
.env
  ├─ PORT (3000)
  ├─ NODE_ENV (development)
  ├─ GEMINI_API_KEY (required)
  ├─ GEMINI_MODEL (gemini-3.1-pro-preview)
  ├─ DB_PATH (./data/arch-sense.db)
  ├─ CORS_ORIGIN (http://localhost:5173)
  └─ LOG_LEVEL (info)
        ↓
    config/index.ts
        ↓
    Available in all modules via import
```

## Development Quick Reference

```bash
# Install dependencies
npm install

# Development server with auto-reload
npm run dev

# Type checking
npm run lint
npm run type-check

# Build for production
npm build
npm start

# Environment setup
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
```

## Key Patterns Used

| Pattern | Location | Purpose |
|---------|----------|---------|
| MVC | controllers/, routes/, services/ | Separation of concerns |
| Repository | db/sessionDb | Database abstraction |
| Service Layer | services/ | Reusable business logic |
| Middleware | middleware/ | Cross-cutting concerns |
| Factory | logger.createLogger() | Object creation |
| Singleton | config, logger, db | Single instance per app |
| Custom Error | AppError class | Type-safe error handling |

## Adding New Features

### To add a new endpoint:
1. Create controller method in `src/controllers/`
2. Add route handler in `src/routes/[feature].ts`
3. Register in `src/routes/index.ts`
4. Add types to `src/types.ts`
5. Create service in `src/services/` if needed

### To persist new data:
1. Add fields to SessionData in `types.ts`
2. Update CREATE TABLE in `db/index.ts`
3. Update sessionDb methods
4. Add service methods as needed

### To add middleware:
1. Create file in `src/middleware/`
2. Export function: `(req, res, next) => {...}`
3. Register in `index.ts` with `app.use()`
