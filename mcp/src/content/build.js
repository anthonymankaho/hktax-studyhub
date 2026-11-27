import vm from "node:vm";
import {
  classifyLegalStatus,
  hubUrl,
  inlineText,
  pageUrl,
  parseSections,
  parseTables,
  parseTitle,
  sectionHtml,
} from "./html.js";
import { DISCLAIMER, PAGE_GROUPS, REQUIRED_PAGES, STATUS_LABEL, YEARS } from "./constants.js";

function parseWindowArray(source, name) {
  const sandbox = { window: {} };
  vm.runInNewContext(source, sandbox, { timeout: 1000 });
  const value = sandbox.window[name];
  if (!Array.isArray(value)) throw new Error(`window.${name} is not an array`);
  return value;
}

function requireText(text, needle, what) {
  if (!String(text).includes(needle)) {
    throw new Error(`catalog: ${what} is missing ${JSON.stringify(needle)}`);
  }
}

function sectionById(html, id) {
  const inner = sectionHtml(html, id);
  if (inner == null) throw new Error(`catalog: missing section #${id}`);
  const sections = parseSections(`<section class="block" id="${id}">${inner}</section>`);
  return { id, html: inner, ...sections[0] };
}

function tableHeader(table) {
  const header = table.rows.find((row) => row.length && row.every((cell) => cell.header));
  return header ? header.map((cell) => cell.text) : [];
}

function tableBody(table) {
  return table.rows
    .filter((row) => row.some((cell) => !cell.header))
    .map((row) => row.map((cell) => cell.text));
}

function parseAllowances(salariesHtml) {
  const section = sectionById(salariesHtml, "allowances");
  const tables = parseTables(section.html);
  const table = tables[0];
  if (!table) throw new Error("catalog: salaries allowance table missing");
  const allowances = [];
  for (const row of table.rows) {
    if (!row.length || /^allowance$/i.test(row[0].text)) continue;
    const proposed = /proposed/i.test(row[0].html) || /proposed/i.test(row[0].text);
    const legal = proposed
      ? { label: "Proposed", status: "proposed", treatAsLaw: false }
      : { label: "Enacted", status: "enacted", treatAsLaw: true };
    allowances.push({
      name: row[0].text.replace(/\s+proposed$/i, ""),
      "2026/27": row[1] ? row[1].text : null,
      "2025/26": row[2] ? row[2].text : null,
      legalStatus: legal.status,
      treatAsLaw: legal.treatAsLaw,
    });
  }
  const basic = allowances.find((row) => row.name === "Basic allowance");
  if (!basic || basic["2026/27"] !== "145,000" || basic["2025/26"] !== "132,000" || !basic.treatAsLaw) {
    throw new Error("catalog: basic allowance table did not match the hub's dual-year figures");
  }
  const proposedChild = allowances.find((row) => row.legalStatus === "proposed");
  if (!proposedChild || proposedChild.treatAsLaw || !String(proposedChild["2026/27"]).includes("160,000")) {
    throw new Error("catalog: proposed child allowance must stay marked as not law");
  }
  return { caption: table.caption, rows: allowances, text: section.text };
}

function parseIrdUpdates(html) {
  const section = sectionById(html, "acted");
  const tables = parseTables(section.html);
  const table = tables[0];
  if (!table) throw new Error("catalog: IRD What's New summary table missing");
  const updates = [];
  for (const row of table.rows) {
    if (row.length < 3 || /^(ird date|date)$/i.test(row[0].text)) continue;
    const statusCell = row[2];
    const tag = statusCell.html.match(/<span\b[^>]*>([\s\S]*?)<\/span>/i);
    const legal = classifyLegalStatus(tag ? inlineText(tag[1]) : statusCell.text);
    const link = row[3] ? row[3].html.match(/href="([^"]+)"/i) : null;
    updates.push({
      date: row[0].text,
      item: row[1].text,
      legalStatus: legal.status,
      statusLabel: legal.label,
      treatAsLaw: legal.treatAsLaw,
      page: row[3] ? row[3].text : null,
      url: link ? hubUrl(link[1]) : null,
    });
  }
  if (!updates.some((row) => row.legalStatus === "proposed" && row.treatAsLaw === false)) {
    throw new Error("catalog: IRD updates have no proposed item marked as not law");
  }
  if (!updates.some((row) => row.legalStatus === "bill" && row.treatAsLaw === false)) {
    throw new Error("catalog: IRD updates have no bill marked as not law");
  }
  if (updates.some((row) => row.legalStatus !== "enacted" && row.treatAsLaw)) {
    throw new Error("catalog: a non-enacted IRD item was marked as law");
  }
  return updates;
}

