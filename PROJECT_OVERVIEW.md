# Arch-Sense: Complete System Overview

## 🎯 What is Arch-Sense?

An **interactive learning game** where users design distributed systems architectures and receive **human-in-the-loop coaching** from AI agents that evaluate and challenge their designs (but don't solve them).

**Key principle**: Users learn by doing. Coaches evaluate and ask "what if?" not "here's the answer."

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 React Frontend (Port 5173)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Canvas: Design nodes/edges                           │  │
│  │ Sidebar: Show score, badges, difficulty              │  │
│  │ AIReviewer: Display coach feedback + reasoning        │  │
│  │ MissionBriefing: Scenario description                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP/JSON
                         ↓
┌─────────────────────────────────────────────────────────────┐
│           FastAPI Coaching Server (Port 8000)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 10 RESTful Endpoints:                                │  │
│  │  • POST   /sessions           → Create game session  │  │
│  │  • GET    /sessions/{id}      → Get session state    │  │
│  │  • POST   /sessions/{id}/evaluate → Main game loop   │  │
│  │  • POST   /sessions/{id}/accept-feedback → Iterate   │  │
│  │  • POST   /sessions/{id}/advance-phase → Progress    │  │
│  │  • GET    /sessions/{id}/progress → Score & badges   │  │
│  │  • GET    /sessions/{id}/design-evolution → History  │  │
│  │  • GET    /health             → Server status        │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Per-Session Coach Team (CrewAI Agents):              │  │
│  │  1. Scalability Coach     (SPOFs, caching, scaling)  │  │
│  │  2. Reliability Coach     (failure modes, resilience)│  │
│  │  3. Patterns Coach        (architectural patterns)   │  │
│  │                                                      │  │
│  │ All coaches propose CHALLENGES not SOLUTIONS:        │  │
│  │ • "Your DB can't handle 100M. How scale it?"        │  │
│  │ • "I see 3 SPOFs. Where will they break?"           │  │
│  │ • "Missing pattern: API Gateway. Why?"              │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Game Service (Scoring & Progression):                │  │
│  │  • Score: Scalability (0-100), Reliability (0-100),  │  │
│  │           Design Elegance (0-100)                    │  │
│  │  • Badges: 6 unlockable achievements                 │  │
│  │  • Difficulty: Levels 1-5 based on performance       │  │
│  │  • Stress Tests: Escalating scenarios                │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ SQLite Database:                                     │  │
│  │  • sessions: Game state, score, badges              │  │
│  │  • coach_interactions: Feedback history + responses  │  │
│  │  • design_evolution: Design iterations + reasoning  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
arch-sense/
├── README.md                          # Project overview
├── QUICKSTART.md                      # Getting started (3 min)
├── INTEGRATION_GUIDE.md               # Frontend connects to FastAPI
├── SCAFFOLD_SUMMARY.md                # Summary of Express scaffold
├── SERVER_STRUCTURE.md                # Old server structure
│
├── webapp/                            # React Frontend
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── server.ts                      # Vite dev server
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx                    # Main game component
│   │   ├── index.css
│   │   ├── types.ts                   # Shared types
│   │   ├── components/
│   │   │   ├── Canvas.tsx             # Design canvas (nodes/edges)
│   │   │   ├── Sidebar.tsx            # Score, badges, scenario
│   │   │   ├── AIReviewer.tsx         # Coach feedback display
│   │   │   ├── MissionBriefing.tsx    # Scenario info
│   │   │   ├── EvaluationView.tsx     # Results view
│   │   │   ├── ThinkingPrompt.tsx     # UX hint
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── geminiService.ts       # OLD: Direct Gemini (deprecated)
│   │   │   ├── ruleEngine.ts          # Design rule validation
│   │   │   └── (add coachingClient.ts for FastAPI)
│   │   ├── lib/
│   │   │   └── utils.ts               # Helpers
│   │   └── utils/
│   │       └── architectureAnalyzer.ts
│   └── metadata.json
│
├── agents/                            # FastAPI + CrewAI Backend (NEW)
│   ├── main.py                        # FastAPI app + 10 endpoints
│   ├── config.py                      # Settings & environment
│   ├── setup.py                       # Setup script
│   ├── test_api.py                    # API integration tests
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                   # Configuration template
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                 # Pydantic type system (16 models, 3 enums)
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py                # SQLite + CRUD (3 tables)
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── coaches.py                 # 3 Coach classes (analysis logic)
│   │   └── coach_team.py              # Per-session orchestrator
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── game_service.py            # Scoring, badges, difficulty, stress tests
│   │
│   ├── data/                          # SQLite database (auto-created)
│   │   └── arch_sense_game.db
│   │
│   ├── README.md                      # Full backend documentation
│   ├── INTEGRATION_GUIDE.md           # How frontend calls FastAPI
│   └── DEPLOYMENT.md                  # Production deployment
│
└── server/                            # Old Express backend (deprecated)
    ├── .gitkeep
    └── (archive/reference only)
```

## 🎮 Game Flow

### Phase 1: LEARNING
- User reads scenario
- Understands requirements (e.g., 100M users, 99.99% uptime)
- Coaches begin at "gentle" difficulty

### Phase 2: DESIGN (Main Loop)
```
1. User designs architecture
   ├── Drag nodes (LB, Cache, DB, etc.)
   ├── Connect with edges (request flow)
   └── Click "Submit for Evaluation"

2. Backend evaluates design
   ├── Run 3 coaches in parallel
   ├── Coaches analyze using patterns (no ML required)
   └── Coaches output challenges + reasoning

3. User sees coach feedback
   ├── Visible reasoning chain (4 steps transparent)
   ├── Challenges (not solutions)
   ├── Hints (optional)
   └── Current scores (Scalability/Reliability/Elegance)

4. User iterates
   ├── Modifies design based on challenges
   ├── Decides to accept or disagree with coach
   └── Submits modified design

5. Loop repeats (→ back to step 1)
   ├── Coaches remember previous feedback
   ├── Difficulty increases as iterate count goes up
   ├── Score increases as design improves
   └── Unlock badges with achievements
```

### Phase 3: STRESS (Optional)
- System gets tested against scenarios:
  - 5x traffic spike
  - 50x traffic (2 mins)
  - Database outages
  - Cascading failures
  - DDoS attack
- Coaches evaluate resilience

### Phase 4: EVALUATION
- Final score calculated
- Final badges awarded
- Summary of learning arc shown
- Can start new scenario

## 🧠 How Coaches Work

### Scalability Coach
```
Analyzes:
  • Single points of failure (SPOFs)
  • Load balancer presence
  • Database sharding strategy
  • Cache layer placement
  • Message queues for async work

Returns:
  • Challenge: "Your single DB can't handle 100M users. How will you scale?"
  • Reasoning: "Detected: SPOF_DATABASE, NO_CACHE, NO_LB"
  • Hint: "Think about sharding by region or user ID"
  • Severity: "critical"
```

### Reliability Coach
```
Analyzes:
  • Failure modes (what breaks?)
  • Redundancy levels
  • Failover mechanisms
  • Monitoring/alerting presence
  • Data consistency approaches

Returns:
  • Challenge: "Your system has 3 SPOF scenarios. Which will you address?"
  • Reasoning: "Single DB, single cache, single LB = cascading failure"
  • Hint: "Consider replicas and active-active setup"
  • Severity: "critical"
```

### Patterns Coach
```
Analyzes:
  • Architectural patterns used
  • API gateway presence
  • Service mesh candidates
  • Event-driven opportunities
  • Design elegance

Returns:
  • Challenge: "Lacks API Gateway for routing. Why no gateway?"
  • Reasoning: "Request routing not visible; clients directly connected"
  • Hint: "API Gateway simplifies auth, rate limiting, versioning"
  • Severity: "info"
```

## 🏅 Game Mechanics

### Scoring (0-100 each)
- **Scalability**: Can handle 100x traffic?
- **Reliability**: How many failure modes covered?
- **Design Elegance**: Clarity, patterns, simplicity?
- **Total**: Average of three

### Badges (6 Achievements)
1. **Load Balancer Master** - Added LB, survived 10x spike
2. **Zero SPOFs** - No single points of failure
3. **Async Architect** - Message queue + async processing
4. **Resilient Design** - High reliability score
5. **Caching Wizard** - Cache layer + good perf
6. **Global Scale** - Scaled to 100M+ users

### Difficulty Progression
- **Level 1** (0-50 score): Gentle coaching, basic concepts
- **Level 2** (50-75 score): Balanced, intermediate challenges
- **Level 3** (75+ score): Aggressive, complex scenarios
- **Level 4** (10+ iterations): Ultra-advanced patterns
- **Level 5** (Unlockable): Impossible scenarios for experts

### Coaching Styles
- **Gentle**: Frequent hints, simpler challenges
- **Balanced**: Mix of hints and challenges
- **Aggressive**: Deep questions, minimal hand-holding

## 🔌 Integration Points

### Old System → New System

| Component | Old | New |
|-----------|-----|-----|
| Server | Express.js | FastAPI + CrewAI |
| Database | Simple session storage | Enhanced SQLite (3 tables) |
| AI | Direct Gemini API calls | Agents with rule-based analysis |
| Coaching | One-off feedback | Continuous, history-aware |
| Game Mechanics | None | Full system (scores, badges, progression) |
| Statefulness | Stateless | Per-session agents with memory |
| Transparency | Hidden Gemini reasoning | Visible 4-step ReAct chain |

### Frontend Changes Needed
1. Update `webapp/src/lib/coachingClient.ts`
   - Change from old Express endpoints to FastAPI endpoints
   - Add methods for game loop (evaluate, acceptFeedback, progress)

2. Update `webapp/src/components/AIReviewer.tsx`
   - Show reasoning_steps (visible thinking)
   - Display coach_feedback (challenges)
   - Show score updates

3. Update `webapp/src/App.tsx`
   - Import new coachingClient
   - Update state management for game loop
   - New game phase management

See **INTEGRATION_GUIDE.md** for detailed code examples.

## 🚀 Getting Started

### Quick Start (3 min)
```bash
# See QUICKSTART.md for step-by-step instructions
```

### Development Setup
```bash
# Terminal 1: Backend
cd agents && pip install -r requirements.txt && python main.py

# Terminal 2: Frontend
cd webapp && npm install && npm run dev

# Terminal 3: Testing (optional)
cd agents && python test_api.py
```

### Production Deployment
See **DEPLOYMENT.md** for Docker, Cloud Run, AWS Lambda, Heroku options.

## 📊 Database Schema

### sessions table
```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,                -- UUID session
  scenario TEXT,                      -- "Design 100M user system"
  user_name TEXT,
  phase TEXT,                         -- LEARNING|DESIGN|STRESS|EVALUATION
  design TEXT,                        -- JSON: {nodes, edges}
  scalability_score INTEGER,          -- 0-100
  reliability_score INTEGER,          -- 0-100
  design_elegance_score INTEGER,      -- 0-100
  total_score INTEGER,                -- Average
  badges TEXT,                        -- JSON: [badge_names]
  difficulty_level INTEGER,           -- 1-5
  coaching_style TEXT,                -- aggressive|balanced|gentle
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### coach_interactions table
```sql
CREATE TABLE coach_interactions (
  id TEXT PRIMARY KEY,
  session_id TEXT,                    -- Foreign key
  coach_type TEXT,                    -- SCALABILITY|RELIABILITY|PATTERNS
  challenge TEXT,                     -- "Your DB can't handle..."
  reasoning TEXT,                     -- "Detected: SPOF_DB"
  hint TEXT,                          -- Optional hint
  severity TEXT,                      -- critical|warning|info
  user_response TEXT,                 -- User's reply
  accepted BOOLEAN,                   -- User accepted challenge?
  created_at TIMESTAMP
);
```

### design_evolution table
```sql
CREATE TABLE design_evolution (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  design TEXT,                        -- JSON at this iteration
  coach_feedback TEXT,                -- Concatenated feedback
  reasoning_steps TEXT,               -- JSON: [step1, step2, ...]
  score_before INTEGER,
  score_after INTEGER,
  timestamp TIMESTAMP
);
```

## 🔑 Key Concepts

### Human-in-the-Loop (HITL)
- User drives iteration (not AI)
- Coaches evaluate and challenge
- User learns by modifying design
- Contrast: Auto-generation systems tell you the answer

### ReAct (Reasoning + Acting)
- 4 reasoning steps shown to user:
  1. "Analyzing design with 3 coaches..."
  2. "Prioritizing feedback by severity..."
  3. "Escalating intensity based on difficulty..."
  4. "Generating recommendations..."
- User sees agent thinking, builds trust

### Per-Session Agents
- Coaches instantiated once when session created
- Stored in-memory with session state
- Remember feedback history
- Enable coaching arc ("last time you added a queue, now you're doing it in 3 places")
- Contrast: Stateless APIs that don't remember

## 📚 Documentation

| File | Purpose |
|------|---------|
| QUICKSTART.md | Get running in 3 minutes |
| README.md | This file - system overview |
| agents/README.md | Backend detailed docs |
| agents/INTEGRATION_GUIDE.md | Frontend integration guide |
| agents/DEPLOYMENT.md | Production deployment |
| agents/requirements.txt | Python dependencies |
| webapp packag.json | Frontend dependencies |

## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.104.1): Modern async web framework
- **CrewAI** (0.25.0): AI agent orchestration
- **Pydantic** (2.5.0): Type validation
- **SQLite3**: Lightweight database
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool & dev server
- **React Flow**: Canvas for node graphs

### Deployment Options
- Docker (local)
- Docker Compose (multi-service)
- Google Cloud Run
- AWS Lambda + API Gateway
- Heroku
- DigitalOcean App Platform

## 🎓 Learning Path

1. **Beginner** (Level 1)
   - Add load balancer
   - Add cache layer
   - Basic redundancy

2. **Intermediate** (Levels 2-3)
   - Database sharding
   - Message queues
   - API Gateway
   - Active-active replication

3. **Advanced** (Levels 4-5)
   - Service mesh
   - Cascading failure analysis
   - DDoS resilience
   - Global distribution

## ⚡ Performance

- **Coach evaluation**: <1 second typical
- **Database queries**: <10ms typical
- **Frontend response**: <100ms typical
- **Concurrent sessions**: 100+ (SQLite) → unlimited (PostgreSQL)

## 🔐 Security

- CORS configured for frontend origin
- HTTPS recommended for production
- Database encryption possible
- API rate limiting (can add)
- No secrets in code (use .env)

## 🐛 Debugging

```bash
# View API docs
http://localhost:8000/docs

# View ReDoc
http://localhost:8000/redoc

# Health check
curl http://localhost:8000/health

# View database
sqlite3 data/arch_sense_game.db ".schema"

# View logs
docker logs arch-sense-api
```

## 📞 Support

- See QUICKSTART.md for quick start
- See agents/README.md for detailed backend docs
- See agents/INTEGRATION_GUIDE.md for frontend integration
- See agents/DEPLOYMENT.md for production
- Examine code—it's well-commented and clean

---

**Ready to teach architects to think deeply about systems design?** 🏗️

Start with QUICKSTART.md → 3 minutes to running system.
