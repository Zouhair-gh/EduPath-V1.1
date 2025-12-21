import { getPool } from '../db/pool.js';
import { MoodleClient } from '../connectors/moodle.js';
import { publishEvent, isPublisherReady, makeEvent } from '../publisher/index.js';
import { logger } from '../common/logger.js';

async function upsertCourse(pool, course) {
  const { id, shortname, fullname, categoryid, visible } = course;
  await pool.query(
    `INSERT INTO courses(external_id, shortname, fullname, category_id, visible)
     VALUES($1,$2,$3,$4,$5)
     ON CONFLICT (external_id) DO UPDATE SET shortname=EXCLUDED.shortname, fullname=EXCLUDED.fullname, category_id=EXCLUDED.category_id, visible=EXCLUDED.visible`,
    [String(id), shortname || null, fullname || null, String(categoryid || ''), !!visible]
  );
}

async function upsertStudent(pool, user) {
  const { id, email, firstname, lastname, username } = user;
  await pool.query(
    `INSERT INTO students(external_id, email, firstname, lastname, username, updated_at)
     VALUES($1,$2,$3,$4,$5,NOW())
     ON CONFLICT (external_id) DO UPDATE SET email=EXCLUDED.email, firstname=EXCLUDED.firstname, lastname=EXCLUDED.lastname, username=EXCLUDED.username, updated_at=EXCLUDED.updated_at`,
    [String(id), email || null, user.firstname || null, user.lastname || null, username || null]
  );
}

async function linkEnrollment(pool, userExternalId, courseExternalId, enrolledAt) {
  const { rows: srows } = await pool.query('SELECT id FROM students WHERE external_id=$1', [userExternalId]);
  const { rows: crows } = await pool.query('SELECT id FROM courses WHERE external_id=$1', [courseExternalId]);
  if (!srows.length || !crows.length) return;
  await pool.query(
    `INSERT INTO enrollments(student_id, course_id, enrolled_at)
     VALUES($1,$2,$3)`,
    [srows[0].id, crows[0].id, enrolledAt ? new Date(enrolledAt * 1000) : null]
  );
}

async function insertGrade(pool, userExternalId, courseExternalId, itemName, grade, gradeMax, ts) {
  const { rows: srows } = await pool.query('SELECT id FROM students WHERE external_id=$1', [userExternalId]);
  const { rows: crows } = await pool.query('SELECT id FROM courses WHERE external_id=$1', [courseExternalId]);
  if (!srows.length || !crows.length) return;
  await pool.query(
    `INSERT INTO grades(student_id, course_id, grade_item, grade_value, grade_max, timestamp)
     VALUES($1,$2,$3,$4,$5,$6)`,
    [srows[0].id, crows[0].id, itemName, grade, gradeMax, ts ? new Date(ts * 1000) : new Date()]
  );
}

async function insertActivity(pool, userExternalId, courseExternalId, type, resourceId, durationSec, ts, metadata) {
  const { rows: srows } = await pool.query('SELECT id FROM students WHERE external_id=$1', [userExternalId]);
  const { rows: crows } = await pool.query('SELECT id FROM courses WHERE external_id=$1', [courseExternalId]);
  if (!srows.length || !crows.length) return;
  await pool.query(
    `INSERT INTO activity_logs(student_id, course_id, activity_type, resource_id, duration_seconds, timestamp, metadata)
     VALUES($1,$2,$3,$4,$5,$6,$7)`,
    [srows[0].id, crows[0].id, type, resourceId || null, durationSec || null, ts ? new Date(ts * 1000) : new Date(), metadata || {}]
  );
}

