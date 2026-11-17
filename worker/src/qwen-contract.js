// Shared by the Worker and Node tests. No credentials or provider configuration.
// Browser payloads are re-validated here; never trust client-supplied limits.

export const LIMITS = Object.freeze({
  MAX_MESSAGE_CHARS: 4000,
  MAX_HISTORY_TURNS: 12,
  MAX_HISTORY_CHARS: 12000,
  MAX_HISTORY_TURN_CHARS: 2000,
  MAX_TITLE_CHARS: 200,
  MAX_SECTION_CHARS: 128,
  MAX_EXCERPT_CHARS: 8000,
  MAX_REPLY_CHARS: 8000,
  MAX_REQUEST_BYTES: 120000,
  MAX_TOKENS: 4096,
  INPUT_TOKEN_LIMIT: 16000,
  DEFAULT_MONTHLY_TOKEN_QUOTA: 20_000_000,
  DEFAULT_TEMP_MONTHLY_TOKEN_QUOTA: 2_000_000,
});

export const YEAR_BASES = Object.freeze(["2026/27", "2025/26"]);

// "main" is the primary Token Plan key; "temp" is the small-quota spare key.
// The browser picks one; the Worker resolves endpoint, model and secret.
export const API_IDS = Object.freeze(["main", "temp"]);

export const HUB_INDEX = Object.freeze([
  { id: "MAIN", title: "Home", titleZh: "主頁" },
  { id: "ird-updates", title: "IRD What's New", titleZh: "稅務局最新消息" },
  { id: "acca-tx-hkg", title: "ACCA TX-HKG", titleZh: "ACCA TX-HKG 考試" },
  { id: "question-bank", title: "Question Bank A", titleZh: "題庫 A" },
  { id: "question-bank-b", title: "Question Bank B", titleZh: "題庫 B" },
  { id: "question-bank-c", title: "Question Bank C", titleZh: "題庫 C" },
  { id: "computation-formats", title: "Computation Formats", titleZh: "計算格式" },
  { id: "tax-reconciliation", title: "Tax Reconciliation", titleZh: "稅務調節" },
  { id: "transaction-checker", title: "Transaction Checker", titleZh: "交易稅務檢查器" },
  { id: "dipn-index", title: "DIPN Index", titleZh: "DIPN 索引" },
  { id: "profits-tax", title: "Profits Tax", titleZh: "利得稅" },
  { id: "profits-tax-entities", title: "Profits Tax by Entity", titleZh: "利得稅：三種實體" },
  { id: "salaries-tax", title: "Salaries Tax", titleZh: "薪俸稅" },
  { id: "property-tax", title: "Property Tax", titleZh: "物業稅" },
  { id: "personal-assessment", title: "Personal Assessment", titleZh: "個人入息課稅" },
  { id: "stamp-duty", title: "Stamp Duty", titleZh: "印花稅" },
  { id: "depreciation-allowances", title: "Depreciation & Allowances", titleZh: "折舊及免稅額" },
  { id: "ird-administration", title: "IRD Administration", titleZh: "稅務局行政" },
  { id: "profits-tax-return-guide", title: "Profits Tax Return Guide", titleZh: "利得稅報稅表指南" },
  { id: "profits-tax-return-finder", title: "Profits Tax Return Box Finder", titleZh: "利得稅報稅表欄位搜尋" },
  { id: "profits-tax-illustrations", title: "Profits Tax — Illustrations", titleZh: "利得稅例題" },
  { id: "salaries-tax-illustrations", title: "Salaries Tax — Illustrations", titleZh: "薪俸稅例題" },
  { id: "property-tax-illustrations", title: "Property Tax — Illustrations", titleZh: "物業稅例題" },
  { id: "stamp-duty-illustrations", title: "Stamp Duty — Illustrations", titleZh: "印花稅例題" },
  { id: "depreciation-allowances-illustrations", title: "Depreciation & Allowances — Illustrations", titleZh: "折舊及免稅額例題" },
  { id: "module9-extra-practice", title: "Module 9 Extra Practice Q&A", titleZh: "Module 9 額外練習問答" },
]);

