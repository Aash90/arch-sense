"""
Individual coach definitions using CrewAI.
Each coach is a specialized critic/mentor for the user's design.
"""

from crewai import Agent, Task
from models.schemas import CoachType, ComponentType, ArchitectureDesign, GameScore, GamePhase

class ScalabilityCoach:
    """Evaluates design for scalability issues and challenges."""
    
    @staticmethod
    def create_agent():
        return Agent(
            role="Scalability Architecture Coach",
            goal="Identify scalability bottlenecks and push user to think about load distribution, caching, and horizontal scaling",
            backstory="""You are an experienced distributed systems coach who has handled systems at scale.
            You don't give solutions—you ask probing questions that force users to think about:
            - Load distribution (where's the bottleneck?)
            - Caching strategies
            - Database scaling (sharding, replication)
            - Queue-based async processing
            - CDN and edge cases
            
            Your role is to be a challenging but fair critic.""",
            verbose=True
        )
    
    @staticmethod
    def analyze_scalability(design: ArchitectureDesign, scenario: str, current_score: GameScore) -> dict:
        """
        Analyze design for scalability issues.
        Returns identified issues, challenges, and next steps.
        """
        issues = []
        spofs = []
        hints = []
        
        # Check for single database (SPOF)
        db_count = sum(1 for n in design.nodes if n.type == ComponentType.DATABASE)
        if db_count == 1:
            spofs.append("Single database instance—10x traffic spike will overwhelm it")
            issues.append("SPOF_DATABASE")
        elif db_count == 0:
            issues.append("NO_DATABASE")
        
        # Check for load balancer
        lb_count = sum(1 for n in design.nodes if n.type in [
            ComponentType.LOAD_BALANCER, ComponentType.L4_LOAD_BALANCER, ComponentType.L7_LOAD_BALANCER
        ])
        if lb_count == 0 and len(design.nodes) > 2:
            issues.append("NO_LOAD_BALANCER")
            spofs.append("No load balancer—all traffic hits one service")
        
        # Check for cache
        cache_count = sum(1 for n in design.nodes if n.type == ComponentType.CACHE)
        if cache_count == 0:
            issues.append("NO_CACHE")
            hints.append("Think about hot data that gets queried repeatedly. Can you cache it?")
        
        # Check for CDN
        cdn_count = sum(1 for n in design.nodes if n.type == ComponentType.CDN)
        if cdn_count == 0:
            hints.append("For global users, where will you cache static assets?")
        
        return {
            "issues": issues,
            "spofs": spofs,
            "hints": hints,
            "challenge": f"Your design has {len(spofs)} potential SPOFs. How will you eliminate them?",
            "next_milestone": "Tolerate 100x traffic spike without service degradation"
        }


