# Agentic System Integration Guide

Connecting the FastAPI coaching server to your React frontend.

## Architecture

```
React Frontend (Port 5173)
    ↓ (HTTP/JSON)
FastAPI Coaching Server (Port 8000)
    ↓
CrewAI Coach Agents (per-session, stateful)
    ↓
SQLite Database (game state + history)
```

## What Changed

### Old System (Express)
- User designs → sends to backend → backend calls Gemini once → returns feedback
- No coaching continuity, no game mechanics, no visible reasoning

### New System (FastAPI + CrewAI)
- User designs → coaches evaluate with ReAct reasoning → propose challenge (not solution)
- User iterates → coaches remember previous feedback → escalate intensity
- Game mechanics: scores, badges, difficulty progression
- Full transparent reasoning chain shown to user

## Frontend Changes Required

### 1. Update Environment

```bash
# webapp/.env
VITE_API_URL=http://localhost:8000/api  # NEW FastAPI server
# NO GEMINI_API_KEY needed (server handles it)
```

### 2. Create API Client

```typescript
// webapp/src/lib/coachingClient.ts

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface CoachingClient {
  createSession: (scenario: string, userName?: string) => Promise<SessionResponse>;
  getSession: (sessionId: string) => Promise<SessionResponse>;
  submitDesign: (sessionId: string, design: ArchitectureDesign) => Promise<EvaluationResult>;
  acceptFeedback: (sessionId: string, accepted: boolean, response?: string) => Promise<any>;
  getProgress: (sessionId: string) => Promise<ProgressResponse>;
  getDesignEvolution: (sessionId: string) => Promise<EvolutionResponse>;
}

export const coachingClient: CoachingClient = {
  createSession: async (scenario, userName) => {
    const res = await fetch(`${API_URL}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario, user_name: userName })
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  getSession: async (sessionId) => {
    const res = await fetch(`${API_URL}/sessions/${sessionId}`);
    if (!res.ok) throw new Error('Session not found');
    return res.json();
  },

  submitDesign: async (sessionId, design) => {
    const res = await fetch(`${API_URL}/sessions/${sessionId}/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ design, user_notes: '' })
    });
    if (!res.ok) throw new Error('Evaluation failed');
    return res.json();
  },

  acceptFeedback: async (sessionId, accepted, response) => {
    const res = await fetch(`${API_URL}/sessions/${sessionId}/accept-feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accepted, user_response: response })
    });
    if (!res.ok) throw new Error('Failed to process feedback');
    return res.json();
  },

  getProgress: async (sessionId) => {
    const res = await fetch(`${API_URL}/sessions/${sessionId}/progress`);
    if (!res.ok) throw new Error('Failed to get progress');
    return res.json();
  },

  getDesignEvolution: async (sessionId) => {
    const res = await fetch(`${API_URL}/sessions/${sessionId}/design-evolution`);
    if (!res.ok) throw new Error('Failed to get evolution');
    return res.json();
  }
};
```

### 3. Update App.tsx Game Flow

```typescript
// webapp/src/App.tsx

import { coachingClient } from './lib/coachingClient';
import { EvaluationResult, SessionResponse } from './types';

