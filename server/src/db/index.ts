import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import { config } from '../config/index.js';
import { SessionData } from '../types.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

let db: Database.Database | null = null;

export function initializeDatabase(): Database.Database {
  const dbPath = config.dbPath;
  
  // Ensure data directory exists
  const dir = path.dirname(dbPath);
  try {
    // Create directory if it doesn't exist
    if (!dir.startsWith('/')) {
      const absolutePath = path.join(process.cwd(), dir);
      require('fs').mkdirSync(absolutePath, { recursive: true });
    }
  } catch (e) {
    // Directory might already exist or we're in a restricted environment
  }

  db = new Database(dbPath);
  db.pragma('journal_mode = WAL');
  
  // Create tables
  createTables();
  
  console.log(`✓ Database initialized at ${dbPath}`);
  return db;
}

export function getDatabase(): Database.Database {
  if (!db) {
    throw new Error('Database not initialized. Call initializeDatabase() first.');
  }
  return db;
}

function createTables() {
  if (!db) return;

  // Sessions table
  db.exec(`
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY,
      nodes TEXT NOT NULL DEFAULT '[]',
      edges TEXT NOT NULL DEFAULT '[]',
      phase TEXT NOT NULL DEFAULT 'PROBLEM_STATEMENT',
      scenario TEXT NOT NULL DEFAULT '',
      scaling_challenge TEXT NOT NULL DEFAULT '',
      signals TEXT NOT NULL DEFAULT '[]',
      messages TEXT NOT NULL DEFAULT '[]',
      evaluation TEXT,
      stress_events TEXT NOT NULL DEFAULT '[]',
      current_stress_index INTEGER NOT NULL DEFAULT -1,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    )
  `);

  // Create index for lookups
  db.exec(`
    CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at)
  `);
}

/**
 * Database operations for sessions
 */
export const sessionDb = {
  create: (id: string, initialData: Partial<SessionData> = {}): SessionData => {
    if (!db) throw new Error('Database not initialized');

    const now = Date.now();
    const data: SessionData = {
      id,
      nodes: initialData.nodes || [],
      edges: initialData.edges || [],
      phase: initialData.phase || 'PROBLEM_STATEMENT',
      scenario: initialData.scenario || '',
      scalingChallenge: initialData.scalingChallenge || '',
      signals: initialData.signals || [],
      messages: initialData.messages || [],
      evaluation: initialData.evaluation || null,
      stressEvents: initialData.stressEvents || [],
      currentStressIndex: initialData.currentStressIndex ?? -1,
      createdAt: now,
      updatedAt: now,
    };

    const stmt = db.prepare(`
      INSERT INTO sessions (
        id, nodes, edges, phase, scenario, scaling_challenge,
        signals, messages, evaluation, stress_events, current_stress_index,
        created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      data.id,
      JSON.stringify(data.nodes),
      JSON.stringify(data.edges),
      data.phase,
      data.scenario,
      data.scalingChallenge,
      JSON.stringify(data.signals),
      JSON.stringify(data.messages),
      data.evaluation ? JSON.stringify(data.evaluation) : null,
      JSON.stringify(data.stressEvents),
      data.currentStressIndex,
      data.createdAt,
      data.updatedAt
    );

    return data;
  },

  get: (id: string): SessionData | null => {
    if (!db) throw new Error('Database not initialized');

    const stmt = db.prepare('SELECT * FROM sessions WHERE id = ?');
    const row = stmt.get(id) as any;

    if (!row) return null;

    return {
      id: row.id,
      nodes: JSON.parse(row.nodes),
      edges: JSON.parse(row.edges),
      phase: row.phase,
      scenario: row.scenario,
      scalingChallenge: row.scaling_challenge,
      signals: JSON.parse(row.signals),
      messages: JSON.parse(row.messages),
      evaluation: row.evaluation ? JSON.parse(row.evaluation) : null,
      stressEvents: JSON.parse(row.stress_events),
      currentStressIndex: row.current_stress_index,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  },

  update: (id: string, updates: Partial<SessionData>): SessionData | null => {
    if (!db) throw new Error('Database not initialized');

    const existing = sessionDb.get(id);
    if (!existing) return null;

    const merged: SessionData = {
      ...existing,
      ...updates,
      updatedAt: Date.now(),
    };

    const stmt = db.prepare(`
      UPDATE sessions SET
        nodes = ?,
        edges = ?,
        phase = ?,
        scenario = ?,
        scaling_challenge = ?,
        signals = ?,
        messages = ?,
        evaluation = ?,
        stress_events = ?,
        current_stress_index = ?,
        updated_at = ?
      WHERE id = ?
    `);

    stmt.run(
      JSON.stringify(merged.nodes),
      JSON.stringify(merged.edges),
      merged.phase,
      merged.scenario,
      merged.scalingChallenge,
      JSON.stringify(merged.signals),
      JSON.stringify(merged.messages),
      merged.evaluation ? JSON.stringify(merged.evaluation) : null,
      JSON.stringify(merged.stressEvents),
      merged.currentStressIndex,
      merged.updatedAt,
      id
    );

    return merged;
  },

  delete: (id: string): boolean => {
    if (!db) throw new Error('Database not initialized');

    const stmt = db.prepare('DELETE FROM sessions WHERE id = ?');
    const result = stmt.run(id);
    return (result.changes ?? 0) > 0;
  },

  listAll: (limit = 100, offset = 0): SessionData[] => {
    if (!db) throw new Error('Database not initialized');

    const stmt = db.prepare(`
      SELECT * FROM sessions
      ORDER BY created_at DESC
      LIMIT ? OFFSET ?
    `);

    const rows = stmt.all(limit, offset) as any[];
    return rows.map(row => ({
      id: row.id,
      nodes: JSON.parse(row.nodes),
      edges: JSON.parse(row.edges),
      phase: row.phase,
      scenario: row.scenario,
      scalingChallenge: row.scaling_challenge,
      signals: JSON.parse(row.signals),
      messages: JSON.parse(row.messages),
      evaluation: row.evaluation ? JSON.parse(row.evaluation) : null,
      stressEvents: JSON.parse(row.stress_events),
      currentStressIndex: row.current_stress_index,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    }));
  },
};

export function closeDatabase() {
  if (db) {
    db.close();
    db = null;
  }
}
