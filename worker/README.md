# HK Tax Study Hub — Qwen Worker

Cloudflare Worker that authenticates GitHub sign-in and proxies Qwen. The
DashScope / Token Plan key stays in a Worker secret. The public Hub never
receives it.

Do not deploy or put secrets in this repository. Configure them locally.

## Bindings

| Setting | Purpose |
| --- | --- |
| `QWEN_BASE_URL` | `https://token-plan.maas.qwencloudapi.com/compatible-mode/v1` |
| `QWEN_MODEL` | `qwen3.8-flash` (falls back to `qwen-plus` if unset) |
| `QWEN_ALLOWED_GITHUB_USER` | `anthonymankaho` |
| `QWEN_MONTHLY_TOKEN_QUOTA` | `20000000` prompt + completion tokens per calendar month (UTC) |
| `GITHUB_CLIENT_ID` | Public GitHub OAuth App client id (not a secret) |
| `DASHSCOPE_API_KEY` | Worker **secret** — main Token Plan key |
| `DASHSCOPE_API_KEY_TEMP` | Worker **secret** — spare small-quota Token Plan key (optional; the panel's API selector only offers "Temp" once this exists) |
| `QWEN_MODEL_TEMP` | Model for the spare key; pinned to `qwen3.8-flash` because the spare plan carries `qwen3.8-*` only (`qwen-plus` returns `model_not_found` there) |
| `QWEN_BASE_URL_TEMP` | Optional endpoint override for the spare key; defaults to `QWEN_BASE_URL` |
| `QWEN_MONTHLY_TOKEN_QUOTA_TEMP` | `2000000` tokens per calendar month for the spare key, counted separately from main |
| `GITHUB_CLIENT_SECRET` | Worker **secret** |
| `QWEN_USAGE` | Optional KV namespace for monthly token counts |

## Two APIs (main / temp)

The panel's composer has an **API selector** (shown only when both keys are
configured). The browser sends `payload.api: "main" | "temp"`; the Worker
resolves the endpoint, model and secret server-side — the browser never sees a
key. Usage is counted per API (`qwen-usage:<login>:<month>` and
`qwen-usage:<login>:<month>:temp`), so a spent main quota does not block the
spare. On a quota error the panel offers a one-click "switch & retry". The
`config` action lists `{ id, available, quotaLimit }` per API — availability
only, never key material.

## One-time setup

1. Create a GitHub OAuth App with callback
   `https://anthonymanhk.github.io/hktax-studyhub/oauth.html`
   (add localhost `/oauth.html` callbacks if you test locally). Scope used by
   the Hub is `read:user` only.
2. Put the client id in `wrangler.jsonc` `vars.GITHUB_CLIENT_ID`.
3. From `worker/`:

```
npx wrangler secret put DASHSCOPE_API_KEY
npx wrangler secret put DASHSCOPE_API_KEY_TEMP
npx wrangler secret put GITHUB_CLIENT_SECRET
npx wrangler kv namespace create QWEN_USAGE
```

4. Production KV is already wired:

```
"kv_namespaces": [{ "binding": "QWEN_USAGE", "id": "e2e5930dec5d44a4b581e68ea398d12d" }]
```

5. Worker URL (deployed): `https://hktax-studyhub-api.anthonym-354.workers.dev`

Still required before Ask Qwen can sign in: a GitHub OAuth App whose
callback is `https://anthonymanhk.github.io/hktax-studyhub/oauth.html`,
then set `vars.GITHUB_CLIENT_ID` and `npx wrangler secret put GITHUB_CLIENT_SECRET`.

## Tests

```
cd worker
node --test test/qwen.test.js
```
