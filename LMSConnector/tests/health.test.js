import request from 'supertest';
import express from 'express';
import healthRouter from '../src/routes/health.js';

const app = express();
app.use(healthRouter);

test('GET /health returns ok shape', async () => {
  const res = await request(app).get('/health');
  expect(res.status).toBe(200);
  expect(res.body).toHaveProperty('status');
});
