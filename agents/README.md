# Arch-Sense Agentic Coaching System

FastAPI + CrewAI game server for teaching architecture design through interactive coaching.

## Overview

This is a **Human-in-the-Loop (HITL) coaching system** where:
- ✅ **3 specialized coaches** evaluate designs (Scalability, Reliability, Patterns)
- ✅ **ReAct reasoning visible** to user (show agent thinking, not just conclusions)
- ✅ **Game mechanics** (scores, badges, difficulty progression)
- ✅ **Per-session agents** with continuity and coaching arc
- ✅ **Challenges not solutions** - users learn by doing, not by being told

## Architecture

```
Frontend (React)
    ↓ (POST /sessions/{id}/evaluate)
FastAPI Server
    ↓
Per-Session Coach Team (CrewAI agents)
    ├── Scalability Coach (identifies SPOFs, caching gaps, scaling issues)
    ├── Reliability Coach (finds failure modes, resilience gaps)
    └── Patterns Coach (checks for architectural patterns)
    ↓
Game Service (scoring, badging, progression)
    ↓
SQLite Database (game state, coach history, design evolution)
```

## Quick Start

### 1. Install

```bash
cd agents
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add GEMINI_API_KEY (optional, for enhanced reasoning)
```

### 3. Run

```bash
python main.py
```

Server starts on `http://localhost:8000`

### 4. API Docs

```
http://localhost:8000/docs  (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

## Game Flow

```
1. User creates session (POST /sessions)
   → Coach team initialized per session
   → Game state stored with initial score

2. User designs on canvas (nodes/edges)

3. User submits design (POST /sessions/{id}/evaluate)
   → Coaches analyze (ReAct reasoning steps visible)
   → Coaches propose challenges (not solutions)
   → Score updated, badges checked
   → Design evolution recorded

4. User iterates
   → Coaches escalate intensity based on iteration count
   → Difficulty increases with score
   → Badges unlock with achievements

5. (Optional) Stress test
   → Coaches suggest scenario based on difficulty
   → Can test against 5x-1000x traffic, failures, etc.

6. Final evaluation
   → Session complete with score, badges, progress path
```

## Key Endpoints

### Sessions
```
POST   /sessions                  Create new session (init coaches)
GET    /sessions                  List all sessions
GET    /sessions/{id}             Get session
DELETE /sessions/{id}             End session + cleanup agents
```

### Game Loop (Main Flow)
```
POST   /sessions/{id}/evaluate    Submit design → Get coach feedback
POST   /sessions/{id}/accept-feedback   User responds to feedback
POST   /sessions/{id}/advance-phase   Move to next phase
```

### Progress & History
```
GET    /sessions/{id}/progress         Current score, badges, next challenge
GET    /sessions/{id}/design-evolution Design history (shows reasoning chain)
```

### Health
```
GET    /health                    Server status & session count
```

## Data Models

### Session State
```python
{
  "id": "abc123",
  "scenario": "Design 100M user notification system",
  "phase": "DESIGN",  # LEARNING | DESIGN | STRESS | EVALUATION
  "design": {
    "nodes": [SystemNode...],
    "edges": [SystemEdge...]
  },
  "score": {
    "scalability": 45,
    "reliability": 60,
    "design_elegance": 70,
    "total": 58
  },
  "badges": [Badge...],
  "coach_history": [CoachFeedback...]
}
```

### Coach Feedback (Not Solutions!)
```python
{
  "coach_type": "SCALABILITY",  # SCALABILITY | RELIABILITY | PATTERNS
  "challenge": "Your single DB can't handle 100M users. How will you scale it?",
  "reasoning": "Detected: SPOF_DATABASE, NO_CACHE, NO_LOAD_BALANCER",
  "hint": "Think about sharding by region or user ID",  # Optional
  "severity": "critical"  # critical | warning | info
}
```

### ReAct Reasoning (Visible to User)
```python
{
  "reasoning_steps": [
    "Analyzing design with three specialized coaches...",
    "🏗️ Scalability Coach: Found 2 SPOFs",
    "🛡️ Reliability Coach: Identified 3 failure modes",
    "🎯 Patterns Coach: Found 2 missing patterns",
    "Prioritizing feedback based on severity...",
    "Added scalability challenge...",
    "..."
  ]
}
```

## Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| ENVIRONMENT | development | Dev mode (verbose) or production |
| DIFFICULTY_LEVEL | 1 | Initial difficulty (1-5) |
| COACHING_STYLE | aggressive | How harsh coaches are |
| ENABLE_HINTS | true | Show hints to users |
| CORS_ORIGIN | http://localhost:5173 | Frontend CORS |

## Game Mechanics

### Scoring
- **Scalability**: How well design handles 100x traffic
- **Reliability**: Fault tolerance and resilience
- **Design Elegance**: Clarity, pattern usage, architectural quality
- **Total**: Average of three scores

### Badges (Gamification)
- "Load Balancer Master" - Added LB and survived 10x spike
- "Zero SPOFs" - No single points of failure
- "Async Architect" - Message queue + async processing
- "Resilient Design" - High reliability score
- "Caching Wizard" - Cache layer + good performance
- "Global Scale" - Scaling to 100M+ users

### Difficulty Progression
- Scores < 50: Difficulty 1 (gentle coaching)
- Scores 50-75: Difficulty 2 (balanced)
- Scores > 75: Difficulty 3 (aggressive)
- 10+ iterations: Difficulty increases
- Can unlock Level 5: Impossible scenarios

### Stress Tests
| Level | Scenario | Challenge |
|-------|----------|-----------|
| 1 | Light Spike | 5x traffic |
| 2 | Flash Spike | 50x traffic (2 min) |
| 3 | DB Outage | Primary DB down |
| 4 | Cascading | Service failure cascades |
| 5 | DDoS | Sustained attack |

## Per-Session Coaches (Stateful)

Each session gets its own initialized coach team. Coaches:
- Remember user's feedback history
- Escalate intensity based on iterations
- Reference previous mistakes: "Last time you added a queue, now you're in 3 places"
- Track user's learning arc

This enables **coaching continuity** unlike stateless API calls.

## Integration with Frontend

### React/TypeScript

```typescript
// Create session
const res = await fetch('http://localhost:8000/sessions', {
  method: 'POST',
  body: JSON.stringify({ scenario: "...", user_name: "..." })
});
const session = await res.json();

