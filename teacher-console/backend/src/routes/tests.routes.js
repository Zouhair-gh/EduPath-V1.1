import express from 'express';
import auth from '../middleware/auth.middleware.js';
import { listRecentTests } from '../services/aggregator.service.js';

const router = express.Router();

router.get('/recent', auth, async (req, res, next) => {
  try {
    const limit = Number(req.query.limit || 10);
    const tests = await listRecentTests(limit);
    res.json(tests);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to fetch recent tests';
    next(e);
  }
});

export default router;
