import { Router } from 'express';
import { SessionController } from '../controllers/sessionController.js';

const router = Router();

// List all sessions or get current session
router.get('/', SessionController.getSessions);

// Create a new session
router.post('/', SessionController.createSession);

// Get specific session
router.get('/:id', SessionController.getSession);

// Update session
router.post('/:id', SessionController.updateSession);

// Get session summary
router.get('/:id/summary', SessionController.getSessionSummary);

// Delete session
router.delete('/:id', SessionController.deleteSession);

export default router;
