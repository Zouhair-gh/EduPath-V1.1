import express from 'express';
import crypto from 'crypto';
import { apiKeyGuard } from '../security/auth.js';
import { getPool } from '../db/pool.js';
import { MoodleClient } from '../connectors/moodle.js';

const router = express.Router();
router.use(apiKeyGuard);

// POST /admin/moodle/bootstrap
// Body: { sourceId?, courseFullname, courseShortname, userEmail, userUsername, userFirstname, userLastname }
router.post('/admin/moodle/bootstrap', async (req, res) => {
  const pool = getPool();
  const { sourceId, courseFullname = 'Demo Course', courseShortname = 'DEMO101', userEmail = 'student@example.com', userUsername = 'student1', userFirstname = 'Student', userLastname = 'One' } = req.body || {};
  try {
    const { rows: sources } = await pool.query(
      sourceId ? 'SELECT * FROM lms_sources WHERE id=$1 AND active=TRUE' : "SELECT * FROM lms_sources WHERE active=TRUE AND type='moodle' LIMIT 1",
      sourceId ? [sourceId] : []
    );
    if (!sources.length) return res.status(404).json({ error: 'No active Moodle source found' });
    const src = sources[0];
    const client = new MoodleClient({ baseUrl: src.base_url, token: src.token });

    // Validate token
    const site = await client.getSiteInfo();

    // Create course
    const courseReq = [{ fullname: courseFullname, shortname: courseShortname, categoryid: 1, visible: 1 }];
    let courseResp;
    try {
      courseResp = await client.createCourses(courseReq);
    } catch (e) {
      return res.status(400).json({ error: 'Course creation failed', detail: e.message, hint: 'Enable core_course_create_courses in Moodle external service for this token' });
    }
    let createdCourse = Array.isArray(courseResp) && courseResp[0] ? courseResp[0] : courseResp;
    // Some Moodle setups return warnings or omit id; fetch by shortname if missing
    let courseId = createdCourse?.id || createdCourse?.courseid || null;
    if (!courseId) {
      const found = await client.getCourseByField('shortname', courseShortname);
      const match = Array.isArray(found) ? found[0] : null;
      courseId = match?.id || null;
      if (match) createdCourse = match;
    }

    // Create user
    const password = crypto.randomBytes(10).toString('hex') + 'A!1';
    const userReq = [{ username: userUsername, password, email: userEmail, firstname: userFirstname, lastname: userLastname }];
    let userResp;
    try {
      userResp = await client.createUsers(userReq);
    } catch (e) {
      return res.status(400).json({ error: 'User creation failed', detail: e.message, hint: 'Enable core_user_create_users in Moodle external service for this token' });
    }
    const createdUser = Array.isArray(userResp) && userResp[0] ? userResp[0] : userResp;

    // Enrol user
    try {
      await client.enrolUserManual(courseId, createdUser.id || createdUser.userid || createdUser, 5);
    } catch (e) {
      return res.status(400).json({ error: 'Enrollment failed', detail: e.message, hint: 'Enable enrol_manual_enrol_users and ensure Manual enrolment plugin is enabled for the course' });
    }

    return res.status(201).json({
      sourceId: src.id,
      site: { sitename: site?.sitename, userid: site?.userid },
      course: { id: courseId, fullname: courseFullname, shortname: courseShortname },
      user: { id: createdUser.id || createdUser.userid || createdUser, username: userUsername, email: userEmail },
      password,
      enrollment: { role: 'student' }
    });
  } catch (err) {
    return res.status(500).json({ error: err.message || String(err) });
  }
});

export default router;
