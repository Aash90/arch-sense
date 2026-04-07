import { Router } from 'express';
import sessionsRouter from './sessions.js';
import aiRouter from './ai.js';
import healthRouter from './health.js';

const router = Router();

// Health check
router.use('/health', healthRouter);

// Sessions endpoints
router.use('/sessions', sessionsRouter);

// AI endpoints
router.use('/ai', aiRouter);

export default router;
