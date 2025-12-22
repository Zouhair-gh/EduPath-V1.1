/*
  Seed development data into the shared analytics database so the admin UI has content.
  Reads connection from env: ANALYTICS_DB_HOST/PORT/NAME/USER/PASSWORD (defaults for local dev).
*/
import 'dotenv/config';
import { Client } from 'pg';

const cfgPrimary = {
  host: process.env.ANALYTICS_DB_HOST || 'localhost',
  port: Number(process.env.ANALYTICS_DB_PORT || 5433),
  database: process.env.ANALYTICS_DB_NAME || 'analytics_db',
  user: process.env.ANALYTICS_DB_USER || 'postgres',
  password: process.env.ANALYTICS_DB_PASSWORD || 'postgres',
};

const secondaryDbName = process.env.SEED_SECONDARY_DB_NAME;
const cfgSecondary = secondaryDbName
  ? {
      host: process.env.ANALYTICS_DB_HOST || 'localhost',
      port: Number(process.env.ANALYTICS_DB_PORT || 5433),
      database: secondaryDbName,
      user: process.env.ANALYTICS_DB_USER || 'postgres',
      password: process.env.ANALYTICS_DB_PASSWORD || 'postgres',
    }
  : null;

function sql(strings, ...vals) {
  let text = strings[0];
  vals.forEach((v, i) => { text += `$${i + 1}${strings[i + 1]}`; });
  return { text, values: vals };
}

async function ensureSchemas(client) {
  // Minimal schemas borrowed from services (PrepaData, StudentProfiler, PathPredictor)
  await client.query(`
    CREATE TABLE IF NOT EXISTS student_metrics (
      id SERIAL PRIMARY KEY,
      student_id INTEGER,
      course_id INTEGER,
      module_id INTEGER,
      engagement_score DECIMAL(5,2),
      success_rate DECIMAL(5,2),
      punctuality_score DECIMAL(5,2),
      previous_module_grade DECIMAL(5,2),
      forum_participation DECIMAL(5,2),
      time_spent_ratio DECIMAL(5,2),
      absence_days_last_30 INTEGER,
      assignment_completion_rate DECIMAL(5,2),
      passed BOOLEAN,
      updated_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS temporal_features (
      id SERIAL PRIMARY KEY,
      student_id INTEGER,
      course_id INTEGER,
      feature_date DATE,
      engagement_ma7 DECIMAL(5,2),
      engagement_ma30 DECIMAL(5,2)
    );

    CREATE TABLE IF NOT EXISTS student_profiles (
      id SERIAL PRIMARY KEY,
      student_id INTEGER,
      profile_id INTEGER,
      profile_label VARCHAR(50),
      confidence_score DECIMAL(5,2),
      assigned_at TIMESTAMP DEFAULT NOW(),
      model_version VARCHAR(20)
    );

    CREATE TABLE IF NOT EXISTS profile_definitions (
      id SERIAL PRIMARY KEY,
      profile_id INTEGER UNIQUE,
      label VARCHAR(50),
      description TEXT,
      avg_engagement DECIMAL(5,2),
      avg_success_rate DECIMAL(5,2),
      avg_punctuality DECIMAL(5,2),
      student_count INTEGER,
      created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS alerts (
      id SERIAL PRIMARY KEY,
      prediction_id INTEGER,
      student_id INTEGER,
      course_id INTEGER,
      severity VARCHAR(10),
      risk_factors JSONB,
      recommended_actions JSONB,
      status VARCHAR(20) DEFAULT 'ACTIVE',
      created_at TIMESTAMP DEFAULT NOW(),
      resolved_at TIMESTAMP
    );
  `);
}

function rand(min, max) { return Math.round((min + Math.random() * (max - min)) * 100) / 100; }

async function seedMetrics(client) {
  // Detect available columns to avoid missing-column errors
  const { rows: colsRows } = await client.query(
    "SELECT column_name FROM information_schema.columns WHERE table_name = 'student_metrics'"
  );
  const cols = new Set(colsRows.map((r) => r.column_name));

  const NUM_COURSES = Number(process.env.NUM_COURSES || 3);
  const STUDENTS_PER_COURSE = Number(process.env.STUDENTS_PER_COURSE || 12);
  const allStudents = [];
  for (let courseId = 1; courseId <= NUM_COURSES; courseId++) {
    for (let i = 0; i < STUDENTS_PER_COURSE; i++) {
      const sid = courseId * 1000 + i; // unique student ids across courses
      allStudents.push({ sid, courseId });
      const candidate = {
        student_id: sid,
        course_id: courseId,
        module_id: courseId * 10 + 1,
        engagement_score: rand(40, 95),
        success_rate: rand(30, 90),
        punctuality_score: rand(50, 95),
        previous_module_grade: rand(40, 90),
        forum_participation: rand(0, 100),
        time_spent_ratio: rand(0.3, 1.2),
        absence_days_last_30: Math.floor(rand(0, 5)),
        assignment_completion_rate: rand(40, 100),
        passed: Math.random() > 0.3,
        login_count: Math.floor(rand(5, 30)),
        total_time_spent: Math.floor(rand(100, 1200)),
        forum_posts_count: Math.floor(rand(0, 25)),
        resources_viewed_count: Math.floor(rand(3, 50)),
        activities_completed: Math.floor(rand(1, 10)),
        activities_total: Math.floor(rand(10, 12)),
        late_submissions: Math.floor(rand(0, 3)),
        avg_grade: rand(40, 95),
        last_activity_date: new Date(),
      };

      const fields = Object.keys(candidate).filter((k) => cols.has(k));
      const placeholders = fields.map((_, i2) => `$${i2 + 1}`).join(',');
      const values = fields.map((k) => candidate[k]);
      const sqlText = `INSERT INTO student_metrics (${fields.join(',')}) VALUES (${placeholders})`;
      await client.query(sqlText, values);

      await client.query(
        'INSERT INTO temporal_features (student_id, course_id, feature_date, engagement_ma7, engagement_ma30) VALUES ($1,$2, CURRENT_DATE, $3, $4)',
        [sid, courseId, rand(40, 95), rand(40, 95)]
      );
    }
  }
  return allStudents.map(s => s.sid);
}

