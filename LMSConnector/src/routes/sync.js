import express from 'express';
import { apiKeyGuard } from '../security/auth.js';
import { getPool } from '../db/pool.js';
import { syncMoodleSource } from '../services/sync.service.js';

const router = express.Router();
router.use(apiKeyGuard);

router.post('/sync/moodle', async (req, res) => {
  const pool = getPool();
  if (!pool) return res.status(409).json({ error: 'DB disabled; cannot sync' });
  const { rows: sources } = await pool.query("SELECT * FROM lms_sources WHERE active=TRUE AND type='moodle'");
  if (!sources.length) return res.status(404).json({ error: 'No active Moodle sources' });
  const results = [];
  for (const src of sources) {
    try {
      const r = await syncMoodleSource(src);
      results.push({ sourceId: src.id, ...r });
    } catch (e) {
      results.push({ sourceId: src.id, error: e.message || String(e) });
    }
  }
  res.json({ results });
});

router.post('/sync/moodle/:sourceId', async (req, res) => {
  const pool = getPool();
  if (!pool) return res.status(409).json({ error: 'DB disabled; cannot sync' });
  const { sourceId } = req.params;
  const { rows: sources } = await pool.query('SELECT * FROM lms_sources WHERE id=$1 AND active=TRUE', [sourceId]);
  if (!sources.length) return res.status(404).json({ error: 'Source not found or inactive' });
  try {
    const r = await syncMoodleSource(sources[0]);
    res.json(r);
  } catch (e) {
    res.status(500).json({ error: e.message || String(e) });
  }
});

router.get('/jobs/:jobId', async (req, res) => {
  const pool = getPool();
  const { jobId } = req.params;
  const { rows } = await pool.query('SELECT * FROM sync_logs WHERE id=$1', [jobId]);
  if (!rows.length) return res.status(404).json({ error: 'Job not found' });
  res.json(rows[0]);
});

export default router;
