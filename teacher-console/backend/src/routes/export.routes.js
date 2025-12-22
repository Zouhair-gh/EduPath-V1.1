import express from 'express';
import auth from '../middleware/auth.middleware.js';
import { exportStudents, exportAlerts } from '../services/aggregator.service.js';

const router = express.Router();

function toCsv(rows, headers) {
  if (!Array.isArray(rows)) return '';
  const escape = (v) => {
    if (v == null) return '';
    const s = String(v);
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
      return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  };
  const head = headers.join(',');
  const body = rows.map((r) => headers.map((h) => escape(r[h])).join(',')).join('\n');
  return head + '\n' + body + '\n';
}

router.get('/students', auth, async (req, res, next) => {
  try {
    const courseId = req.query.courseId ? Number(req.query.courseId) : undefined;
    const rows = await exportStudents(courseId);
    const headers = ['id', 'name', 'email', 'courseId', 'engagement', 'successRate'];
    const csv = toCsv(rows, headers);
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="students.csv"');
    res.send(csv);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to export students';
    next(e);
  }
});

router.get('/alerts', auth, async (req, res, next) => {
  try {
    const courseId = req.query.courseId ? Number(req.query.courseId) : undefined;
    const rows = await exportAlerts(courseId);
    const headers = ['id', 'studentId', 'studentName', 'courseId', 'severity', 'status', 'createdAt'];
    const csvRows = rows.map((r) => ({
      id: r.id,
      studentId: r.studentId,
      studentName: r.studentName,
      courseId: r.courseId,
      severity: r.severity,
      status: r.status,
      createdAt: r.createdAt,
    }));
    const csv = toCsv(csvRows, headers);
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="alerts.csv"');
    res.send(csv);
  } catch (e) {
    e.status = 502;
    e.message = e.message || 'Failed to export alerts';
    next(e);
  }
});

export default router;
