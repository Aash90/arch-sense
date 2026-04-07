from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

# Enums
class ComponentType(str, Enum):
    LOAD_BALANCER = "LOAD_BALANCER"
    L4_LOAD_BALANCER = "L4_LOAD_BALANCER"
    L7_LOAD_BALANCER = "L7_LOAD_BALANCER"
    API_GATEWAY = "API_GATEWAY"
    MICROSERVICE = "MICROSERVICE"
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    MESSAGE_QUEUE = "MESSAGE_QUEUE"
    CDN = "CDN"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    COMMENT = "COMMENT"

class GamePhase(str, Enum):
    LEARNING = "LEARNING"
    DESIGN = "DESIGN"
    STRESS = "STRESS"
    EVALUATION = "EVALUATION"

class CoachType(str, Enum):
    SCALABILITY = "SCALABILITY"
    RELIABILITY = "RELIABILITY"
    PATTERNS = "PATTERNS"

# Architecture Models
class SystemNode(BaseModel):
    id: str
    type: ComponentType
    x: float
    y: float
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class SystemEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None

class ArchitectureDesign(BaseModel):
    nodes: List[SystemNode] = Field(default_factory=list)
    edges: List[SystemEdge] = Field(default_factory=list)

# Game/Session Models
class GameScore(BaseModel):
    scalability: int = 0
    reliability: int = 0
    design_elegance: int = 0
    total: int = 0

class Badge(BaseModel):
    name: str
    description: str
    earned_at: datetime
    icon: str

class CoachFeedback(BaseModel):
    coach_type: CoachType
    challenge: str  # The question/challenge, not the answer
    reasoning: str  # Why this matters
    hint: Optional[str] = None  # Help (optional)
    severity: str  # critical, warning, info

class EvaluationResult(BaseModel):
    session_id: str
    design: ArchitectureDesign
    feedback: List[CoachFeedback]
    current_score: GameScore
    recommendations: List[str]  # Next challenges to address
    design_signals: List[str]  # Detected patterns
    coach_observations: Dict[str, Any]  # Detailed coach analysis
    reasoning_steps: List[str]  # ReAct reasoning chain (transparent)

class SessionCreate(BaseModel):
    scenario: str
    user_name: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    scenario: str
    phase: GamePhase
    design: ArchitectureDesign
    score: GameScore
    badges: List[Badge] = Field(default_factory=list)
    coach_history: List[CoachFeedback] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class DesignSubmission(BaseModel):
    design: ArchitectureDesign
    user_notes: Optional[str] = None

class CoachDecision(BaseModel):
    accepted: bool
    user_response: Optional[str] = None

# Coach/Agent Models
class CoachPrompt(BaseModel):
    design: ArchitectureDesign
    scenario: str
    phase: GamePhase
    coach_type: CoachType
    difficulty_level: int
    coaching_style: str
    coach_history: List[CoachFeedback] = Field(default_factory=list)
    current_score: GameScore = Field(default_factory=GameScore)

class CoachAnalysis(BaseModel):
    identified_issues: List[str]
    spofs: List[str]  # Single points of failure
    missing_patterns: List[str]
    improvement_score: int  # 0-100
    challenge_proposed: str
    next_milestone: str
