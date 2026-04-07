import { Request, Response } from 'express';
import { AIService } from '../services/aiService.js';
import { SessionService } from '../services/sessionService.js';
import { AppError } from '../middleware/errorHandler.js';
import { logger } from '../middleware/logger.js';
import { ApiResponse, Message, Evaluation } from '../types.js';

export class AIController {
  /**
   * POST /api/ai/feedback
   * Get architect feedback on current design
   */
  static async getArchitectFeedback(
    req: Request,
    res: Response<ApiResponse<{ feedback: string }>>
  ) {
    try {
      const { sessionId, nodes, edges, history, phase, scenario, scalingChallenge } = req.body;

      // Validate required fields
      if (!nodes || !Array.isArray(nodes) || !edges || !Array.isArray(edges)) {
        throw new AppError(400, 'nodes and edges are required');
      }

      if (!history || !Array.isArray(history)) {
        throw new AppError(400, 'history is required');
      }

      if (!phase || !scenario) {
        throw new AppError(400, 'phase and scenario are required');
      }

      const feedback = await AIService.getArchitectFeedback(
        nodes,
        edges,
        history,
        phase,
        scenario,
        scalingChallenge || ''
      );

      res.json({
        success: true,
        data: { feedback },
      });
    } catch (error) {
      if (error instanceof AppError) throw error;
      logger.error('Error getting architect feedback', error);
      throw new AppError(500, 'Failed to get architect feedback');
    }
  }

  /**
   * POST /api/ai/evaluate
   * Get final evaluation of the design
   */
  static async evaluateDesign(
    req: Request,
    res: Response<ApiResponse<{ evaluation: Evaluation }>>
  ) {
    try {
      const { nodes, edges, history, scenario, scalingChallenge } = req.body;

      // Validate required fields
      if (!nodes || !Array.isArray(nodes) || !edges || !Array.isArray(edges)) {
        throw new AppError(400, 'nodes and edges are required');
      }

      if (!history || !Array.isArray(history)) {
        throw new AppError(400, 'history is required');
      }

      if (!scenario) {
        throw new AppError(400, 'scenario is required');
      }

      const evaluation = await AIService.getFinalEvaluation(
        nodes,
        edges,
        history,
        scenario,
        scalingChallenge || ''
      );

      res.json({
        success: true,
        data: { evaluation },
      });
    } catch (error) {
      if (error instanceof AppError) throw error;
      logger.error('Error evaluating design', error);
      throw new AppError(500, 'Failed to evaluate design');
    }
  }

  /**
   * POST /api/ai/message
   * Send a message to the architect AI and get a response
   */
  static async sendMessage(
    req: Request,
    res: Response<ApiResponse<{ message: string }>>,
    next: any
  ) {
    try {
      const { sessionId, userMessage, nodes, edges, history, context } = req.body;

      // Validate required fields
      if (!userMessage || typeof userMessage !== 'string') {
        throw new AppError(400, 'userMessage is required');
      }

      if (!nodes || !Array.isArray(nodes) || !edges || !Array.isArray(edges)) {
        throw new AppError(400, 'nodes and edges are required');
      }

      if (!history || !Array.isArray(history)) {
        throw new AppError(400, 'history is required');
      }

      if (!context) {
        throw new AppError(400, 'context is required');
      }

      const message = await AIService.getArchitectMessage(
        userMessage,
        history,
        nodes,
        edges,
        context
      );

      // If session ID provided, update it with the new message
      if (sessionId) {
        const session = SessionService.getSession(sessionId);
        if (session) {
          const updatedMessages: Message[] = [
            ...history,
            {
              id: Date.now().toString(),
              role: 'user',
              content: userMessage,
              timestamp: Date.now(),
            },
            {
              id: (Date.now() + 1).toString(),
              role: 'architect',
              content: message,
              timestamp: Date.now() + 1,
            },
          ];
          SessionService.updateSession(sessionId, { messages: updatedMessages });
        }
      }

      res.json({
        success: true,
        data: { message },
      });
    } catch (error) {
      if (error instanceof AppError) throw error;
      logger.error('Error sending message', error);
      throw new AppError(500, 'Failed to send message');
    }
  }
}
