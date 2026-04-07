"""
Game service: Handles scoring, badging, progression, and game mechanics.
"""

from typing import List, Optional, Dict
from datetime import datetime
from models.schemas import GameScore, Badge, GamePhase
from db.database import db

class GameService:
    """Manages game mechanics: scoring, badges, difficulty progression."""
    
    # Badge definitions
    BADGES = {
        "load_balancer_master": Badge(
            name="Load Balancer Master",
            description="Added a load balancer and handled 10x spike",
            earned_at=datetime.now(),
            icon="⚖️"
        ),
        "zero_spofs": Badge(
            name="Zero SPOFs",
            description="Eliminated all single points of failure",
            earned_at=datetime.now(),
            icon="🛡️"
        ),
        "async_architect": Badge(
            name="Async Architect",
            description="Implemented message queue with async processing",
            earned_at=datetime.now(),
            icon="📨"
        ),
        "resilient_design": Badge(
            name="Resilient Design",
            description="Survived reliability stress test",
            earned_at=datetime.now(),
            icon="💪"
        ),
        "caching_wizard": Badge(
            name="Caching Wizard",
            description="Added cache layer and improved performance",
            earned_at=datetime.now(),
            icon="⚡"
        ),
        "global_scale": Badge(
            name="Global Scale",
            description="Designed for 100M+ users",
            earned_at=datetime.now(),
            icon="🌍"
        ),
    }
    
    @staticmethod
    def update_score(session_id: str, new_score: GameScore) -> GameScore:
        """Update session score in database."""
        db.update_session(
            session_id,
            scalability_score=new_score.scalability,
            reliability_score=new_score.reliability,
            design_elegance_score=new_score.design_elegance,
            total_score=new_score.total
        )
        return new_score
    
    @staticmethod
    def check_badges(session_id: str, design: Dict, current_score: GameScore,
                    design_signals: List[str]) -> List[Badge]:
        """Check if user earned any badges based on design and score."""
        
        earned = []
        session = db.get_session(session_id)
        existing_badges = session.get('badges', []) if session else []
        existing_badge_names = [b.get('name') if isinstance(b, dict) else b.name for b in existing_badges]
        
        # Load balancer badge
        if "HAS_LOAD_BALANCER" in design_signals and "Load Balancer Master" not in existing_badge_names:
            earned.append(GameService.BADGES["load_balancer_master"])
        
        # Zero SPOFs badge
        spof_count = sum(1 for s in design_signals if "SPOF" in s)
        if spof_count == 0 and "Zero SPOFs" not in existing_badge_names:
            earned.append(GameService.BADGES["zero_spofs"])
        
        # Async architect badge
        if "HAS_MESSAGE_QUEUE" in design_signals and "ASYNC_PROCESSING" in design_signals:
            if "Async Architect" not in existing_badge_names:
                earned.append(GameService.BADGES["async_architect"])
        
        # Caching badge
        if "HAS_CACHE" in design_signals and current_score.scalability > 60:
            if "Caching Wizard" not in existing_badge_names:
                earned.append(GameService.BADGES["caching_wizard"])
        
        # Resilient design badge
        if current_score.reliability > 75:
            if "Resilient Design" not in existing_badge_names:
                earned.append(GameService.BADGES["resilient_design"])
        
        # Global scale badge
        if current_score.scalability > 80:
            if "Global Scale" not in existing_badge_names:
                earned.append(GameService.BADGES["global_scale"])
        
        # Save to database
        if earned:
            all_badges = existing_badges + earned
            db.update_session(session_id, badges=all_badges)
        
        return earned
    
    @staticmethod
    def calculate_difficulty_level(current_score: GameScore, iteration: int) -> int:
        """Calculate difficulty level based on score and iteration count."""
        
        base_level = 1
        
        # Increase difficulty as user gets better
        if current_score.total > 75:
            base_level = 3
        elif current_score.total > 50:
            base_level = 2
        
        # Increase with iterations (user is engaged)
        if iteration > 10:
            base_level = min(5, base_level + 1)
        
        return base_level
    
    @staticmethod
    def get_next_milestone(current_score: GameScore, design_signals: List[str]) -> str:
        """Get the next challenge/milestone for the user."""
        
        if current_score.scalability < 50:
            return "Add a load balancer to distribute traffic"
        
        if current_score.reliability < 50:
            return "Eliminate single points of failure (use replication)"
        
        if "HAS_MESSAGE_QUEUE" not in design_signals:
            return "Add a message queue for async processing"
        
        if "HAS_CACHE" not in design_signals:
            return "Add a caching layer for hot data"
        
        if current_score.design_elegance < 50:
            return "Refactor your design for clarity and elegance"
        
        if current_score.total < 80:
            return "Prepare for stress testing—can you handle 100x traffic?"
        
        return "Congratulations! Your design is ready for production."
    
    @staticmethod
    def suggest_stress_scenario(difficulty_level: int, phase: str) -> Dict:
        """Suggest a stress test scenario based on difficulty."""
        
        scenarios = {
            1: {
                "title": "Light Traffic Spike",
                "description": "Traffic increases by 5x. Can your system handle it?",
                "multiplier": 5,
                "expected_duration": 60  # seconds
            },
            2: {
                "title": "Flash Spike",
                "description": "Celebrity mentions your app. 50x traffic in 2 minutes.",
                "multiplier": 50,
                "expected_duration": 120
            },
            3: {
                "title": "Database Outage",
                "description": "Your primary database goes down. What happens?",
                "failure_type": "database",
                "expected_duration": 180
            },
            4: {
                "title": "Cascading Failure",
                "description": "One microservice fails. Does failure cascade?",
                "failure_type": "service",
                "expected_duration": 240
            },
            5: {
                "title": "DDoS Attack",
                "description": "Sustained attack with malicious traffic patterns.",
                "multiplier": 1000,
                "expected_duration": 300
            }
        }
        
        return scenarios.get(difficulty_level, scenarios[1])


