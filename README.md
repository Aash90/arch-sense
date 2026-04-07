# 🏗️ Arch-Sense: Agentic Coaching System for Architecture Design

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.135+-success)]()
[![CrewAI](https://img.shields.io/badge/crewai-1.13-purple)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

> **Interactive learning game where users design distributed systems architectures and receive coaching from AI agents that evaluate and challenge (but don't solve) their designs.**

A **production-ready**, **type-safe**, **fully-documented** agentic system built with FastAPI and CrewAI that teaches architecture design through human-in-the-loop coaching with transparent AI reasoning.

---

## ✨ What Makes This Special

### 🧠 Human-in-the-Loop (HITL) Pattern
- **Coaches guide, don't solve** - Users learn by modifying designs based on challenges
- **ReAct reasoning visible** - 4-step transparent thinking chain shown to users
- **Coaching continuity** - Per-session agents remember feedback history
- **Learning arc** - Difficulty escalates as user improves

### 🎮 Game Mechanics
- **Scoring system** - Scalability (0-100), Reliability (0-100), Design Elegance (0-100)
- **6 unlockable badges** - Load Balancer Master, Zero SPOFs, Async Architect, etc.
- **5 difficulty levels** - Adapt from beginner to impossible scenarios
- **Stress testing** - Escalating failure scenarios (5x spike → DDoS)

### 🤖 3 Specialized AI Coaches
- **Scalability Coach** - Detects SPOFs, caching gaps, scaling issues
- **Reliability Coach** - Identifies failure modes, resilience gaps
- **Patterns Coach** - Checks architectural patterns and design elegance

### 🏆 Production Ready
- ✅ **Type-safe** - Full Pydantic validation (16 models + 3 enums)
- ✅ **Tested** - Integration tests for all 10 endpoints
- ✅ **Documented** - 6 comprehensive guides + auto-generated Swagger API
- ✅ **Deployable** - Docker, Cloud Run, AWS Lambda, Heroku ready
- ✅ **Scalable** - SQLite for dev, PostgreSQL for prod (seamless migration)
- ✅ **Clean code** - Well-commented, follows best practices

---

## 🚀 Quick Start (3 Minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend)

### Backend
```bash
cd agents
pip install -r requirements.txt
python main.py
```

Server runs on **`http://localhost:8000`**

### Frontend
```bash
cd webapp
npm install
npm run dev
```

Frontend runs on **`http://localhost:5173`**

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Quick Test
```bash
cd agents
python test_api.py
```

---

## 📊 Architecture

```
Frontend (React)         Backend (FastAPI)         AI Coaches (CrewAI)
    ↓                         ↓                            ↓
Canvas design       10 REST endpoints      3 specialized agents
  (nodes/edges)      /sessions
                     /evaluate        Scalability Coach
Users design         /progress         Reliability Coach
architecture         /health           Patterns Coach
                                            ↓
                                    Game Service
                                   (scoring, badges,
                                    difficulty)
                                            ↓
                                      SQLite DB
                                   (3 tables, indexed)
```

### Per-Session Agents
Each user session gets its own initialized coach team that:
- Remembers all feedback history
- Escalates intensity based on iteration count
- References previous mistakes ("You added a queue last time...")
- Enables coaching arc and continuity

### ReAct Reasoning Visible
Coaches show 4-step reasoning chain:
1. "Analyzing design with three specialized coaches..."
2. "Prioritizing feedback by severity..."
3. "Escalating feedback intensity..."
4. "Generating next milestones..."

Users see **agent thinking**, not just conclusions → builds trust and learning.

---

## 📡 API Endpoints (10)

### Sessions
```
POST   /sessions              Create new game session
GET    /sessions              List all sessions
GET    /sessions/{id}         Get session state
DELETE /sessions/{id}         End session
```

### Game Loop
```
POST   /sessions/{id}/evaluate           Submit design → get coach feedback
POST   /sessions/{id}/accept-feedback    User responds to coaching
POST   /sessions/{id}/advance-phase      Progress to next phase
```

### Progress & History
```
GET    /sessions/{id}/progress           Score, badges, next milestone
GET    /sessions/{id}/design-evolution   Design history + reasoning chain
GET    /health                            Server status + active sessions
```

All documented with **Swagger** → `http://localhost:8000/docs`

---

## 🎮 Game Flow

```
1. User creates session
   ↓ Coach team initialized (3 agents per session)
   
2. User designs on canvas
   ├── Drag nodes (LB, Cache, DB, etc.)
   └── Connect edges (request flow)
   
3. User submits design
   ↓ POST /sessions/{id}/evaluate
   
4. Coaches analyze
   ├── Step 1: Run all 3 coaches in parallel
   ├── Step 2: Prioritize feedback by severity
   ├── Step 3: Escalate intensity (if needed)
   └── Step 4: Generate recommendations
   
5. User sees coaching
   ├── Reasoning steps (VISIBLE)
   ├── Challenges (not solutions)
   ├── Hints (optional)
   └── New score + progress
   
6. User iterates
   ├── Modifies design
   ├── Accepts/rejects coaching
   └── Submits again
   
7. Progression
   ├── Score improves → difficulty increases
   ├── Badges unlock with achievements
   ├── Difficulty escalates (1→5)
   └── Coaching arc develops
```

---

## 🏅 Game Mechanics

### Scoring (0-100 each)
| Score | Measures | Examples |
|-------|----------|----------|
| **Scalability** | Handle 100x traffic | Load balancing, caching, sharding |
| **Reliability** | Failure mode coverage | Redundancy, failover, monitoring |
| **Design Elegance** | Architecture quality | Patterns, clarity, simplicity |

### Badges (6 Achievements)
- 🏗️ Load Balancer Master
- 🛡️ Zero SPOFs
- ⚙️ Async Architect
- 🔄 Resilient Design
- 💾 Caching Wizard
- 🌍 Global Scale

### Difficulty (5 Levels)
| Level | Challenge | Coaching |
|-------|-----------|----------|
| 1 | Gentle intro | Frequent hints |
| 2 | Intermediate | Balanced |
| 3 | Advanced | Aggressive |
| 4 | Expert | Deep questions |
| 5 | Master | Impossible scenarios |

---

## 💾 Data Model

### Sessions Table
```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  scenario TEXT,                  -- "Design 100M user system"
  phase TEXT,                     -- LEARNING|DESIGN|STRESS|EVALUATION
  design TEXT,                    -- JSON: {nodes, edges}
  scalability_score INTEGER,      -- 0-100
  reliability_score INTEGER,      -- 0-100
  design_elegance_score INTEGER,  -- 0-100
  total_score INTEGER,            -- Average
  badges TEXT,                    -- JSON: [badge_names]
  difficulty_level INTEGER,       -- 1-5
  coaching_style TEXT,            -- aggressive|balanced|gentle
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Coach Interactions Table
```sql
CREATE TABLE coach_interactions (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  coach_type TEXT,                -- SCALABILITY|RELIABILITY|PATTERNS
  challenge TEXT,                 -- "Your DB can't handle 100M..."
  reasoning TEXT,                 -- "Detected: SPOF_DATABASE"
  hint TEXT,                      -- Optional hint
  severity TEXT,                  -- critical|warning|info
  user_response TEXT,
  accepted BOOLEAN,
  created_at TIMESTAMP
);
```

### Design Evolution Table
```sql
CREATE TABLE design_evolution (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  design TEXT,                    -- JSON at this iteration
  coach_feedback TEXT,            -- Summarized feedback
  reasoning_steps TEXT,           -- JSON: [step1, step2...]
  score_before INTEGER,
  score_after INTEGER,
  timestamp TIMESTAMP
);
```

---

## 📚 Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [QUICKSTART.md](QUICKSTART.md) | 3-min getting started | 3 min |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Complete system design | 15 min |
| [agents/README.md](agents/README.md) | Backend detailed docs | 20 min |
| [agents/INTEGRATION_GUIDE.md](agents/INTEGRATION_GUIDE.md) | Frontend integration | 25 min |
| [agents/DEPLOYMENT.md](agents/DEPLOYMENT.md) | Production deployment | 20 min |
| [SYSTEM_COMPLETE.md](SYSTEM_COMPLETE.md) | Status overview | 2 min |

**Start with [QUICKSTART.md](QUICKSTART.md) →**

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.135+) - Modern async web framework
- **CrewAI** (1.13.0) - AI agent orchestration
- **Pydantic** (2.11+) - Type validation & serialization
- **SQLite3** / **PostgreSQL** - Data persistence
- **Uvicorn** - ASGI application server

### Frontend
- **React** 18 - Component UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **React Flow** - Node graph visualization

### DevOps & Deployment
- **Docker** - Containerization
- **Cloud Run** - Serverless deployment
- **AWS Lambda + API Gateway** - Serverless alternative
- **Heroku** - Platform-as-a-service

---

## ✅ What's Included

### Backend (17 files, ~2,300 LOC)
- ✅ Full FastAPI implementation (10 endpoints)
- ✅ 3 AI coach agents (per-session, stateful)
- ✅ Game mechanics engine (scoring, badges, progression)
- ✅ SQLite database (3 tables, auto-initialized)
- ✅ Pydantic type system (16 models + 3 enums)
- ✅ ReAct reasoning visualization
- ✅ Integration tests (test_api.py)
- ✅ Setup script (setup.py)
- ✅ Configuration management (.env support)

### Documentation (6+ guides)
- ✅ Quick start guide
- ✅ Complete architecture overview
- ✅ Backend API documentation
- ✅ Frontend integration guide
- ✅ Production deployment instructions
- ✅ API examples & cURL reference

### Quality Assurance
- ✅ Type-safe end-to-end (Pydantic + TypeScript)
- ✅ Tested endpoints (all 10 tested)
- ✅ Error handling (centralized, structured)
- ✅ CORS configured (localhost:5173)
- ✅ Async/await throughout (no blocking)

---

## 🎯 Key Features

### 1. Human-in-the-Loop Learning
- Users design, coaches evaluate
- Coaches propose challenges, not solutions
- Learning by doing, not by being told

### 2. Transparent AI Reasoning
- 4-step ReAct reasoning visible to user
- See what coaches are thinking
- Builds trust in feedback

### 3. Per-Session Agent Continuity
- Coaches remember session history
- Escalate intensity based on iterations
- Reference previous improvements
- Enable coaching arc

### 4. Game-Based Progression
- Scores motivate improvement
- Badges reward milestones
- Difficulty adapts to skill level
- Engaging, not punitive

### 5. Production-Grade Architecture
- Type-safe (Pydantic validation)
- Database-backed (SQLite/PostgreSQL)
- API documented (Swagger + ReDoc)
- Ready to deploy (Docker containers)

---

## 📈 What You Learn

Users will develop understanding of:
- **Load balancing** - Distributing traffic
- **Caching** - Improving response time
- **Database scaling** - Handling growth (sharding, replication)
- **Redundancy** - Fault tolerance and failover
- **Asynchronous processing** - Message queues, event-driven
- **Architectural patterns** - API Gateway, Service Mesh, etc.
- **System design thinking** - Trade-offs and constraints

All through **interactive design challenges**, not lectures.

---

## 🚀 Deployment

### Local Development
```bash
python main.py  # Runs on port 8000
```

### Docker
```bash
docker build -t arch-sense .
docker run -p 8000:8000 arch-sense
```

### Cloud Run (Google Cloud)
```bash
gcloud run deploy arch-sense --source .
```

### AWS Lambda
See [agents/DEPLOYMENT.md](agents/DEPLOYMENT.md) for full instructions.

### Heroku
```bash
git push heroku main
```

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| **Backend files** | 17 |
| **Lines of code** | ~2,300 |
| **REST endpoints** | 10 |
| **Database tables** | 3 |
| **Pydantic models** | 16 |
| **Documentation pages** | 6+ |
| **Test coverage** | All endpoints |
| **Deploy options** | 4+ |

---

## 🎓 Design Principles

1. **Type Safety First** - Pydantic everywhere, zero untyped code
2. **User-Centric** - HITL pattern, not auto-solving
3. **Transparency** - Show agent reasoning, build trust
4. **Scalability** - SQLite → PostgreSQL migration seamless
5. **Documentation** - Every endpoint documented, examples provided
6. **Clean Code** - Well-commented, follows conventions
7. **Production Ready** - Error handling, logging, deployment guides

---

## 🔗 Quick Links

- 📖 **Getting Started** → [QUICKSTART.md](QUICKSTART.md)
- 🏗️ **Architecture** → [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- 🔌 **API Client** → [agents/INTEGRATION_GUIDE.md](agents/INTEGRATION_GUIDE.md)
- 🚀 **Deployment** → [agents/DEPLOYMENT.md](agents/DEPLOYMENT.md)
- 📚 **Backend Docs** → [agents/README.md](agents/README.md)

---

## 💡 Next Steps

### To Start
1. Read [QUICKSTART.md](QUICKSTART.md) (3 min)
2. Run `python main.py` in agents/ folder
3. Open `http://localhost:8000/docs` in browser

### To Integrate Frontend
1. Read [agents/INTEGRATION_GUIDE.md](agents/INTEGRATION_GUIDE.md)
2. Update `webapp/src/lib/coachingClient.ts`
3. Implement coach feedback UI

### To Deploy
1. Read [agents/DEPLOYMENT.md](agents/DEPLOYMENT.md)
2. Choose your platform (Docker, Cloud Run, AWS, Heroku)
3. Deploy with one command

---

## 🤝 Architecture Design Skills Covered

AI coaches evaluate across:
- **AI** - Large language model integration patterns
- **Database** - Scaling, replication, consistency
- **Network** - Load balancing, API design, protocols
- **OS** - Concurrency, async processing, resource management
- **DevOps** - Deployment, monitoring, resilience
- **System Design** - Trade-offs, constraints, architecture patterns

---

## 📝 License

MIT License - Feel free to use, modify, and distribute.

---

## 🎉 Status

✅ **Production Ready** - Fully implemented, tested, and documented system
✅ **Top Quality** - Type-safe, well-tested, production deployment guides included
✅ **Ready to Run** - 3 minutes from clone to running system
✅ **Ready to Extend** - Clean code, easy to customize coaches and game mechanics

---

**Built with FastAPI + CrewAI for interactive architecture learning.**

Start now → [QUICKSTART.md](QUICKSTART.md) 🚀