class ReliabilityCoach:
    """Evaluates design for fault tolerance and reliability."""
    
    @staticmethod
    def create_agent():
        return Agent(
            role="Reliability & Fault Tolerance Coach",
            goal="Identify reliability risks and challenge user to build fault-tolerant systems",
            backstory="""You are a battle-hardened SRE who has dealt with outages.
            You focus on:
            - Redundancy and failover
            - Circuit breakers and retries
            - Graceful degradation
            - Health checks and monitoring
            - Disaster recovery
            
            You challenge users with scenarios: "Your database is down. What happens?"
            and "Third-party API you depend on is out. How do you recover?"
            """,
            verbose=True
        )
    
    @staticmethod
    def analyze_reliability(design: ArchitectureDesign, scenario: str, current_score: GameScore) -> dict:
        """
        Analyze design for reliability issues.
        Returns identified failure modes and challenges.
        """
        issues = []
        spofs = []
        hints = []
        
        # Check for multiple databases (replication)
        db_nodes = [n for n in design.nodes if n.type == ComponentType.DATABASE]
        if len(db_nodes) == 1:
            spofs.append("Single database—if it fails, all users are affected")
            issues.append("NO_DB_REPLICATION")
        
        # Check for message queue (async resilience)
        queue_count = sum(1 for n in design.nodes if n.type == ComponentType.MESSAGE_QUEUE)
        if queue_count == 0:
            issues.append("NO_MESSAGE_QUEUE")
            hints.append("Synchronous calls to external services are risky. What if they're slow?")
        
        # Check for direct external calls (anti-pattern)
        external_direct = False
        for edge in design.edges:
            target_node = next((n for n in design.nodes if n.id == edge.target), None)
            if target_node and target_node.type == ComponentType.EXTERNAL_SERVICE:
                source_node = next((n for n in design.nodes if n.id == edge.source), None)
                if source_node and source_node.type != ComponentType.MESSAGE_QUEUE:
                    external_direct = True
                    break
        
        if external_direct:
            issues.append("DIRECT_EXTERNAL_CALLS")
            spofs.append("Direct calls to external services without queue—failures cascade")
        
        # Check for monitoring/health
        if len(design.nodes) > 0 and not any("monitor" in n.label.lower() for n in design.nodes):
            hints.append("How will you know when something breaks? Where's your monitoring?")
        
        return {
            "issues": issues,
            "spofs": spofs,
            "hints": hints,
            "challenge": f"I see {len(spofs)} failure modes. Can you handle an outage?",
            "next_milestone": "Survive any service failure without user impact"
        }


class PatternsCoach:
    """Evaluates design for architectural patterns and elegance."""
    
    @staticmethod
    def create_agent():
        return Agent(
            role="Architecture Patterns & Design Coach",
            goal="Challenge user to use proven patterns and think about system elegance",
            backstory="""You are a patterns expert who knows CQRS, event sourcing, saga pattern, strangler fig, and more.
            You focus on:
            - Are the right patterns being used?
            - Is the design understandable?
            - Are there anti-patterns?
            - Could this be simplified?
            
            You push for clean, elegant architecture—not overcomplicated.""",
            verbose=True
        )
    
    @staticmethod
    def analyze_patterns(design: ArchitectureDesign, scenario: str, current_score: GameScore) -> dict:
        """
        Analyze design for architectural patterns.
        Returns pattern observations and challenges.
        """
        issues = []
        missing_patterns = []
        hints = []
        
        # Check for async processing pattern
        has_queue = any(n.type == ComponentType.MESSAGE_QUEUE for n in design.nodes)
        has_async = False
        if has_queue:
            for edge in design.edges:
                source_node = next((n for n in design.nodes if n.id == edge.source), None)
                target_node = next((n for n in design.nodes if n.id == edge.target), None)
                if source_node and source_node.type == ComponentType.MESSAGE_QUEUE:
                    if target_node and target_node.type == ComponentType.MICROSERVICE:
                        has_async = True
        
        if not has_async and has_queue:
            issues.append("QUEUE_WITHOUT_ASYNC_PROCESSING")
        
        # Check for API gateway
        has_api_gateway = any(n.type == ComponentType.API_GATEWAY for n in design.nodes)
        if not has_api_gateway and len(design.nodes) > 2:
            missing_patterns.append("API_GATEWAY")
            hints.append("How do clients talk to your microservices? Do you need an API gateway?")
        
        # Check for circuit breaker pattern (implied if external services exist)
        has_external = any(n.type == ComponentType.EXTERNAL_SERVICE for n in design.nodes)
        if has_external:
            hints.append("External services can fail. Where's your circuit breaker pattern?")
        
        # Elegance scoring
        total_components = len(design.nodes)
        total_connections = len(design.edges)
        
        if total_components > 10:
            hints.append("Is your design getting too complex? Can you simplify?")
        
        if total_connections < total_components - 1:
            hints.append("Is your system fully connected? Could data flow be clearer?")
        
        return {
            "issues": issues,
            "missing_patterns": missing_patterns,
            "hints": hints,
            "challenge": "Your design is functional but lacks elegance. What patterns would improve it?",
            "next_milestone": "Design should be intuitive and testable"
        }
