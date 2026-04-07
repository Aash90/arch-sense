import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from models.schemas import GamePhase, CoachFeedback, GameScore, Badge

class GameDatabase:
    def __init__(self, db_path: str = "data/arch_sense_game.db"):
        self.db_path = db_path
        self._ensure_path()
        self.init_schema()
    
    def _ensure_path(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_schema(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Sessions with game mechanics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                scenario TEXT NOT NULL,
                user_name TEXT,
                phase TEXT NOT NULL DEFAULT 'LEARNING',
                design TEXT NOT NULL DEFAULT '{"nodes":[],"edges":[]}',
                scalability_score INTEGER DEFAULT 0,
                reliability_score INTEGER DEFAULT 0,
                design_elegance_score INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0,
                badges TEXT DEFAULT '[]',
                coach_history TEXT DEFAULT '[]',
                difficulty_level INTEGER DEFAULT 1,
                coaching_style TEXT DEFAULT 'aggressive',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Coach interactions (for continuity)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coach_interactions (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                coach_type TEXT NOT NULL,
                challenge TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                hint TEXT,
                severity TEXT,
                user_response TEXT,
                accepted BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Design history for ReAct reasoning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS design_evolution (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                design TEXT NOT NULL,
                coach_feedback TEXT,
                reasoning_steps TEXT,
                score_before INTEGER,
                score_after INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coach_session ON coach_interactions(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_design_session ON design_evolution(session_id)')
        
        conn.commit()
        conn.close()
    
    # Session CRUD
    def create_session(self, session_id: str, scenario: str, user_name: Optional[str] = None, 
                      difficulty_level: int = 1, coaching_style: str = "aggressive") -> Dict:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions 
            (id, scenario, user_name, phase, difficulty_level, coaching_style)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, scenario, user_name, GamePhase.LEARNING.value, difficulty_level, coaching_style))
        
        conn.commit()
        conn.close()
        
        return self.get_session(session_id)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def update_session(self, session_id: str, **updates) -> Dict:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Handle JSON fields
        if 'design' in updates and isinstance(updates['design'], dict):
            updates['design'] = json.dumps(updates['design'])
        if 'badges' in updates and isinstance(updates['badges'], list):
            updates['badges'] = json.dumps(updates['badges'])
        if 'coach_history' in updates and isinstance(updates['coach_history'], list):
            updates['coach_history'] = json.dumps(updates['coach_history'])
        
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
        values = list(updates.values()) + [session_id]
        
        cursor.execute(f'UPDATE sessions SET {set_clause} WHERE id = ?', values)
        conn.commit()
        conn.close()
        
        return self.get_session(session_id)
    
    def list_sessions(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM sessions ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (limit, offset)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    # Coach interactions
    def add_coach_feedback(self, feedback_id: str, session_id: str, coach_type: str,
                         challenge: str, reasoning: str, hint: Optional[str] = None,
                         severity: str = "info") -> Dict:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO coach_interactions
            (id, session_id, coach_type, challenge, reasoning, hint, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (feedback_id, session_id, coach_type, challenge, reasoning, hint, severity))
        
        conn.commit()
        conn.close()
    
    def get_coach_history(self, session_id: str) -> List[Dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM coach_interactions WHERE session_id = ? ORDER BY created_at DESC',
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    # Design evolution (for ReAct reasoning)
    def record_design_evolution(self, evolution_id: str, session_id: str, design: Dict,
                               coach_feedback: str, reasoning_steps: List[str],
                               score_before: int, score_after: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO design_evolution
            (id, session_id, design, coach_feedback, reasoning_steps, score_before, score_after)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (evolution_id, session_id, json.dumps(design), coach_feedback,
              json.dumps(reasoning_steps), score_before, score_after))
        
        conn.commit()
        conn.close()
    
    def get_design_evolution(self, session_id: str) -> List[Dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM design_evolution WHERE session_id = ? ORDER BY timestamp DESC',
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def delete_session(self, session_id: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM coach_interactions WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM design_evolution WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def _row_to_dict(self, row) -> Dict:
        data = dict(row)
        
        # Parse JSON fields
        if 'design' in data and isinstance(data['design'], str):
            data['design'] = json.loads(data['design'])
        if 'badges' in data and isinstance(data['badges'], str):
            data['badges'] = json.loads(data['badges'])
        if 'coach_history' in data and isinstance(data['coach_history'], str):
            data['coach_history'] = json.loads(data['coach_history'])
        if 'reasoning_steps' in data and isinstance(data['reasoning_steps'], str):
            data['reasoning_steps'] = json.loads(data['reasoning_steps'])
        
        return data

# Global instance
db = GameDatabase()
