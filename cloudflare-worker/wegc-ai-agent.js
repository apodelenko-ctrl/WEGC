/*
 * WEGC AI sales agent — Cloudflare Worker
 * --------------------------------------------------------------------------
 * A Telegram bot that talks to clients as a WEGC consultant ("Анна"):
 * qualifies the lead, answers from the knowledge base, handles objections
 * and hands a warm lead to the human manager (Telegram notification + Zoom).
 *
 * Flow:
 *   client → @your_bot  →  Telegram webhook → this Worker
 *   Worker  → Anthropic Claude (with KB system prompt + conversation memory)
 *   Worker  → reply to client  +  (when qualified) notify the owner chat
 *
 * The notification relay (wegc-form-relay) stays separate and untouched.
 *
 * REQUIRED secrets (wrangler secret put ...):
 *   AGENT_BOT_TOKEN    Telegram bot token from @BotFather (client-facing bot)
 *   ANTHROPIC_API_KEY  Anthropic API key
 *   OWNER_CHAT_ID      Telegram chat id that receives warm-lead notifications
 *   WEBHOOK_SECRET     random string; also passed to Telegram setWebhook
 *
 * Optional vars (wrangler.toml [vars]):
 *   ANTHROPIC_MODEL    default "claude-3-5-sonnet-latest"
 *   MAX_HISTORY        default 24 (messages kept per conversation)
 *
 * Bindings:
 *   CONV   KV namespace for per-chat conversation memory
 *
 * One-time webhook registration (after deploy + secrets):
 *   curl "https://api.telegram.org/bot<AGENT_BOT_TOKEN>/setWebhook" \
 *     -d "url=https://<worker>.workers.dev/tg" \
 *     -d "secret_token=<WEBHOOK_SECRET>"
 */

import { buildSystemPrompt, HANDOFF_TOOL } from "./wegc-kb.js";

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const DEFAULT_MODEL = "claude-sonnet-4-6";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/") {
      return new Response("WEGC AI agent is running.", { status: 200 });
    }

    if (request.method === "GET" && url.pathname === "/health") {
      let dialogs = null;
      if (env.DB) {
        try {
          const row = await env.DB.prepare(
            "SELECT COUNT(*) AS c FROM leads WHERE updated_at >= datetime('now', '-1 day')"
          ).first();
          dialogs = row?.c ?? 0;
        } catch (_) {}
      }
      return Response.json({
        ok: true,
        service: "wegc-ai-agent",
        ts: new Date().toISOString(),
        dialogs_24h: dialogs,
        d1_ok: dialogs !== null,
      });
    }

    // Admin dashboard — lead log
    if (request.method === "GET" && url.pathname === "/admin") {
      if (!env.ADMIN_KEY || url.searchParams.get("key") !== env.ADMIN_KEY) {
        return new Response("forbidden", { status: 403 });
      }
      return renderAdmin(env, url);
    }

    // On-site chat widget endpoint (synchronous: returns Anna's reply)
    if (url.pathname === "/web") {
      const cors = webCors(request, env);
      if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
      if (request.method !== "POST") return new Response("method", { status: 405, headers: cors });
      return handleWeb(request, env, cors);
    }

    // Telegram webhook endpoint
    if (request.method === "POST" && url.pathname === "/tg") {
      // Verify Telegram secret header
      const sig = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
      if (!env.WEBHOOK_SECRET || sig !== env.WEBHOOK_SECRET) {
        return new Response("forbidden", { status: 403 });
      }
      let update;
      try {
        update = await request.json();
      } catch {
        return new Response("bad json", { status: 400 });
      }
      // Respond 200 immediately; process in the background so Telegram
      // does not retry on slow LLM calls.
      ctx.waitUntil(handleUpdate(update, env).catch((e) => console.error("handleUpdate", e)));
      return new Response("ok", { status: 200 });
    }

    return new Response("not found", { status: 404 });
  },
};