export default function App() {
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [showReasoningChain, setShowReasoningChain] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);

  // Create session on mount
  useEffect(() => {
    const createNewSession = async () => {
      try {
        const newSession = await coachingClient.createSession(
          INITIAL_SCENARIO,
          "Player Name"
        );
        setSession(newSession);
      } catch (error) {
        console.error('Failed to create session:', error);
      }
    };
    createNewSession();
  }, []);

  // Submit design for coach evaluation
  const handleEvaluateDesign = async () => {
    if (!session) return;
    
    setIsEvaluating(true);
    try {
      const result = await coachingClient.submitDesign(session.id, {
        nodes,
        edges
      });
      setEvaluation(result);
      setShowReasoningChain(true);  // Show agent thinking
    } catch (error) {
      console.error('Evaluation failed:', error);
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="game-container">
      {/* Existing Canvas and Sidebar */}
      <Canvas nodes={nodes} setNodes={setNodes} edges={edges} setEdges={setEdges} />
      <Sidebar />

      {/* Score & Progress */}
      {session && (
        <ScoreDisplay
          score={session.score}
          badges={session.badges}
        />
      )}

      {/* Coach Evaluation Panel */}
      {evaluation && (
        <div className="coach-panel">
          {/* Show ReAct Reasoning Chain */}
          {showReasoningChain && (
            <div className="reasoning-chain">
              <h3>🧠 Coach's Reasoning</h3>
              {evaluation.reasoning_steps.map((step, i) => (
                <div key={i} className="reasoning-step">
                  <span className="step-number">{i + 1}.</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          )}

          {/* Coach Feedback - Challenges, Not Solutions */}
          <div className="coach-feedback">
            <h3>👥 Coach Feedback</h3>
            {evaluation.feedback.map((f, i) => (
              <div key={i} className={`feedback-card severity-${f.severity}`}>
                <div className="coach-name">
                  {f.coach_type === 'SCALABILITY' && '🏗️'}
                  {f.coach_type === 'RELIABILITY' && '🛡️'}
                  {f.coach_type === 'PATTERNS' && '🎯'}
                  {' ' + f.coach_type}
                </div>
                <div className="coach-challenge">
                  <strong>Challenge:</strong> {f.challenge}
                </div>
                {f.hint && (
                  <div className="coach-hint">
                    <strong>💡 Hint:</strong> {f.hint}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Next Actions */}
          <div className="next-actions">
            <h3>📋 Next Steps</h3>
            {evaluation.recommendations.map((r, i) => (
              <div key={i} className="recommendation">✓ {r}</div>
            ))}
          </div>

          {/* User Decision */}
          <div className="coach-decision">
            <button onClick={() => handleAcceptFeedback(true)}>
              ✅ Accept Challenge
            </button>
            <button onClick={() => handleAcceptFeedback(false)}>
              ❌ Disagree & Continue
            </button>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={handleEvaluateDesign}
        disabled={isEvaluating}
        className="evaluate-btn"
      >
        {isEvaluating ? '🤔 Coaches Thinking...' : '📊 Submit for Evaluation'}
      </button>
    </div>
  );

  const handleAcceptFeedback = async (accepted: boolean) => {
    if (!session) return;
    try {
      await coachingClient.acceptFeedback(
        session.id,
        accepted,
        accepted ? 'Modifying design' : 'Trying a different approach'
      );
      setShowReasoningChain(false);
      // User can now edit design and submit again
    } catch (error) {
      console.error('Failed to process feedback:', error);
    }
  };
}
```

### 4. Create UI Components

```typescript
// webapp/src/components/ScoreDisplay.tsx

interface ScoreDisplayProps {
  score: GameScore;
  badges: Badge[];
}

export function ScoreDisplay({ score, badges }: ScoreDisplayProps) {
  return (
    <div className="score-panel">
      <div className="score-card">
        <div className="score-value">{score.scalability}</div>
        <div className="score-label">Scalability</div>
      </div>
      <div className="score-card">
        <div className="score-value">{score.reliability}</div>
        <div className="score-label">Reliability</div>
      </div>
      <div className="score-card">
        <div className="score-value">{score.design_elegance}</div>
        <div className="score-label">Elegance</div>
      </div>
      <div className="score-card total">
        <div className="score-value">{score.total}</div>
        <div className="score-label">Total</div>
      </div>

      {/* Badges */}
      <div className="badges">
        {badges.map(badge => (
          <div key={badge.name} className="badge" title={badge.description}>
            {badge.icon} {badge.name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

```typescript
// webapp/src/components/ReasoningChain.tsx

interface ReasoningChainProps {
  steps: string[];
}

export function ReasoningChain({ steps }: ReasoningChainProps) {
  return (
    <div className="reasoning-panel">
      <h3>🧠 How Coaches Think</h3>
      <div className="steps">
        {steps.map((step, i) => (
          <div key={i} className="step">
            <span className="step-num">{i + 1}</span>
            <span className="step-text">{step}</span>
          </div>
        ))}
      </div>
      <p className="info">
        These are the reasoning steps the coaches used to evaluate your design.
      </p>
    </div>
  );
}
```

### 5. Update Types

```typescript
// webapp/src/types/coaching.ts

export interface GameScore {
  scalability: number;
  reliability: number;
  design_elegance: number;
  total: number;
}

export interface Badge {
  name: string;
  description: string;
  icon: string;
  earned_at: string;
}

export interface CoachFeedback {
  coach_type: 'SCALABILITY' | 'RELIABILITY' | 'PATTERNS';
  challenge: string;  // Question, not answer
  reasoning: string;
  hint?: string;
  severity: 'critical' | 'warning' | 'info';
}

export interface EvaluationResult {
  session_id: string;
  design: ArchitectureDesign;
  feedback: CoachFeedback[];
  current_score: GameScore;
  recommendations: string[];
  design_signals: string[];
  reasoning_steps: string[];  // ReAct chain
  coach_observations: Record<string, any>;
}

export interface SessionResponse {
  id: string;
  scenario: string;
  phase: 'LEARNING' | 'DESIGN' | 'STRESS' | 'EVALUATION';
  design: ArchitectureDesign;
  score: GameScore;
  badges: Badge[];
  coach_history: CoachFeedback[];
}

export interface ProgressResponse {
  session_id: string;
  score: GameScore;
  badges: Badge[];
  phase: string;
  difficulty_level: number;
  iterations: number;
  next_milestone: string;
  suggested_stress_test: {
    title: string;
    description: string;
    multiplier?: number;
  };
}
```

## Running Both Servers

### Terminal 1: FastAPI Coaching Server
```bash
cd agents
pip install -r requirements.txt
cp .env.example .env
# Edit .env with GEMINI_API_KEY if desired
python main.py
```

Server runs on `http://localhost:8000`

### Terminal 2: React Frontend
```bash
cd webapp
npm run dev
```

Frontend runs on `http://localhost:5173`

## Testing the Integration

1. **Create Session**
   ```bash
   curl -X POST http://localhost:8000/sessions \
     -H "Content-Type: application/json" \
     -d '{"scenario":"Design notification system"}'
   # Returns session_id
   ```

2. **Submit Design**
   ```bash
   curl -X POST http://localhost:8000/sessions/{session_id}/evaluate \
     -H "Content-Type: application/json" \
     -d '{
       "design": {
         "nodes": [...],
         "edges": [...]
       }
     }'
   # Returns feedback + reasoning_steps
   ```

3. **Check Progress**
   ```bash
   curl http://localhost:8000/sessions/{session_id}/progress
   ```

## Key Differences from Old System

| Aspect | Old (Express) | New (FastAPI) |
|--------|---------------|---------------|
| Server | Express.js | FastAPI |
| AI | Direct Gemini calls | CrewAI agents |
| Coaching | One-off feedback | Continuous coaching |
| Game mechanics | None | Full scoring/badges/progression |
| Statefulness | Stateless | Per-session stateful |
| Reasoning | Hidden | Visible (ReAct) |
| User role | Passive | Active (HITL) |

## Migration Checklist

- [ ] FastAPI server running on 8000
- [ ] React env var updated (VITE_API_URL)
- [ ] API client created (`coachingClient`)
- [ ] App.tsx updated for game loop
- [ ] Components created (ScoreDisplay, ReasoningChain)
- [ ] Types updated (coaching.ts)
- [ ] Test: Create session via curl
- [ ] Test: Submit design via curl
- [ ] Test: Frontend receives evaluation + reasoning
- [ ] Test: User can iterate and improve score
- [ ] Remove old Express server from architecture
- [ ] Update documentation

## Next Steps

1. Start servers (both terminals)
2. Create session in frontend
3. Design on canvas
4. Submit for evaluation
5. See coaches' reasoning chain
6. See challenges (not solutions)
7. Modify design based on challenges
8. Submit again
9. See score improve, badges earned
10. Play through all difficulty levels

---

FastAPI + CrewAI agentic system is now your coaching engine! 🎮
