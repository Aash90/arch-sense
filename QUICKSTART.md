# 🚀 Quick Start: Arch-Sense Agentic Coaching System

Get the coaching system running in **3 minutes**.

## Prerequisites

- Python 3.9+
- Node.js 16+ (for frontend)
- Git

## Step 1: Setup Backend (FastAPI + CrewAI)

```bash
# Navigate to agents directory
cd agents

# Install Python dependencies
pip install -r requirements.txt

# Run setup script (creates DB, validates config)
python setup.py

# Configure environment
cp .env.example .env
# (Optional: Edit .env to add GEMINI_API_KEY for real AI coaching)

# Start the server
python main.py
```

✅ Server running on `http://localhost:8000`

API Docs: `http://localhost:8000/docs`

## Step 2: Setup Frontend (React)

In a **new terminal**:

```bash
# Navigate to webapp directory
cd webapp

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running on `http://localhost:5173`

## Step 3: Test Integration

### Option A: Use Frontend
1. Open `http://localhost:5173` in browser
2. Click "New Game"
3. Design architecture on canvas
4. Click "Submit for Evaluation"
5. See coaches' reasoning and challenges
6. Modify design and submit again
7. Watch score improve!

### Option B: Use API Directly (Testing)

```bash
# In a **third terminal**:
cd agents

# Run API tests (Fast integration test)
python test_api.py
```

This tests all 10 endpoints without needing the frontend.

### Option C: Use cURL (Manual Testing)

```bash
# 1. Create a session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "Design notification system for 100M users",
    "user_name": "TestPlayer"
  }'

# Save the session ID from response
SESSION_ID="abc123"

# 2. Submit design for evaluation
curl -X POST http://localhost:8000/sessions/$SESSION_ID/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "design": {
      "nodes": [
        {"id": "1", "type": "WEB_SERVER", "label": "Web Server"},
        {"id": "2", "type": "DATABASE", "label": "Database"}
      ],
      "edges": [
        {"from": "1", "to": "2"}
      ]
    }
  }'

# 3. View reasoning chain
# (Check the reasoning_steps in the response)

# 4. Get progress
curl http://localhost:8000/sessions/$SESSION_ID/progress
```

## Architecture Overview

```
Frontend (React)
├── Canvas: Design nodes/edges
├── Sidebar: Show score & badges
└── Coach Panel: Show challenges & reasoning

    ↓ HTTP POST /evaluate

Backend (FastAPI)
├── Session Manager: Track game state
├── Email Coach Team: 3 specialized coaches
│   ├── Scalability Coach
│   ├── Reliability Coach
│   └── Patterns Coach
├── Game Service: Scoring, badges, progression
└── Database: SQLite (game state + history)
```

## Game Loop

```
1. User creates session
   ↓
2. User designs on canvas (nodes + edges)
   ↓
3. User submits design → /sessions/{id}/evaluate
   ↓
4. Coaches analyze (4-step ReAct reasoning visible)
   ↓
5. Coaches propose challenges (not solutions):
   - "Your single DB can't handle 100M users. How?"
   - "No cache layer detected. Where should it go?"
   - "Improves: Consider API gateway for routing"
   ↓
6. User sees:
   - Coaches' reasoning steps (transparent thinking)
   - Challenges to address (learn by doing)
   - Current score (Scalability, Reliability, Elegance)
   - Score progress
   ↓
7. User modifies design
   ↓
8. Loop back to step 3
   ↓
9. When ready, advance to stress testing phase
   ↓
10. Complete evaluation when finished
```

## Key Files

### Backend (`/agents`)
```
main.py                   # FastAPI app with 10 endpoints
config.py                 # Settings & environment
models/schemas.py         # Pydantic type system
db/database.py            # SQLite + CRUD
agents/coaches.py         # 3 coach analyzers
agents/coach_team.py      # Per-session orchestration
services/game_service.py  # Game mechanics: scores, badges
requirements.txt          # Python dependencies
setup.py                  # Setup script
test_api.py               # API integration tests
README.md                 # Full documentation
INTEGRATION_GUIDE.md      # Frontend integration guide
DEPLOYMENT.md             # Production deployment
```

### Frontend (`/webapp`)
```
src/App.tsx               # Main app component
src/components/
├── Canvas.tsx            # Design canvas
├── Sidebar.tsx           # Score & progress
├── AIReviewer.tsx        # Coach feedback display
└── ...

src/services/
└── coachingClient.ts     # API client (needs update)

src/lib/
└── utils.ts              # Helper functions
```

