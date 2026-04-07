# arch-sense Server

Backend server for arch-sense - AI validator for Architecture design and simulation.

## Overview

This is a TypeScript/Express.js backend that provides:
- Session management for architecture design workflows
- Integration with Google Gemini AI for real-time architect feedback
- Architecture analysis and design signal detection
- SQLite database for persisting design sessions
- REST API for frontend integration

## Architecture

```
src/
├── index.ts                 # Entry point
├── types.ts                 # Shared type definitions
├── config/                  # Configuration management
│   └── index.ts
├── db/                      # Database layer
│   └── index.ts
├── middleware/              # Express middleware
│   ├── errorHandler.ts      # Error handling
│   └── logger.ts            # Request logging
├── services/                # Business logic
│   ├── sessionService.ts    # Session management
│   └── aiService.ts         # AI integration
├── controllers/             # Request handlers
│   ├── sessionController.ts
│   └── aiController.ts
└── routes/                  # API routes
    ├── index.ts
    ├── health.ts
    ├── sessions.ts
    └── ai.ts
```

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd server
npm install
```

### Configuration

Create a `.env` file in the server directory:

```bash
cp .env.example .env
```

Edit `.env` and add your:
- `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/app/apikey)
- Other configuration as needed

### Development

```bash
npm run dev
```

Server runs on `http://localhost:3000` by default.

### Building

```bash
npm run build
npm start
```

## API Endpoints

### Health Check
- `GET /api/health` - Server health status

### Sessions
- `GET /api/sessions` - List all sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/:id` - Get specific session
- `POST /api/sessions/:id` - Update session
- `GET /api/sessions/:id/summary` - Get session summary
- `DELETE /api/sessions/:id` - Delete session

### AI Feedback
- `POST /api/ai/feedback` - Get architect feedback on design
- `POST /api/ai/evaluate` - Get final evaluation of design
- `POST /api/ai/message` - Send message to architect AI

## Database Schema

### Sessions Table
```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  nodes TEXT,                    -- JSON array of SystemNode
  edges TEXT,                    -- JSON array of SystemEdge
  phase TEXT,                    -- 'PROBLEM_STATEMENT' | 'DESIGN' | 'STRESS' | 'EVALUATION'
  scenario TEXT,
  scaling_challenge TEXT,
  signals TEXT,                  -- JSON array of DesignSignal
  messages TEXT,                 -- JSON array of Message
  evaluation TEXT,               -- JSON Evaluation object
  stress_events TEXT,            -- JSON array of StressEvent
  current_stress_index INTEGER,
  created_at INTEGER,            -- Timestamp
  updated_at INTEGER             -- Timestamp
)
```

## Key Features

### Session Management
- Create and manage design sessions
- Store complete architecture state (nodes, edges, metadata)
- Track phase progression through design workflow
- Persist conversation history

### AI Integration
- Real-time architect feedback using Gemini API
- Context-aware responses based on current design
- Final evaluation with scoring (scalability, reliability, clarity)
- Conversational interaction with AI architect

### Architecture Analysis
- Automatic design signal detection:
  - Presence of message queues
  - Load balancer configuration
  - Direct external calls
  - Async processing patterns
  - Single points of failure (database)

### Error Handling
- Comprehensive error responses
- Request validation
- Graceful error messages
- Structured error logging

### Logging
- Request/response logging
- Error tracking
- Timestamp and level information
- Color-coded status in development

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | development | Environment (development/production) |
| `PORT` | 3000 | Server port |
| `GEMINI_API_KEY` | (required) | Google Gemini API key |
| `GEMINI_MODEL` | gemini-3.1-pro-preview | AI model to use |
| `DB_PATH` | ./data/arch-sense.db | SQLite database path |
| `CORS_ORIGIN` | http://localhost:5173 | CORS allowed origin |
| `LOG_LEVEL` | info | Logging level |

## Type Definitions

Key types are defined in `src/types.ts`:

- `SystemNode` - Architecture component node
- `SystemEdge` - Connection between nodes
- `SimulationState` - Current workflow state
- `Message` - Chat message in session
- `Evaluation` - AI evaluation scores and feedback
- `DesignSignal` - Detected architecture patterns
- `SessionData` - Complete session state

## Development Notes

### Adding New Endpoints
1. Create controller method in `src/controllers/`
2. Add route handler in `src/routes/`
3. Register route in `src/routes/index.ts`
4. Update types in `src/types.ts` if needed

### Database Operations
Use the `sessionDb` operations in `src/db/index.ts`:
- `sessionDb.create()` - Create new session
- `sessionDb.get()` - Fetch session
- `sessionDb.update()` - Update session
- `sessionDb.delete()` - Delete session
- `sessionDb.listAll()` - List sessions

### Error Handling
Throw `AppError` for API errors:
```typescript
throw new AppError(404, 'Session not found');
```

## Testing

AI endpoints require valid `GEMINI_API_KEY`. Test with:

```bash
# Get architect feedback
curl -X POST http://localhost:3000/api/ai/feedback \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "nodes": [...],
  "edges": [...],
  "history": [...],
  "phase": "DESIGN",
  "scenario": "...",
  "scalingChallenge": "..."
}
EOF
```

## License

Same as parent project
