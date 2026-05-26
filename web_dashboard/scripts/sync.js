const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');
const bcrypt = require('bcryptjs');

// Helper to parse CSV robustly
function parseCSV(text) {
  const lines = text.split(/\r?\n/);
  if (lines.length === 0 || !lines[0].trim()) return [];
  
  const headers = parseCSVLine(lines[0]);
  const result = [];
  
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const values = parseCSVLine(line);
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] || '';
    });
    result.push(row);
  }
  return result;
}

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.replace(/^"|"$/g, '').trim());
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.replace(/^"|"$/g, '').trim());
  return result;
}

// Helper to parse Markdown files
function parseMarkdownProduct(content) {
  // Strip HTML tags and "Harga Upload:" to clean data before DB insertion
  let cleanContent = content.replace(/<[^>]*>?/gm, '');
  cleanContent = cleanContent.replace(/Harga Upload:\s*/gi, '');
  
  const lines = cleanContent.split('\n');
  let title = 'Tanpa Judul';
  let originalPrice = '0';
  let storeLink = '';
  let productLink = '';
  let specs = [];
  let description = '';
  let variations = [];
  let images = [];
  
  let section = '';
  let descLines = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    
    if (line.startsWith('# ') && i === 0) {
      title = line.substring(2).trim();
      continue;
    }
    
    if (line.startsWith('## ')) {
      section = line.substring(3).trim();
      continue;
    }
    
    if (section.includes('Harga')) {
      originalPrice = line.trim();
      continue;
    }
    
    if (section.includes('Toko')) {
      storeLink = line.trim();
      continue;
    }
    
    if (section.includes('Produk') && !section.includes('Variasi') && !section.includes('Gambar')) {
      productLink = line.trim();
      continue;
    }
    
    if (section.includes('Spesifikasi')) {
      if (line.startsWith('|') && !line.includes('Spesifikasi | Detail') && !line.includes(':---')) {
        const parts = line.split('|').map(p => p.trim()).filter(Boolean);
        if (parts.length >= 2) {
          const key = parts[0].replace(/\*\*/g, '').trim();
          let val = parts[1].trim();
          if (key.toLowerCase().includes('kategori') && val.startsWith('Shopee ')) {
            val = val.replace(/^Shopee\s+/, '');
          }
          specs.push({ key, val });
        }
      }
      continue;
    }
    
    if (section.includes('Deskripsi')) {
      descLines.push(line);
      continue;
    }
    
    if (section.includes('Variasi')) {
      if (line.startsWith('- ')) {
        const text = line.substring(2).trim();
        // Parse image if exists
        const imgMatch = text.match(/\((https?:\/\/[^\)]+)\)/);
        const imgUrl = imgMatch ? imgMatch[1] : null;
        
        // Remove image link text
        const namePrice = text.split('|')[0].trim();
        
        // Extract name and price using Regex: everything before the last price occurrence
        const match = namePrice.match(/^(.*?)\s*:\s*(Rp[0-9.,]+)/);
        if (match) {
          const name = match[1].trim();
          const price = match[2].trim();
          variations.push({ name, price, imgUrl });
        } else {
          // Fallback
          const parts = namePrice.split(':');
          if (parts.length >= 2) {
            const name = parts.slice(0, -1).join(':').trim();
            const price = parts[parts.length - 1].trim().split('(')[0].trim();
            variations.push({ name, price, imgUrl });
          }
        }
      }
      continue;
    }
    
    if (section.includes('Gambar')) {
      const match = line.match(/\((https?:\/\/[^\)]+)\)/);
      if (match) {
        images.push(match[1]);
      }
      continue;
    }
  }
  
  description = descLines.join('\n').replace(/[~_=]{2,}/g, '').trim();
  
  // Extract tags from description
  const tagsMatch = description.match(/#[\w\u00C0-\u024F]+/g);
  const tags = tagsMatch ? [...new Set(tagsMatch)] : [];
  
  // Remove tags from description text for clean rendering
  description = description.replace(/#[\w\u00C0-\u024F]+/g, '').trim();
  
  return { title, originalPrice, storeLink, productLink, specs, description, tags, variations, images };
}

async function sync() {
  console.log('🔄 Memulai sinkronisasi data ke SQLite...');
  
  const csvPath = path.resolve(__dirname, '../../shopee_links.csv');
  const mdPath = path.resolve(__dirname, '../../hasil_md');
  const dbPath = path.resolve(__dirname, '../database.sqlite');
  
  // 1. Open SQLite Connection
  const db = await open({
    filename: dbPath,
    driver: sqlite3.Database
  });
  
  // 2. Initialize Schemas
  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE,
      password_hash TEXT
    );
    
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE,
      original_price TEXT,
      store_link TEXT,
      product_link TEXT,
      category TEXT,
      description TEXT,
      images TEXT,
      specs TEXT,
      variations TEXT,
      tags TEXT
    );
    
    CREATE TABLE IF NOT EXISTS scraping_links (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      category TEXT,
      keyword TEXT,
      location TEXT,
      link TEXT UNIQUE,
      rating TEXT,
      chat_status TEXT,
      status TEXT,
      shop TEXT
    );
  `);
  
  // 3. Seed Default Admin User if not exists
  const adminExists = await db.get('SELECT * FROM users WHERE username = ?', ['admin']);
  if (!adminExists) {
    const passwordHash = await bcrypt.hash('admin123', 10);
    await db.run('INSERT INTO users (username, password_hash) VALUES (?, ?)', ['admin', passwordHash]);
    console.log('🔑 Akun Admin Default Dibuat (Username: admin | Password: admin123)');
  }
  
  // 4. Sync CSV Links
  if (fs.existsSync(csvPath)) {
    const csvContent = fs.readFileSync(csvPath, 'utf-8');
    const rows = parseCSV(csvContent);
    let linkSynced = 0;
    const validLinks = new Set();
    
    for (const row of rows) {
      const category = row['Kategori'] || '';
      const keyword = row['Keyword'] || '';
      const location = row['Lokasi'] || '';
      const link = row['Link Produk'] || '';
      const rating = row['Rating'] || '';
      const chatStatus = row['Status Chat'] || '';
      const status = row['Status'] || '';
      const shop = row['Toko'] || '';
      
      if (!link) continue;
      
      try {
        await db.run(`
          INSERT INTO scraping_links (category, keyword, location, link, rating, chat_status, status, shop)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(link) DO UPDATE SET
            category = excluded.category,
            keyword = excluded.keyword,
            location = excluded.location,
            rating = excluded.rating,
            chat_status = excluded.chat_status,
            status = excluded.status,
            shop = excluded.shop
        `, [category, keyword, location, link, rating, chatStatus, status, shop]);
        linkSynced++;
        validLinks.add(link);
      } catch (err) {
        console.error(`⚠️ Gagal menyimpan link ${link}:`, err.message);
      }
    }
    console.log(`📊 Berhasil sinkronisasi ${linkSynced} link dari shopee_links.csv`);
    
    const allDbLinks = await db.all('SELECT id, link FROM scraping_links');
    const linksToDelete = allDbLinks.filter(row => !validLinks.has(row.link));
    for (const row of linksToDelete) {
      await db.run('DELETE FROM scraping_links WHERE id = ?', [row.id]);
    }
    if (linksToDelete.length > 0) {
      console.log(`🗑️ Dihapus ${linksToDelete.length} link usang dari database (sinkronisasi dari CSV)`);
    }
  } else {
    console.log('⚠️ File shopee_links.csv tidak ditemukan. Lewati sinkronisasi link.');
  }
  
  // 5. Sync Markdown Products
  if (fs.existsSync(mdPath)) {
    const categories = fs.readdirSync(mdPath).filter(f => fs.statSync(path.join(mdPath, f)).isDirectory());
    let prodSynced = 0;
    const validProductNames = new Set();
    
    for (const cat of categories) {
      const catDir = path.join(mdPath, cat);
      const files = fs.readdirSync(catDir).filter(f => f.endsWith('.md'));
      
      for (const file of files) {
        const filePath = path.join(catDir, file);
        try {
          const content = fs.readFileSync(filePath, 'utf-8');
          const parsed = parseMarkdownProduct(content);
          const name = file.replace('.md', '');
          
          await db.run(`
            INSERT INTO products (name, original_price, store_link, product_link, category, description, images, specs, variations, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
              original_price = excluded.original_price,
              store_link = excluded.store_link,
              product_link = excluded.product_link,
              category = excluded.category,
              description = excluded.description,
              images = excluded.images,
              specs = excluded.specs,
              variations = excluded.variations,
              tags = excluded.tags
          `, [
            name,
            parsed.originalPrice,
            parsed.storeLink,
            parsed.productLink,
            cat,
            parsed.description,
            JSON.stringify(parsed.images),
            JSON.stringify(parsed.specs),
            JSON.stringify(parsed.variations),
            JSON.stringify(parsed.tags)
          ]);
          prodSynced++;
          validProductNames.add(name);
        } catch (err) {
          console.error(`⚠️ Gagal menyimpan produk markdown ${file}:`, err.message);
        }
      }
    }
    console.log(`📦 Berhasil sinkronisasi ${prodSynced} produk dari folder hasil_md/`);

    const allDbProducts = await db.all('SELECT id, name FROM products');
    const productsToDelete = allDbProducts.filter(row => !validProductNames.has(row.name));
    for (const row of productsToDelete) {
      await db.run('DELETE FROM products WHERE id = ?', [row.id]);
    }
    if (productsToDelete.length > 0) {
      console.log(`🗑️ Dihapus ${productsToDelete.length} produk usang dari database (sinkronisasi dari hasil_md)`);
    }
  } else {
    console.log('⚠️ Folder hasil_md/ tidak ditemukan. Lewati sinkronisasi produk.');
  }
  
  await db.close();
  console.log('✅ Sinkronisasi database SQLite Berhasil Selesai!');
}

sync().catch(err => {
  console.error('❌ Sinkronisasi Gagal:', err);
  process.exit(1);
});
