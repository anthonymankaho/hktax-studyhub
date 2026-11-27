# HK Tax Study Hub — MCP server

Remote [MCP](https://modelcontextprotocol.io) server so an agent can search the
Hub instead of scraping the HTML. Streamable HTTP, stateless, no login.

This is **not** the Ask Qwen Worker. That Worker (`worker/`,
`hktax-studyhub-api`) holds the DashScope keys and the GitHub OAuth client
secret. This one has no secrets and no KV. Do not put those keys here, and do
not add MCP routes to the Qwen Worker.

## Endpoint

| | |
|---|---|
| **URL** | `https://hktax-studyhub-mcp.anthonym-354.workers.dev/mcp` |
| **Transport** | Streamable HTTP (POST JSON-RPC; a single JSON response or an SSE stream) |
| **Auth** | Not required. Send no `Authorization` header and no API key. |
| **Discovery** | `GET /` on the same host returns the tool list and this URL. `GET /mcp` is 405 — that is the stateless server, not a broken deploy. |

The host is the `workers.dev` name Wrangler assigns for Worker `hktax-studyhub-mcp`
on the same account as `hktax-studyhub-api.anthonym-354.workers.dev`. This
repository does not deploy it. `npx wrangler deploy` prints the live URL; if
the account subdomain is ever different, use that printed URL.

Browser `Origin`s other than localhost and this Worker host are rejected
(DNS-rebinding protection). Cursor, Claude Code, and other non-browser MCP
clients omit `Origin` and are accepted.

## Connect

No headers.

**Cursor** — Settings → MCP → add a custom server, or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "hktax-studyhub": {
      "url": "https://hktax-studyhub-mcp.anthonym-354.workers.dev/mcp"
    }
  }
}
```

**Claude Code:**

```
claude mcp add --transport http hktax-studyhub https://hktax-studyhub-mcp.anthonym-354.workers.dev/mcp
```

**MCP Inspector:** `npx @modelcontextprotocol/inspector@latest`, then connect to the URL above. No token.

## Tools

Every tool result repeats the disclaimer. Filing figures and section cites must
be checked against Cap. 112, Cap. 117, and current IRD guidance.

Rates are the same for **YA 2026/27** (current work) and **YA 2025/26** (ACCA
TX-HKG through December 2026). Only allowances differ. `treatAsLaw` is true
only for enacted figures. Proposed and bill items — including the $160,000
child allowance and the stamp-duty association-test bill — are not law.

| Tool | What it returns |
|---|---|
| `classify_transaction` | Transaction Checker hit: taxable / non-taxable / deductible / non-deductible / dutiable / no duty / allowance, with the section and page URL. |
| `lookup_dipn` | DIPN, SOIPN, or EDOIPN by number or topic. `core` has a study page; `reference` is a summary only. |
| `get_rates_and_allowances` | Profits, salaries, property, stamp duty, and depreciation rates, plus both allowance columns. Proposed rows stay marked not law. |
| `get_page_section` | One section of a core page (profits, property, salaries, stamp duty, depreciation, return guide, IRD administration, personal assessment, computation formats, and the other study pages). Omit `page` to list pages. |
| `search_hub` | Keyword search across those pages, with a short snippet and anchor. |
| `list_ird_updates` | IRD What's New rows marked enacted, bill, proposed, or another non-law status. |
| `search_return_boxes` | BIR51 / BIR52 / BIR54 box finder. |
| `search_questions` | Original ACCA TX-HKG practice banks. `A` MCQs, `B` OT cases, `C` constructed response. |

Section A and B question pages are generated from `assets/qbank.json` and
`assets/qbank-b.json`, so they are searched with `search_questions` rather than
copied a second time as HTML.

## Deploy

There is no GitHub Action that deploys Workers. From a machine logged into the
Cloudflare account that already hosts `hktax-studyhub-api`:

```
cd mcp
npm install
npm test
npx wrangler deploy
```

No `wrangler secret put`. A dry run that only bundles is `npm run dry-run`.

After editing a page or a data file under `assets/js/` or `assets/qbank*.json`,
rebuild the catalog the Worker bundles and commit it:

```
cd mcp
npm run build
npm test
```

`npm test` fails if `src/catalog.json` does not match the Hub sources.

## Tests

```
cd mcp
npm install
npm test
```

The tests rebuild the catalog from `pages/`, `assets/js/transactions-data.js`,
`assets/js/dipn-index-data.js`, `assets/js/bir-finder-data.js`, and the question
banks, then call the tools and the streamable HTTP handler. They check the
dual-year allowances, that proposed and bill items are not law, and that a
fake DashScope or GitHub secret passed in the environment is not returned.
