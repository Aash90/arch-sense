import { sessionDb } from '../db/index.js';
import { SessionData, UpdateSessionRequest, DesignSignal } from '../types.js';
import { logger } from '../middleware/logger.js';
import { v4 as uuidv4 } from 'crypto';

export class SessionService {
  /**
   * Create a new session
   */
  static createSession(scenario?: string): SessionData {
    const sessionId = uuidv4().split('-')[0]; // Short ID for simplicity
    
    const session = sessionDb.create(sessionId, {
      scenario: scenario || '',
    });
    
    logger.info(`Session created: ${sessionId}`);
    return session;
  }

  /**
   * Get a session by ID
   */
  static getSession(id: string): SessionData | null {
    const session = sessionDb.get(id);
    if (!session) {
      logger.warn(`Session not found: ${id}`);
    }
    return session;
  }

  /**
   * Update a session
   */
  static updateSession(id: string, updates: UpdateSessionRequest): SessionData | null {
    const existing = sessionDb.get(id);
    if (!existing) {
      logger.warn(`Cannot update non-existent session: ${id}`);
      return null;
    }

    const updated = sessionDb.update(id, updates);
    logger.info(`Session updated: ${id}`, { updatedFields: Object.keys(updates) });
    return updated;
  }

  /**
   * Delete a session
   */
  static deleteSession(id: string): boolean {
    const deleted = sessionDb.delete(id);
    if (deleted) {
      logger.info(`Session deleted: ${id}`);
    }
    return deleted;
  }

  /**
   * List all sessions
   */
  static listSessions(limit = 100, offset = 0): SessionData[] {
    return sessionDb.listAll(limit, offset);
  }

  /**
   * Get session summary
   */
  static getSessionSummary(session: SessionData) {
    return {
      id: session.id,
      phase: session.phase,
      nodesCount: session.nodes.length,
      edgesCount: session.edges.length,
      messagesCount: session.messages.length,
      signals: session.signals,
      hasEvaluation: !!session.evaluation,
      createdAt: session.createdAt,
      updatedAt: session.updatedAt,
    };
  }

  /**
   * Analyze design signals from architecture
   */
  static analyzeArchitectureSignals(nodes: any[], edges: any[]): DesignSignal[] {
    const signals: DesignSignal[] = [];

    // Check for Message Queue
    const hasQueue = nodes.some(n => n.type === 'MESSAGE_QUEUE');
    if (hasQueue) {
      signals.push('HAS_MESSAGE_QUEUE');
    }

    // Check for Load Balancer
    const hasLB = nodes.some(n => 
      n.type === 'LOAD_BALANCER' || 
      n.type === 'L4_LOAD_BALANCER' || 
      n.type === 'L7_LOAD_BALANCER'
    );
    if (!hasLB && nodes.length > 2) {
      signals.push('NO_LOAD_BALANCER');
    }

    // Check for Direct External Calls
    const externalNodes = nodes.filter(n => n.type === 'EXTERNAL_SERVICE');
    const queueNodes = nodes.filter(n => n.type === 'MESSAGE_QUEUE');

    const hasDirectExternalCall = edges.some(edge => {
      const targetIsExternal = externalNodes.some(n => n.id === edge.target);
      const sourceIsQueue = queueNodes.some(n => n.id === edge.source);
      return targetIsExternal && !sourceIsQueue;
    });

    if (hasDirectExternalCall) {
      signals.push('DIRECT_EXTERNAL_CALL');
    }

    // Check for Async Processing
    const hasAsyncProcessing = edges.some(edge => {
      const sourceIsQueue = queueNodes.some(n => n.id === edge.source);
      const targetIsMicroservice = nodes.some(n => 
        n.id === edge.target && n.type === 'MICROSERVICE'
      );
      return sourceIsQueue && targetIsMicroservice;
    });

    if (hasAsyncProcessing) {
      signals.push('ASYNC_PROCESSING');
    }

    // Check for SPOF Database
    const dbNodes = nodes.filter(n => n.type === 'DATABASE');
    if (dbNodes.length === 1) {
      signals.push('SPOF_DATABASE');
    }

    return signals;
  }

  /**
   * Validate session data
   */
  static validateSessionData(data: UpdateSessionRequest): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (data.nodes !== undefined && !Array.isArray(data.nodes)) {
      errors.push('nodes must be an array');
    }

    if (data.edges !== undefined && !Array.isArray(data.edges)) {
      errors.push('edges must be an array');
    }

    if (data.phase && !['PROBLEM_STATEMENT', 'DESIGN', 'STRESS', 'EVALUATION'].includes(data.phase)) {
      errors.push('Invalid phase');
    }

    if (data.messages !== undefined && !Array.isArray(data.messages)) {
      errors.push('messages must be an array');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
