import { GoogleGenAI } from '@google/genai';
import { config } from '../config/index.js';
import { Message, Evaluation } from '../types.js';
import { logger } from '../middleware/logger.js';

export class AIService {
  private static ai: GoogleGenAI | null = null;

  static initialize() {
    if (!config.geminiApiKey) {
      logger.warn('GEMINI_API_KEY not configured. AI features will not work.');
      return;
    }

    this.ai = new GoogleGenAI({ apiKey: config.geminiApiKey });
    logger.info('AI service initialized');
  }

  /**
   * Get architect feedback on the current design
   */
  static async getArchitectFeedback(
    nodes: any[],
    edges: any[],
    history: Message[],
    currentPhase: string,
    scenario: string,
    scalingChallenge: string
  ): Promise<string> {
    if (!this.ai) {
      throw new Error('AI service not initialized');
    }

    const systemPrompt = `You are a Senior Architect Reviewer. Your goal is to validate a user's system design thinking.
  
Problem Statement: ${scenario}
Current Phase: ${currentPhase}
User's Scaling Goal: ${scalingChallenge}

Design Graph:
Nodes: ${JSON.stringify(nodes, null, 2)}
Edges: ${JSON.stringify(edges, null, 2)}

Note: Nodes of type 'COMMENT' represent user annotations. If a comment node is connected to another node via an edge, it means the comment specifically applies to that connected component.

Principles:
- Never provide a full "correct" architecture.
- Challenge assumptions actively.
- Ask probing questions about trade-offs (e.g., "Why a SQL database here?", "How does this handle a 10x traffic spike?").
- If in STRESS phase, introduce a specific failure or load event and ask how the system handles it.
- Be demanding but fair.

Response Format:
- Keep it concise.
- Focus on one or two specific areas of the design.
- Use a professional, slightly critical but constructive tone.`;

    try {
      const response = await this.ai.models.generateContent({
        model: config.geminiModel,
        contents: history.map(m => ({
          role: m.role === 'architect' ? 'model' : 'user',
          parts: [{ text: m.content }]
        })),
        config: {
          systemInstruction: systemPrompt,
          temperature: 0.7,
        },
      });

      logger.info('Architect feedback generated');
      return response.text || 'Unable to generate feedback at this time.';
    } catch (error) {
      logger.error('Error generating architect feedback', error);
      throw error;
    }
  }

  /**
   * Get final evaluation of the design
   */
  static async getFinalEvaluation(
    nodes: any[],
    edges: any[],
    history: Message[],
    scenario: string,
    scalingChallenge: string
  ): Promise<Evaluation> {
    if (!this.ai) {
      throw new Error('AI service not initialized');
    }

    const systemPrompt = `You are a Senior Architect Reviewer. Provide a final evaluation of the user's system design.

Problem Statement: ${scenario}
User's Scaling Goal: ${scalingChallenge}

Design Graph:
Nodes: ${JSON.stringify(nodes, null, 2)}
Edges: ${JSON.stringify(edges, null, 2)}

Note: Nodes of type 'COMMENT' represent user annotations. If a comment node is connected to another node via an edge, it means the comment specifically applies to that connected component.

Evaluate across:
1. Scalability (0-100): Can the system handle growth in users/load?
2. Reliability (0-100): Does it handle failures gracefully?
3. Clarity of Thought (0-100): Is the design well-reasoned and documented?

Provide structured feedback in JSON format only (no markdown, just pure JSON):
{
  "scalability": number,
  "reliability": number,
  "clarity": number,
  "feedback": "Overall summary",
  "strengths": ["string"],
  "weaknesses": ["string"]
}`;

    try {
      const response = await this.ai.models.generateContent({
        model: config.geminiModel,
        contents: [
          { role: 'user', parts: [{ text: 'Evaluate my design based on our discussion and the final graph.' }] },
          ...history.map(m => ({
            role: m.role === 'architect' ? 'model' : 'user',
            parts: [{ text: m.content }]
          }))
        ],
        config: {
          systemInstruction: systemPrompt,
          responseMimeType: 'application/json',
        },
      });

      const text = response.text || '{}';
      const evaluation = JSON.parse(text) as Evaluation;
      logger.info('Final evaluation generated');
      return evaluation;
    } catch (error) {
      logger.error('Error generating final evaluation', error);
      throw error;
    }
  }

  /**
   * Get a chat response from the architect
   */
  static async getArchitectMessage(
    userMessage: string,
    history: Message[],
    nodes: any[],
    edges: any[],
    context: any
  ): Promise<string> {
    if (!this.ai) {
      throw new Error('AI service not initialized');
    }

    const systemPrompt = `You are a Senior Architect Reviewer in an interactive design session.

Current context:
- Phase: ${context.phase}
- Scenario: ${context.scenario}
- Scaling Challenge: ${context.scalingChallenge}

Design Graph:
Nodes: ${JSON.stringify(nodes, null, 2)}
Edges: ${JSON.stringify(edges, null, 2)}

Be conversational but critical. Ask probing questions. Challenge assumptions.
Keep responses concise (2-3 sentences max for quick feedback).`;

    try {
      const response = await this.ai.models.generateContent({
        model: config.geminiModel,
        contents: [
          ...history.map(m => ({
            role: m.role === 'architect' ? 'model' : 'user',
            parts: [{ text: m.content }]
          })),
          {
            role: 'user',
            parts: [{ text: userMessage }]
          }
        ],
        config: {
          systemInstruction: systemPrompt,
          temperature: 0.7,
        },
      });

      logger.info('Architect message generated');
      return response.text || 'I appreciate your input, but I need more context to respond meaningfully.';
    } catch (error) {
      logger.error('Error generating architect message', error);
      throw error;
    }
  }
}
