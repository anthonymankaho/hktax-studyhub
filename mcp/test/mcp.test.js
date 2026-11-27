import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { buildCatalog } from "../src/content/build.js";
import { PUBLIC_MCP_URL } from "../src/content/constants.js";
import worker from "../src/index.js";
import {
  classifyTransaction,
  getPageSection,
  getRatesAndAllowances,
  listIrdUpdates,
  lookupDipn,
  searchHub,
  searchQuestions,
  searchReturnBoxes,
  TOOL_NAMES,
} from "../src/tools.js";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");
const skip = new Set(["question-bank.html", "question-bank-b.html"]);

function read(path) {
  return readFileSync(join(repo, path), "utf8");
}

const pages = readdirSync(join(repo, "pages"))
  .filter((file) => file.endsWith(".html") && !skip.has(file))
  .sort()
  .map((file) => ({ file, html: readFileSync(join(repo, "pages", file), "utf8") }));

const catalog = buildCatalog({
  transactionsSource: read("assets/js/transactions-data.js"),
  dipnSource: read("assets/js/dipn-index-data.js"),
  birSource: read("assets/js/bir-finder-data.js"),
  qbank: JSON.parse(read("assets/qbank.json")),
  qbankB: JSON.parse(read("assets/qbank-b.json")),
  pages,
});

const committed = JSON.parse(readFileSync(join(here, "../src/catalog.json"), "utf8"));

const CTX = { waitUntil() {}, passThroughOnException() {} };
const SECRET_ENV = {
  DASHSCOPE_API_KEY: "dashscope-secret-should-not-leak",
  DASHSCOPE_API_KEY_TEMP: "dashscope-temp-secret-should-not-leak",
  GITHUB_CLIENT_SECRET: "github-client-secret-should-not-leak",
};

function endpoint(path, host = "http://localhost") {
  return new URL(path, host);
}

function firstMismatch(actual, expected) {
  const left = JSON.stringify(actual);
  const right = JSON.stringify(expected);
  if (left === right) return "";
  let index = 0;
  const limit = Math.min(left.length, right.length);
  while (index < limit && left[index] === right[index]) index += 1;
  return `at ${index}: ${left.slice(Math.max(0, index - 50), index + 50)} != ${right.slice(Math.max(0, index - 50), index + 50)}`;
}

async function postMcp(body, { host = "http://localhost", origin } = {}) {
  const url = endpoint("/mcp", host);
  const headers = {
    Host: url.host,
    "Content-Type": "application/json",
    Accept: "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-06-18",
  };
  if (origin) headers.Origin = origin;
  const response = await worker.fetch(
    new Request(url, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    }),
    SECRET_ENV,
    CTX,
  );
  const text = await response.text();
  return { response, text, body: parseMcpBody(response, text) };
}

function parseMcpBody(response, text) {
  const type = response.headers.get("content-type") || "";
  if (!text) return null;
  if (type.includes("text/event-stream")) {
    const messages = text
      .split("\n")
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trim())
      .filter(Boolean)
      .map((line) => JSON.parse(line));
    return messages.at(-1) ?? null;
  }
  return JSON.parse(text);
}

function toolPayload(message) {
  const text = message?.result?.content?.find((item) => item.type === "text")?.text;
  assert.ok(text, `expected tool text, got ${JSON.stringify(message)}`);
  return JSON.parse(text);
}

describe("catalog matches the hub sources", () => {
  it("committed catalog.json is the build of the current pages and data files", () => {
    const mismatch = firstMismatch(catalog, committed);
    assert.equal(mismatch, "", mismatch);
  });

  it("covers the core pages, the DIPN index, and both question banks", () => {
    for (const id of ["profits-tax", "property-tax", "salaries-tax", "stamp-duty", "depreciation-allowances", "personal-assessment", "ird-administration", "computation-formats", "profits-tax-return-guide"]) {
      assert.ok(catalog.pages.some((page) => page.id === id), id);
    }
    assert.equal(catalog.dipn.length, 73);
    assert.equal(catalog.questions.filter((row) => row.bank === "A").length, 282);
    assert.equal(catalog.questions.filter((row) => row.bank === "B").length, 30);
    assert.ok(catalog.questions.filter((row) => row.bank === "C").length >= 8);
  });
});

