import { Request, Response, NextFunction } from 'express';

const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3,
};

export function createLogger() {
  return {
    log: (level: keyof typeof logLevels, message: string, data?: any) => {
      const timestamp = new Date().toISOString();
      const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
      
      if (data) {
        console.log(`${prefix} ${message}`, data);
      } else {
        console.log(`${prefix} ${message}`);
      }
    },
    
    error: (message: string, error?: Error | any) => {
      const timestamp = new Date().toISOString();
      console.error(`[${timestamp}] [ERROR] ${message}`, error);
    },
    
    info: (message: string, data?: any) => {
      const timestamp = new Date().toISOString();
      if (data) {
        console.log(`[${timestamp}] [INFO] ${message}`, data);
      } else {
        console.log(`[${timestamp}] [INFO] ${message}`);
      }
    },
    
    warn: (message: string, data?: any) => {
      const timestamp = new Date().toISOString();
      if (data) {
        console.warn(`[${timestamp}] [WARN] ${message}`, data);
      } else {
        console.warn(`[${timestamp}] [WARN] ${message}`);
      }
    },
    
    debug: (message: string, data?: any) => {
      const timestamp = new Date().toISOString();
      if (data) {
        console.log(`[${timestamp}] [DEBUG] ${message}`, data);
      } else {
        console.log(`[${timestamp}] [DEBUG] ${message}`);
      }
    },
  };
}

export const logger = createLogger();

/**
 * Express middleware for request logging
 */
export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    const statusColor = res.statusCode >= 400 ? '\x1b[31m' : '\x1b[32m';
    const reset = '\x1b[0m';
    
    logger.info(
      `${req.method} ${req.path} ${statusColor}${res.statusCode}${reset} ${duration}ms`
    );
  });
  
  next();
}
