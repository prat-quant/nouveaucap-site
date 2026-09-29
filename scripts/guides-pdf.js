// Prints the guides built by guides.py (build/guides/*.html) to docs/guides/<slug>.pdf, A4, with a small
// footer (guide name and page number). Needs Node and Playwright with Chromium (present in Claude Code
// cloud sessions). Usage, from the repository root: python3 guides.py && node scripts/guides-pdf.js [slug]
const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

let playwright;
try { playwright = require('playwright'); } catch (e) {
  playwright = require(path.join(execSync('npm root -g').toString().trim(), 'playwright'));
}

const ROOT = path.join(__dirname, '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.woff2': 'font/woff2', '.png': 'image/png' };

// Serves the repository so that /guides/guide.css and /assets/... resolve as on the site.
const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const only = process.argv[2];
  const slugs = fs.readdirSync(path.join(ROOT, 'build', 'guides')).filter(f => f.endsWith('.html'))
    .map(f => f.slice(0, -5)).filter(s => !only || s === only);
  fs.mkdirSync(path.join(ROOT, 'docs', 'guides'), { recursive: true });
  const browser = await playwright.chromium.launch();
  const page = await browser.newPage();
  for (const slug of slugs) {
    await page.goto(`${base}/build/guides/${slug}.html`, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const short = await page.getAttribute('meta[name=short]', 'content');
    const out = path.join(ROOT, 'docs', 'guides', `${slug}.pdf`);
    await page.pdf({
      path: out, format: 'A4', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
      headerTemplate: '<span></span>',
      footerTemplate: `<div style="width:100%;font:7.5px Arial,sans-serif;color:#6F7E94;padding:0 15mm;display:flex;justify-content:space-between">
        <span>Nouveau Cap · ${short} · nouveaucap.pixapop.fr</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`
    });
    console.log(`docs/guides/${slug}.pdf`);
  }
  await browser.close();
  server.close();
})();
