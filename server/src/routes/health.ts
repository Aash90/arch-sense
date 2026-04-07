import { Router, Request, Response } from 'express';
import { ApiResponse } from '../types.js';

const router = Router();

router.get('/', (req: Request, res: Response<ApiResponse<{ status: string; timestamp: string }>>) => {
  res.json({
    success: true,
    data: {
      status: 'ok',
      timestamp: new Date().toISOString(),
    },
  });
});

export default router;
