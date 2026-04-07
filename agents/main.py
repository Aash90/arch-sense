"""
FastAPI main application with game flow routes.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from models.schemas import (
    SessionCreate, SessionResponse, DesignSubmission, CoachDecision,
    GamePhase, ArchitectureDesign, GameScore, EvaluationResult
)
from db.database import db
from agents.coach_team import CoachTeam
from services.game_service import GameService, SessionService, EvaluationService

# Global session store for per-session agents
_session_agents: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("🎮 Arch-Sense Coaching Game Server Starting...")
    db.init_schema()
    print("✅ Database initialized")
    yield
    print("🎮 Server shutting down...")
    _session_agents.clear()

app = FastAPI(
    title="Arch-Sense Game Server",
    description="Agentic coaching system for architecture design learning",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# SESSION ENDPOINTS
# ============================================================================

@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreate) -> SessionResponse:
    """Create new game session with initialized coach team."""
    
    import uuid
    session_id = str(uuid.uuid4())[:12]
    
    # Create session in database
    session = SessionService.create_session(
        session_id,
        request.scenario,
        request.user_name,
        difficulty_level=settings.difficulty_level,
        coaching_style=settings.coaching_style
    )
    
    # Initialize coach team for this session
    _session_agents[session_id] = CoachTeam(
        session_id=session_id,
        difficulty_level=settings.difficulty_level,
        coaching_style=settings.coaching_style,
        scenario=request.scenario
    )
    
    return SessionResponse(**session)

@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """Get session details and progress."""
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(**session)

@app.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(limit: int = Query(100), offset: int = Query(0)) -> list:
    """List all sessions."""
    sessions = SessionService.list_sessions(limit, offset)
    return [SessionResponse(**s) for s in sessions]

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete session and cleanup agents."""
    success = SessionService.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Cleanup agents
    if session_id in _session_agents:
        del _session_agents[session_id]
    
    return {"status": "deleted"}

# ============================================================================
# GAME LOOP ENDPOINTS (Main coaching flow)
# ============================================================================

@app.post("/sessions/{session_id}/evaluate", response_model=EvaluationResult)
async def evaluate_design(session_id: str, submission: DesignSubmission) -> EvaluationResult:
    """
    Submit design for evaluation.
    Coaches analyze and propose challenges (not solutions).
    Returns ReAct reasoning chain visible to user.
    """
    
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get or create coach team
    if session_id not in _session_agents:
        _session_agents[session_id] = CoachTeam(
            session_id=session_id,
            difficulty_level=session.get("difficulty_level", 1),
            coaching_style=session.get("coaching_style", "aggressive"),
            scenario=session.get("scenario", "")
        )
    
    coach_team = _session_agents[session_id]
    
    # Get current score
    current_score = GameScore(
        scalability=session.get("scalability_score", 0),
        reliability=session.get("reliability_score", 0),
        design_elegance=session.get("design_elegance_score", 0),
        total=session.get("total_score", 0)
    )
    
    # Evaluate design with coaches
    evaluation = coach_team.evaluate_design(
        submission.design,
        current_score,
        GamePhase(session.get("phase", "DESIGN"))
    )
    
    # Update session with new score
    GameService.update_score(session_id, evaluation.current_score)
    
    # Check for earned badges
    earned_badges = GameService.check_badges(
        session_id,
        {"nodes": submission.design.nodes, "edges": submission.design.edges},
        evaluation.current_score,
        evaluation.design_signals
    )
    
    # Save evaluation to history
    EvaluationService.save_evaluation(session_id, evaluation)
    
    # Add earned badges to response
    if earned_badges:
        evaluation.recommendations.append(f"🏆 BADGE EARNED: {earned_badges[0].name}")
    
    # Add next milestone suggestion
    next_milestone = GameService.get_next_milestone(evaluation.current_score, evaluation.design_signals)
    evaluation.recommendations.append(f"Next: {next_milestone}")
    
    return evaluation

