import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

export async function GET() {
  try {
    const db = await getDb();
    
    // 1. General counts
    const totalRow = await db.get('SELECT COUNT(*) as count FROM scraping_links');
    const totalTargets = totalRow ? totalRow.count : 0;
    
    const scrapedRow = await db.get("SELECT COUNT(*) as count FROM scraping_links WHERE status = 'Done' OR status = 'Sent'");
    const scrapedTargets = scrapedRow ? scrapedRow.count : 0;
    
    const chatSentRow = await db.get("SELECT COUNT(*) as count FROM scraping_links WHERE chat_status = 'Sent'");
    const chatSentTargets = chatSentRow ? chatSentRow.count : 0;
    
    const categoriesRow = await db.all('SELECT DISTINCT category FROM products');
    const totalCategories = categoriesRow ? categoriesRow.length : 0;
    
    // 2. Category detailed analytics
    // Merge ALL categories from both scraping_links AND products
    const categoryStats = await db.all(`
      SELECT 
        all_cats.category,
        COALESCE(sl.total, 0) as total,
        COALESCE(sl.scraped, 0) as scraped,
        COALESCE(sl.chatSent, 0) as chatSent,
        COALESCE(p.productCount, 0) as productCount
      FROM (
        SELECT DISTINCT category FROM scraping_links WHERE category IS NOT NULL AND category != ''
        UNION
        SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''
      ) all_cats
      LEFT JOIN (
        SELECT 
          category,
          COUNT(*) as total,
          SUM(CASE WHEN status = 'Done' OR status = 'Sent' THEN 1 ELSE 0 END) as scraped,
          SUM(CASE WHEN chat_status = 'Sent' THEN 1 ELSE 0 END) as chatSent
        FROM scraping_links
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
      ) sl ON all_cats.category = sl.category
      LEFT JOIN (
        SELECT category, COUNT(*) as productCount
        FROM products
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
      ) p ON all_cats.category = p.category
      ORDER BY all_cats.category ASC
    `);
    
    return NextResponse.json({
      totalTargets,
      scrapedTargets,
      chatSentTargets,
      totalCategories,
      categoryStats: categoryStats || []
    });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
