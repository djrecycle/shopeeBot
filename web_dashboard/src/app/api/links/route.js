import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import jwt from 'jsonwebtoken';
import fs from 'fs';
import path from 'path';
const JWT_SECRET = 'shopee-bot-super-secret-key-12345';

function getSession(request) {
  const token = request.cookies.get('auth_token')?.value;
  if (!token) return null;
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (err) {
    return null;
  }
}

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const category = searchParams.get('category');
    const status = searchParams.get('status');
    const chat_status = searchParams.get('chat_status');
    const search = searchParams.get('search');
    
    const db = await getDb();
    
    let query = 'SELECT * FROM scraping_links';
    const params = [];
    
    const clauses = [];
    if (category) {
      clauses.push(' category = ?');
      params.push(category);
    }
    if (status) {
      if (status === 'Done') {
        clauses.push(" (status = 'Done' OR status = 'Sent')");
      } else {
        clauses.push(" (status != 'Done' AND status != 'Sent')");
      }
    }
    if (chat_status) {
      if (chat_status === 'Sent') {
        clauses.push(" chat_status = 'Sent'");
      } else if (chat_status === 'Skip') {
        clauses.push(" chat_status LIKE 'Skip%'");
      } else if (chat_status === 'Failed') {
        clauses.push(" chat_status = 'Failed'");
      } else if (chat_status === 'Pending') {
        clauses.push(" (chat_status IS NULL OR chat_status = '' OR chat_status = 'nan' OR chat_status = '-')");
      }
    }
    if (search) {
      clauses.push(' (shop LIKE ? OR link LIKE ? OR keyword LIKE ?)');
      params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }
    
    if (clauses.length > 0) {
      query += ' WHERE' + clauses.join(' AND');
    }
    
    query += ' ORDER BY id DESC';
    
    const links = await db.all(query, params);
    return NextResponse.json(links);
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

// Protected DELETE: Remove selected or all links
export async function DELETE(request) {
  const session = getSession(request);
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    const all = searchParams.get('all');
    
    const db = await getDb();
    
    if (all === 'true') {
      try {
        const csvPath = path.join(process.cwd(), '../shopee_links.csv');
        if (fs.existsSync(csvPath)) {
          const content = fs.readFileSync(csvPath, 'utf-8');
          const firstLine = content.split(/\r?\n/)[0] || '';
          fs.writeFileSync(csvPath, firstLine + '\n');
        }
      } catch (fsErr) {
        console.error('Failed to clear CSV:', fsErr);
      }
      
      await db.run('DELETE FROM scraping_links');
      return NextResponse.json({ success: true, message: 'Semua link dihapus' });
    }
    
    if (!id) {
      return NextResponse.json({ error: 'ID link wajib disertakan' }, { status: 400 });
    }
    
    const linkRow = await db.get('SELECT link FROM scraping_links WHERE id = ?', [id]);
    if (linkRow) {
      try {
        const csvPath = path.join(process.cwd(), '../shopee_links.csv');
        if (fs.existsSync(csvPath)) {
          const content = fs.readFileSync(csvPath, 'utf-8');
          const lines = content.split(/\r?\n/);
          
          if (lines.length > 0) {
            const newLines = lines.filter((line, idx) => {
              if (idx === 0) return true;
              if (!line.trim()) return false;
              return !line.includes(linkRow.link);
            });
            fs.writeFileSync(csvPath, newLines.join('\n') + '\n');
          }
        }
      } catch (fsErr) {
        console.error('Failed to update CSV:', fsErr);
      }
      
      await db.run('DELETE FROM scraping_links WHERE id = ?', [id]);
    }
    return NextResponse.json({ success: true, message: 'Link berhasil dihapus' });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