@app.post("/sessions/{session_id}/accept-feedback")
async def accept_feedback(session_id: str, decision: CoachDecision):
    """
    User accepts coaching feedback and proposes next move.
    Coach responds with encouragement and next challenge.
    """
    
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    coach_team = _session_agents.get(session_id)
    if not coach_team:
        raise HTTPException(status_code=400, detail="Coach team not initialized")
    
    if decision.accepted:
        response_text = f"Great! You accepted the feedback: {decision.user_response or 'proceeding with design changes'}"
    else:
        response_text = f"Noted your disagreement. Let's see if you can prove it works! {decision.user_response or ''}"
    
    return {
        "status": "processed",
        "coach_response": response_text,
        "encouragement": "Keep iterating—every design is a learning opportunity!"
    }

@app.post("/sessions/{session_id}/advance-phase")
async def advance_phase(session_id: str, new_phase: str):
    """Advance to next game phase (LEARNING → DESIGN → STRESS → EVALUATION)."""
    
    valid_phases = [p.value for p in GamePhase]
    if new_phase not in valid_phases:
        raise HTTPException(status_code=400, detail=f"Invalid phase. Must be one of {valid_phases}")
    
    session = SessionService.advance_phase(session_id, GamePhase(new_phase))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "phase_advanced", "new_phase": new_phase}

@app.get("/sessions/{session_id}/progress")
async def get_progress(session_id: str):
    """Get game progress: score, badges, coach history, next challenges."""
    
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    coach_history = EvaluationService.get_coach_history(session_id)
    design_evolution = EvaluationService.get_design_evolution(session_id)
    
    current_score = GameScore(
        scalability=session.get("scalability_score", 0),
        reliability=session.get("reliability_score", 0),
        design_elegance=session.get("design_elegance_score", 0),
        total=session.get("total_score", 0)
    )
    
    difficulty_level = GameService.calculate_difficulty_level(
        current_score,
        len(design_evolution)
    )
    
    next_stress = GameService.suggest_stress_scenario(difficulty_level, session.get("phase"))
    
    return {
        "session_id": session_id,
        "score": current_score.model_dump(),
        "badges": session.get("badges", []),
        "phase": session.get("phase"),
        "difficulty_level": difficulty_level,
        "iterations": len(design_evolution),
        "coach_feedback_count": len(coach_history),
        "next_milestone": GameService.get_next_milestone(current_score, []),
        "suggested_stress_test": next_stress,
        "coach_history_summary": [
            {
                "coach": h.get("coach_type"),
                "severity": h.get("severity"),
                "challenge": h.get("challenge", "")[:100]
            }
            for h in coach_history[:5]
        ]
    }

@app.get("/sessions/{session_id}/design-evolution")
async def get_design_evolution_endpoint(session_id: str):
    """Get full design evolution (shows ReAct reasoning chain)."""
    
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    evolution = EvaluationService.get_design_evolution(session_id)
    
    return {
        "session_id": session_id,
        "evolution": evolution,
        "total_iterations": len(evolution)
    }

# ============================================================================
# HEALTH & INFO
# ============================================================================

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "active_sessions": len(_session_agents),
        "environment": settings.environment,
        "coaching_style": settings.coaching_style
    }

@app.get("/")
async def root():
    """API info."""
    return {
        "name": "Arch-Sense Game Server",
        "version": "1.0.0",
        "description": "Agentic coaching system for architecture design",
        "endpoints": {
            "sessions": "POST /sessions, GET /sessions, GET /sessions/{id}, DELETE /sessions/{id}",
            "game_loop": "POST /sessions/{id}/evaluate, POST /sessions/{id}/accept-feedback",
            "progress": "GET /sessions/{id}/progress, GET /sessions/{id}/design-evolution",
            "health": "GET /health"
        }
    }

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=False  # Use: uvicorn main:app --reload for development
    )
