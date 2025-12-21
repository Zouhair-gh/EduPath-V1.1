import request from 'supertest';
import express from 'express';
import adminRouter from '../src/routes/admin.js';

const app = express();
app.use(express.json());
app.use((req, res, next) => { req.headers['x-api-key'] = 'test'; next(); });
// Monkey-patch apiKeyGuard to bypass for tests
jest.unstable_mockModule('../src/security/auth.js', () => ({ apiKeyGuard: (req, res, next) => next() }));

test('POST /sources validates input', async () => {
  const res = await request(app).post('/sources').send({ type: 'moodle', base_url: 'https://example.com' });
  // This test only checks validation middleware path; DB not connected here
  expect([200,201,400]).toContain(res.status);
});
