import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

const JWT_SECRET = 'shopee-bot-super-secret-key-12345';

export async function POST(request) {
  try {
    const { username, password } = await request.json();
    
    if (!username || !password) {
      return NextResponse.json({ error: 'Username dan password wajib diisi' }, { status: 400 });
    }
    
    const db = await getDb();
    const user = await db.get('SELECT * FROM users WHERE username = ?', [username]);
    
    if (!user) {
      return NextResponse.json({ error: 'Kredensial tidak valid' }, { status: 401 });
    }
    
    const isMatch = await bcrypt.compare(password, user.password_hash);
    if (!isMatch) {
      return NextResponse.json({ error: 'Kredensial tidak valid' }, { status: 401 });
    }
    
    // Create JWT
    const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '7d' });
    
    // Create Response
    const response = NextResponse.json({ success: true, username: user.username });
    
    // Set HTTP-Only Cookie
    response.cookies.set('auth_token', token, {
      httpOnly: true,
      secure: false, // Set to false to work easily in local dev (http://localhost)
      sameSite: 'strict',
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/'
    });
    
    return response;
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