class SessionService:
    """Manages session lifecycle and state."""
    
    @staticmethod
    def create_session(session_id: str, scenario: str, user_name: Optional[str] = None,
                      difficulty_level: int = 1, coaching_style: str = "aggressive") -> Dict:
        """Create new game session."""
        return db.create_session(session_id, scenario, user_name, difficulty_level, coaching_style)
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        return db.get_session(session_id)
    
    @staticmethod
    def update_session(session_id: str, **updates) -> Dict:
        """Update session state."""
        return db.update_session(session_id, **updates)
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete session."""
        return db.delete_session(session_id)
    
    @staticmethod
    def list_sessions(limit: int = 100, offset: int = 0) -> List[Dict]:
        """List all sessions."""
        return db.list_sessions(limit, offset)
    
    @staticmethod
    def advance_phase(session_id: str, new_phase: GamePhase) -> Dict:
        """Advance to next game phase."""
        session = db.get_session(session_id)
        if not session:
            return None
        
        return db.update_session(session_id, phase=new_phase.value)


class EvaluationService:
    """Manages coach evaluations and feedback cycles."""
    
    @staticmethod
    def save_evaluation(session_id: str, evaluation_result) -> None:
        """Save evaluation result and coach feedback."""
        
        # Record coach history
        for feedback in evaluation_result.feedback:
            feedback_id = f"{session_id}_{feedback.coach_type}_{feedback.severity}"
            db.add_coach_feedback(
                feedback_id,
                session_id,
                feedback.coach_type.value,
                feedback.challenge,
                feedback.reasoning,
                feedback.hint,
                feedback.severity
            )
        
        # Record design evolution
        evolution_id = f"{session_id}_v{len(evaluation_result.reasoning_steps)}"
        db.record_design_evolution(
            evolution_id,
            session_id,
            {
                "nodes": [n.model_dump() for n in evaluation_result.design.nodes],
                "edges": [e.model_dump() for e in evaluation_result.design.edges]
            },
            str(evaluation_result.feedback),
            evaluation_result.reasoning_steps,
            0,  # Would come from previous score
            evaluation_result.current_score.total
        )
    
    @staticmethod
    def get_coach_history(session_id: str) -> List[Dict]:
        """Get coach feedback history for a session."""
        return db.get_coach_history(session_id)
    
    @staticmethod
    def get_design_evolution(session_id: str) -> List[Dict]:
        """Get design evolution history (for ReAct reasoning visibility)."""
        return db.get_design_evolution(session_id)
