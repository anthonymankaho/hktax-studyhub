import { DISCLAIMER, YEARS } from "./content/constants.js";

const MAX_LIMIT = 20;
const SECTION_CAP = 12000;

function clampLimit(value, fallback = 8) {
  const number = Number(value);
  if (!Number.isInteger(number)) return fallback;
  return Math.min(MAX_LIMIT, Math.max(1, number));
}

function queryText(value) {
  if (typeof value !== "string") return "";
  return value.trim().slice(0, 300);
}

function tokens(query) {
  return query
    .toLowerCase()
    .split(/[^a-z0-9.%]+/i)
    .filter((token) => token.length > 1);
}

function fieldScore(query, fields) {
  const q = query.toLowerCase();
  const parts = tokens(query);
  let score = 0;
  for (const field of fields) {
    const hay = String(field.text || "").toLowerCase();
    if (!hay) continue;
    if (hay.includes(q)) score += 100 * field.weight;
    for (const token of parts) {
      if (hay.includes(token)) score += 8 * field.weight;
    }
  }
  return score;
}

function rank(items, query, fieldsOf, limit) {
  const scored = [];
  for (let index = 0; index < items.length; index++) {
    const score = fieldScore(query, fieldsOf(items[index]));
    if (score > 0) scored.push({ item: items[index], score, index });
  }
  scored.sort((a, b) => b.score - a.score || a.index - b.index);
  return scored.slice(0, limit).map((row) => row.item);
}

function envelope(payload) {
  return { disclaimer: DISCLAIMER, years: YEARS, ...payload };
}

function clip(text, cap = SECTION_CAP) {
  const value = String(text || "");
  if (value.length <= cap) return { text: value, truncated: false };
  return { text: `${value.slice(0, cap)}\n…[truncated — call get_page_section for this anchor]`, truncated: true };
}

function findPage(catalog, page) {
  const id = queryText(page).replace(/\.html$/, "");
  if (!id) return null;
  return catalog.pages.find((item) => item.id === id) || null;
}

export function classifyTransaction(catalog, args = {}) {
  const query = queryText(args.query);
  if (!query) return { error: "query is required" };
  let rows = catalog.transactions;
  if (args.tax) rows = rows.filter((row) => row.tax === args.tax);
  const matches = rank(
    rows,
    query,
    (row) => [
      { text: row.item, weight: 3 },
      { text: row.section, weight: 3 },
      { text: row.tax, weight: 1 },
      { text: row.note, weight: 1 },
      { text: row.statusLabel, weight: 1 },
    ],
    clampLimit(args.limit),
  );
  return envelope({
    tool: "classify_transaction",
    query,
    tax: args.tax || null,
    count: matches.length,
    matches,
  });
}