async function handleUpdate(update, env) {
  const msg = update.message || update.edited_message;
  if (!msg || !msg.chat) return;
  const chatId = String(msg.chat.id);
  const text = (msg.text || "").trim();
  if (!text) {
    await tg(env, "sendMessage", {
      chat_id: chatId,
      text: "Пришлите, пожалуйста, текстовое сообщение — и я помогу с подбором. 🙂",
    });
    return;
  }

  // /id — utility: reply with this chat id (used to configure OWNER_CHAT_ID)
  if (text === "/id") {
    await tg(env, "sendMessage", {
      chat_id: chatId,
      text: `chat id: ${chatId}`,
    });
    return;
  }

  // /start — greeting, reset conversation
  if (text === "/start" || text === "/reset") {
    await kvSet(env, chatId, { messages: [], handoff: false });
    await tg(env, "sendChatAction", { chat_id: chatId, action: "typing" });
    await tg(env, "sendMessage", {
      chat_id: chatId,
      text:
        "Здравствуйте! Меня зовут Анна, я консультант WEGC по недвижимости на Пхукете. " +
        "Помогу подобрать объект под вашу цель и бюджет и отвечу на вопросы по оплате, рассрочке и оформлению.\n\n" +
        "Расскажите, что ищете? Например: для жизни, под аренду или как инвестицию — и в каком бюджете ориентируетесь.",
    });
    return;
  }

  await tg(env, "sendChatAction", { chat_id: chatId, action: "typing" });

  const identity = {
    convKey: chatId,
    logId: chatId,
    source: "Telegram",
    name: [msg.chat.first_name, msg.chat.last_name].filter(Boolean).join(" "),
    username: msg.chat.username ? `@${msg.chat.username}` : "",
    lang: (msg.from && msg.from.language_code) || "",
  };

  let result;
  try {
    result = await converse(env, identity, text);
  } catch (e) {
    console.error("claude error", e);
    await tg(env, "sendMessage", {
      chat_id: chatId,
      text:
        "Извините, на моей стороне небольшая техническая заминка. " +
        "Напишите ещё раз через минуту или оставьте контакт (Telegram/телефон/email) — менеджер свяжется с вами лично.",
    });
    return;
  }

  const out =
    result.reply ||
    "Спасибо! Передала ваш запрос менеджеру — он свяжется с вами в ближайшее рабочее время. " +
      "Если удобно, подскажите время для короткого онлайн-созвона (Zoom), чтобы показать подходящие объекты.";
  await tg(env, "sendMessage", { chat_id: chatId, text: out, disable_web_page_preview: true });
}

// --- On-site chat widget handler (synchronous request/response) ---
async function handleWeb(request, env, cors) {
  let data;
  try {
    data = await request.json();
  } catch {
    return jsonResp({ error: "bad json" }, 400, cors);
  }
  if (data._gotcha) return jsonResp({ reply: "" }, 200, cors); // honeypot

  const sid = String(data.sid || "").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 64);
  const lang = String(data.lang || "ru").slice(0, 5);
  if (!sid) return jsonResp({ error: "sid required" }, 400, cors);

  // Widget open ping — logs funnel step without calling Claude.
  if (data.event === "open") {
    await logOpen(env, sid, lang);
    return jsonResp({ ok: true }, 200, cors);
  }

  const text = String(data.text || "").trim().slice(0, 2000);
  if (!text) return jsonResp({ error: "text required" }, 400, cors);

  const identity = {
    convKey: `web:${sid}`,
    logId: `web:${sid}`,
    source: "Сайт",
    name: String(data.name || "").slice(0, 80),
    username: String(data.contact || "").slice(0, 120),
    lang,
  };

  try {
    const result = await converse(env, identity, text);
    return jsonResp({ reply: result.reply, handoff: result.handedOff }, 200, cors);
  } catch (e) {
    console.error("web claude error", e);
    return jsonResp(
      {
        reply:
          "Извините, небольшая техническая заминка. Напишите ещё раз через минуту или оставьте " +
          "email/телефон — менеджер свяжется с вами лично.",
      },
      200,
      cors
    );
  }
}

