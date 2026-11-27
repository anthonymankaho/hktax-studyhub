/** HTML helpers shared by the catalog build. No filesystem and no Worker bindings. */

export const SITE = "https://anthonymanhk.github.io/hktax-studyhub/";

const NAMED = {
  amp: "&",
  lt: "<",
  gt: ">",
  quot: '"',
  apos: "'",
  nbsp: " ",
  middot: "·",
  rarr: "→",
  mdash: "—",
  ndash: "–",
  hellip: "…",
  times: "×",
  minus: "−",
};

export function decodeEntities(value) {
  return String(value)
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, num) => String.fromCodePoint(Number(num)))
    .replace(/&([a-z]+);/gi, (all, name) => {
      const key = name.toLowerCase();
      return Object.prototype.hasOwnProperty.call(NAMED, key) ? NAMED[key] : all;
    });
}

export function htmlToText(html) {
  let text = String(html)
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/(p|div|h[1-6]|li|caption|section|table|thead|tbody|details)>/gi, "\n")
    .replace(/<li[^>]*>/gi, "\n- ")
    .replace(/<\/tr>/gi, "\n")
    .replace(/<\/(th|td)>/gi, " | ")
    .replace(/<[^>]+>/g, "");
  text = decodeEntities(text);
  text = text.replace(/[ \t]+\|/g, " |");
  text = text.replace(/\|\s*(\n|$)/g, "$1");
  text = text.replace(/[ \t]{2,}/g, " ");
  text = text.replace(/[ \t]*\n[ \t]*/g, "\n");
  text = text.replace(/\n{3,}/g, "\n\n");
  return text.trim();
}

export function inlineText(html) {
  return htmlToText(html).replace(/\s+/g, " ").trim();
}

export function hubUrl(pageRef) {
  if (!pageRef) return null;
  const clean = String(pageRef).trim();
  if (/^https?:\/\//i.test(clean)) return clean;
  return `${SITE}pages/${clean.replace(/^\.?\//, "").replace(/^pages\//, "")}`;
}

export function pageUrl(file, sectionId) {
  const base = `${SITE}pages/${file}`;
  return sectionId ? `${base}#${sectionId}` : base;
}

/** Inner HTML of a `<section class="block" id="...">`, up to the next section. */
export function sectionHtml(html, id) {
  const re = new RegExp(`<section\\b(?=[^>]*\\bid="${id}")(?=[^>]*\\bclass="[^"]*\\bblock\\b)[^>]*>`, "i");
  const match = re.exec(html);
  if (!match) return null;
  const start = match.index + match[0].length;
  const rest = html.slice(start);
  const next = rest.search(/<section\b/i);
  let chunk = next === -1 ? rest : rest.slice(0, next);
  const close = chunk.lastIndexOf("</section>");
  if (close !== -1) chunk = chunk.slice(0, close);
  return chunk;
}

export function parseSections(html) {
  const opens = [];
  const re = /<section\b([^>]*)>/gi;
  let match;
  while ((match = re.exec(html))) {
    const attrs = match[1];
    if (!/\bclass="[^"]*\bblock\b/.test(attrs)) continue;
    const idMatch = attrs.match(/\bid="([^"]+)"/);
    opens.push({
      id: idMatch ? idMatch[1] : "",
      contentStart: match.index + match[0].length,
      tagStart: match.index,
    });
  }
  return opens.map((open, index) => {
    const stop = index + 1 < opens.length ? opens[index + 1].tagStart : html.length;
    let chunk = html.slice(open.contentStart, stop);
    const close = chunk.lastIndexOf("</section>");
    if (close !== -1) chunk = chunk.slice(0, close);
    const headingMatch = chunk.match(/<h2\b[^>]*>([\s\S]*?)<\/h2>/i);
    return {
      id: open.id,
      heading: headingMatch ? inlineText(headingMatch[1]) : open.id,
      text: htmlToText(chunk),
    };
  });
}

export function parseTitle(html) {
  const match = html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i);
  return match ? inlineText(match[1]) : "";
}

export function parseTables(html) {
  const tables = [];
  const re = /<table\b[^>]*>[\s\S]*?<\/table>/gi;
  let match;
  while ((match = re.exec(html))) {
    const table = match[0];
    const captionMatch = table.match(/<caption\b[^>]*>([\s\S]*?)<\/caption>/i);
    const rows = [];
    const rowRe = /<tr\b[^>]*>([\s\S]*?)<\/tr>/gi;
    let row;
    while ((row = rowRe.exec(table))) {
      const cells = [];
      const cellRe = /<(th|td)\b[^>]*>([\s\S]*?)<\/\1>/gi;
      let cell;
      while ((cell = cellRe.exec(row[1]))) {
        cells.push({
          text: inlineText(cell[2]),
          html: cell[2],
          header: cell[1].toLowerCase() === "th",
        });
      }
      if (cells.length) rows.push(cells);
    }
    tables.push({
      caption: captionMatch ? inlineText(captionMatch[1]) : "",
      rows,
    });
  }
  return tables;
}

/**
 * Map a hub status label onto enacted / bill / proposed / other.
 * Only "enacted" (and the summary-table synonyms Current / Published) is law.
 */
export function classifyLegalStatus(label) {
  const raw = String(label || "").trim();
  const head = raw.toLowerCase().split(/[—–:]/)[0].trim();
  let status = "other";
  if (head === "enacted" || head === "current" || head === "published") status = "enacted";
  else if (head === "bill" || head.startsWith("gazetted")) status = "bill";
  else if (head === "proposed") status = "proposed";
  else if (head === "consultation") status = "consultation";
  else if (head === "signed") status = "signed";
  else if (head === "advisory") status = "advisory";
  else if (head === "context") status = "context";
  return { label: raw, status, treatAsLaw: status === "enacted" };
}
