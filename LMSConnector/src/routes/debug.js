import express from 'express';
import { apiKeyGuard } from '../security/auth.js';
import { getPool } from '../db/pool.js';
import { MoodleClient } from '../connectors/moodle.js';

const router = express.Router();
router.use(apiKeyGuard);

router.get('/debug/moodle/:sourceId', async (req, res) => {
  const pool = getPool();
  const { sourceId } = req.params;
  const { rows } = await pool.query('SELECT * FROM lms_sources WHERE id=$1 AND active=TRUE', [sourceId]);
  if (!rows.length) return res.status(404).json({ error: 'Source not found or inactive' });
  const src = rows[0];
  const client = new MoodleClient({ baseUrl: src.base_url, token: src.token });
  try {
    const site = await client.getSiteInfo();
    const courses = await client.getCourses();
    const firstCourse = Array.isArray(courses) && courses.length ? courses[0] : null;
    let users = [];
    if (firstCourse) {
      users = await client.getEnrolledUsers(firstCourse.id);
    }
    res.json({
      siteInfo: { sitename: site?.sitename, userid: site?.userid, release: site?.release },
      coursesShape: Array.isArray(courses) ? 'array' : typeof courses,
      coursesCount: Array.isArray(courses) ? courses.length : 0,
      sampleCourse: firstCourse ? { id: firstCourse.id, fullname: firstCourse.fullname, shortname: firstCourse.shortname } : null,
      enrolledUsersCount: Array.isArray(users) ? users.length : 0,
      sampleUser: Array.isArray(users) && users.length ? { id: users[0].id, email: users[0].email, username: users[0].username } : null,
    });
  } catch (e) {
    res.status(500).json({ error: e.message || String(e) });
  }
});

export default router;
