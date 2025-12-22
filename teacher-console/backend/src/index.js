import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import jwt from 'jsonwebtoken';
import { randomUUID } from 'crypto';

import dashboardRoutes from './routes/dashboard.routes.js';
import studentsRoutes from './routes/students.routes.js';
import alertsRoutes from './routes/alerts.routes.js';
import exportRoutes from './routes/export.routes.js';

const app = express();
app.use(cors());
app.use(express.json());

// Attach a per-request ID for correlation
app.use((req, _res, next) => {
  req.id = req.id || randomUUID();
  next();
});

// Structured request logging with request id
morgan.token('id', (req) => req.id);
app.use(
  morgan(':date[iso] [:id] :method :url :status :response-time ms - :res[content-length]')
);

app.get('/', (req, res) => res.json({ status: 'ok', service: 'TeacherConsole Gateway' }));

// Simple dev login endpoint to issue a JWT for testing
app.post('/api/auth/login', (req, res) => {
  try {
    const user = req.body?.user || { id: 1, role: 'teacher', courses: [1] };
    const token = jwt.sign(user, process.env.JWT_SECRET, { expiresIn: process.env.JWT_EXPIRES_IN || '24h' });
    res.json({ token, user });
  } catch (e) {
    res.status(500).json({ error: 'Login failed' });
  }
});
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/students', studentsRoutes);
app.use('/api/alerts', alertsRoutes);
app.use('/api/export', exportRoutes);

// Global error handler
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, _next) => {
  const status = err.status || 502;
  const message = err.message || 'Upstream service error';
  console.error(`[ERR ${req.id}]`, message, err.stack || '');
  res.status(status).json({ error: message, requestId: req.id });
});

const port = process.env.PORT || 4000;
app.listen(port, () => {
  console.log(`TeacherConsole API running on http://localhost:${port}`);
});

// Process-level error logging to avoid silent crashes
process.on('unhandledRejection', (reason) => {
  console.error('[unhandledRejection]', reason);
});
process.on('uncaughtException', (err) => {
  console.error('[uncaughtException]', err);
});