const PAGE_IDS = new Set(["page", ...HUB_INDEX.map((page) => page.id)]);
const PAGE_ID_PATTERN = /^[A-Za-z0-9_-]{1,80}$/;
const SECTION_PATTERN = /^[A-Za-z0-9_-]{0,128}$/;

const object = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (message) => {
  throw new Error(message);
};

export function estimateTokens(text) {
  return Math.ceil(String(text ?? "").length / 4);
}

export function exactKeys(value, allowed, label) {
  if (!object(value)) fail(`${label} must be an object.`);
  if (Object.keys(value).some((key) => !allowed.includes(key))) fail(`Unknown ${label.toLowerCase()} field.`);
}

export function compactHub(hub) {
  exactKeys(hub ?? {}, ["pageId", "pageTitle", "yearBasis", "sectionId", "excerpt"], "Hub");
  const pageId = typeof hub.pageId === "string" && PAGE_IDS.has(hub.pageId) && PAGE_ID_PATTERN.test(hub.pageId) ? hub.pageId : "page";
  const pageTitle =
    typeof hub.pageTitle === "string" ? hub.pageTitle.trim().slice(0, LIMITS.MAX_TITLE_CHARS) : "";
  const yearBasis = YEAR_BASES.includes(hub.yearBasis) ? hub.yearBasis : "2026/27";
  const sectionId =
    typeof hub.sectionId === "string" && SECTION_PATTERN.test(hub.sectionId)
      ? hub.sectionId.slice(0, LIMITS.MAX_SECTION_CHARS)
      : "";
  const excerpt =
    typeof hub.excerpt === "string" ? hub.excerpt.replace(/\s+/g, " ").trim().slice(0, LIMITS.MAX_EXCERPT_CHARS) : "";
  return { pageId, pageTitle, yearBasis, sectionId, excerpt };
}

export function validateRequest(payload) {
  exactKeys(payload, ["message", "history", "hub", "api"], "Request");
  if (new TextEncoder().encode(JSON.stringify(payload)).byteLength > LIMITS.MAX_REQUEST_BYTES)
    fail("AI request is too large.");
  if (
    typeof payload.message !== "string" ||
    !payload.message.trim() ||
    payload.message.length > LIMITS.MAX_MESSAGE_CHARS
  )
    fail("Message must contain 1–4000 characters.");
  const api = payload.api ?? "main";
  if (!API_IDS.includes(api)) fail("Unknown API selection.");
  const history = payload.history ?? [];
  if (!Array.isArray(history) || history.length > LIMITS.MAX_HISTORY_TURNS)
    fail("Conversation history is too long.");
  let characters = 0;
  for (const turn of history) {
    exactKeys(turn, ["role", "content"], "History");
    if (
      !["user", "assistant"].includes(turn.role) ||
      typeof turn.content !== "string" ||
      turn.content.length > LIMITS.MAX_HISTORY_TURN_CHARS
    )
      fail("Invalid conversation history.");
    characters += turn.content.length;
  }
  if (characters > LIMITS.MAX_HISTORY_CHARS) fail("Conversation history is too large.");
  return {
    message: payload.message.trim(),
    history,
    hub: compactHub(payload.hub),
    api,
  };
}

export function validateReply(parsed) {
  exactKeys(parsed, ["message"], "Reply");
  if (
    typeof parsed.message !== "string" ||
    !parsed.message.trim() ||
    parsed.message.length > LIMITS.MAX_REPLY_CHARS
  )
    fail("Invalid assistant message.");
  return { message: parsed.message };
}

export function assertPromptBudget(messages) {
  const tokens = estimateTokens(JSON.stringify(messages));
  if (tokens > LIMITS.INPUT_TOKEN_LIMIT)
    fail("This request is too large for the assistant. Shorten or clear the conversation.");
  return tokens;
}
