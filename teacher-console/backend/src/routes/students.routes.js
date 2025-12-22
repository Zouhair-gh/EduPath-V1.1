import express from 'express';
import auth from '../middleware/auth.middleware.js';
import { listStudents, listAllStudents, getStudentProfile, sendMessage, addStudentNote, listStudentNotes, addStudentTag, removeStudentTag } from '../services/aggregator.service.js';

const router = express.Router();

router.get('/', auth, async (req, res, next) => {
  const { courseId, ...filters } = req.query;
  try {
    const students = await listStudents(courseId, filters);
    res.json(students);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to list students';
    next(e);
  }
});

router.get('/all', auth, async (req, res, next) => {
  try {
    const limit = Number(req.query.limit || 5000);
    const students = await listAllStudents(limit);
    res.json(students);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to list all students';
    next(e);
  }
});

router.get('/:id/profile', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const data = await getStudentProfile(id);
    res.json(data);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to fetch student profile';
    next(e);
  }
});

router.post('/:id/message', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const result = await sendMessage(id, req.body);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to send message';
    next(e);
  }
});

router.get('/:id/notes', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const courseId = req.query.courseId ? Number(req.query.courseId) : undefined;
    const notes = await listStudentNotes(id, courseId);
    res.json(notes);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to list notes';
    next(e);
  }
});

router.post('/:id/notes', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const author = req.user?.email || req.user?.id || 'teacher';
    const { content, courseId } = req.body || {};
    const result = await addStudentNote(id, courseId, author, content);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to add note';
    next(e);
  }
});

router.post('/:id/tags', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const { tag, courseId } = req.body || {};
    const result = await addStudentTag(id, tag, courseId);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to add tag';
    next(e);
  }
});

router.delete('/:id/tags/:tag', auth, async (req, res, next) => {
  try {
    const id = req.params.id;
    const tag = req.params.tag;
    const courseId = req.query.courseId ? Number(req.query.courseId) : undefined;
    const result = await removeStudentTag(id, tag, courseId);
    res.json(result);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to remove tag';
    next(e);
  }
});

export default router;