function headlineRates(pagesById) {
  const profits = sectionById(pagesById["profits-tax"], "rates");
  const salaries = sectionById(pagesById["salaries-tax"], "rates");
  const property = sectionById(pagesById["property-tax"], "overview");
  const shares = sectionById(pagesById["stamp-duty"], "shares");
  const avd = sectionById(pagesById["stamp-duty"], "property");
  const bsd = sectionById(pagesById["stamp-duty"], "bsd-ssd");
  const leases = sectionById(pagesById["stamp-duty"], "leases");
  const buildings = sectionById(pagesById["depreciation-allowances"], "buildings");
  const plant = sectionById(pagesById["depreciation-allowances"], "pm");

  requireText(salaries.text, "2025/26 and continuing into 2026/27", "salaries rate caption");
  requireText(profits.text, "8.25%", "profits tax corporate first tier");
  requireText(profits.text, "16.5%", "profits tax corporate remainder");
  requireText(profits.text, "7.5%", "profits tax unincorporated first tier");
  requireText(profits.text, "15%", "profits tax unincorporated remainder");
  requireText(profits.text, "2,000,000", "profits tax two-tier threshold");
  requireText(salaries.text, "2%", "salaries first band");
  requireText(salaries.text, "17%", "salaries top band");
  requireText(salaries.text, "15%", "salaries standard rate");
  requireText(salaries.text, "16%", "salaries standard rate above 5,000,000");
  requireText(property.text, "15%", "property tax standard rate");
  requireText(shares.text, "0.2%", "stamp duty on stock");
  requireText(bsd.text, "0%", "BSD/SSD rate");
  requireText(buildings.text, "20%", "industrial building initial allowance");
  requireText(buildings.text, "4%", "building annual allowance");
  requireText(plant.text, "60%", "plant initial allowance");
  requireText(plant.text, "10%", "10% pool");
  requireText(plant.text, "20%", "20% pool");
  requireText(plant.text, "30%", "30% pool");

  const profitsTable = parseTables(profits.html)[0];
  const salariesTable = parseTables(salaries.html)[0];
  const propertyTable = parseTables(property.html)[0];

  return {
    years: YEARS,
    basisNote:
      "Rates are the same on YA 2026/27 and YA 2025/26. Only personal allowances differ. The salaries-tax rate caption in the Hub says the progressive bands apply for 2025/26 and continue into the 2026/27 basis.",
    profitsTax: {
      source: pageUrl("profits-tax.html", "rates"),
      caption: profitsTable ? profitsTable.caption : "",
      header: profitsTable ? tableHeader(profitsTable) : [],
      rows: profitsTable ? tableBody(profitsTable) : [],
      text: profits.text,
    },
    salariesTax: {
      source: pageUrl("salaries-tax.html", "rates"),
      caption: salariesTable ? salariesTable.caption : "",
      header: salariesTable ? tableHeader(salariesTable) : [],
      bands: salariesTable ? tableBody(salariesTable) : [],
      text: salaries.text,
    },
    propertyTax: {
      source: pageUrl("property-tax.html", "overview"),
      caption: propertyTable ? propertyTable.caption : "",
      header: propertyTable ? tableHeader(propertyTable) : [],
      rows: propertyTable ? tableBody(propertyTable) : [],
      repairsAllowance: "20% statutory allowance for repairs and outgoings (s.5(1A)(b))",
      text: property.text,
    },
    stampDuty: {
      stock: { source: pageUrl("stamp-duty.html", "shares"), text: shares.text },
      property: { source: pageUrl("stamp-duty.html", "property"), text: avd.text },
      buyersAndSpecial: { source: pageUrl("stamp-duty.html", "bsd-ssd"), text: bsd.text },
      leases: { source: pageUrl("stamp-duty.html", "leases"), text: leases.text },
    },
    depreciation: {
      buildings: { source: pageUrl("depreciation-allowances.html", "buildings"), text: buildings.text },
      plantAndMachinery: { source: pageUrl("depreciation-allowances.html", "pm"), text: plant.text },
    },
  };
}

function stripQuestion(value) {
  return inlineText(value == null ? "" : String(value));
}

