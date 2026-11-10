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
| `DASHSCOPE_API_KEY` | Worker **secret** |
| `GITHUB_CLIENT_SECRET` | Worker **secret** |
| `QWEN_USAGE` | Optional KV namespace for monthly token counts |

## One-time setup

1. Create a GitHub OAuth App with callback
   `https://anthonymanhk.github.io/hktax-studyhub/oauth.html`
   (add localhost `/oauth.html` callbacks if you test locally). Scope used by
   the Hub is `read:user` only.
2. Put the client id in `wrangler.jsonc` `vars.GITHUB_CLIENT_ID`.
3. From `worker/`:

```
npx wrangler secret put DASHSCOPE_API_KEY
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
