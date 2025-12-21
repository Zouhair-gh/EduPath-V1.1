import express from 'express';
import { apiKeyGuard } from '../security/auth.js';
import { getPool } from '../db/pool.js';
import { body } from 'express-validator';
import { validationResult } from 'express-validator';

const router = express.Router();
router.use(apiKeyGuard);

router.get('/sources', async (req, res) => {
  const pool = getPool();
  const { rows } = await pool.query('SELECT id, type, base_url, active, created_at FROM lms_sources ORDER BY created_at DESC');
  res.json(rows);
});

router.post('/sources',
  body('type').isString().isIn(['moodle']),
  body('base_url').isString().isURL(),
  body('token').optional().isString(),
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });
    const { type, base_url, token, oauth_client_id, oauth_client_secret, active = true } = req.body || {};
    const pool = getPool();
    const { rows } = await pool.query(
      'INSERT INTO lms_sources(type, base_url, token, oauth_client_id, oauth_client_secret, active) VALUES($1,$2,$3,$4,$5,$6) RETURNING id, type, base_url, active, created_at',
      [type, base_url, token || null, oauth_client_id || null, oauth_client_secret || null, active]
    );
    res.status(201).json(rows[0]);
  }
);

export default router;
