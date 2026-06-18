/*
 * WEGC form relay — Cloudflare Worker
 * --------------------------------------------------------------------------
 * Receives JSON form submissions from wegc.fund and forwards them to a
 * Telegram chat via the Bot API. The bot token never reaches the browser:
 * it lives only as a Worker secret. Formspree + mailto remain as fallbacks
 * on the site side, so this relay can fail safely.
 *
 * SETUP (one time):
 *   1. Create a bot:  Telegram -> @BotFather -> /newbot  -> copy the TOKEN.
 *   2. Get your chat id:
 *        - write any message to your new bot, then open:
 *          https://api.telegram.org/bot<TOKEN>/getUpdates
 *          and read result[].message.chat.id
 *        - or add the bot to a group and read the negative group chat id.
 *   3. Deploy this Worker (Cloudflare dashboard or Wrangler), then set secrets:
 *        wrangler secret put TELEGRAM_BOT_TOKEN
 *        wrangler secret put TELEGRAM_CHAT_ID
 *   4. Put the deployed Worker URL into the site:
 *        window.WEGC_RELAY = "https://<your-worker>.workers.dev"
 *
 * Optional env vars:
 *   ALLOWED_ORIGINS  comma-separated list, default "https://wegc.fund,https://www.wegc.fund"
 */

const DEFAULT_ALLOWED = "https://wegc.fund,https://www.wegc.fund";

function corsHeaders(origin, allowed) {
  const ok = allowed.includes(origin);
  return {
    "Access-Control-Allow-Origin": ok ? origin : allowed[0],
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export default {
  async fetch(request, env) {
    const allowed = (env.ALLOWED_ORIGINS || DEFAULT_ALLOWED)
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, allowed);
    const path = new URL(request.url).pathname.replace(/\/+$/, "") || "/";

    if (request.method === "GET" && (path === "/health" || path === "/")) {
      return json({ ok: true, service: "wegc-form-relay", ts: new Date().toISOString() }, 200, cors);
    }

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405, headers: cors });
    }

    let data = {};
    try {
      const ct = request.headers.get("Content-Type") || "";
      if (ct.includes("application/json")) {
        data = await request.json();
      } else {
        const form = await request.formData();
        for (const [k, v] of form.entries()) data[k] = v;
      }
    } catch (e) {
      return json({ ok: false, error: "bad payload" }, 400, cors);
    }

    // Honeypot: silently accept bot spam without forwarding.
    if (data._gotcha) return json({ ok: true }, 200, cors);

    if (!env.TELEGRAM_BOT_TOKEN || !env.TELEGRAM_CHAT_ID) {
      return json({ ok: false, error: "relay not configured" }, 500, cors);
    }

    const page = data._page || "";
    const lang = data._lang || "";
    const order = ["name", "email", "phone", "jurisdiction", "company", "interest", "project", "message"];
    const seen = new Set();
    const rows = [];
    for (const k of order) {
      if (data[k]) {
        rows.push(`<b>${esc(k.toUpperCase())}:</b> ${esc(data[k])}`);
        seen.add(k);
      }
    }
    for (const k of Object.keys(data)) {
      if (k.startsWith("_") || seen.has(k) || k === "agree" || !data[k]) continue;
      rows.push(`<b>${esc(k.toUpperCase())}:</b> ${esc(data[k])}`);
    }

    const header = "🏝 <b>New WEGC enquiry</b>";
    const meta = [page && `Page: ${esc(page)}`, lang && `Lang: ${esc(lang)}`]
      .filter(Boolean)
      .join(" · ");
    const text = [header, meta, "", rows.join("\n")].filter(Boolean).join("\n");

    const tg = await fetch(
      `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: env.TELEGRAM_CHAT_ID,
          text,
          parse_mode: "HTML",
          disable_web_page_preview: true,
        }),
      }
    );

    if (!tg.ok) {
      const detail = await tg.text().catch(() => "");
      return json({ ok: false, error: "telegram failed", detail }, 502, cors);
    }

    if (env.DB) {
      await logFormLead(env, data).catch((e) => console.error("logFormLead", e));
    }

    if (env.ORCHESTRATOR_INGEST_URL && env.ORCHESTRATOR_INGEST_SECRET) {
      forwardIngest(env, data, text).catch(() => {});
    }

    return json({ ok: true }, 200, cors);
  },
};

// Mirror the form enquiry into the shared `leads` table (same DB as the AI
// agent), so site forms and chat conversations show up together in /admin.
async function logFormLead(env, data) {
  const str = (v, n) => String(v == null ? "" : v).slice(0, n);
  const now = new Date().toISOString();
  const chatId = `form:${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  const name = str(data.name, 120);
  const contact = str(data.phone || data.email, 160);
  const lang = str(data._lang, 8);
  const budget = str(data.budget, 120);
  const interest = str(data.project || data.interest, 200);
  const parts = [];
  if (data.email) parts.push(`Email: ${str(data.email, 160)}`);
  if (data.phone) parts.push(`Тел: ${str(data.phone, 60)}`);
  if (data.company) parts.push(`Компания: ${str(data.company, 120)}`);
  if (data.jurisdiction) parts.push(`Юрисдикция: ${str(data.jurisdiction, 80)}`);
  if (data.message) parts.push(`Сообщение: ${str(data.message, 800)}`);
  const page = str(data._page, 120);
  const summary = `📩 Заявка с формы${page ? ` (${page})` : ""}. ${parts.join(" · ")}`.slice(0, 1200);
  await env.DB.prepare(
    `INSERT INTO leads (chat_id, created_at, updated_at, name, username, lang, status, budget, interested_projects, summary, msg_count, opened, transcript)
     VALUES (?1, ?2, ?2, ?3, ?4, ?5, 'form', ?6, ?7, ?8, 0, 0, '[]')`
  )
    .bind(chatId, now, name, contact, lang, budget, interest, summary)
    .run();
}

async function forwardIngest(env, data, text) {
  const base = String(env.ORCHESTRATOR_INGEST_URL || "").replace(/\/$/, "");
  await fetch(`${base}/api/ingest/lead`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${env.ORCHESTRATOR_INGEST_SECRET}`,
    },
    body: JSON.stringify({
      system_id: "wegc-form-relay",
      title: data.project || data.interest || "WEGC enquiry",
      contact: data.phone || data.email,
      source: data._page || "wegc.fund",
      metadata: data,
    }),
  });
}

function json(obj, status, cors) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...cors },
  });
}