function questionsFromBanks(qbank, qbankB, sectionCPage) {
  const questions = [];
  for (const question of qbank.questions || []) {
    const options = (question.options || []).map(stripQuestion);
    questions.push({
      bank: "A",
      id: question.id,
      area: question.area_name || question.area || "",
      topic: question.topic || "",
      difficulty: question.difficulty || "",
      question: stripQuestion(question.q),
      options,
      answerIndex: question.answer,
      answer: options[question.answer] || "",
      explain: stripQuestion(question.explain),
      ref: question.ref || "",
    });
  }
  for (const item of qbankB.cases || []) {
    for (const question of item.questions || []) {
      const options = (question.options || []).map(stripQuestion);
      questions.push({
        bank: "B",
        id: question.id,
        caseId: item.id,
        caseLabel: item.label,
        scenario: stripQuestion(item.scenario),
        topic: question.topic || "",
        question: stripQuestion(question.q),
        options,
        answerIndex: question.answer,
        answer: options[question.answer] || "",
        explain: stripQuestion(question.explain),
        ref: question.ref || "",
      });
    }
  }
  if (sectionCPage) {
    for (const section of sectionCPage.sections) {
      const match = section.heading.match(/^Question\s+(\d+)/i);
      if (!match) continue;
      questions.push({
        bank: "C",
        id: `C${match[1]}`,
        topic: section.heading,
        question: section.text.slice(0, 1200),
        ref: "",
        page: sectionCPage.id,
        section: section.id,
        url: pageUrl(sectionCPage.file, section.id),
      });
    }
  }
  return questions;
}

/**
 * Build the MCP catalog from hub source strings. Throws if a figure the tools
 * promise to return is no longer in the page, so a stale allowance cannot ship.
 */
export function buildCatalog({ transactionsSource, dipnSource, birSource, qbank, qbankB, pages }) {
  const transactions = parseWindowArray(transactionsSource, "TRANSACTIONS").map((row) => {
    if (!STATUS_LABEL[row.status]) throw new Error(`catalog: unknown transaction status ${row.status}`);
    return {
      tax: row.tax,
      item: row.item,
      status: row.status,
      statusLabel: STATUS_LABEL[row.status],
      section: row.section,
      note: row.note || "",
      page: row.page || null,
      url: row.page ? hubUrl(row.page) : null,
    };
  });

  const dipn = parseWindowArray(dipnSource, "DIPN_INDEX").map((row) => ({
    no: row.no,
    title: row.title,
    group: row.group,
    date: row.date,
    status: row.status,
    example: Boolean(row.example),
    summary: row.summary,
    page: row.link || null,
    url: row.link ? hubUrl(row.link) : null,
  }));

  const boxes = parseWindowArray(birSource, "BIR_BOXES").map((row) => ({
    form: row.form,
    part: row.part,
    box: String(row.box),
    label: row.label,
    note: row.note || "",
    page: row.link || null,
    url: row.link ? hubUrl(row.link) : null,
  }));

  const builtPages = pages.map(({ file, html }) => {
    const id = file.replace(/\.html$/, "");
    return {
      id,
      file,
      title: parseTitle(html),
      group: PAGE_GROUPS[id] || "Other",
      url: pageUrl(file),
      sections: parseSections(html).map((section) => ({
        id: section.id,
        heading: section.heading,
        text: section.text,
        url: pageUrl(file, section.id),
      })),
    };
  });

  const pagesByFile = Object.fromEntries(pages.map((page) => [page.file, page.html]));
  for (const id of REQUIRED_PAGES) {
    if (!builtPages.some((page) => page.id === id)) throw new Error(`catalog: missing page ${id}`);
  }

  const allowances = parseAllowances(pagesByFile["salaries-tax.html"]);
  const rates = headlineRates({
    "profits-tax": pagesByFile["profits-tax.html"],
    "salaries-tax": pagesByFile["salaries-tax.html"],
    "property-tax": pagesByFile["property-tax.html"],
    "stamp-duty": pagesByFile["stamp-duty.html"],
    "depreciation-allowances": pagesByFile["depreciation-allowances.html"],
  });
  rates.allowances = allowances;
  rates.allowanceSource = pageUrl("salaries-tax.html", "allowances");

  const irdUpdates = parseIrdUpdates(pagesByFile["ird-updates.html"]);
  const sectionC = builtPages.find((page) => page.id === "question-bank-c");

  return {
    disclaimer: DISCLAIMER,
    site: "https://anthonymanhk.github.io/hktax-studyhub/",
    years: YEARS,
    pages: builtPages,
    transactions,
    dipn,
    boxes,
    questions: questionsFromBanks(qbank, qbankB, sectionC),
    irdUpdates,
    rates,
  };
}
