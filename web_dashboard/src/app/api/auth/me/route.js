import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';

const JWT_SECRET = 'shopee-bot-super-secret-key-12345';

export async function GET(request) {
  const token = request.cookies.get('auth_token')?.value;
  
  if (!token) {
    return NextResponse.json({ authenticated: false }, { status: 200 });
  }
  
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    return NextResponse.json({ authenticated: true, username: decoded.username }, { status: 200 });
  } catch (err) {
    return NextResponse.json({ authenticated: false }, { status: 200 });
  }
}
