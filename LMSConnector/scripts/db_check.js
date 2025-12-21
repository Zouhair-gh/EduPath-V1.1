import { Pool } from 'pg';
import { config } from '../src/config.js';

async function main() {
  if (config.db.disable) {
    console.error('DB disabled by configuration');
    process.exit(1);
  }
  const pool = new Pool({
    host: config.db.host,
    port: config.db.port,
    user: config.db.user,
    password: config.db.password,
    database: config.db.database,
  });
  const q = async (sql) => (await pool.query(sql)).rows;
  const counts = {
    students: (await q('SELECT COUNT(*)::int AS c FROM students'))[0].c,
    courses: (await q('SELECT COUNT(*)::int AS c FROM courses'))[0].c,
    enrollments: (await q('SELECT COUNT(*)::int AS c FROM enrollments'))[0].c,
    grades: (await q('SELECT COUNT(*)::int AS c FROM grades'))[0].c,
    activity_logs: (await q('SELECT COUNT(*)::int AS c FROM activity_logs'))[0].c,
    sync_logs: (await q('SELECT COUNT(*)::int AS c FROM sync_logs'))[0].c,
  };
  const latestJobs = await q('SELECT id, lms_type, sync_type, status, records_processed, started_at, completed_at, stats_json FROM sync_logs ORDER BY started_at DESC LIMIT 5');
  console.log(JSON.stringify({ counts, latestJobs }, null, 2));
  await pool.end();
}

main().catch(err => { console.error(err); process.exit(1); });