## Configuration

### .env File

```bash
# Server
ENVIRONMENT=development              # development | production
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/arch_sense_game.db

# AI (optional - coaches work without it)
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-3.1-pro-preview

# Game
DIFFICULTY_LEVEL=1                   # Starting difficulty
COACHING_STYLE=balanced              # aggressive | balanced | gentle
ENABLE_HINTS=true

# Frontend
CORS_ORIGIN=http://localhost:5173
CORS_ALLOW_CREDENTIALS=true
```

## Troubleshooting

### "Cannot connect to server"
- ✅ Is FastAPI running? (`python main.py`)
- ✅ Is port 8000 free? (`lsof -i :8000`)
- ✅ Check firewall/network settings

### "Module not found" error
- ✅ Did you install dependencies? (`pip install -r requirements.txt`)
- ✅ Are you in the `agents` directory?

### "Database locked"
- ✅ Close other connections to SQLite
- ✅ Delete `data/arch_sense_game.db` and restart

### "CORS errors in browser console"
- ✅ Check CORS_ORIGIN in .env matches frontend URL
- ✅ Restart FastAPI server after changing .env

### "API returns 400: invalid JSON"
- ✅ Check request body format (nodes/edges structure)
- ✅ Verify all required fields sent

## Performance Tips

- **Coaching speed**: Adjust COACHING_STYLE
  - `gentle` = faster responses
  - `aggressive` = slower, deeper analysis
- **UI updates**: Coaches typically respond in <1s
- **Database**: SQLite fine for dev, use PostgreSQL for 100+ concurrent users
- **Load testing**: Run `test_api.py` before production

## Next Steps

### For Development
1. ✅ Run both servers (backend + frontend)
2. 🔨 Modify coaches in `agents/coaches.py`
3. 🎨 Customize game scoring in `services/game_service.py`
4. 🧠 Add more badges in `services/game_service.py`
5. 📊 View all games via `/sessions` endpoint

### For Frontend Integration
1. Update `webapp/src/lib/coachingClient.ts` (see INTEGRATION_GUIDE.md)
2. Add coach feedback display in `webapp/src/components/`
3. Show reasoning_steps in UI
4. Display badges and score updates
5. Test full game loop

### For Production
1. See DEPLOYMENT.md for Docker, Cloud Run, AWS Lambda, Heroku
2. Configure real database (PostgreSQL)
3. Set GEMINI_API_KEY for enhanced coaching
4. Enable logging and monitoring
5. Set up backups

## Learning Resources

### Coaches' Eval Logic
- Read `agents/coaches.py` to understand how coaches analyze
- See `agents/coach_team.py` for reasoning chain
- Check `services/game_service.py` for scoring rules

### FastAPI
- API docs auto-generated: `http://localhost:8000/docs`
- Full API reference: https://fastapi.tiangolo.com/

### CrewAI
- Agent framework: https://github.com/joaomdmoura/crewai
- Used for per-session coaching continuity

### Game Design
- See badges/progression in `services/game_service.py`
- Difficulty scaling logic in `GameService.calculate_difficulty_level()`
- Stress scenarios in `GameService.suggest_stress_scenario()`

## Common Tasks

### Change Coaching Intensity
Edit `.env`:
```bash
COACHING_STYLE=aggressive  # or gentle, balanced
```

### Add a New Badge
In `services/game_service.py`:
```python
BADGES = {
    "new_badge_name": Badge(
        name="New Badge",
        description="...",
        icon="🏆",
        condition=lambda design: ...
    )
}
```

### Increase Difficulty Speed
In `services/game_service.py`:
```python
# Adjust calculate_difficulty_level() logic
```

### Custom Scenarios
In `main.py` POST /sessions:
```python
# Add scenario selection logic
# Pass to coach_team initialization
```

## Support

- 📖 See README.md in `agents/` folder
- 🔗 See INTEGRATION_GUIDE.md for frontend setup
- 🚀 See DEPLOYMENT.md for production
- 🐛 Check error logs: `docker logs arch-sense-api`

---

**You're all set! 🎮 Start designing and learn architecture through coaching!**

Questions? Check the docs or examine the code—it's clean and well-commented.
