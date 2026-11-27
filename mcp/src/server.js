import { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { DISCLAIMER, YEARS } from "./content/constants.js";
import {
  classifyTransaction,
  getPageSection,
  getRatesAndAllowances,
  listIrdUpdates,
  lookupDipn,
  searchHub,
  searchQuestions,
  searchReturnBoxes,
} from "./tools.js";

const tax = z.enum([
  "Profits Tax",
  "Property Tax",
  "Salaries Tax",
  "Stamp Duty",
  "Depreciation & Allowances",
]);

const limit = z.number().int().min(1).max(20).optional();

const readOnly = {
  readOnlyHint: true,
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false,
};

function textResult(payload) {
  return {
    isError: Boolean(payload && payload.error),
    content: [{ type: "text", text: JSON.stringify(payload, null, 2) }],
  };
}

export function createTaxServer(catalog) {
  const server = new McpServer({
    name: "hktax-studyhub",
    version: "1.0.0",
    instructions: [
      "Hong Kong tax study hub for agents. Not professional advice.",
      DISCLAIMER,
      `${YEARS.currentUse} ${YEARS.examUse}`,
      "Rates are identical across those two years; only allowances differ.",
      "classify_transaction maps a keyword to taxable, deductible, dutiable, or allowance plus the section.",
      "lookup_dipn finds a DIPN, SOIPN, or EDOIPN.",
      "get_rates_and_allowances returns both years and flags proposed figures that are not law.",
      "get_page_section and search_hub retrieve study pages.",
      "list_ird_updates marks enacted, bill, and proposed. Never treat proposed or bill as law.",
      "search_return_boxes searches BIR51, BIR52, and BIR54.",
      "search_questions searches the ACCA TX-HKG practice banks.",
    ].join(" "),
  });

  server.registerTool(
    "classify_transaction",
    {
      title: "Classify transaction",
      description:
        "Classify a transaction from the Hub Transaction Checker. Returns Taxable, Non-taxable, Deductible, Non-deductible, Dutiable, No duty, or Allowance, with the ordinance section, note, and study-page URL.",
      inputSchema: z.object({
        query: z.string().describe("Keyword, transaction, or section such as 'bank deposit interest' or 's.16(1)(a)'"),
        tax: tax.optional().describe("Limit to one head of charge"),
        limit,
      }),
      annotations: readOnly,
    },
    async (args) => textResult(classifyTransaction(catalog, args)),
  );

  server.registerTool(
    "lookup_dipn",
    {
      title: "Look up DIPN",
      description:
        "Look up a DIPN, SOIPN, or EDOIPN by number or topic. status core has a Hub study page; status reference is a summary only. Summaries are paraphrases, not the IRD PDF.",
      inputSchema: z.object({
        query: z.string().describe("Number or topic, such as 'DIPN 21' or 'locality of profits'"),
        group: z.string().optional().describe("Optional group such as Profits Tax or Stamp Duty"),
        limit,
      }),
      annotations: readOnly,
    },
    async (args) => textResult(lookupDipn(catalog, args)),
  );

  server.registerTool(
    "get_rates_and_allowances",
    {
      title: "Rates and allowances",
      description:
        "Current Hong Kong tax rates and personal allowances for YA 2026/27 (current work) and YA 2025/26 (ACCA TX-HKG through December 2026). Rates match; allowances differ. Proposed allowances are included and marked treatAsLaw false — do not use them in a filing.",
      inputSchema: z.object({
        year: z.enum(["2026/27", "2025/26", "both"]).optional().describe("Which allowance column to highlight. Defaults to both. Rates are returned either way."),
      }),
      annotations: readOnly,
    },
    async (args) => textResult(getRatesAndAllowances(catalog, args)),
  );

  server.registerTool(
    "get_page_section",
    {
      title: "Get page section",
      description:
        "Retrieve one Hub study section (profits tax, property tax, salaries tax, stamp duty, depreciation allowances, return guide, IRD administration, personal assessment, computation formats, and the other core pages). Omit page to list pages. Omit section to list that page's anchors.",
      inputSchema: z.object({
        page: z.string().optional().describe("Page id, such as salaries-tax or stamp-duty"),
        section: z.string().optional().describe("Section id or heading fragment, such as allowances or s.8"),
      }),
      annotations: readOnly,
    },
    async (args) => textResult(getPageSection(catalog, args)),
  );

  server.registerTool(
    "search_hub",
    {
      title: "Search hub",
      description:
        "Search study-page text for a keyword or section reference and return a short snippet plus the page anchor. Use get_page_section to read the whole section.",
      inputSchema: z.object({
        query: z.string().describe("Words or a section reference to find"),
        page: z.string().optional().describe("Optional page id to search inside"),
        limit,
      }),
      annotations: readOnly,
    },
    async (args) => textResult(searchHub(catalog, args)),
  );

  server.registerTool(
    "list_ird_updates",
    {
      title: "IRD What's New",
      description:
        "List IRD What's New items as read into the Hub, each marked enacted, bill, proposed, or another non-law status. treatAsLaw is true only for enacted items. Proposed and bill items must not be applied as law.",
      inputSchema: z.object({
        status: z.enum(["enacted", "bill", "proposed", "consultation", "signed", "advisory", "context", "other"]).optional(),
      }),
      annotations: readOnly,
    },
    async (args) => textResult(listIrdUpdates(catalog, args)),
  );

  server.registerTool(
    "search_return_boxes",
    {
      title: "Search return boxes",
      description:
        "Search BIR51, BIR52, and BIR54 profits tax return boxes from the Hub Box Finder, including the note and the study-page link.",
      inputSchema: z.object({
        query: z.string().describe("Box topic, such as two-tiered or depreciation"),
        form: z.enum(["BIR51", "BIR52", "BIR54"]).optional(),
        limit,
      }),
      annotations: readOnly,
    },
    async (args) => textResult(searchReturnBoxes(catalog, args)),
  );

  server.registerTool(
    "search_questions",
    {
      title: "Search question banks",
      description:
        "Search the Hub's original ACCA TX-HKG practice questions. Bank A is standalone MCQs, B is OT cases, C is constructed-response prompts. Answers are study material, not a marking scheme from ACCA.",
      inputSchema: z.object({
        query: z.string().describe("Topic, section, or words from the question"),
        bank: z.enum(["A", "B", "C"]).optional(),
        limit,
      }),
      annotations: readOnly,
    },
    async (args) => textResult(searchQuestions(catalog, args)),
  );

  return server;
}