// Submit design for evaluation
const res = await fetch(`http://localhost:8000/sessions/${session.id}/evaluate`, {
  method: 'POST',
  body: JSON.stringify({
    design: { nodes: [...], edges: [...] },
    user_notes: "..."
  })
});
const evaluation = await res.json();

// Show coaches' reasoning steps
evaluation.reasoning_steps.forEach(step => console.log(step));

// Show feedback challenges (not solutions)
evaluation.feedback.forEach(f => {
  console.log(`${f.coach_type}: ${f.challenge}`);
  if (f.hint) console.log(`Hint: ${f.hint}`);
});

// Get progress
const res = await fetch(`http://localhost:8000/sessions/${session.id}/progress`);
const progress = await res.json();
console.log(`Score: ${progress.score.total}`, `Badges: ${progress.badges.length}`);
```

## Development

### Add New Coach Type

1. Create coach class in `agents/coaches.py`
2. Add method `create_agent()` and `analyze_*()
3. Add to `CoachTeam.evaluate_design()`
4. Update `CoachType` enum in `models/schemas.py`

### Modify Game Scoring

Edit `GameService.calculate_score()` in `services/game_service.py`

### Add More Badges

Add to `GameService.BADGES` dict in `services/game_service.py`

### Change Coaching Intensity

Edit `CoachTeam.evaluate_design()` in `agents/coach_team.py`

## Database Schema

```sql
-- Sessions with game state
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  scenario TEXT,
  phase TEXT,  -- LEARNING | DESIGN | STRESS | EVALUATION
  design TEXT,  -- JSON
  scalability_score INTEGER,
  reliability_score INTEGER,
  design_elegance_score INTEGER,
  total_score INTEGER,
  badges TEXT,  -- JSON array
  difficulty_level INTEGER,
  coaching_style TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Coach interactions (for continuity)
CREATE TABLE coach_interactions (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  coach_type TEXT,
  challenge TEXT,
  reasoning TEXT,
  hint TEXT,
  severity TEXT,
  user_response TEXT,
  accepted BOOLEAN,
  created_at TIMESTAMP
);

-- Design evolution (shows user progress)
CREATE TABLE design_evolution (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  design TEXT,  -- JSON
  coach_feedback TEXT,
  reasoning_steps TEXT,  -- JSON
  score_before INTEGER,
  score_after INTEGER,
  timestamp TIMESTAMP
);
```

## Environment Variables

```bash
# Server
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/arch_sense_game.db

# AI (optional, for enhanced agent reasoning)
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-3.1-pro-preview

# Game
DIFFICULTY_LEVEL=1
ENABLE_HINTS=true
COACHING_STYLE=aggressive

# Frontend CORS
CORS_ORIGIN=http://localhost:5173
```

## Notes

- **Coaches don't solve**: Each coach asks "why?" and "what if?"
- **Reasoning visible**: Users see agent thinking, builds trust
- **Per-session state**: Coaches remember, enabling coaching arc
- **Game loop simple**: Submit → Evaluate → Iterate (HITL not auto)
- **SQLite by default**: No external dependencies, easy to deploy

## Next Steps

1. Start server: `python main.py`
2. Create session: `POST /sessions`
3. Submit design: `POST /sessions/{id}/evaluate`
4. View reasoning: Check `reasoning_steps` in response
5. Iterate: Show user challenges, they modify design, repeat

---

Built with FastAPI + CrewAI for arch-sense learning game.
