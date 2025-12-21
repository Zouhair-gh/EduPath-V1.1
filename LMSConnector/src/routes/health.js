import express from 'express';
import { checkDbConnection } from '../db/pool.js';

const router = express.Router();

router.get('/health', async (req, res) => {
  const dbConnected = await checkDbConnection();
  res.json({ status: 'ok', dbConnected });
});

export default router;