export async function syncMoodleSource(source) {
  const pool = getPool();
  const client = new MoodleClient({ baseUrl: source.base_url, token: source.token });
  const { rows: jobRows } = await pool.query(
    `INSERT INTO sync_logs(lms_type, sync_type, status, started_at) VALUES('moodle','incremental','running', NOW()) RETURNING id`
  );
  const jobId = jobRows[0].id;
  let processed = 0;
  const stats = { courses: 0, users: 0, grades: 0, completions: 0, accesses: 0 };
  try {
    await client.getSiteInfo(); // validate token
    const courses = await client.getCourses();
    if (!Array.isArray(courses)) {
      logger.warn({ type: typeof courses }, 'Courses result not iterable');
    }
    for (const course of (Array.isArray(courses) ? courses : [])) {
      await upsertCourse(pool, course);
      stats.courses++;
      if (isPublisherReady()) {
        const evt = makeEvent({ actorId: String(source.id), verb: 'upsert', objectId: String(course.id), objectType: 'course', context: { title: course.fullname }, sourceId: source.id });
        publishEvent('course.upsert', evt);
      }
      const users = await client.getEnrolledUsers(course.id);
      for (const user of (Array.isArray(users) ? users : [])) {
        await upsertStudent(pool, user);
        await linkEnrollment(pool, String(user.id), String(course.id), user.firstaccess || user.timecreated);
        stats.users++;
        if (isPublisherReady()) {
          const evt = makeEvent({ actorId: String(user.id), verb: 'enrolled', objectId: String(course.id), objectType: 'course', sourceId: source.id });
          publishEvent('enrollment.link', evt);
        }
        // Grades
        try {
          const gradeItems = await client.getUserGradeItems(course.id, user.id);
          if (gradeItems && gradeItems.usergrades && gradeItems.usergrades.length) {
            for (const ug of gradeItems.usergrades) {
              for (const item of (ug.gradeitems || [])) {
                const gv = item.graderaw !== undefined ? Number(item.graderaw) : null;
                const gm = item.grademax !== undefined ? Number(item.grademax) : null;
                await insertGrade(pool, String(user.id), String(course.id), item.itemname || item.itemtype, gv, gm, item.grademodified || ug.graderawmodified);
                if (isPublisherReady()) {
                  const evt = makeEvent({ actorId: String(user.id), verb: 'graded', objectId: String(course.id), objectType: 'course', context: { item: item.itemname || item.itemtype, value: gv, max: gm }, sourceId: source.id });
                  publishEvent('grade.insert', evt);
                }
                processed++;
                stats.grades++;
              }
            }
          }
        } catch (e) {
          logger.warn({ err: e, courseId: course.id, userId: user.id }, 'Grade fetch failed');
        }
        // Completion status -> activity logs
        try {
          const comp = await client.getActivitiesCompletionStatus(course.id, user.id);
          if (comp && comp.statuses) {
            for (const s of comp.statuses) {
              await insertActivity(pool, String(user.id), String(course.id), 'completion', String(s.cmid), null, s.timemodified || comp.timestamp, { state: s.state });
              if (isPublisherReady()) {
                const evt = makeEvent({ actorId: String(user.id), verb: 'completed', objectId: String(s.cmid), objectType: 'module', context: { state: s.state, courseId: String(course.id) }, sourceId: source.id });
                publishEvent('activity.completion', evt);
              }
              processed++;
              stats.completions++;
            }
          }
        } catch (e) {}
        // Last access
        if (user.lastaccess) {
          await insertActivity(pool, String(user.id), String(course.id), 'last_access', null, null, user.lastaccess, { from: 'user.lastaccess' });
          if (isPublisherReady()) {
            const evt = makeEvent({ actorId: String(user.id), verb: 'accessed', objectId: String(course.id), objectType: 'course', context: { source: 'lastaccess' }, sourceId: source.id });
            publishEvent('activity.access', evt);
          }
          processed++;
          stats.accesses++;
        }
      }
    }
    await pool.query('UPDATE sync_logs SET status=$1, records_processed=$2, completed_at=NOW(), stats_json=$4 WHERE id=$3', ['completed', processed, jobId, JSON.stringify(stats)]);
    return { jobId, status: 'completed', recordsProcessed: processed };
  } catch (err) {
    await pool.query('UPDATE sync_logs SET status=$1, error_message=$2, completed_at=NOW() WHERE id=$3', ['failed', err.message || String(err), jobId]);
    throw err;
  }
}
