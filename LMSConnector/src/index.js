import express from 'express';
import helmet from 'helmet';
import cron from 'node-cron';
import { config } from './config.js';
import healthRouter from './routes/health.js';
import adminRouter from './routes/admin.js';
import syncRouter from './routes/sync.js';
import rootRouter from './routes/root.js';
import debugRouter from './routes/debug.js';
import bootstrapRouter from './routes/bootstrap.js';
import { getPool } from './db/pool.js';
import rateLimit from 'express-rate-limit';
import { logger } from './common/logger.js';
import { initPublisher } from './publisher/index.js';
import { initOtel } from './observability/otel.js';
import { initSwagger } from './observability/swagger.js';

const app = express();
app.use(helmet());
app.use(express.json({ limit: '1mb' }));
app.use((req, res, next) => { // structured request logging
  logger.info({ method: req.method, url: req.url }, 'Incoming request');
  next();
});

// Rate limit admin endpoints
const adminLimiter = rateLimit({ windowMs: 60 * 1000, max: 60 });
app.use(adminLimiter);

// Routes
app.use(rootRouter);
app.use(healthRouter);
app.use(adminRouter);
app.use(syncRouter);
app.use(debugRouter);
app.use(bootstrapRouter);

// Startup: DB migration (optional)
(async () => {
  if (config.otel.enable) {
    await initOtel();
    logger.info('OpenTelemetry initialized');
  }
  if (!config.db.disable) {
    try {
      const pool = getPool();
      await pool.query('SELECT NOW()');
      logger.info('DB connected');
      // Seed default Moodle source if env provided
      if (config.moodle.baseUrl && config.moodle.token) {
        const { rows } = await pool.query(
          "SELECT id FROM lms_sources WHERE type='moodle' AND base_url=$1 LIMIT 1",
          [config.moodle.baseUrl]
        );
        if (!rows.length) {
          await pool.query(
            'INSERT INTO lms_sources(type, base_url, token, active) VALUES($1,$2,$3,TRUE)',
            ['moodle', config.moodle.baseUrl, config.moodle.token]
          );
          logger.info('Seeded default Moodle source from env');
        }
      }
    } catch (e) {
      logger.error({ err: e }, 'DB connection failed');
    }
  } else {
    logger.warn('DB disabled by configuration');
  }
  await initPublisher();
  initSwagger(app);
})();

// Cron: every 6 hours
cron.schedule('0 */6 * * *', async () => {
  try {
    console.log('[Cron] Scheduled Moodle sync starting');
    const pool = getPool();
    if (!pool) {
      console.warn('[Cron] DB disabled; skipping sync');
      return;
    }
    const { rows: sources } = await pool.query("SELECT * FROM lms_sources WHERE active=TRUE AND type='moodle'");
    const { syncMoodleSource } = await import('./services/sync.service.js');
    for (const src of sources) {
      try {
        await syncMoodleSource(src);
        console.log(`[Cron] Source ${src.id} synced`);
      } catch (e) {
        console.error(`[Cron] Source ${src.id} failed:`, e.message);
      }
    }
  } catch (e) {
    console.error('[Cron] Unexpected error:', e.message);
  }
});

app.listen(config.port, () => {
  logger.info({ port: config.port }, 'LMSConnector listening');
});
