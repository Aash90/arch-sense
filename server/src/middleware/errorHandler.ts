import { Request, Response, NextFunction } from 'express';
import { ApiResponse } from '../types.js';
import { logger } from './logger.js';

export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational: boolean = true
  ) {
    super(message);
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Express error handling middleware
 */
export function errorHandler(
  err: Error | AppError,
  req: Request,
  res: Response<ApiResponse<null>>,
  next: NextFunction
) {
  logger.error('Request error', err);

  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      success: false,
      error: err.message,
    });
  }

  // Unexpected errors
  if (process.env.NODE_ENV === 'production') {
    res.status(500).json({
      success: false,
      error: 'Internal Server Error',
    });
  } else {
    res.status(500).json({
      success: false,
      error: err.message || 'Internal Server Error',
    });
  }
}

/**
 * 404 handler
 */
export function notFoundHandler(
  req: Request,
  res: Response<ApiResponse<null>>,
  next: NextFunction
) {
  throw new AppError(404, `Route ${req.method} ${req.path} not found`);
}
