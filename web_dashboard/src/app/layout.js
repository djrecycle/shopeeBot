import './globals.css';

export const metadata = {
  title: 'ShopeeBot Professional Web Portal',
  description: 'Premium Shopee Dropship & Scraping Management Catalog',
};

export default function RootLayout({ children }) {
  return (
    <html lang="id">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