async function seedProfiles(client, students) {
  const defs = [
    { profile_id: 0, label: 'À risque', description: 'Faible engagement et réussite', avg_engagement: 45, avg_success_rate: 40, avg_punctuality: 70, student_count: 0 },
    { profile_id: 1, label: 'Stable', description: 'Moyennes stables', avg_engagement: 65, avg_success_rate: 60, avg_punctuality: 80, student_count: 0 },
    { profile_id: 2, label: 'Engagé', description: 'Haut engagement et réussite', avg_engagement: 85, avg_success_rate: 80, avg_punctuality: 90, student_count: 0 },
  ];
  for (const d of defs) {
    await client.query(
      'INSERT INTO profile_definitions (profile_id, label, description, avg_engagement, avg_success_rate, avg_punctuality, student_count) VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT (profile_id) DO UPDATE SET label=EXCLUDED.label, description=EXCLUDED.description, avg_engagement=EXCLUDED.avg_engagement, avg_success_rate=EXCLUDED.avg_success_rate, avg_punctuality=EXCLUDED.avg_punctuality, student_count=EXCLUDED.student_count',
      [d.profile_id, d.label, d.description, d.avg_engagement, d.avg_success_rate, d.avg_punctuality, d.student_count]
    );
  }
  let i = 0;
  for (const sid of students) {
    const pid = i % 3;
    const label = defs[pid].label;
    const conf = rand(60, 95);
    await client.query(
      'INSERT INTO student_profiles (student_id, profile_id, profile_label, confidence_score, model_version) VALUES ($1,$2,$3,$4,$5)',
      [sid, pid, label, conf, 'v1.0']
    );
    i++;
  }
}

async function seedAlerts(client, students) {
  // Group students by course via sid encoding: courseId = floor(sid / 1000)
  const byCourse = new Map();
  for (const sid of students) {
    const courseId = Math.floor(Number(sid) / 1000);
    const list = byCourse.get(courseId) || [];
    list.push(Number(sid));
    byCourse.set(courseId, list);
  }
  for (const [courseId, sids] of byCourse.entries()) {
    const sampleIds = sids.slice(0, Math.min(4, sids.length));
    for (const sid of sampleIds) {
      const severity = Math.random() > 0.5 ? 'HIGH' : 'MEDIUM';
      const risk = { low_engagement: rand(0.4, 0.9), missing_assignments: Math.floor(Math.random() * 5) };
      const actions = severity === 'HIGH' ? ['Contacter étudiant', 'Proposer tutorat'] : ['Envoyer rappel'];
      await client.query(
        'INSERT INTO alerts (prediction_id, student_id, course_id, severity, risk_factors, recommended_actions, status) VALUES ($1,$2,$3,$4,$5::jsonb,$6::jsonb,$7)',
        [null, sid, courseId, severity, JSON.stringify(risk), JSON.stringify(actions), 'ACTIVE']
      );
    }
  }
}

async function seedForConfig(label, cfg) {
  const client = new Client(cfg);
  await client.connect();
  console.log(`[${label}] Connected`, cfg);
  try {
    await ensureSchemas(client);
    const students = await seedMetrics(client);
    await seedProfiles(client, students);
    await seedAlerts(client, students);
    const res1 = await client.query('SELECT COUNT(*)::int AS c FROM student_metrics');
    const res2 = await client.query("SELECT COUNT(DISTINCT student_id)::int AS c FROM student_profiles");
    const res3 = await client.query("SELECT COUNT(*)::int AS c FROM alerts WHERE status='ACTIVE'");
    console.log(`[${label}] Seed complete: metrics=${res1.rows[0].c}, profiles=${res2.rows[0].c}, active_alerts=${res3.rows[0].c}`);
  } finally {
    await client.end();
  }
}

async function main() {
  await seedForConfig('primary', cfgPrimary);
  if (cfgSecondary) {
    await seedForConfig('secondary', cfgSecondary);
  }
}

main().catch((e) => { console.error('Seed failed', e); process.exit(1); });