describe("tools against hub data", () => {
  it("classifies bank-deposit interest as non-taxable and corporate HK interest as taxable", () => {
    const source = read("assets/js/transactions-data.js");
    assert.match(source, /Interest on a Hong Kong bank deposit/);
    assert.match(source, /s\.15\(1\)\(f\)/);

    const deposit = classifyTransaction(catalog, { query: "Hong Kong bank deposit interest", tax: "Profits Tax" });
    assert.equal(deposit.matches[0].status, "nontaxable");
    assert.match(deposit.matches[0].section, /Interest Income/);
    assert.match(deposit.matches[0].url, /^https:\/\/anthonymanhk\.github\.io\/hktax-studyhub\/pages\//);

    const corporate = classifyTransaction(catalog, { query: "s.15(1)(f)" });
    assert.equal(corporate.matches[0].status, "taxable");
    assert.equal(corporate.matches[0].section, "s.15(1)(f)");
    assert.match(deposit.disclaimer, /not professional advice/);
    assert.match(deposit.disclaimer, /Cap\. 112/);
  });

  it("looks up DIPN 21 and a stamp-duty SOIPN", () => {
    const dipn = lookupDipn(catalog, { query: "DIPN 21" });
    assert.equal(dipn.matches[0].no, "DIPN 21");
    assert.match(dipn.matches[0].title, /Locality of Profits/);
    assert.equal(dipn.matches[0].status, "core");

    const soipn = lookupDipn(catalog, { query: "SOIPN 8" });
    assert.equal(soipn.matches[0].no, "SOIPN 8");
    assert.equal(soipn.matches[0].group, "Stamp Duty");
  });

  it("returns both allowance years and refuses to treat the proposed child allowance as law", () => {
    const salaries = read("pages/salaries-tax.html");
    assert.match(salaries, /145,000/);
    assert.match(salaries, /132,000/);
    assert.match(salaries, /160,000/);
    assert.match(salaries, /2025\/26 and continuing into 2026\/27/);

    const rates = getRatesAndAllowances(catalog, { year: "both" });
    assert.equal(rates.years.ratesIdentical, true);
    assert.equal(rates.years.allowancesDiffer, true);
    assert.equal(rates.years.current, "2026/27");
    assert.equal(rates.years.exam, "2025/26");

    const basic = rates.allowances.find((row) => row.name === "Basic allowance");
    assert.equal(basic["2026/27"], "145,000");
    assert.equal(basic["2025/26"], "132,000");
    assert.equal(basic.treatAsLaw, true);

    const enactedChild = rates.allowances.find((row) => row.name.startsWith("Child allowance (1st"));
    assert.match(enactedChild["2026/27"], /140,000/);
    assert.equal(enactedChild.treatAsLaw, true);

    const proposed = rates.allowances.find((row) => row.legalStatus === "proposed");
    assert.match(proposed["2026/27"], /160,000/);
    assert.equal(proposed.treatAsLaw, false);
    assert.equal(rates.profitsTax.rows[0][0], "Corporations");
    assert.equal(rates.profitsTax.rows[0][1], "8.25%");
    assert.equal(rates.profitsTax.rows[0][2], "16.5%");
    assert.equal(rates.profitsTax.rows[1][1], "7.5%");
    assert.equal(rates.profitsTax.rows[1][2], "15%");
    assert.match(rates.propertyTax.text, /15%/);
    assert.match(rates.depreciation.plantAndMachinery.text, /60%/);
    assert.match(rates.stampDuty.stock.text, /0\.2%/);
    assert.ok(rates.notLaw.every((row) => row.treatAsLaw === false));
  });

  it("retrieves a core section and a computation format", () => {
    const section = getPageSection(catalog, { page: "salaries-tax", section: "allowances" });
    assert.equal(section.section.id, "allowances");
    assert.match(section.section.text, /145,000/);
    assert.match(section.section.text, /132,000/);
    assert.match(section.section.url, /salaries-tax\.html#allowances$/);

    const formats = getPageSection(catalog, { page: "computation-formats", section: "property" });
    assert.match(formats.section.heading, /Property Tax/);
    const admin = searchHub(catalog, { query: "objection", page: "ird-administration" });
    assert.ok(admin.matches.length > 0);
    assert.equal(admin.matches[0].page, "ird-administration");
  });

  it("marks proposed and bill IRD items as not law", () => {
    const source = read("pages/ird-updates.html");
    assert.match(source, /not<\/strong> law/);
    const updates = listIrdUpdates(catalog, {});
    const proposed = updates.updates.filter((row) => row.legalStatus === "proposed");
    assert.ok(proposed.some((row) => /160,000/.test(row.item)));
    assert.ok(proposed.every((row) => row.treatAsLaw === false));
    const bill = updates.updates.find((row) => /No\. 3/.test(row.item));
    assert.equal(bill.legalStatus, "bill");
    assert.equal(bill.treatAsLaw, false);
    const enacted = updates.updates.find((row) => /No\. 2/.test(row.item));
    assert.equal(enacted.legalStatus, "enacted");
    assert.equal(enacted.treatAsLaw, true);
    for (const row of updates.updates) {
      if (row.legalStatus !== "enacted") assert.equal(row.treatAsLaw, false);
    }
    const onlyProposed = listIrdUpdates(catalog, { status: "proposed" });
    assert.ok(onlyProposed.updates.every((row) => row.legalStatus === "proposed"));
  });

  it("finds the two-tiered profits tax return box and a section A question", () => {
    const boxes = searchReturnBoxes(catalog, { query: "two-tiered", form: "BIR51" });
    assert.equal(boxes.matches[0].box, "4");
    assert.match(boxes.matches[0].label, /two-tiered/i);

    const questions = searchQuestions(catalog, { query: "s.51(2)", bank: "A" });
    assert.equal(questions.matches[0].id, "Q001");
    assert.match(questions.matches[0].ref, /s\.51\(2\)/);
    assert.match(questions.matches[0].answer, /4 months/);
  });
});

describe("streamable HTTP MCP", () => {
  it("serves a discovery document and does not require auth", async () => {
    const home = endpoint("/");
    const response = await worker.fetch(new Request(home, { method: "GET", headers: { Host: home.host } }), SECRET_ENV, CTX);
    assert.equal(response.status, 200);
    const body = await response.json();
    assert.equal(body.auth.required, false);
    assert.deepEqual(body.auth.headers, []);
    assert.equal(body.transport, "streamable-http");
    assert.equal(body.documentedUrl, PUBLIC_MCP_URL);
    assert.deepEqual(body.tools, TOOL_NAMES);
    assert.match(body.disclaimer, /not professional advice/);
    assert.equal(body.mcp, "http://localhost/mcp");
  });

  it("lists the tools and classifies a real transaction over JSON-RPC", async () => {
    const listed = await postMcp({ jsonrpc: "2.0", id: 1, method: "tools/list" });
    assert.equal(listed.response.status, 200);
    const names = listed.body.result.tools.map((tool) => tool.name).sort();
    assert.deepEqual(names, [...TOOL_NAMES].sort());

    const called = await postMcp({
      jsonrpc: "2.0",
      id: 2,
      method: "tools/call",
      params: { name: "classify_transaction", arguments: { query: "s.15(1)(f)" } },
    });
    assert.equal(called.response.status, 200);
    const payload = toolPayload(called.body);
    assert.equal(payload.matches[0].section, "s.15(1)(f)");
    assert.equal(payload.matches[0].status, "taxable");
    assert.equal(called.body.result.isError, false);
  });

  it("returns DIPN 21, dual-year allowances, and a proposed item that is not law", async () => {
    const dipn = await postMcp({
      jsonrpc: "2.0",
      id: 3,
      method: "tools/call",
      params: { name: "lookup_dipn", arguments: { query: "locality of profits" } },
    });
    assert.equal(toolPayload(dipn.body).matches[0].no, "DIPN 21");

    const rates = await postMcp({
      jsonrpc: "2.0",
      id: 4,
      method: "tools/call",
      params: { name: "get_rates_and_allowances", arguments: { year: "2025/26" } },
    });
    const ratesBody = toolPayload(rates.body);
    const basic = ratesBody.allowances.find((row) => row.name === "Basic allowance");
    assert.equal(basic.amount, "132,000");
    assert.equal(basic["2026/27"], "145,000");
    const proposed = ratesBody.allowances.find((row) => row.legalStatus === "proposed");
    assert.equal(proposed.treatAsLaw, false);

    const updates = await postMcp({
      jsonrpc: "2.0",
      id: 5,
      method: "tools/call",
      params: { name: "list_ird_updates", arguments: { status: "proposed" } },
    });
    const updateBody = toolPayload(updates.body);
    assert.ok(updateBody.updates.length >= 2);
    assert.ok(updateBody.updates.every((row) => row.treatAsLaw === false));
  });

  it("retrieves a salaries-tax section on the workers.dev host with no Origin", async () => {
    const called = await postMcp(
      {
        jsonrpc: "2.0",
        id: 6,
        method: "tools/call",
        params: { name: "get_page_section", arguments: { page: "stamp-duty", section: "shares" } },
      },
      { host: "https://hktax-studyhub-mcp.anthonym-354.workers.dev" },
    );
    assert.equal(called.response.status, 200);
    const payload = toolPayload(called.body);
    assert.match(payload.section.text, /0\.2%/);
    assert.match(payload.section.url, /stamp-duty\.html#shares$/);
  });

  it("does not echo Worker secrets and rejects a foreign browser Origin", async () => {
    const called = await postMcp({ jsonrpc: "2.0", id: 7, method: "tools/list" });
    for (const secret of Object.values(SECRET_ENV)) {
      assert.equal(called.text.includes(secret), false);
    }
    const blocked = await postMcp(
      { jsonrpc: "2.0", id: 8, method: "tools/list" },
      { origin: "https://evil.example" },
    );
    assert.equal(blocked.response.status, 403);
    assert.match(blocked.text, /Invalid Origin/);
    assert.equal(blocked.text.includes(SECRET_ENV.GITHUB_CLIENT_SECRET), false);
  });

  it("answers initialize and leaves session deletion unsupported", async () => {
    const init = await postMcp({
      jsonrpc: "2.0",
      id: 9,
      method: "initialize",
      params: {
        protocolVersion: "2025-06-18",
        capabilities: {},
        clientInfo: { name: "hktax-test", version: "1.0.0" },
      },
    });
    assert.equal(init.response.status, 200);
    assert.equal(init.body.result.serverInfo.name, "hktax-studyhub");
    assert.ok(init.body.result.protocolVersion);

    const missingUrl = endpoint("/nope");
    const missing = await worker.fetch(
      new Request(missingUrl, { headers: { Host: missingUrl.host } }),
      SECRET_ENV,
      CTX,
    );
    assert.equal(missing.status, 404);
    const sseUrl = endpoint("/mcp");
    const sse = await worker.fetch(
      new Request(sseUrl, { method: "GET", headers: { Host: sseUrl.host } }),
      SECRET_ENV,
      CTX,
    );
    assert.equal(sse.status, 405);
  });
});
