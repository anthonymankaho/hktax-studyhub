import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildCatalog } from "../src/content/build.js";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");
const skip = new Set(["question-bank.html", "question-bank-b.html"]);

const pages = readdirSync(join(repo, "pages"))
  .filter((file) => file.endsWith(".html") && !skip.has(file))
  .sort()
  .map((file) => ({
    file,
    html: readFileSync(join(repo, "pages", file), "utf8"),
  }));

const catalog = buildCatalog({
  transactionsSource: readFileSync(join(repo, "assets/js/transactions-data.js"), "utf8"),
  dipnSource: readFileSync(join(repo, "assets/js/dipn-index-data.js"), "utf8"),
  birSource: readFileSync(join(repo, "assets/js/bir-finder-data.js"), "utf8"),
  qbank: JSON.parse(readFileSync(join(repo, "assets/qbank.json"), "utf8")),
  qbankB: JSON.parse(readFileSync(join(repo, "assets/qbank-b.json"), "utf8")),
  pages,
});

const out = join(here, "..", "src", "catalog.json");
writeFileSync(out, `${JSON.stringify(catalog)}\n`);
const bytes = Buffer.byteLength(JSON.stringify(catalog));
console.log(
  `catalog ${bytes} bytes: ${catalog.pages.length} pages, ${catalog.transactions.length} transactions, ${catalog.dipn.length} DIPNs, ${catalog.boxes.length} return boxes, ${catalog.questions.length} questions, ${catalog.irdUpdates.length} IRD updates`,
);
