import { createMcpHandler } from "agents/mcp/server";
import catalog from "./catalog.json" with { type: "json" };
import { DISCLAIMER, MCP_ENDPOINT_PATH, PUBLIC_MCP_URL, YEARS } from "./content/constants.js";
import { createTaxServer } from "./server.js";
import { TOOL_NAMES } from "./tools.js";

// Fresh server per request. The catalog is immutable study data, so there is
// no MCP session and no Durable Object. See mcp/README.md.
function createServer() {
  return createTaxServer(catalog);
}

const handler = createMcpHandler(createServer, { route: MCP_ENDPOINT_PATH });

function discovery(url) {
  return {
    name: "hktax-studyhub",
    transport: "streamable-http",
    mcp: new URL(MCP_ENDPOINT_PATH, url.origin).href,
    documentedUrl: PUBLIC_MCP_URL,
    auth: { required: false, headers: [] },
    tools: TOOL_NAMES,
    years: YEARS,
    disclaimer: DISCLAIMER,
  };
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    console.log(JSON.stringify({ message: "request", method: request.method, path: url.pathname }));

    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "")) {
      return Response.json(discovery(url), {
        headers: {
          "Cache-Control": "no-store",
          "Access-Control-Allow-Origin": "*",
        },
      });
    }

    if (url.pathname !== MCP_ENDPOINT_PATH) {
      return Response.json({ error: "Not found", mcp: MCP_ENDPOINT_PATH }, { status: 404 });
    }

    try {
      return await handler(request, env, ctx);
    } catch (error) {
      console.error(JSON.stringify({
        message: "mcp failed",
        error: error instanceof Error ? error.message : "request failed",
      }));
      return Response.json({ error: "MCP request failed" }, { status: 500 });
    }
  },
};
