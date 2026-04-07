import 'express-async-errors';
import express from 'express';
import { config, validateConfig } from './config/index.js';
import { initializeDatabase, closeDatabase } from './db/index.js';
import { AIService } from './services/aiService.js';
import { logger, requestLogger } from './middleware/logger.js';
import { errorHandler, notFoundHandler } from './middleware/errorHandler.js';
import apiRoutes from './routes/index.js';

async function startServer() {
  const app = express();

  // Validate configuration
  validateConfig();

  // Initialize database
  try {
    initializeDatabase();
  } catch (error) {
    logger.error('Failed to initialize database', error);
    process.exit(1);
  }

  // Initialize AI service
  AIService.initialize();

  // Middleware
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ limit: '10mb', extended: true }));

  // Logging middleware
  app.use(requestLogger);

  // CORS headers (simple approach - can be enhanced)
  app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', config.corsOrigin);
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    if (req.method === 'OPTIONS') {
      return res.sendStatus(200);
    }
    
    next();
  });

  // API routes
  app.use(`${config.apiPrefix}`, apiRoutes);

  // 404 handler
  app.use(notFoundHandler);

  // Error handler (must be last)
  app.use(errorHandler);

  // Graceful shutdown
  process.on('SIGTERM', () => {
    logger.info('SIGTERM received, shutting down gracefully...');
    closeDatabase();
    server.close(() => {
      logger.info('Server closed');
      process.exit(0);
    });
  });

  process.on('SIGINT', () => {
    logger.info('SIGINT received, shutting down gracefully...');
    closeDatabase();
    server.close(() => {
      logger.info('Server closed');
      process.exit(0);
    });
  });

  // Start server
  const port = config.port;
  const server = app.listen(port, '0.0.0.0', () => {
    logger.info(`🚀 Server running on http://localhost:${port}`);
    logger.info(`📝 Environment: ${config.nodeEnv}`);
    logger.info(`📊 Database: ${config.dbPath}`);
  });
}

startServer().catch(error => {
  logger.error('Failed to start server', error);
  process.exit(1);
});
