# Data folder — how the refresh workflow works

This study hub does **not** live-fetch ird.gov.hk from inside the HTML pages
(browsers block that for local files). Instead, refreshing is a 3-step manual
loop:

1. **Download** the updated document from the source and drop it into the
   matching subfolder below (keep the original filename, or something
   recognisable).
2. **Run** `scripts\Refresh-Data-Manifest.bat` (double-click it). It rescans
   this folder and rebuilds `assets/js/data-manifest.js` with the file names
   and last-modified dates — no internet access, no content parsing.
3. **Reload** the relevant study hub page. If the new file is newer than that
   page's "last reviewed" date, the freshness banner at the top turns amber/
   red and tells you which page needs a re-check. Ask Claude (in a Claude Code
   session) to re-read the updated file and refresh that page's content —
   the manifest only tracks *that a file changed*, not *what changed in it*.

## Folder map

| Folder | What goes here | Source |
|---|---|---|
| `CAP112/` | Consolidated Inland Revenue Ordinance (Cap. 112) — Profits Tax, Property Tax, Salaries Tax, Depreciation Allowances, administration provisions | https://www.elegislation.gov.hk/hk/cap112 |
| `CAP117/` | Consolidated Stamp Duty Ordinance (Cap. 117) — a *separate* ordinance from Cap. 112. **Populated** (current to 26 Feb 2026); re-download after any further amendment. | https://www.elegislation.gov.hk/hk/cap117 (gated behind a JS/cookie check — a browser download works fine even though automated fetch does not) |
| `DIPN/Profits-Tax/` | DIPNs on profits tax / source of profits / deductibility | https://www.ird.gov.hk/eng/ppr/dip.htm |
| `DIPN/Property-Tax/` | DIPNs on property tax | https://www.ird.gov.hk/eng/ppr/dip.htm |
| `DIPN/Salaries-Tax/` | DIPNs on salaries tax | https://www.ird.gov.hk/eng/ppr/dip.htm |
| `DIPN/Stamp-Duty/` | DIPNs on stamp duty | https://www.ird.gov.hk/eng/ppr/dip.htm |
| `DIPN/Depreciation-Allowances/` | DIPNs on depreciation / capital allowances | https://www.ird.gov.hk/eng/ppr/dip.htm |
| `IRD-Administration/` | IRD guides on filing, assessment, objections, appeals, penalties | https://www.ird.gov.hk |
| `PwC/` | Saved PwC Worldwide Tax Summaries pages (cross-check only, not a primary legal source) | https://taxsummaries.pwc.com/hong-kong-sar |

Category names above must match the `sources: [...]` list declared at the top
of each page's `<script>` block (`window.PAGE_META`) — that's how the
freshness banner knows which files to watch.
