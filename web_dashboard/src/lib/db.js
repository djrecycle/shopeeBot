import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';

let dbInstance = null;

export async function getDb() {
  if (dbInstance) {
    // Verify connection is still alive
    try {
      await dbInstance.get('SELECT 1');
      return dbInstance;
    } catch {
      dbInstance = null;
    }
  }

  const dbPath = path.resolve(process.cwd(), 'database.sqlite');

  dbInstance = await open({
    filename: dbPath,
    driver: sqlite3.Database,
  });

  // Enable WAL mode for better concurrent read performance
  await dbInstance.exec('PRAGMA journal_mode=WAL;');

  return dbInstance;
}
