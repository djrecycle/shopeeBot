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
    const search = searchParams.get('search');
    
    const db = await getDb();
    
    let query = 'SELECT * FROM products';
    const params = [];
    
    if (category || search) {
      query += ' WHERE';
      const clauses = [];
      if (category) {
        clauses.push(' category = ?');
        params.push(category);
      }
      if (search) {
        clauses.push(' (name LIKE ? OR description LIKE ?)');
        params.push(`%${search}%`, `%${search}%`);
      }
      query += clauses.join(' AND');
    }
    
    query += ' ORDER BY id DESC';
    const products = await db.all(query, params);
    
    // Parse JSON fields
    const parsedProducts = products.map(p => ({
      ...p,
      images: JSON.parse(p.images || '[]'),
      specs: JSON.parse(p.specs || '[]'),
      variations: JSON.parse(p.variations || '[]'),
      tags: JSON.parse(p.tags || '[]')
    }));
    
    return NextResponse.json(parsedProducts);
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

// Protected POST: Edit product original price or category/details
export async function POST(request) {
  const session = getSession(request);
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const { id, name, original_price, category, description } = await request.json();
    
    if (!id) {
      return NextResponse.json({ error: 'Product ID wajib disertakan' }, { status: 400 });
    }
    
    const db = await getDb();
    const oldProduct = await db.get('SELECT name, category FROM products WHERE id = ?', [id]);
    
    if (!oldProduct) {
      return NextResponse.json({ error: 'Produk tidak ditemukan' }, { status: 404 });
    }
    
    await db.run(`
      UPDATE products
      SET name = ?, original_price = ?, category = ?, description = ?
      WHERE id = ?
    `, [name, original_price, category, description, id]);
    
    // Update local Markdown file
    try {
      const mdBase = path.join(process.cwd(), '../hasil_md');
      const oldPath = path.join(mdBase, oldProduct.category, `${oldProduct.name}.md`);
      
      if (fs.existsSync(oldPath)) {
        let content = fs.readFileSync(oldPath, 'utf-8');
        
        // Update Title
        if (name !== oldProduct.name) {
          content = content.replace(/^# .+/m, `# ${name}`);
        }
        
        // Update Price
        if (original_price) {
          const priceRegex = /(## (?:💰 )?Harga\n)([\s\S]*?)(?=\n## |\Z)/;
          if (priceRegex.test(content)) {
            content = content.replace(priceRegex, `$1${original_price}\n\n`);
          }
        }
        
        // Update Description
        if (description) {
          const descRegex = /(## (?:📝 )?Deskripsi\n)([\s\S]*?)(?=\n## |\Z)/;
          if (descRegex.test(content)) {
            content = content.replace(descRegex, `$1${description}\n\n`);
          }
        }
        
        // Handle move/rename
        if (name !== oldProduct.name || category !== oldProduct.category) {
          const newCatDir = path.join(mdBase, category);
          if (!fs.existsSync(newCatDir)) fs.mkdirSync(newCatDir, { recursive: true });
          
          const newPath = path.join(newCatDir, `${name}.md`);
          fs.writeFileSync(newPath, content);
          fs.unlinkSync(oldPath);
          
          // Cleanup old dir if empty
          const oldCatDir = path.join(mdBase, oldProduct.category);
          if (fs.existsSync(oldCatDir) && fs.readdirSync(oldCatDir).length === 0) {
            fs.rmdirSync(oldCatDir);
          }
        } else {
          fs.writeFileSync(oldPath, content);
        }
      }
    } catch (fsErr) {
      console.error('Failed to update MD file:', fsErr);
    }
    
    // Auto regenerate preview.html
    try {
      const { exec } = require('child_process');
      const scriptPath = path.join(process.cwd(), '../modules/generate_site.py');
      exec(`python3 "${scriptPath}" --no-open`, (error) => {
        if (error) console.error('Failed to regenerate preview:', error);
      });
    } catch(e) {}
    
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

// Protected DELETE: Remove product
export async function DELETE(request) {
  const session = getSession(request);
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    
    if (!id) {
      return NextResponse.json({ error: 'Product ID wajib disertakan' }, { status: 400 });
    }
    
    const db = await getDb();
    const product = await db.get('SELECT name, category FROM products WHERE id = ?', [id]);
    
    if (product) {
      try {
        const mdPath = path.join(process.cwd(), '../hasil_md', product.category, `${product.name}.md`);
        if (fs.existsSync(mdPath)) {
          fs.unlinkSync(mdPath);
          
          // Cleanup dir if empty
          const dirPath = path.dirname(mdPath);
          if (fs.existsSync(dirPath) && fs.readdirSync(dirPath).length === 0) {
            fs.rmdirSync(dirPath);
          }
        }
      } catch (fsErr) {
        console.error('Failed to delete MD file:', fsErr);
      }
      
      await db.run('DELETE FROM products WHERE id = ?', [id]);
    }
    
    // Auto regenerate preview.html
    try {
      const { exec } = require('child_process');
      const scriptPath = path.join(process.cwd(), '../modules/generate_site.py');
      exec(`python3 "${scriptPath}" --no-open`, (error) => {
        if (error) console.error('Failed to regenerate preview:', error);
      });
    } catch(e) {}
    
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
