import { Router } from 'express';
import { AIController } from '../controllers/aiController.js';

const router = Router();

// Get architect feedback
router.post('/feedback', AIController.getArchitectFeedback);

// Get final evaluation
router.post('/evaluate', AIController.evaluateDesign);

// Send message to architect
router.post('/message', AIController.sendMessage);

export default router;
