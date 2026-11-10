import { handleQwen, AIError, readBoundedJSON } from "./qwen.js";

const GITHUB_OAUTH_URL = "https://github.com/login/oauth/access_token";
const DEFAULT_ORIGIN = "https://anthonymanhk.github.io";

const ALLOWED_ORIGINS = new Set([
  DEFAULT_ORIGIN,
  "https://anthonymankaho.github.io",
  "http://localhost:3000",
  "http://localhost:5173",
  "http://localhost:5500",
  "http://localhost:8000",
  "http://localhost:8080",
  "http://127.0.0.1:3000",
  "http://127.0.0.1:5173",
  "http://127.0.0.1:5500",
  "http://127.0.0.1:8000",
  "http://127.0.0.1:8080",
]);

function corsHeaders(origin) {
  const allowedOrigin = origin && ALLOWED_ORIGINS.has(origin) ? origin : DEFAULT_ORIGIN;
  return {
    "Access-Control-Allow-Origin": allowedOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };
}

function jsonResponse(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      ...corsHeaders(origin),
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

function errorResponse(message, status, origin, code) {
  return jsonResponse({ error: message, ...(code ? { code } : {}) }, status, origin);
}

function isAllowedRedirect(uri, origin) {
  let parsed;
  try {
    parsed = new URL(uri);
  } catch {
    return false;
  }
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return false;
  if (parsed.username || parsed.password || parsed.hash || parsed.search) return false;
  if (origin && parsed.origin !== origin) return false;
  if (!ALLOWED_ORIGINS.has(parsed.origin)) return false;
  return parsed.pathname === "/oauth.html" || parsed.pathname === "/hktax-studyhub/oauth.html";
}

async function handleConfig(env, origin) {
  const clientId = String(env.GITHUB_CLIENT_ID || "");
  const ready = Boolean(clientId && clientId !== "REPLACE_ME" && env.GITHUB_CLIENT_SECRET);
  return jsonResponse(
    {
      githubClientId: ready ? clientId : "",
      oauthReady: ready,
    },
    200,
    origin,
  );
}

async function handleAuth(payload, env, origin) {
  if (origin && !ALLOWED_ORIGINS.has(origin)) return errorResponse("Origin is not allowed.", 403, origin);
  if (!env.GITHUB_CLIENT_SECRET || !env.GITHUB_CLIENT_ID || env.GITHUB_CLIENT_ID === "REPLACE_ME") {
    return errorResponse("GitHub OAuth is not configured.", 503, origin, "AI_UNAVAILABLE");
  }
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return errorResponse("Invalid OAuth request.", 400, origin);
  }
  const code = payload.code;
  const redirectUri = payload.redirect_uri;
  if (typeof code !== "string" || code.length < 8 || code.length > 256 || /\s/.test(code)) {
    return errorResponse("Invalid OAuth request.", 400, origin);
  }
  if (typeof redirectUri !== "string" || !isAllowedRedirect(redirectUri, origin)) {
    return errorResponse("Invalid OAuth redirect.", 400, origin);
  }
  try {
    const response = await fetch(GITHUB_OAUTH_URL, {
      method: "POST",
      redirect: "manual",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify({
        client_id: env.GITHUB_CLIENT_ID,
        client_secret: env.GITHUB_CLIENT_SECRET,
        code,
        redirect_uri: redirectUri,
      }),
    });
    if (!response.ok) {
      if (response.body) await response.body.cancel();
      return errorResponse("GitHub OAuth request failed.", 502, origin);
    }
    const result = await readBoundedJSON(response, 32768);
    const token = result.access_token;
    if (typeof token !== "string" || token.length < 10 || token.length > 512) {
      return errorResponse("GitHub OAuth request failed.", 502, origin);
    }
    return jsonResponse({ access_token: token }, 200, origin);
  } catch {
    return errorResponse("GitHub OAuth request failed.", 502, origin);
  }
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin");

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }
    if (request.method !== "POST") {
      return errorResponse("Method not allowed.", 405, origin);
    }

    let body;
    try {
      body = await readBoundedJSON(request, 131072);
    } catch (error) {
      if (error instanceof AIError && error.code === "AI_TOO_LARGE") {
        return errorResponse("Request body must be valid JSON.", 413, origin);
      }
      return errorResponse("Request body must be valid JSON.", 400, origin);
    }
    if (!body || typeof body !== "object" || Array.isArray(body)) {
      return errorResponse("Request body must be a JSON object.", 400, origin);
    }

    const payload = body.payload ?? {};

    switch (body.action) {
      case "config":
        return handleConfig(env, origin);
      case "auth":
        return handleAuth(payload, env, origin);
      case "qwen": {
        if (origin && !ALLOWED_ORIGINS.has(origin)) return errorResponse("Origin is not allowed.", 403, origin);
        try {
          const reply = await handleQwen(payload, request.headers.get("Authorization"), env);
          return jsonResponse(reply, 200, origin);
        } catch (error) {
          const known = error instanceof AIError;
          return new Response(
            JSON.stringify({
              error: known ? error.message : "Qwen is temporarily unavailable.",
              code: known ? error.code : "AI_UNAVAILABLE",
            }),
            {
              status: known ? error.status : 503,
              headers: {
                ...corsHeaders(origin),
                "Content-Type": "application/json; charset=utf-8",
                "Cache-Control": "no-store",
                ...(known && error.retryAfter ? { "Retry-After": String(error.retryAfter) } : {}),
              },
            },
          );
        }
      }
      default:
        return errorResponse("Unknown action.", 400, origin);
    }
  },
};
