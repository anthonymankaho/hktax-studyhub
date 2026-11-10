/* Ask Qwen — GitHub-authenticated study assistant.
 *
 * Talks only to the HK Tax Study Hub Worker. The provider key never ships
 * in this file. Conversation stays in memory. Page excerpts are sent as
 * untrusted data; replies are escaped and rendered as text.
 */
(function () {
  var API = "https://hktax-studyhub-api.anthonym-354.workers.dev";
  var TOKEN_KEY = "hktax_qwen_token";
  var STATE_KEY = "hktax_qwen_oauth_state";
  var OAUTH_MSG = "hktax-qwen-oauth";
  var PAGE_IDS = {
    MAIN: 1,
    "ird-updates": 1,
    "acca-tx-hkg": 1,
    "question-bank": 1,
    "question-bank-b": 1,
    "question-bank-c": 1,
    "computation-formats": 1,
    "tax-reconciliation": 1,
    "transaction-checker": 1,
    "dipn-index": 1,
    "profits-tax": 1,
    "profits-tax-entities": 1,
    "salaries-tax": 1,
    "property-tax": 1,
    "personal-assessment": 1,
    "stamp-duty": 1,
    "depreciation-allowances": 1,
    "ird-administration": 1,
    "profits-tax-return-guide": 1,
    "profits-tax-return-finder": 1,
    "profits-tax-illustrations": 1,
    "salaries-tax-illustrations": 1,
    "property-tax-illustrations": 1,
    "stamp-duty-illustrations": 1,
    "depreciation-allowances-illustrations": 1,
    "module9-extra-practice": 1,
  };

  function isOAuthPage() {
    return /oauth\.html$/i.test(location.pathname || "");
  }

  function oauthRedirectUri() {
    var path = location.pathname || "/";
    if (path.indexOf("/hktax-studyhub") === 0) return location.origin + "/hktax-studyhub/oauth.html";
    return location.origin + "/oauth.html";
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function getToken() {
    try {
      return sessionStorage.getItem(TOKEN_KEY) || "";
    } catch (e) {
      return "";
    }
  }

  function setToken(token) {
    try {
      if (token) sessionStorage.setItem(TOKEN_KEY, token);
      else sessionStorage.removeItem(TOKEN_KEY);
    } catch (e) {}
  }

  function getOAuthState() {
    try {
      return localStorage.getItem(STATE_KEY) || "";
    } catch (e) {
      return "";
    }
  }

  function setOAuthState(state) {
    try {
      if (state) localStorage.setItem(STATE_KEY, state);
      else localStorage.removeItem(STATE_KEY);
    } catch (e) {}
  }

  function signedIn() {
    return getToken().length >= 10;
  }

  function currentHub() {
    var panel = document.querySelector(".tab-panel.active");
    var pageId = "page";
    var pageTitle = document.title || "";
    if (panel && panel.id && PAGE_IDS[panel.id]) {
      pageId = panel.id;
      pageTitle = panel.getAttribute("data-label") || pageTitle;
    } else {
      var file = ((location.pathname || "").split("/").pop() || "").replace(/\.html?$/i, "");
      if (PAGE_IDS[file]) pageId = file;
    }
    var sectionId = "";
    var hash = (location.hash || "").replace(/^#/, "");
    if (/^[A-Za-z0-9_-]{1,128}$/.test(hash)) sectionId = hash;
    var source = panel || document.querySelector("main.content") || document.querySelector("main") || document.body;
    var excerpt = ((source && source.innerText) || "").replace(/\s+/g, " ").trim().slice(0, 8000);
    var yearEl = document.getElementById("qwen-year");
    var yearBasis = yearEl && yearEl.value === "2025/26" ? "2025/26" : "2026/27";
    return {
      pageId: pageId,
      pageTitle: String(pageTitle).slice(0, 200),
      yearBasis: yearBasis,
      sectionId: sectionId,
      excerpt: excerpt,
    };
  }

  async function call(action, payload, signal) {
    var headers = { "Content-Type": "application/json" };
    var token = getToken();
    if (token) headers.Authorization = "Bearer " + token;
    var response = await fetch(API, {
      method: "POST",
      signal: signal,
      headers: headers,
      body: JSON.stringify({ action: action, payload: payload || {} }),
    });
    var result = await response.json().catch(function () {
      return {};
    });
    if (!response.ok) {
      var error = new Error(result.error || "Request failed (" + response.status + ")");
      error.code = result.code;
      error.status = response.status;
      error.retryAfter = Number(response.headers.get("Retry-After")) || 0;
      throw error;
    }
    return result;
  }

  async function handleOAuthCallback() {
    var params = new URLSearchParams(location.search);
    var code = params.get("code");
    if (!code || !window.opener) return false;
    var stateParam = params.get("state");
    var saved = getOAuthState();
    if (!stateParam || stateParam !== saved) {
      window.opener.postMessage({ type: OAUTH_MSG, error: "GitHub sign-in state did not match." }, location.origin);
      setOAuthState("");
      window.close();
      return true;
    }
    try {
      var result = await call("auth", { code: code, redirect_uri: oauthRedirectUri() });
      var token = result.access_token;
      if (!token) throw new Error("The API did not return an access token.");
      setOAuthState("");
      window.opener.postMessage({ type: OAUTH_MSG, token: token }, location.origin);
    } catch (error) {
      setOAuthState("");
      window.opener.postMessage(
        { type: OAUTH_MSG, error: error.message || "GitHub sign-in failed." },
        location.origin,
      );
    }
    window.close();
    return true;
  }

  function startLogin(clientId) {
    var stateParam = Array.from(crypto.getRandomValues(new Uint8Array(24)), function (value) {
      return value.toString(16).padStart(2, "0");
    }).join("");
    setOAuthState(stateParam);
    var authorizationUrl = new URL("https://github.com/login/oauth/authorize");
    authorizationUrl.searchParams.set("client_id", clientId);
    authorizationUrl.searchParams.set("redirect_uri", oauthRedirectUri());
    authorizationUrl.searchParams.set("scope", "read:user");
    authorizationUrl.searchParams.set("state", stateParam);
    var popup = window.open(authorizationUrl, "hktax-qwen-oauth", "width=600,height=720");
    return Boolean(popup);
  }

  function ensureCss() {
    if (document.getElementById("qwen-assistant-css") || document.querySelector('link[href*="qwen-assistant.css"]'))
      return;
    var href = "";
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].getAttribute("src") || "";
      if (src.indexOf("qwen-assistant.js") !== -1) {
        href = src.replace(/js\/qwen-assistant\.js.*$/, "css/qwen-assistant.css");
        break;
      }
    }
    if (!href) return;
    var link = document.createElement("link");
    link.id = "qwen-assistant-css";
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
  }

  function ensureTrigger() {
    var existing = document.getElementById("ask-qwen");
    if (existing) return existing;
    var btn = document.createElement("button");
    btn.id = "ask-qwen";
    btn.type = "button";
    btn.className = "toolbtn";
    btn.textContent = "Ask Qwen";
    btn.title = "Ask Qwen about Hong Kong tax (GitHub sign-in required)";
    var anchor = document.querySelector(".ai-prompt-btn");
    if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(btn, anchor);
    else {
      var bar = document.querySelector(".topbar, .site-header .bar");
      if (bar) bar.appendChild(btn);
      else return null;
    }
    return btn;
  }

  function mountPanel() {
    if (document.getElementById("qwen-panel")) return;
    var panel = document.createElement("dialog");
    panel.id = "qwen-panel";
    panel.className = "qwen-panel";
    panel.setAttribute("aria-labelledby", "qwen-title");
    panel.setAttribute("aria-modal", "true");
    panel.innerHTML =
      '<div class="qwen-shell">' +
      '<header class="qwen-heading"><div><p class="eyebrow">HK Tax Study Hub</p><h2 id="qwen-title">Ask Qwen · 問 Qwen</h2></div>' +
      '<button class="qwen-close" id="qwen-close" type="button" aria-label="Close Qwen">×</button></header>' +
      '<p class="qwen-intro">Sends a trimmed copy of the page you are on (not the whole Hub). Replies are study help only — citations are not checked. Conversation stays in this tab. · 只傳送你正在閱讀的頁面摘要（非整個平台）。回覆僅供學習參考，引文未經核實。對話只留在本分頁。</p>' +
      '<div class="qwen-scroll" id="qwen-scroll">' +
      '<div class="qwen-auth" id="qwen-auth"></div>' +
      '<div id="qwen-conversation" role="log" aria-label="Qwen conversation" aria-live="polite" aria-relevant="additions text"></div>' +
      '<div id="qwen-feedback" role="status" aria-live="polite"></div>' +
      '<div id="qwen-quota" role="status"></div>' +
      "</div>" +
      '<form class="qwen-composer" id="qwen-form">' +
      '<label for="qwen-message">Message Qwen · 訊息</label>' +
      '<textarea id="qwen-message" rows="3" maxlength="4000" required placeholder="Ask about a Hong Kong tax rule, computation, or this page… / 詢問香港稅務規則、計算或本頁內容…"></textarea>' +
      '<div class="qwen-composer-row">' +
      '<label class="qwen-basis">Year · 課稅年度 <select id="qwen-year"><option value="2026/27" selected>2026/27 current law</option><option value="2025/26">2025/26 ACCA TX-HKG</option></select></label>' +
      "<span>In-memory only · 不儲存對話</span>" +
      "</div>" +
      '<div class="qwen-actions">' +
      '<button class="qwen-btn" type="submit" id="qwen-send">Send · 傳送</button>' +
      '<button class="qwen-btn secondary" type="button" id="qwen-signin">Sign in with GitHub · 登入</button>' +
      '<button class="qwen-btn secondary" type="button" id="qwen-signout" hidden>Sign out · 登出</button>' +
      "</div></form></div>";
    document.body.appendChild(panel);
  }

  function boot() {
    if (isOAuthPage()) return;
    ensureCss();
    var trigger = ensureTrigger();
    if (!trigger) return;
    mountPanel();

    var panel = document.getElementById("qwen-panel");
    var historyEl = document.getElementById("qwen-conversation");
    var feedback = document.getElementById("qwen-feedback");
    var quota = document.getElementById("qwen-quota");
    var authBox = document.getElementById("qwen-auth");
    var input = document.getElementById("qwen-message");
    var send = document.getElementById("qwen-send");
    var form = document.getElementById("qwen-form");
    var signin = document.getElementById("qwen-signin");
    var signout = document.getElementById("qwen-signout");
    var memory = {
      history: [],
      busy: false,
      error: null,
      lastPrompt: "",
      quota: null,
      config: null,
    };
    var retryReadyAt = 0;
    var retryTimer;

    function available() {
      return signedIn() && memory.config && memory.config.oauthReady;
    }

    function render() {
      var turns = memory.history.length
        ? memory.history
            .map(function (turn) {
              return (
                '<article class="qwen-turn" data-role="' +
                turn.role +
                '"><h3>' +
                (turn.role === "user" ? "You · 你" : "Qwen") +
                "</h3><p>" +
                escapeHtml(turn.content) +
                "</p></article>"
              );
            })
            .join("")
        : '<div class="qwen-empty"><strong>A second pair of eyes for this page · 本頁的學習助手</strong><p>Ask a Hong Kong tax question. Qwen sees a trimmed excerpt of the current page, not the whole Hub, and cannot change these notes.</p></div>';
      historyEl.innerHTML = turns;
      historyEl.setAttribute("aria-busy", String(memory.busy));
      quota.innerHTML = memory.quota
        ? "<p" +
          (memory.quota.used >= memory.quota.limit * 0.8 ? ' data-warn="true"' : "") +
          ">Tokens this month · 本月用量: " +
          Number(memory.quota.used).toLocaleString() +
          " / " +
          Number(memory.quota.limit).toLocaleString() +
          "</p>"
        : "";
      var canSend = available() && !memory.busy && Date.now() >= retryReadyAt;
      send.disabled = !canSend;
      input.disabled = memory.busy || !available();
      send.textContent = memory.busy ? "Thinking… · 思考中" : Date.now() < retryReadyAt ? "Wait to retry" : "Send · 傳送";
      signin.hidden = signedIn();
      signout.hidden = !signedIn();
      signin.disabled = !(memory.config && memory.config.oauthReady);
      authBox.innerHTML = signedIn()
        ? "<p>Signed in with GitHub · 已用 GitHub 登入</p>"
        : memory.config && memory.config.oauthReady
          ? "<p>Sign in with GitHub to use Qwen. Only the allowed account can spend quota. · 請先以 GitHub 登入；僅獲准帳戶可使用配額。</p>"
          : "<p>Qwen is not available on this copy yet. Open the published site after the Worker is configured, or use AI Prompts to copy a template. · 此副本尚未接上 Qwen。請在 Worker 設定後使用已發布網站，或改用 AI Prompts 複製提示詞。</p>";
      feedback.dataset.kind = memory.error ? "error" : "";
      var unavailable = memory.error && ["AI_UNAVAILABLE", "AI_FORBIDDEN", "AI_AUTH_REQUIRED"].indexOf(memory.error.code) !== -1;
      if (memory.busy) feedback.innerHTML = "<p>Qwen is thinking. The Hub is unchanged. · Qwen 思考中，本平台內容未改動。</p>";
      else if (memory.error)
        feedback.innerHTML =
          "<p>" +
          (unavailable ? "Assistant unavailable. · 助手暫停。 " : "") +
          escapeHtml(memory.error.message) +
          '</p><button class="qwen-btn secondary" id="qwen-retry" type="button"' +
          (Date.now() < retryReadyAt ? " disabled" : "") +
          ">Retry · 重試</button>";
      else feedback.innerHTML = "";
      var retryBtn = document.getElementById("qwen-retry");
      if (retryBtn)
        retryBtn.addEventListener("click", function () {
          submit(memory.lastPrompt, true);
        });
    }

    async function loadConfig() {
      try {
        memory.config = await call("config", {});
      } catch (error) {
        memory.config = { githubClientId: "", oauthReady: false };
        memory.error = {
          message: "Could not reach the Qwen service. Open the published Hub on GitHub Pages. · 未能連線 Qwen 服務。請在 GitHub Pages 開啟已發布版本。",
          code: "AI_UNAVAILABLE",
        };
      }
      render();
    }

    async function submit(message, retry) {
      if (memory.busy || !message || !String(message).trim() || Date.now() < retryReadyAt) return;
      if (!signedIn()) {
        memory.error = { message: "Sign in with GitHub to use Qwen. · 請先以 GitHub 登入。", code: "AI_AUTH_REQUIRED" };
        render();
        return;
      }
      var text = String(message).trim().slice(0, 4000);
      memory.lastPrompt = text;
      var replacing = retry && memory.history.length && memory.history[memory.history.length - 1].role === "user";
      var priorSource = replacing ? memory.history.slice(0, -1) : memory.history;
      var prior = priorSource.slice(-6).map(function (turn) {
        return { role: turn.role, content: String(turn.content).slice(0, 2000) };
      });
      if (!replacing) memory.history.push({ role: "user", content: text });
      memory.history = memory.history.slice(-24);
      memory.busy = true;
      memory.error = null;
      render();
      var controller = new AbortController();
      var timeout = setTimeout(function () {
        controller.abort();
      }, 35000);
      try {
        var result = await call("qwen", { message: text, history: prior, hub: currentHub() }, controller.signal);
        if (!result || typeof result.message !== "string") throw new Error("Qwen returned an invalid response. Please retry.");
        memory.history.push({ role: "assistant", content: result.message });
        memory.quota = result.quota || null;
        input.value = "";
      } catch (error) {
        memory.error = {
          message: controller.signal.aborted ? "Qwen timed out. Please retry. · 逾時，請重試。" : error.message || "Qwen could not complete this request.",
          code: controller.signal.aborted ? "AI_TIMEOUT" : error.code,
          status: error.status,
          retryAfter: error.retryAfter || 0,
        };
        retryReadyAt = Date.now() + Math.min(300, Math.max(0, error.retryAfter || 0)) * 1000;
        clearTimeout(retryTimer);
        if (retryReadyAt > Date.now())
          retryTimer = setTimeout(render, retryReadyAt - Date.now());
      } finally {
        clearTimeout(timeout);
        memory.busy = false;
        render();
        if (panel.open && !input.disabled) input.focus();
      }
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      submit(input.value.trim());
    });
    signin.addEventListener("click", function () {
      if (!memory.config || !memory.config.oauthReady) return;
      if (!startLogin(memory.config.githubClientId)) {
        memory.error = { message: "Allow popups to sign in with GitHub. · 請允許彈出視窗以登入 GitHub。" };
        render();
      }
    });
    signout.addEventListener("click", function () {
      setToken("");
      memory.error = null;
      render();
    });
    trigger.addEventListener("click", function () {
      render();
      if (typeof panel.showModal === "function") panel.showModal();
      loadConfig();
      if (!input.disabled) input.focus();
    });
    document.getElementById("qwen-close").addEventListener("click", function () {
      panel.close();
    });
    panel.addEventListener("close", function () {
      trigger.focus();
    });
    window.addEventListener("message", function (event) {
      if (event.origin !== location.origin || !event.data || event.data.type !== OAUTH_MSG) return;
      if (event.data.token) {
        setToken(event.data.token);
        memory.error = null;
      } else if (event.data.error) {
        memory.error = { message: event.data.error, code: "AI_AUTH_REQUIRED" };
      }
      render();
    });
    render();
  }

  if (isOAuthPage()) {
    handleOAuthCallback();
    return;
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
