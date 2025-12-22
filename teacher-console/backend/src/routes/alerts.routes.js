import express from 'express';
import auth from '../middleware/auth.middleware.js';
import { listAlerts, resolveAlert, unresolveAlert, updateAlertSeverity, addAlertComment, bulkResolveAlerts, assignAlert } from '../services/aggregator.service.js';

const router = express.Router();

router.get('/', auth, async (req, res, next) => {
  try {
    const { courseId, severity } = req.query;
    const alerts = await listAlerts(courseId, severity);
    res.json(alerts);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to list alerts';
    next(e);
  }
});

router.patch('/:id/resolve', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const note = req.body?.note;
    const actor = req.user?.email || req.user?.id || 'teacher';
    const result = await resolveAlert(id, actor, note);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to resolve alert';
    next(e);
  }
});

router.patch('/:id/unresolve', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const actor = req.user?.email || req.user?.id || 'teacher';
    const result = await unresolveAlert(id, actor);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to unresolve alert';
    next(e);
  }
});

router.patch('/:id/severity', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const { severity } = req.body || {};
    const actor = req.user?.email || req.user?.id || 'teacher';
    const result = await updateAlertSeverity(id, severity, actor);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to update alert severity';
    next(e);
  }
});

router.post('/:id/comment', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const author = req.user?.email || req.user?.id || 'teacher';
    const { content } = req.body || {};
    const result = await addAlertComment(id, author, content);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to add alert comment';
    next(e);
  }
});

router.post('/bulk/resolve', auth, async (req, res, next) => {
  try {
    const ids = req.body?.ids || [];
    const actor = req.user?.email || req.user?.id || 'teacher';
    const result = await bulkResolveAlerts(ids, actor);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to bulk resolve alerts';
    next(e);
  }
});

router.patch('/:id/assign', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const { assignee } = req.body || {};
    const actor = req.user?.email || req.user?.id || 'teacher';
    const result = await assignAlert(id, assignee, actor);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to assign alert';
    next(e);
  }
});

export default router;
