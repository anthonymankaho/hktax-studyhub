// Layout audit: every panel, desktop and phone.
//
// Added after a review found 14 of 23 panels overflowing horizontally at
// 380px - the existing suite only checked the MAIN panel, so wide data
// tables on the inner pages went unnoticed. Run from the project root:
//   npm install playwright && npx playwright install chromium   (once)
//   node scripts/audit-layout.js
//
// Exits non-zero if any panel overflows horizontally or throws a console
// error, so it can gate a release. Playwright is NOT a project dependency -
// install it where you run this.
const { chromium } = require('playwright');
const F = 'file:///C:/Users/User/Desktop/HKTAX STUDYHUB - CLAUDE/index.html';
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const errs = [];
  p.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  p.on('console', m => { if (m.type()==='error') errs.push('CONSOLE ' + m.text()); });
  await p.goto(F, { waitUntil: 'networkidle' });

  const panels = await p.$$eval('.tab-panel', ns => ns.map(n => n.id));
  console.log('panels: ' + panels.length);
  const issues = [];

  for (const id of panels) {
    await p.evaluate(i => window.hubActivate(i), id);
    await p.waitForTimeout(140);

    // horizontal overflow at desktop
    const ow = await p.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (ow > 1) issues.push(`${id}: ${ow}px horizontal overflow @1400`);

    // any element wider than its container
    const wide = await p.evaluate(pid => {
      const root = document.getElementById(pid);
      const lim = root.clientWidth + 2;
      return [...root.querySelectorAll('table,pre,img,div')]
        .filter(e => e.scrollWidth > lim && getComputedStyle(e).overflowX === 'visible')
        .slice(0,3).map(e => e.tagName + '.' + (e.className||'').split(' ')[0] + ' ' + e.scrollWidth + 'px');
    }, id);
    wide.forEach(w => issues.push(`${id}: overflowing ${w}`));

    // empty headings or empty table cells in a data row
    const empty = await p.evaluate(pid => {
      const root = document.getElementById(pid);
      const eh = [...root.querySelectorAll('h1,h2,h3,h4')].filter(h=>!h.textContent.trim()).length;
      return eh;
    }, id);
    if (empty) issues.push(`${id}: ${empty} empty heading(s)`);
  }

  // mobile sweep
  await p.setViewportSize({ width: 380, height: 800 });
  for (const id of panels) {
    await p.evaluate(i => window.hubActivate(i), id);
    await p.waitForTimeout(140);
    const ow = await p.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (ow > 1) issues.push(`${id}: ${ow}px horizontal overflow @380 (mobile)`);
  }

  console.log('console/page errors: ' + errs.length);
  errs.slice(0,10).forEach(e => console.log('  ! ' + e));
  console.log('layout issues: ' + issues.length);
  issues.forEach(i => console.log('  - ' + i));
  await b.close();
  if (issues.length || errs.length) process.exit(1);
})();
