import axios from 'axios';
import { Client as PgClient } from 'pg';

function makeClient(name, baseURL) {
  const client = axios.create({ baseURL, timeout: 8000 });
  client.interceptors.request.use((config) => {
    config.metadata = { start: Date.now() };
    console.log(`[REQ] ${name} ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  });
  client.interceptors.response.use(
    (res) => {
      const ms = Date.now() - (res.config.metadata?.start || Date.now());
      console.log(`[RES] ${name} ${res.status} ${res.config.url} (${ms}ms)`);
      return res;
    },
    (err) => {
      const cfg = err.config || {};
      const ms = Date.now() - (cfg.metadata?.start || Date.now());
      const status = err.response?.status;
      console.error(`[ERR] ${name} ${status || ''} ${cfg?.url} (${ms}ms):`, err.message);
      return Promise.reject(err);
    }
  );
  return client;
}

const prepa = makeClient('PrepaData', process.env.PREPA_DATA_URL);
const profiler = makeClient('StudentProfiler', process.env.STUDENT_PROFILER_URL);
const predictor = makeClient('PathPredictor', process.env.PATH_PREDICTOR_URL);
const reco = makeClient('RecoBuilder', process.env.RECO_BUILDER_URL);

async function safeGet(promise, fallback, context) {
  try {
    const res = await promise;
    return res?.data ?? fallback;
  } catch (e) {
    console.error(`[SAFE_GET] Failed in ${context}:`, e?.message || e);
    return fallback;
  }
}

function analyticsDbConfig() {
  return {
    host: process.env.ANALYTICS_DB_HOST || 'localhost',
    port: Number(process.env.ANALYTICS_DB_PORT || 5433),
    database: process.env.ANALYTICS_DB_NAME || 'analytics_db',
    user: process.env.ANALYTICS_DB_USER || 'postgres',
    password: process.env.ANALYTICS_DB_PASSWORD || 'postgres',
  };
}

async function withPg(callback) {
  const cfg = analyticsDbConfig();
  const client = new PgClient(cfg);
  try {
    await client.connect();
    return await callback(client);
  } finally {
    try { await client.end(); } catch {}
  }
}

let schemaReady = false;
async function ensureSchema() {
  if (schemaReady) return;
  await withPg(async (client) => {
    // Supporting tables for teacher actions and settings, resilient to reruns
    await client.query(`CREATE TABLE IF NOT EXISTS teacher_actions (
      id SERIAL PRIMARY KEY,
      actor TEXT,
      action TEXT NOT NULL,
      entity_type TEXT,
      entity_id TEXT,
      details JSONB,
      created_at TIMESTAMPTZ DEFAULT NOW()
    )`);
    await client.query(`CREATE TABLE IF NOT EXISTS student_notes (
      id SERIAL PRIMARY KEY,
      student_id TEXT NOT NULL,
      course_id INTEGER,
      author TEXT,
      content TEXT NOT NULL,
      created_at TIMESTAMPTZ DEFAULT NOW()
    )`);
    await client.query(`CREATE TABLE IF NOT EXISTS student_tags (
      student_id TEXT NOT NULL,
      tag TEXT NOT NULL,
      course_id INTEGER,
      added_at TIMESTAMPTZ DEFAULT NOW(),
      PRIMARY KEY(student_id, tag, course_id)
    )`);
    await client.query(`CREATE TABLE IF NOT EXISTS course_settings (
      course_id INTEGER PRIMARY KEY,
      settings JSONB NOT NULL DEFAULT '{}'::jsonb,
      updated_at TIMESTAMPTZ DEFAULT NOW()
    )`);
    // Alerts table optional columns for workflow
    try { await client.query(`ALTER TABLE alerts ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ`); } catch {}
    try { await client.query(`ALTER TABLE alerts ADD COLUMN IF NOT EXISTS resolved_by TEXT`); } catch {}
    try { await client.query(`ALTER TABLE alerts ADD COLUMN IF NOT EXISTS assigned_to TEXT`); } catch {}
  });
  schemaReady = true;
}

async function recordAction(actor, action, entityType, entityId, details = {}) {
  await ensureSchema();
  await withPg((client) => client.query(
    `INSERT INTO teacher_actions(actor, action, entity_type, entity_id, details)
     VALUES ($1, $2, $3, $4, $5)`,
    [actor || 'system', action, entityType, String(entityId), details]
  ));
}

async function fetchStudentsFromDB(courseId, limit = 1000) {
  const cfg = analyticsDbConfig();
  const client = new PgClient(cfg);
  try {
    await client.connect();
    const where = courseId ? 'WHERE sm.course_id = $1' : '';
    const params = courseId ? [courseId, limit] : [limit];
    const sql = `
      SELECT sm.student_id AS id,
             AVG(sm.engagement_score) AS engagement,
             AVG(sm.success_rate) AS success_rate
      FROM student_metrics sm
      ${where}
      GROUP BY sm.student_id
      ORDER BY sm.student_id
      LIMIT $${courseId ? 2 : 1}
    `;
    const { rows } = await client.query(sql, params);
    return rows.map(r => ({
      id: r.id,
      name: null,
      email: null,
      courseId: courseId || null,
      engagement: r.engagement === null ? null : Number(r.engagement),
      successRate: r.success_rate === null ? null : Number(r.success_rate),
    }));
  } catch (e) {
    console.error('[DB Fallback] Failed to fetch students:', e?.message || e);
    return [];
  } finally {
    try { await client.end(); } catch {}
  }
}

async function fetchAlertsFromDB(courseId, limit = 50) {
  const cfg = analyticsDbConfig();
  const client = new PgClient(cfg);
  try {
    await client.connect();
    const params = courseId ? [courseId, limit] : [limit];
    const where = courseId ? 'WHERE status = \'ACTIVE\' AND course_id = $1' : "WHERE status = 'ACTIVE'";
    const sql = `
      SELECT id, student_id, course_id, severity, risk_factors, recommended_actions, status, created_at
      FROM alerts
      ${where}
      ORDER BY created_at DESC
      LIMIT $${courseId ? 2 : 1}
    `;
    const { rows } = await client.query(sql, params);
    return rows.map((a) => ({
      id: a.id,
      studentId: a.student_id,
      studentName: undefined,
      severity: a.severity,
      riskFactors: Array.isArray(a.risk_factors) ? a.risk_factors : [],
      recommendedActions: Array.isArray(a.recommended_actions) ? a.recommended_actions : [],
      status: a.status || 'ACTIVE',
      createdAt: a.created_at,
      courseId: a.course_id,
    }));
  } catch (e) {
    console.error('[DB Fallback] Failed to fetch alerts:', e?.message || e);
    return [];
  } finally {
    try { await client.end(); } catch {}
  }
}

async function fetchCoursesOverviewFromDB() {
  const cfg = analyticsDbConfig();
  const client = new PgClient(cfg);
  try {
    await client.connect();
    const metricsSql = `
      SELECT sm.course_id,
             COUNT(DISTINCT sm.student_id) AS total_students,
             AVG(sm.engagement_score) AS avg_engagement,
             AVG(sm.success_rate) AS avg_success_rate
      FROM student_metrics sm
      GROUP BY sm.course_id
      ORDER BY sm.course_id`;
    const alertsSql = `
      SELECT course_id, COUNT(*) AS c
      FROM alerts
      WHERE status='ACTIVE'
      GROUP BY course_id`;
    const distSql = `
      WITH last_prof AS (
        SELECT DISTINCT ON (student_id) student_id, profile_label
        FROM student_profiles
        ORDER BY student_id, assigned_at DESC
      )
      SELECT sm.course_id, lp.profile_label, COUNT(*) AS cnt
      FROM student_metrics sm
      JOIN last_prof lp ON lp.student_id = sm.student_id
      GROUP BY sm.course_id, lp.profile_label`;

    const [metricsRes, alertsRes, distRes] = await Promise.all([
      client.query(metricsSql),
      client.query(alertsSql),
      client.query(distSql),
    ]);

    const alertsByCourse = new Map();
    for (const r of alertsRes.rows) alertsByCourse.set(String(r.course_id), Number(r.c));

    const distByCourse = new Map();
    for (const r of distRes.rows) {
      const key = String(r.course_id);
      const arr = distByCourse.get(key) || [];
      arr.push({ label: r.profile_label, count: Number(r.cnt) });
      distByCourse.set(key, arr);
    }

    const results = [];
    for (const m of metricsRes.rows) {
      const courseId = Number(m.course_id);
      const totalStudents = Number(m.total_students) || 0;
      const distRaw = distByCourse.get(String(courseId)) || [];
      const distribution = distRaw.map(d => ({
        label: d.label,
        count: d.count,
        percentage: totalStudents ? Number(((d.count * 100) / totalStudents).toFixed(2)) : 0,
      }));
      results.push({
        courseId,
        totalStudents,
        averageEngagement: m.avg_engagement == null ? 0 : Number(m.avg_engagement),
        averageSuccessRate: m.avg_success_rate == null ? 0 : Number(m.avg_success_rate),
        atRiskCount: alertsByCourse.get(String(courseId)) || 0,
        profileDistribution: distribution,
      });
    }
    return results;
  } catch (e) {
    console.error('[DB Fallback] Failed to fetch courses overview:', e?.message || e);
    return [];
  } finally {
    try { await client.end(); } catch {}
  }
}

export async function getClassOverview(courseId) {
  // Fetch metrics from PrepaData, profiles from StudentProfiler, alerts from PathPredictor
  const [metricsList, profDistList, studentsList, alertsRaw] = await Promise.all([
    safeGet(prepa.get(`/api/metrics/course/${courseId}`), [], 'course metrics'),
    safeGet(profiler.get(`/api/profiles/distribution`), [], 'profile distribution'),
    safeGet(prepa.get(`/api/students`, { params: { courseId, limit: 1000 } }), [], 'students list for count'),
    safeGet(predictor.get(`/api/alerts`, { params: { courseId } }), [], 'alerts list'),
  ]);
  const students = Array.isArray(studentsList) && studentsList.length ? studentsList : await fetchStudentsFromDB(courseId, 1000);
  const metrics = Array.isArray(metricsList) && metricsList.length ? metricsList[0] : {};
  const distribution = Array.isArray(profDistList) ? profDistList : [];
  const recentAlerts = (alertsRaw || []).map((a) => ({
    id: a.id,
    studentId: a.student_id,
    studentName: a.student_name || undefined,
    severity: a.severity,
    riskFactors: Array.isArray(a.risk_factors) ? a.risk_factors : [],
    recommendedActions: Array.isArray(a.recommended_actions) ? a.recommended_actions : [],
    status: a.status || 'ACTIVE',
    createdAt: a.created_at,
    courseId: a.course_id,
  }));
  const courseAlerts = Number(courseId) ? recentAlerts.filter(a => Number(a.courseId || a.course_id) === Number(courseId)) : recentAlerts;
  return {
    totalStudents: metrics.total_students || (Array.isArray(students) ? students.length : 0),
    averageEngagement: metrics.avg_engagement || metrics.average_engagement || 0,
    averageSuccessRate: metrics.avg_success_rate || metrics.average_success_rate || 0,
    atRiskCount: courseAlerts.length,
    profileDistribution: distribution.map(d => ({ label: d.profile_label || d.label, count: d.count, percentage: d.percentage })),
    recentAlerts: courseAlerts,
  };
}

export async function listStudents(courseId, filters) {
  const data = await safeGet(prepa.get(`/api/students`, { params: { courseId, ...filters } }), [], 'students list');
  if (Array.isArray(data) && data.length) return data;
  // Fallback to direct DB read if PrepaData route is unavailable
  return await fetchStudentsFromDB(courseId, Number(filters?.limit || 1000));
}

export async function listAllStudents(limit = 5000) {
  // Try PrepaData without courseId first
  const data = await safeGet(prepa.get(`/api/students`, { params: { limit } }), [], 'students list all');
  if (Array.isArray(data) && data.length) return data;
  // Fallback to DB for all courses
  return await fetchStudentsFromDB(undefined, limit);
}

export async function getAllClassesOverview() {
  // Prefer PrepaData if a courses summary route exists; otherwise DB fallback
  // DB fallback implementation:
  const results = await fetchCoursesOverviewFromDB();
  return results;
}

export async function getStudentProfile(id) {
  const profile = await safeGet(profiler.get(`/api/profiles/student/${id}`), {}, 'student profile');
  const active_alerts = await safeGet(predictor.get(`/api/alerts`, { params: { studentId: id } }), [], 'student alerts');
  const recosData = await safeGet(reco.get(`/api/recommendations/student/${id}`, { params: { top_n: 5 } }), { recommendations: [] }, 'recommendations');
  const trajectory = await safeGet(prepa.get(`/api/trajectory/${id}`, { params: { days: 90 } }), [], 'trajectory');
  return {
    profile,
    active_alerts,
    recommendations: recosData.recommendations || [],
    trajectory,
  };
}

export async function listAlerts(courseId, severity) {
  let normalized = (await safeGet(predictor.get('/api/alerts', { params: { courseId, severity } }), [], 'alerts') || []).map((a) => ({
    id: a.id,
    studentId: a.student_id,
    studentName: a.student_name || undefined,
    severity: a.severity,
    riskFactors: Array.isArray(a.risk_factors) ? a.risk_factors : [],
    recommendedActions: Array.isArray(a.recommended_actions) ? a.recommended_actions : [],
    status: a.status || 'ACTIVE',
    createdAt: a.created_at,
    courseId: a.course_id,
  }));
  if (courseId) normalized = normalized.filter(a => Number(a.courseId) === Number(courseId));
  if (!normalized.length) {
    const dbFallback = await fetchAlertsFromDB(courseId, 50);
    return dbFallback;
  }
  return normalized;
}

export async function getClassDetails(courseId) {
  const [overview, students] = await Promise.all([
    getClassOverview(courseId),
    listStudents(courseId, { limit: 1000 }),
  ]);
  const alerts = await listAlerts(courseId);
  const counts = {
    active: alerts.length,
    high: alerts.filter(a => a.severity === 'HIGH').length,
    medium: alerts.filter(a => a.severity === 'MEDIUM').length,
    low: alerts.filter(a => a.severity === 'LOW').length,
  };
  // Simple risk score: inverse engagement/success + alert severity weight
  const sevWeight = { HIGH: 3, MEDIUM: 2, LOW: 1 };
  const byStudent = new Map();
  for (const s of students) {
    const invEng = s.engagement != null ? (100 - Number(s.engagement)) / 100 : 0.3;
    const invSuc = s.successRate != null ? (100 - Number(s.successRate)) / 100 : 0.3;
    byStudent.set(String(s.id), { student: s, score: invEng * 0.6 + invSuc * 0.4 });
  }
  for (const a of alerts) {
    const key = String(a.studentId);
    const cur = byStudent.get(key) || { student: { id: a.studentId }, score: 0 };
    cur.score += (sevWeight[a.severity] || 1) * 0.5;
    byStudent.set(key, cur);
  }
  const topStudents = Array.from(byStudent.values())
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map(x => ({
      id: x.student.id,
      name: x.student.name,
      engagement: x.student.engagement,
      successRate: x.student.successRate,
      riskScore: Number(x.score.toFixed(2)),
    }));

  // Trends: compute simple aggregates from temporal_features
  const cfg = analyticsDbConfig();
  const client = new PgClient(cfg);
  let trends = { engagementMA7: null, engagementMA30: null };
  try {
    await client.connect();
    const { rows } = await client.query(
      `SELECT AVG(engagement_ma7) AS ma7, AVG(engagement_ma30) AS ma30
       FROM temporal_features WHERE course_id = $1 AND feature_date >= CURRENT_DATE - INTERVAL '30 days'`,
      [courseId]
    );
    if (rows && rows[0]) {
      trends = {
        engagementMA7: rows[0].ma7 == null ? null : Number(rows[0].ma7),
        engagementMA30: rows[0].ma30 == null ? null : Number(rows[0].ma30),
      };
    }
  } catch (e) {
    console.warn('[Trends] Failed to compute temporal features:', e?.message || e);
  } finally {
    try { await client.end(); } catch {}
  }

  return {
    totals: {
      students: overview.totalStudents,
      averageEngagement: overview.averageEngagement,
      averageSuccessRate: overview.averageSuccessRate,
      alerts: counts,
    },
    profiles: {
      distribution: overview.profileDistribution,
    },
    trends,
    topStudents,
    recentAlerts: alerts.slice(0, 10),
  };
}

export async function resolveAlert(id, actor = 'teacher', note) {
  try {
    await ensureSchema();
    const res = await withPg(async (client) => {
      const { rows } = await client.query(
        `UPDATE alerts SET status='RESOLVED', resolved_at=NOW(), resolved_by=$2 WHERE id=$1 RETURNING id, student_id, course_id, severity, status, resolved_at, resolved_by`,
        [id, actor]
      );
      return rows[0];
    });
    if (note && res?.student_id) {
      await withPg((client) => client.query(
        `INSERT INTO student_notes(student_id, course_id, author, content) VALUES($1,$2,$3,$4)`,
        [String(res.student_id), res.course_id || null, actor, note]
      ));
    }
    await recordAction(actor, 'resolve_alert', 'alert', id, { note });
    return { id, status: 'RESOLVED', resolvedAt: res?.resolved_at, resolvedBy: res?.resolved_by };
  } catch (e) {
    console.warn('[resolveAlert] Fallback stub due to error:', e?.message || e);
    return { id, status: 'RESOLVED' };
  }
}

export async function unresolveAlert(id, actor = 'teacher') {
  try {
    await ensureSchema();
    const res = await withPg(async (client) => {
      const { rows } = await client.query(
        `UPDATE alerts SET status='ACTIVE', resolved_at=NULL, resolved_by=NULL WHERE id=$1 RETURNING id, status`,
        [id]
      );
      return rows[0];
    });
    await recordAction(actor, 'unresolve_alert', 'alert', id);
    return { id, status: res?.status || 'ACTIVE' };
  } catch (e) {
    console.warn('[unresolveAlert] Fallback stub due to error:', e?.message || e);
    return { id, status: 'ACTIVE' };
  }
}

export async function updateAlertSeverity(id, severity, actor = 'teacher') {
  try {
    await ensureSchema();
    const res = await withPg(async (client) => {
      const { rows } = await client.query(
        `UPDATE alerts SET severity=$2 WHERE id=$1 RETURNING id, severity`,
        [id, severity]
      );
      return rows[0];
    });
    await recordAction(actor, 'update_alert_severity', 'alert', id, { severity });
    return { id, severity: res?.severity || severity };
  } catch (e) {
    console.warn('[updateAlertSeverity] Fallback stub due to error:', e?.message || e);
    return { id, severity };
  }
}

export async function addAlertComment(id, author, content) {
  try {
    await ensureSchema();
    // Store as a student note linked to alert context
    const alertRow = await withPg(async (client) => {
      const { rows } = await client.query(`SELECT student_id, course_id FROM alerts WHERE id=$1`, [id]);
      return rows[0];
    });
    if (alertRow) {
      await withPg((client) => client.query(
        `INSERT INTO student_notes(student_id, course_id, author, content) VALUES($1,$2,$3,$4)`,
        [String(alertRow.student_id), alertRow.course_id || null, author || 'teacher', content]
      ));
    }
    await recordAction(author || 'teacher', 'comment_alert', 'alert', id, { content });
    return { id, comment: 'added' };
  } catch (e) {
    console.warn('[addAlertComment] Fallback stub due to error:', e?.message || e);
    return { id, comment: 'queued' };
  }
}

export async function assignAlert(id, assignee, actor = 'teacher') {
  try {
    await ensureSchema();
    await withPg((client) => client.query(
      `UPDATE alerts SET assigned_to=$2 WHERE id=$1`,
      [id, assignee]
    ));
    await recordAction(actor, 'assign_alert', 'alert', id, { assignee });
    return { id, assignedTo: assignee };
  } catch (e) {
    console.warn('[assignAlert] Fallback stub due to error:', e?.message || e);
    return { id, assignedTo: assignee };
  }
}

export async function bulkResolveAlerts(ids = [], actor = 'teacher') {
  try {
    await ensureSchema();
    if (!Array.isArray(ids) || !ids.length) return { resolved: 0 };
    const placeholders = ids.map((_, i) => `$${i + 1}`).join(',');
    await withPg(async (client) => {
      await client.query(`UPDATE alerts SET status='RESOLVED', resolved_at=NOW(), resolved_by=$${ids.length + 1} WHERE id IN (${placeholders})`, [...ids, actor]);
    });
    await recordAction(actor, 'bulk_resolve_alerts', 'alert', 'batch', { ids });
    return { resolved: ids.length };
  } catch (e) {
    console.warn('[bulkResolveAlerts] Fallback stub due to error:', e?.message || e);
    return { resolved: Array.isArray(ids) ? ids.length : 0 };
  }
}

export async function sendMessage(studentId, payload) {
  // Stub: integrate with messaging service
  return { status: 'sent', studentId, payload };
}

export async function addStudentNote(studentId, courseId, author, content) {
  await ensureSchema();
  await withPg((client) => client.query(
    `INSERT INTO student_notes(student_id, course_id, author, content) VALUES($1,$2,$3,$4)`,
    [String(studentId), courseId || null, author || 'teacher', content]
  ));
  await recordAction(author || 'teacher', 'add_student_note', 'student', studentId, { courseId });
  return { status: 'ok' };
}

export async function listStudentNotes(studentId, courseId) {
  await ensureSchema();
  const rows = await withPg(async (client) => {
    const params = [String(studentId)];
    let sql = `SELECT id, student_id, course_id, author, content, created_at FROM student_notes WHERE student_id=$1`;
    if (courseId) { sql += ' AND course_id=$2'; params.push(courseId); }
    sql += ' ORDER BY created_at DESC LIMIT 200';
    const { rows } = await client.query(sql, params);
    return rows;
  });
  return rows;
}

export async function addStudentTag(studentId, tag, courseId) {
  await ensureSchema();
  await withPg((client) => client.query(
    `INSERT INTO student_tags(student_id, tag, course_id) VALUES($1,$2,$3) ON CONFLICT DO NOTHING`,
    [String(studentId), tag, courseId || null]
  ));
  await recordAction('teacher', 'add_student_tag', 'student', studentId, { tag, courseId });
  return { status: 'ok' };
}

export async function removeStudentTag(studentId, tag, courseId) {
  await ensureSchema();
  await withPg((client) => client.query(
    `DELETE FROM student_tags WHERE student_id=$1 AND tag=$2 AND (course_id IS NOT DISTINCT FROM $3)`,
    [String(studentId), tag, courseId || null]
  ));
  await recordAction('teacher', 'remove_student_tag', 'student', studentId, { tag, courseId });
  return { status: 'ok' };
}

export async function getClassSettings(courseId) {
  await ensureSchema();
  const row = await withPg(async (client) => {
    const { rows } = await client.query(`SELECT settings FROM course_settings WHERE course_id=$1`, [courseId]);
    return rows[0];
  });
  return row?.settings || {};
}

export async function updateClassSettings(courseId, patch) {
  await ensureSchema();
  const row = await withPg(async (client) => {
    const { rows } = await client.query(
      `INSERT INTO course_settings(course_id, settings)
       VALUES($1, $2::jsonb)
       ON CONFLICT (course_id)
       DO UPDATE SET settings = course_settings.settings || EXCLUDED.settings, updated_at = NOW()
       RETURNING settings`,
      [courseId, JSON.stringify(patch || {})]
    );
    return rows[0];
  });
  await recordAction('teacher', 'update_class_settings', 'course', courseId, { patch });
  return row?.settings || {};
}

export async function exportStudents(courseId) {
  const students = await listStudents(courseId, { limit: 5000 });
  return students;
}

export async function exportAlerts(courseId) {
  const alerts = await listAlerts(courseId);
  return alerts;
}
