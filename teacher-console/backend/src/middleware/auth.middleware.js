import jwt from 'jsonwebtoken';

export default function authMiddleware(req, res, next) {
  // Dev bypass: allow requests without a token when explicitly enabled
  if (process.env.DEV_BYPASS_AUTH === 'true') {
    req.user = req.user || { id: 1, role: 'teacher', courses: [1] };
    if (!req.headers.authorization) {
      console.log(`[AUTH BYPASS] ${req.method} ${req.originalUrl}`);
    }
    return next();
  }
  const header = req.headers.authorization || '';
  const token = header.startsWith('Bearer ') ? header.substring(7) : null;
  if (!token) return res.status(401).json({ error: 'Token manquant' });
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded; // { id, role: 'teacher', courses: [...] }
    next();
  } catch (e) {
    console.warn('[AUTH ERROR] Invalid token:', e?.message || e);
    return res.status(403).json({ error: 'Token invalide' });
  }
}