// --- Shared conversation core (channel-agnostic) ---
async function converse(env, identity, userText) {
  const state = (await kvGet(env, identity.convKey)) || { messages: [], handoff: false };
  state.messages.push({ role: "user", content: userText });

  const out = await askClaude(env, state.messages, {
    lang: (identity.lang || "ru").slice(0, 2).toLowerCase(),
    channel: String(identity.convKey).startsWith("web:") ? "web" : "tg",
  });
  const reply = stripMarkdown(out.reply);
  const toolCall = out.toolCall;
  if (reply) state.messages.push({ role: "assistant", content: reply });

  let handedOff = false;
  if (toolCall && !state.handoff) {
    state.handoff = true;
    handedOff = true;
    await notifyOwner(env, identity, toolCall.input);
    await logHandoff(env, identity.logId, toolCall.input);
  }

  const max = parseInt(env.MAX_HISTORY || "24", 10);
  if (state.messages.length > max) state.messages = state.messages.slice(state.messages.length - max);
  await kvSet(env, identity.convKey, state);
  await logTurn(env, identity, state);

  return { reply, toolCall, handedOff };
}

// Strip Markdown artifacts so replies render cleanly as plain text in
// Telegram and the on-site chat (model sometimes uses **bold**, ##, ---, especially in ZH/EN).
function stripMarkdown(s) {
  if (!s) return s;
  let t = String(s);
  t = t.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, "$1: $2"); // [text](url) -> text: url
  t = t.replace(/```[a-zA-Z]*\n?/g, "").replace(/`([^`]+)`/g, "$1"); // code fences/inline
  t = t.replace(/\*\*([^*]+)\*\*/g, "$1").replace(/__([^_]+)__/g, "$1"); // bold
  t = t.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1$2"); // italic *text*
  t = t
    .split("\n")
    .map((line) => {
      if (/^\s*([-*_=~])\1{2,}\s*$/.test(line)) return ""; // hr: ---, ***, ===
      line = line.replace(/^\s*#{1,6}\s+/, ""); // headings
      line = line.replace(/^(\s*)[*+]\s+/, "$1— "); // * / + bullets -> —
      return line;
    })
    .join("\n");
  t = t.replace(/\*\*/g, "").replace(/\n{3,}/g, "\n\n"); // stray markers, collapse blanks
  return t.trim();
}

async function askClaude(env, messages, opts) {
  const model = env.ANTHROPIC_MODEL || DEFAULT_MODEL;
  const body = {
    model,
    max_tokens: 700,
    // Cache the (large) system prompt so bursts of concurrent users reuse it:
    // ~90% cheaper + faster on repeated calls. A few variants (lang/channel) each warm up once.
    system: [{ type: "text", text: buildSystemPrompt(opts || {}), cache_control: { type: "ephemeral" } }],
    tools: [HANDOFF_TOOL],
    messages: messages.map((m) => ({ role: m.role, content: m.content })),
  };

  // Retry transient rate-limit / overload / 5xx with short backoff to smooth bursts.
  let res, lastDetail = "";
  for (let attempt = 0; attempt < 3; attempt++) {
    res = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify(body),
    });
    if (res.ok) break;
    lastDetail = await res.text().catch(() => "");
    const retriable = res.status === 429 || res.status === 529 || res.status >= 500;
    if (!retriable || attempt === 2) {
      throw new Error(`anthropic ${res.status}: ${lastDetail.slice(0, 300)}`);
    }
    const wait = 400 * Math.pow(2, attempt) + Math.floor(Math.random() * 300); // 0.4s, 0.8s (+jitter)
    await new Promise((r) => setTimeout(r, wait));
  }

  const data = await res.json();
  let reply = "";
  let toolCall = null;
  for (const block of data.content || []) {
    if (block.type === "text") reply += block.text;
    else if (block.type === "tool_use" && block.name === HANDOFF_TOOL.name) {
      toolCall = { input: block.input || {} };
    }
  }
  return { reply: reply.trim(), toolCall };
}

