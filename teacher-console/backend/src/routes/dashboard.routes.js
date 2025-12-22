import express from 'express';
import auth from '../middleware/auth.middleware.js';
import { getClassOverview, getClassDetails, getAllClassesOverview, getClassSettings, updateClassSettings } from '../services/aggregator.service.js';

const router = express.Router();

router.get('/class/:courseId', auth, async (req, res, next) => {
  try {
    const courseId = req.params.courseId;
    const data = await getClassOverview(courseId);
    res.json(data);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to fetch class overview';
    next(e);
  }
});

export default router;

router.get('/class/:courseId/details', auth, async (req, res, next) => {
  try {
    const courseId = req.params.courseId;
    const data = await getClassDetails(courseId);
    res.json(data);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to fetch class details';
    next(e);
  }
});

router.get('/classes', auth, async (_req, res, next) => {
  try {
    const data = await getAllClassesOverview();
    res.json(data);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to fetch classes overview';
    next(e);
  }
});

router.get('/class/:courseId/settings', auth, async (req, res, next) => {
  try {
    const courseId = Number(req.params.courseId);
    const settings = await getClassSettings(courseId);
    res.json(settings);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to fetch class settings';
    next(e);
  }
});

router.put('/class/:courseId/settings', auth, async (req, res, next) => {
  try {
    const courseId = Number(req.params.courseId);
    const patch = req.body || {};
    const settings = await updateClassSettings(courseId, patch);
    res.json(settings);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to update class settings';
    next(e);
  }
});
