import { config } from '../config.js';

export function apiKeyGuard(req, res, next) {
  const headerKey = req.header('X-API-Key') || req.header('x-api-key');
  if (!config.apiKey) {
    return res.status(500).json({ error: 'API key not configured' });
  }
  if (!headerKey || headerKey !== config.apiKey) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
}
