import { Request, Response } from 'express';
import { SessionService } from '../services/sessionService.js';
import { AppError } from '../middleware/errorHandler.js';
import { logger } from '../middleware/logger.js';
import { ApiResponse, SessionData } from '../types.js';

export class SessionController {
  /**
   * GET /api/sessions
   * Get current session or list all sessions
   */
  static async getSessions(req: Request, res: Response<ApiResponse<SessionData | SessionData[]>>) {
    try {
      const { limit = 10, offset = 0 } = req.query;
      const sessions = SessionService.listSessions(
        parseInt(limit as string),
        parseInt(offset as string)
      );

      res.json({
        success: true,
        data: sessions,
      });
    } catch (error) {
      logger.error('Error fetching sessions', error);
      throw new AppError(500, 'Failed to fetch sessions');
    }
  }

  /**
   * POST /api/sessions
   * Create a new session
   */
  static async createSession(req: Request, res: Response<ApiResponse<SessionData>>) {
    try {
      const { scenario } = req.body;
      const session = SessionService.createSession(scenario);

      res.status(201).json({
        success: true,
        data: session,
      });
    } catch (error) {
      logger.error('Error creating session', error);
      throw new AppError(500, 'Failed to create session');
    }
  }

  /**
   * GET /api/sessions/:id
   * Get a specific session
   */
  static async getSession(req: Request, res: Response<ApiResponse<SessionData>>) {
    try {
      const { id } = req.params;
      const session = SessionService.getSession(id);

      if (!session) {
        throw new AppError(404, `Session ${id} not found`);
      }

      res.json({
        success: true,
        data: session,
      });
    } catch (error) {
      if (error instanceof AppError) throw error;
      logger.error('Error fetching session', error);
      throw new AppError(500, 'Failed to fetch session');
    }
  }

  /**
   * POST /api/sessions/:id
   * Update a session
   */
  static async updateSession(req: Request, res: Response<ApiResponse<SessionData>>) {
    try {
      const { id } = req.params;
      const updates = req.body;

      // Validate request
      const validation = SessionService.validateSessionData(updates);
      if (!validation.valid) {
        throw new AppError(400, `Validation failed: ${validation.errors.join(', ')}`);
      }

      // If nodes or edges present, auto-detect signals
      if (updates.nodes || updates.edges) {
        const existing = SessionService.getSession(id);
        if (existing) {
          const nodes = updates.nodes || existing.nodes;
          const edges = updates.edges || existing.edges;
          updates.signals = SessionService.analyzeArchitectureSignals(nodes, edges);
        }
      }

      const session = SessionService.updateSession(id, updates);

      if (!session) {
        throw new AppError(404, `Session ${id} not found`);
      }

      res.json({
        success: true,
        data: session,
      });
    } catch (error) {
      if (error instanceof AppError) throw error;
      logger.error('Error updating session', error);
      throw new AppError(500, 'Failed to update session');
    }
  }

  /**
   * DELETE /api/sessions/:id
   * Delete a session
   */
  static async deleteSession(req: Request, res: Response<ApiResponse<null>>) {
    try {
      const { id } = req.params;
      const deleted = SessionService.deleteSession(id);

      if (!deleted) {
        throw new AppError(404, `Session ${id} not found`);
      }

      res.json({
        success: true,
      });
    } catch (error) {
      if (error instanceof AppError) throw error;
      logger.error('Error deleting session', error);
      throw new AppError(500, 'Failed to delete session');
    }
  }

  /**
   * GET /api/sessions/:id/summary
   * Get session summary
   */
  static async getSessionSummary(req: Request, res: Response<ApiResponse<any>>) {
    try {
      const { id } = req.params;
      const session = SessionService.getSession(id);

      if (!session) {
        throw new AppError(404, `Session ${id} not found`);
      }

      const summary = SessionService.getSessionSummary(session);

      res.json({
        success: true,
        data: summary,
      });
    } catch (error) {
      if (error instanceof AppError) throw error;
      logger.error('Error fetching session summary', error);
      throw new AppError(500, 'Failed to fetch session summary');
    }
  }
}
