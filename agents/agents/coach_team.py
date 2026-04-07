"""
CoachTeam: Manages per-session coach agents and game flow.
Each session gets its own coach team that remembers interactions.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from models.schemas import (
    CoachType, ArchitectureDesign, GameScore, CoachFeedback, GamePhase,
    EvaluationResult
)
from agents.coaches import ScalabilityCoach, ReliabilityCoach, PatternsCoach
from db.database import db

class CoachTeam:
    """
    Stateful coach team for a single session.
    Remembers user interactions and escalates challenges.
    """
    
    def __init__(self, session_id: str, difficulty_level: int = 1, 
                 coaching_style: str = "aggressive", scenario: str = ""):
        self.session_id = session_id
        self.difficulty_level = difficulty_level
        self.coaching_style = coaching_style
        self.scenario = scenario
        
        # Initialize coaches
        self.scalability_coach = ScalabilityCoach.create_agent()
        self.reliability_coach = ReliabilityCoach.create_agent()
        self.patterns_coach = PatternsCoach.create_agent()
        
        # Track iterations
        self.iteration_count = 0
        self.coach_history = []
    
    def evaluate_design(self, design: ArchitectureDesign, current_score: GameScore,
                       phase: GamePhase = GamePhase.DESIGN) -> EvaluationResult:
        """
        Main evaluation method. Coaches analyze design, propose challenges.
        Returns structured feedback with ReAct reasoning visible.
        """
        
        self.iteration_count += 1
        reasoning_steps = []
        all_feedback = []
        
        # REASONING STEP 1: Analyze with all coaches
        reasoning_steps.append("Analyzing design with three specialized coaches...")
        
        scalability_analysis = ScalabilityCoach.analyze_scalability(design, self.scenario, current_score)
        reasoning_steps.append(f"🏗️ Scalability Coach: Found {len(scalability_analysis['spofs'])} SPOFs")
        
        reliability_analysis = ReliabilityCoach.analyze_reliability(design, self.scenario, current_score)
        reasoning_steps.append(f"🛡️ Reliability Coach: Identified {len(reliability_analysis['spofs'])} failure modes")
        
        patterns_analysis = PatternsCoach.analyze_patterns(design, self.scenario, current_score)
        reasoning_steps.append(f"🎯 Patterns Coach: Found {len(patterns_analysis['missing_patterns'])} missing patterns")
        
        # REASONING STEP 2: Prioritize feedback
        reasoning_steps.append("Prioritizing feedback based on severity and coaching style...")
        
        severity_map = {
            "critical": 3,
            "warning": 2,
            "info": 1
        }
        
        # Build coach feedback
        if scalability_analysis['spofs']:
            feedback = self._create_feedback(
                CoachType.SCALABILITY,
                scalability_analysis,
                severity="critical" if self.difficulty_level > 1 else "warning",
                iteration=self.iteration_count
            )
            all_feedback.append(feedback)
            reasoning_steps.append(f"Added scalability challenge: {feedback.challenge[:50]}...")
        
        if reliability_analysis['spofs']:
            feedback = self._create_feedback(
                CoachType.RELIABILITY,
                reliability_analysis,
                severity="critical" if len(reliability_analysis['spofs']) > 2 else "warning",
                iteration=self.iteration_count
            )
            all_feedback.append(feedback)
            reasoning_steps.append(f"Added reliability challenge: {feedback.challenge[:50]}...")
        
        if patterns_analysis['missing_patterns']:
            feedback = self._create_feedback(
                CoachType.PATTERNS,
                patterns_analysis,
                severity="info",
                iteration=self.iteration_count
            )
            all_feedback.append(feedback)
            reasoning_steps.append(f"Added patterns challenge: {feedback.challenge[:50]}...")
        
        # REASONING STEP 3: Escalate based on coaching style
        if self.coaching_style == "aggressive" and self.iteration_count > 3:
            reasoning_steps.append("Escalating feedback intensity (aggressive mode)...")
            for feedback in all_feedback:
                if feedback.severity == "info":
                    feedback.severity = "warning"
                feedback.challenge = f"⚠️ IMPORTANT: {feedback.challenge}"
        
        # REASONING STEP 4: Generate recommendations
        reasoning_steps.append("Generating next milestones...")
        recommendations = []
        
        if scalability_analysis['hints']:
            recommendations.extend(scalability_analysis['hints'])
        if reliability_analysis['hints']:
            recommendations.extend(reliability_analysis['hints'])
        if patterns_analysis['hints']:
            recommendations.extend(patterns_analysis['hints'])
        
        # Calculate scores (mock)
        new_score = self._calculate_score(design, current_score, all_feedback)
        
        # Detect design signals
        signals = self._detect_signals(design)
        
        reasoning_steps.append(f"Session phase: {phase.value}, Difficulty: {self.difficulty_level}")
        reasoning_steps.append("Coaches ready for next iteration...")
        
        # Store in history
        self.coach_history = all_feedback
        
        return EvaluationResult(
            session_id=self.session_id,
            design=design,
            feedback=all_feedback,
            current_score=new_score,
            recommendations=recommendations,
            design_signals=signals,
            coach_observations={
                "scalability": scalability_analysis,
                "reliability": reliability_analysis,
                "patterns": patterns_analysis
            },
            reasoning_steps=reasoning_steps
        )
    
    def _create_feedback(self, coach_type: CoachType, analysis: Dict,
                        severity: str = "info", iteration: int = 1) -> CoachFeedback:
        """Create structured feedback from coach analysis."""
        
        challenge = analysis.get("challenge", "Keep improving your design")
        
        # Escalate challenge based on iteration
        if iteration > 2:
            challenge = f"(Iteration {iteration}) {challenge}"
        
        return CoachFeedback(
            coach_type=coach_type,
            challenge=challenge,
            reasoning=f"Detected: {', '.join(analysis.get('issues', []))}",
            hint=analysis.get('hints', [None])[0],
            severity=severity
        )
    
    def _calculate_score(self, design: ArchitectureDesign, current_score: GameScore,
                        feedback: List[CoachFeedback]) -> GameScore:
        """Calculate game score based on design and feedback."""
        
        new_score = GameScore(
            scalability=current_score.scalability,
            reliability=current_score.reliability,
            design_elegance=current_score.design_elegance
        )
        
        # Increment based on number of nodes/edges (more complete design)
        new_score.scalability += len(design.nodes) * 2
        new_score.reliability += len(design.edges) * 1
        new_score.design_elegance += min(len(design.nodes), 5)
        
        # Cap at 100
        new_score.scalability = min(100, new_score.scalability)
        new_score.reliability = min(100, new_score.reliability)
        new_score.design_elegance = min(100, new_score.design_elegance)
        
        # Total
        new_score.total = (new_score.scalability + new_score.reliability + new_score.design_elegance) // 3
        
        return new_score
    
    def _detect_signals(self, design: ArchitectureDesign) -> List[str]:
        """Detect architectural patterns in the design."""
        
        signals = []
        
        # Check for message queue
        if any(n.type.value == "MESSAGE_QUEUE" for n in design.nodes):
            signals.append("HAS_MESSAGE_QUEUE")
        
        # Check for load balancer
        if any(n.type.value in ["LOAD_BALANCER", "L4_LOAD_BALANCER", "L7_LOAD_BALANCER"] for n in design.nodes):
            signals.append("HAS_LOAD_BALANCER")
        
        # Check for cache
        if any(n.type.value == "CACHE" for n in design.nodes):
            signals.append("HAS_CACHE")
        
        # Check for CDN
        if any(n.type.value == "CDN" for n in design.nodes):
            signals.append("HAS_CDN")
        
        # Check for API Gateway
        if any(n.type.value == "API_GATEWAY" for n in design.nodes):
            signals.append("HAS_API_GATEWAY")
        
        # Check for multiple databases
        db_count = sum(1 for n in design.nodes if n.type.value == "DATABASE")
        if db_count > 1:
            signals.append("HAS_REPLICATED_DB")
        elif db_count == 1:
            signals.append("SPOF_DATABASE")
        
        return signals