async function notifyOwner(env, identity, lead) {
  if (!env.OWNER_CHAT_ID) return;
  const fields = [
    ["Имя", lead.name || identity.name],
    ["Контакт", lead.contact || identity.username || identity.logId],
    ["Цель", lead.goal],
    ["Бюджет", lead.budget],
    ["Район", lead.district],
    ["Сроки", lead.timeline],
    ["Тип", lead.property_type],
    ["Интерес", lead.interested_projects],
  ]
    .filter(([, v]) => v)
    .map(([k, v]) => `<b>${esc(k)}:</b> ${esc(v)}`);

  const text = [
    "🔥 <b>Тёплый лид от AI-агента</b>",
    `Источник: ${esc(identity.source)} · ${esc(identity.username || identity.name || identity.logId)}`,
    "",
    fields.join("\n"),
    "",
    lead.summary ? `<b>Резюме:</b> ${esc(lead.summary)}` : "",
  ]
    .filter(Boolean)
    .join("\n");

  await tg(env, "sendMessage", {
    chat_id: env.OWNER_CHAT_ID,
    text,
    parse_mode: "HTML",
    disable_web_page_preview: true,
  });
}

// --- Telegram helper ---
async function tg(env, method, payload) {
  const res = await fetch(`https://api.telegram.org/bot${env.AGENT_BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ parse_mode: undefined, ...payload }),
  });
  if (!res.ok) console.error(`tg ${method}`, res.status, await res.text().catch(() => ""));
  return res;
}

// --- KV helpers ---
async function kvGet(env, chatId) {
  if (!env.CONV) return null;
  return await env.CONV.get(`conv:${chatId}`, { type: "json" });
}
async function kvSet(env, chatId, state) {
  if (!env.CONV) return;
  // expire stale conversations after 30 days
  await env.CONV.put(`conv:${chatId}`, JSON.stringify(state), { expirationTtl: 60 * 60 * 24 * 30 });
}

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// --- Web CORS / JSON helpers ---
const DEFAULT_WEB_ORIGINS = "https://wegc.fund,https://www.wegc.fund";
function webCors(request, env) {
  const allowed = (env.ALLOWED_ORIGINS || DEFAULT_WEB_ORIGINS).split(",").map((s) => s.trim()).filter(Boolean);
  const origin = request.headers.get("Origin") || "";
  const ok = allowed.includes(origin);
  return {
    "Access-Control-Allow-Origin": ok ? origin : allowed[0],
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}
function jsonResp(obj, status, cors) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...(cors || {}) },
  });
}

// --- D1 lead log ---
async function logOpen(env, sid, lang) {
  if (!env.DB) return;
  const now = new Date().toISOString();
  const chatId = `web:${sid}`;
  try {
    await env.DB.prepare(
      `INSERT INTO leads (chat_id, created_at, updated_at, lang, opened, msg_count, transcript)
       VALUES (?1, ?2, ?2, ?3, 1, 0, '[]')
       ON CONFLICT(chat_id) DO UPDATE SET opened=1, updated_at=?2, lang=COALESCE(?3, lang)`
    )
      .bind(chatId, now, lang || "")
      .run();
  } catch (e) {
    console.error("logOpen", e);
  }
}

function countUserMsgs(transcriptJson) {
  let msgs = [];
  try { msgs = JSON.parse(transcriptJson || "[]"); } catch {}
  return msgs.filter((m) => m.role === "user").length;
}

function isTestSession(r) {
  const s = `${r.chat_id || ""} ${r.username || ""}`;
  return /(?:^|\/)(?:dt_|testweb|burst_|ent\d|pay\d|fpay|lnk|nodown|finish|adversarial|smqc|smqb)/i.test(s)
    || s.includes("olga_test");
}

function funnelStats(rows) {
  const live = rows.filter((r) => !isTestSession(r) && r.status !== "form");
  let opens = 0, sends = 0, engaged = 0, handed = 0;
  for (const r of live) {
    const users = countUserMsgs(r.transcript);
    const total = (() => { try { return JSON.parse(r.transcript || "[]").length; } catch { return 0; } })();
    if (r.opened || users > 0 || total > 0) opens++;
    if (users >= 1) sends++;
    if (users >= 1 && total >= 3) engaged++;
    if (r.status === "handed_off") handed++;
  }
  return { live: live.length, opens, sends, engaged, handed };
}

async function logTurn(env, identity, state) {
  if (!env.DB) return;
  const now = new Date().toISOString();
  try {
    await env.DB.prepare(
      `INSERT INTO leads (chat_id, created_at, updated_at, name, username, lang, opened, msg_count, transcript)
       VALUES (?1, ?2, ?2, ?3, ?4, ?5, 1, ?6, ?7)
       ON CONFLICT(chat_id) DO UPDATE SET
         updated_at=?2, name=COALESCE(NULLIF(?3,''),name), username=COALESCE(NULLIF(?4,''),username),
         lang=?5, opened=1, msg_count=?6, transcript=?7`
    )
      .bind(identity.logId, now, identity.name || "", identity.username || "", identity.lang || "", state.messages.length, JSON.stringify(state.messages))
      .run();
  } catch (e) {
    console.error("logTurn", e);
  }
}

async function logHandoff(env, chatId, lead) {
  if (!env.DB) return;
  const now = new Date().toISOString();
  try {
    await env.DB.prepare(
      `UPDATE leads SET status='handed_off', updated_at=?1,
         goal=?2, budget=?3, district=?4, timeline=?5, property_type=?6,
         interested_projects=?7, summary=?8,
         name=COALESCE(NULLIF(?9,''), name)
       WHERE chat_id=?10`
    )
      .bind(
        now,
        lead.goal || "",
        lead.budget || "",
        lead.district || "",
        lead.timeline || "",
        lead.property_type || "",
        lead.interested_projects || "",
        lead.summary || "",
        lead.name || "",
        chatId
      )
      .run();
  } catch (e) {
    console.error("logHandoff", e);
  }
}

async function renderAdmin(env, url) {
  if (!env.DB) return new Response("D1 not bound", { status: 500 });
  const statusFilter = url.searchParams.get("status");
  let rows = [];
  try {
    const q = statusFilter
      ? env.DB.prepare("SELECT * FROM leads WHERE status=?1 ORDER BY updated_at DESC LIMIT 300").bind(statusFilter)
      : env.DB.prepare("SELECT * FROM leads ORDER BY updated_at DESC LIMIT 300");
    const res = await q.all();
    rows = res.results || [];
  } catch (e) {
    return new Response("DB error: " + e.message, { status: 500 });
  }

  const key = esc(url.searchParams.get("key") || "");
  const total = rows.length;
  const handed = rows.filter((r) => r.status === "handed_off").length;
  const forms = rows.filter((r) => r.status === "form").length;
  const funnel = funnelStats(rows);
  const pct = (n, d) => (d ? Math.round((n / d) * 100) : 0);

  const fmtTime = (iso) => {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString("ru-RU", { timeZone: "Asia/Bangkok", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
  };

  const cards = rows.map((r) => {
    let msgs = [];
    try { msgs = JSON.parse(r.transcript || "[]"); } catch {}
    const transcript = msgs
      .map((m) => {
        const who = m.role === "user" ? "Клиент" : "Анна";
        const cls = m.role === "user" ? "u" : "a";
        return `<div class="b ${cls}"><span class="who">${who}</span>${esc(m.content)}</div>`;
      })
      .join("");
    const qual = [
      ["Цель", r.goal],
      ["Бюджет", r.budget],
      ["Район", r.district],
      ["Сроки", r.timeline],
      ["Тип", r.property_type],
      ["Интерес", r.interested_projects],
    ].filter(([, v]) => v).map(([k, v]) => `<span class="chip"><b>${k}:</b> ${esc(v)}</span>`).join("");
    const badge = r.status === "handed_off"
      ? '<span class="badge hot">🔥 Передан</span>'
      : r.status === "form"
      ? '<span class="badge form">📩 Заявка</span>'
      : '<span class="badge new">в работе</span>';
    return `<div class="card">
      <div class="hd">
        <div>
          <div class="nm">${esc(r.name || "Без имени")} ${badge}</div>
          <div class="meta">${esc(r.username || ("id " + r.chat_id))} · ${esc(r.lang || "—")} · ${r.msg_count || 0} сообщ. · ${fmtTime(r.updated_at)}</div>
        </div>
      </div>
      ${qual ? `<div class="chips">${qual}</div>` : ""}
      ${r.summary ? `<div class="sum">${esc(r.summary)}</div>` : ""}
      <details><summary>Переписка (${msgs.length})</summary><div class="tr">${transcript}</div></details>
    </div>`;
  }).join("");

  const html = `<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>WEGC · База обращений</title>
<style>
  :root{--gold:#b8945e;--bg:#0c0f17;--card:#141925;--line:#232a39;--muted:#8b95a7}
  *{box-sizing:border-box}body{margin:0;background:var(--bg);color:#e8edf5;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;padding:18px}
  h1{font-size:19px;margin:0 0 4px}.top{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:16px}
  .stat{color:var(--muted);font-size:13px}.filters a{color:var(--gold);text-decoration:none;font-size:13px;margin-left:12px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:12px}
  .hd{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
  .nm{font-weight:600;font-size:15px}.meta{color:var(--muted);font-size:12.5px;margin-top:3px}
  .badge{font-size:11px;padding:2px 8px;border-radius:999px;margin-left:6px;vertical-align:middle}
  .badge.hot{background:rgba(214,120,90,.18);color:#e88b6f}.badge.new{background:rgba(120,160,255,.14);color:#8fb0ff}
  .badge.form{background:rgba(184,148,94,.2);color:#d8b277}
  .chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 4px}
  .chip{background:rgba(184,148,94,.1);border:1px solid rgba(184,148,94,.3);color:#d8c3a0;font-size:12px;padding:3px 9px;border-radius:6px}
  .chip b{color:#b8945e;font-weight:600}
  .sum{margin:8px 0 4px;font-size:13.5px;color:#cdd6e4}
  details{margin-top:8px}summary{cursor:pointer;color:var(--gold);font-size:13px}
  .tr{margin-top:10px;display:flex;flex-direction:column;gap:6px}
  .b{padding:8px 11px;border-radius:9px;font-size:13.5px;white-space:pre-wrap;max-width:90%}
  .b .who{display:block;font-size:10.5px;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:.05em}
  .b.u{background:#1b2231;align-self:flex-end}.b.a{background:#10261c;align-self:flex-start}
  .funnel{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 18px}
  .fstep{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
  .fstep .n{font-size:22px;font-weight:700;color:var(--gold)}.fstep .l{font-size:12px;color:var(--muted);margin-top:2px}
  .fstep .p{font-size:11px;color:#6b7585;margin-top:4px}
  .funnel-note{color:var(--muted);font-size:12px;margin:-8px 0 14px}
  @media(max-width:720px){.funnel{grid-template-columns:repeat(2,1fr)}}
</style></head><body>
<div class="top">
  <div><h1>WEGC · База обращений</h1><div class="stat">Всего: ${total} · заявки с форм: ${forms} · передано менеджеру: ${handed} · без тестов: ${funnel.live}</div></div>
  <div class="filters">Фильтр:
    <a href="?key=${key}">все</a>
    <a href="?key=${key}&status=form">📩 заявки</a>
    <a href="?key=${key}&status=handed_off">🔥 тёплые</a>
    <a href="?key=${key}&status=new">в работе</a>
  </div>
</div>
<div class="funnel">
  <div class="fstep"><div class="n">${funnel.opens}</div><div class="l">Открыли чат</div><div class="p">chat_open</div></div>
  <div class="fstep"><div class="n">${funnel.sends}</div><div class="l">Написали</div><div class="p">${pct(funnel.sends, funnel.opens)}% от open · chat_send</div></div>
  <div class="fstep"><div class="n">${funnel.engaged}</div><div class="l">Диалог 3+ сообщ.</div><div class="p">${pct(funnel.engaged, funnel.sends)}% от send</div></div>
  <div class="fstep"><div class="n">${funnel.handed}</div><div class="l">Тёплые лиды</div><div class="p">${pct(funnel.handed, funnel.sends)}% от send · chat_lead</div></div>
</div>
<div class="funnel-note">Воронка без тестовых сессий (dt_, burst_, olga_test и др.). «Открыли» — ping с сайта + сессии с сообщениями.</div>
${cards || '<div class="stat">Пока пусто — обращений нет.</div>'}
</body></html>`;

  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
}
