import { Pool } from 'pg';
import { config } from '../config.js';

let pool = null;

export function getPool() {
  if (config.db.disable) return null;
  if (!pool) {
    pool = new Pool({
      host: config.db.host,
      port: config.db.port,
      user: config.db.user,
      password: config.db.password,
      database: config.db.database,
      max: 10,
    });
  }
  return pool;
}

export async function checkDbConnection() {
  if (config.db.disable) return false;
  try {
    const client = await getPool().connect();
    client.release();
    return true;
  } catch (e) {
    return false;
  }
}