export function lookupDipn(catalog, args = {}) {
  const query = queryText(args.query);
  if (!query) return { error: "query is required" };
  let rows = catalog.dipn;
  if (args.group) {
    const group = queryText(args.group).toLowerCase();
    rows = rows.filter((row) => row.group.toLowerCase().includes(group));
  }
  const number = query.match(/^(?:dipn|soipn|edoipn)?\s*#?\s*(\d+[a-z]?)$/i);
  const matches = rank(
    rows,
    query,
    (row) => {
      const exact = number && row.no.toLowerCase().endsWith(number[1].toLowerCase()) && row.no.match(/\d+[a-z]?/i)?.[0].toLowerCase() === number[1].toLowerCase();
      return [
        { text: exact ? query : "", weight: 20 },
        { text: row.no, weight: 4 },
        { text: row.title, weight: 3 },
        { text: row.summary, weight: 1 },
        { text: row.group, weight: 1 },
      ];
    },
    clampLimit(args.limit),
  );
  return envelope({
    tool: "lookup_dipn",
    query,
    count: matches.length,
    note: "status core means the Hub has a study page. status reference means the note is summarized only. Summaries are paraphrases, not the IRD text.",
    matches,
  });
}

export function getRatesAndAllowances(catalog, args = {}) {
  const year = args.year && args.year !== "both" ? args.year : "both";
  if (year !== "both" && year !== YEARS.current && year !== YEARS.exam) {
    return { error: `year must be ${YEARS.current}, ${YEARS.exam}, or both` };
  }
  const rates = catalog.rates;
  const allowances = rates.allowances.rows.map((row) => ({
    ...row,
    amount: year === "both" ? null : row[year],
    enactedForFiling: row.treatAsLaw,
  }));
  return envelope({
    tool: "get_rates_and_allowances",
    showing: year,
    basisNote: rates.basisNote,
    allowanceSource: rates.allowanceSource,
    allowanceCaption: rates.allowances.caption,
    allowances,
    profitsTax: { source: rates.profitsTax.source, caption: rates.profitsTax.caption, rows: rates.profitsTax.rows, ...clip(rates.profitsTax.text, 8000) },
    salariesTax: { source: rates.salariesTax.source, caption: rates.salariesTax.caption, bands: rates.salariesTax.bands, ...clip(rates.salariesTax.text, 8000) },
    propertyTax: {
      source: rates.propertyTax.source,
      caption: rates.propertyTax.caption,
      rows: rates.propertyTax.rows,
      repairsAllowance: rates.propertyTax.repairsAllowance,
      ...clip(rates.propertyTax.text, 4000),
    },
    stampDuty: {
      stock: { source: rates.stampDuty.stock.source, ...clip(rates.stampDuty.stock.text, 4000) },
      property: { source: rates.stampDuty.property.source, ...clip(rates.stampDuty.property.text, 8000) },
      buyersAndSpecial: { source: rates.stampDuty.buyersAndSpecial.source, ...clip(rates.stampDuty.buyersAndSpecial.text, 4000) },
      leases: { source: rates.stampDuty.leases.source, ...clip(rates.stampDuty.leases.text, 4000) },
    },
    depreciation: {
      buildings: { source: rates.depreciation.buildings.source, ...clip(rates.depreciation.buildings.text, 5000) },
      plantAndMachinery: { source: rates.depreciation.plantAndMachinery.source, ...clip(rates.depreciation.plantAndMachinery.text, 5000) },
    },
    notLaw: catalog.irdUpdates.filter((row) => !row.treatAsLaw),
  });
}

export function getPageSection(catalog, args = {}) {
  const pageId = queryText(args.page);
  if (!pageId) {
    return envelope({
      tool: "get_page_section",
      pages: catalog.pages.map((page) => ({
        id: page.id,
        title: page.title,
        group: page.group,
        url: page.url,
        sections: page.sections.map((section) => ({ id: section.id, heading: section.heading })),
      })),
    });
  }
  const page = findPage(catalog, pageId);
  if (!page) {
    return { error: `Unknown page ${pageId}`, pages: catalog.pages.map((item) => item.id) };
  }
  const sectionQuery = queryText(args.section);
  if (!sectionQuery) {
    return envelope({
      tool: "get_page_section",
      page: { id: page.id, title: page.title, group: page.group, url: page.url },
      sections: page.sections.map((section) => ({ id: section.id, heading: section.heading, url: section.url })),
    });
  }
  const wanted = sectionQuery.replace(/^#/, "").toLowerCase();
  const exact = page.sections.find((section) => section.id.toLowerCase() === wanted);
  const matches = exact
    ? [exact]
    : rank(
        page.sections,
        sectionQuery,
        (section) => [
          { text: section.id, weight: 3 },
          { text: section.heading, weight: 2 },
        ],
        3,
      );
  if (!matches.length) {
    return { error: `No section matching ${sectionQuery} on ${page.id}`, sections: page.sections.map((section) => section.id) };
  }
  const section = matches[0];
  return envelope({
    tool: "get_page_section",
    page: { id: page.id, title: page.title, url: page.url },
    section: {
      id: section.id,
      heading: section.heading,
      url: section.url,
      ...clip(section.text),
    },
    alsoMatched: matches.slice(1).map((item) => ({ id: item.id, heading: item.heading })),
  });
}

export function searchHub(catalog, args = {}) {
  const query = queryText(args.query);
  if (!query) return { error: "query is required" };
  let pages = catalog.pages;
  if (args.page) {
    const page = findPage(catalog, args.page);
    if (!page) return { error: `Unknown page ${args.page}` };
    pages = [page];
  }
  const hits = [];
  for (const page of pages) {
    for (const section of page.sections) {
      const score = fieldScore(query, [
        { text: section.heading, weight: 3 },
        { text: section.text, weight: 1 },
        { text: page.title, weight: 1 },
      ]);
      if (score > 0) hits.push({ page, section, score });
    }
  }
  hits.sort((a, b) => b.score - a.score);
  const matches = hits.slice(0, clampLimit(args.limit, 6)).map(({ page, section }) => ({
    page: page.id,
    title: page.title,
    section: section.id,
    heading: section.heading,
    url: section.url,
    ...clip(snippet(section.text, query), 900),
  }));
  return envelope({ tool: "search_hub", query, count: matches.length, matches });
}

function snippet(text, query) {
  const hay = String(text || "");
  const at = hay.toLowerCase().indexOf(query.toLowerCase());
  const radius = 280;
  if (at < 0) return hay.slice(0, radius * 2);
  const start = Math.max(0, at - radius);
  const end = Math.min(hay.length, at + query.length + radius);
  return `${start > 0 ? "…" : ""}${hay.slice(start, end)}${end < hay.length ? "…" : ""}`;
}

export function listIrdUpdates(catalog, args = {}) {
  let rows = catalog.irdUpdates;
  if (args.status) rows = rows.filter((row) => row.legalStatus === args.status);
  return envelope({
    tool: "list_ird_updates",
    rule: "treatAsLaw is true only for enacted items. Proposed, bill, consultation, signed, and advisory items are not law. Do not apply them.",
    count: rows.length,
    updates: rows,
  });
}

export function searchReturnBoxes(catalog, args = {}) {
  const query = queryText(args.query);
  if (!query) return { error: "query is required" };
  let rows = catalog.boxes;
  if (args.form) rows = rows.filter((row) => row.form === args.form);
  const matches = rank(
    rows,
    query,
    (row) => [
      { text: row.label, weight: 3 },
      { text: row.box, weight: 2 },
      { text: row.note, weight: 2 },
      { text: row.part, weight: 1 },
      { text: row.form, weight: 1 },
    ],
    clampLimit(args.limit),
  );
  return envelope({
    tool: "search_return_boxes",
    query,
    form: args.form || null,
    count: matches.length,
    matches,
  });
}

export function searchQuestions(catalog, args = {}) {
  const query = queryText(args.query);
  if (!query) return { error: "query is required" };
  let rows = catalog.questions;
  if (args.bank) rows = rows.filter((row) => row.bank === args.bank);
  const matches = rank(
    rows,
    query,
    (row) => [
      { text: row.question, weight: 3 },
      { text: row.topic, weight: 2 },
      { text: row.ref, weight: 3 },
      { text: row.explain, weight: 1 },
      { text: row.scenario, weight: 1 },
      { text: row.area, weight: 1 },
    ],
    clampLimit(args.limit, 5),
  ).map((row) => ({
    ...row,
    explain: row.explain ? clip(row.explain, 800).text : undefined,
    scenario: row.scenario ? clip(row.scenario, 600).text : undefined,
    question: clip(row.question, 1200).text,
  }));
  return envelope({
    tool: "search_questions",
    query,
    bank: args.bank || null,
    count: matches.length,
    note: "Original ACCA TX-HKG practice questions written for this Hub. They are not past-paper reproductions.",
    matches,
  });
}

export const TOOL_NAMES = [
  "classify_transaction",
  "lookup_dipn",
  "get_rates_and_allowances",
  "get_page_section",
  "search_hub",
  "list_ird_updates",
  "search_return_boxes",
  "search_questions",
];
