// Daily collector: reads monitored Telegram channels, asks Claude to extract
// new-project events (presentation / presale / launch / new phase / price change),
// builds a Russian morning digest and sends it to OWNER_CHAT_ID via a Telegram bot.
import { TelegramClient } from "telegram";
import { StringSession } from "telegram/sessions/index.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const STATE_FILE = path.join(__dirname, ".state.json");

const apiId = Number(process.env.TG_API_ID);
const apiHash = process.env.TG_API_HASH;
const session = process.env.TG_SESSION;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const ANTHROPIC_MODEL = process.env.ANTHROPIC_MODEL || "claude-sonnet-4-6";
const BOT_TOKEN = process.env.TG_BOT_TOKEN;
const OWNER_CHAT_ID = process.env.OWNER_CHAT_ID;

const LOOKBACK_HOURS = Number(process.env.LOOKBACK_HOURS || 30);
const MAX_PER_CHANNEL = 80;
const MAX_CANDIDATES = 120;

function die(m) { console.error(m); process.exit(1); }
if (!apiId || !apiHash || !session) die("Missing TG_API_ID / TG_API_HASH / TG_SESSION.");
if (!ANTHROPIC_API_KEY) die("Missing ANTHROPIC_API_KEY.");
if (!BOT_TOKEN || !OWNER_CHAT_ID) die("Missing TG_BOT_TOKEN / OWNER_CHAT_ID.");

const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, "channels.json"), "utf8"));
const channels = (cfg.channels || []).filter((c) => c && !c.startsWith("@example"));
const keywords = (cfg.keywords || []).map((k) => k.toLowerCase());
if (!channels.length) die("channels.json has no real channels yet (only examples). Add channels and re-run.");

let state = {};
try { state = JSON.parse(fs.readFileSync(STATE_FILE, "utf8")); } catch { state = {}; }

function normUser(c) {
  return c.replace(/^https?:\/\/t\.me\//, "").replace(/^@/, "").replace(/\/.*$/, "").trim();
}
function matchesKeyword(text) {
  const t = text.toLowerCase();
  return keywords.some((k) => t.includes(k));
}

const client = new TelegramClient(new StringSession(session), apiId, apiHash, { connectionRetries: 5 });
await client.connect();

const sinceTs = Math.floor(Date.now() / 1000) - LOOKBACK_HOURS * 3600;
const candidates = [];
const newState = { ...state };

for (const raw of channels) {
  const uname = normUser(raw);
  try {
    const entity = await client.getEntity(uname);
    const lastId = state[uname] || 0;
    const opts = { limit: MAX_PER_CHANNEL };
    if (lastId) opts.minId = lastId;
    const msgs = await client.getMessages(entity, opts);
    let maxId = lastId;
    for (const m of msgs) {
      if (m.id > maxId) maxId = m.id;
      const text = (m.message || "").trim();
      if (!text) continue;
      if (!lastId && m.date < sinceTs) continue; // first run: only recent
      if (!matchesKeyword(text)) continue;
      const link = entity.username ? `https://t.me/${entity.username}/${m.id}` : `(${uname})`;
      candidates.push({
        channel: entity.title || uname,
        date: new Date(m.date * 1000).toISOString().slice(0, 16).replace("T", " "),
        link,
        text: text.slice(0, 600),
      });
    }
    newState[uname] = maxId;
    console.log(`[${uname}] scanned ${msgs.length}, new candidates so far ${candidates.length}`);
  } catch (e) {
    console.error(`[${uname}] ERROR: ${e.message}`);
  }
}
await client.disconnect();

fs.writeFileSync(STATE_FILE, JSON.stringify(newState, null, 2));

const today = new Date().toLocaleDateString("ru-RU", { day: "numeric", month: "long", timeZone: "Asia/Bangkok" });

if (!candidates.length) {
  await sendTelegram(`📭 Дайджест Пхукет / новостройки — ${today}\n\nЗначимых анонсов за сутки не найдено. Бот отработал штатно.`);
  console.log("No candidates. Sent empty digest.");
  process.exit(0);
}

const trimmed = candidates.slice(0, MAX_CANDIDATES);
const blob = trimmed
  .map((c, i) => `#${i + 1} [${c.channel}] (${c.date})\nИсточник: ${c.link}\n${c.text}`)
  .join("\n\n---\n\n");

const digest = await askClaude(blob, today);
await sendTelegram(digest);
console.log("Digest sent. Candidates:", trimmed.length);
process.exit(0);

// ---------------- helpers ----------------
async function askClaude(blob, today) {
  const system =
    "Ты — аналитик рынка недвижимости Пхукета. На вход даны сообщения из Telegram-каналов застройщиков, " +
    "агентств и новостников за последние сутки. Твоя задача — собрать КОРОТКИЙ утренний дайджест ТОЛЬКО про значимые события " +
    "по новостройкам: презентация/ивент проекта, старт пресейла, старт продаж, новый этап/фаза, изменение цен, новый запуск. " +
    "Игнорируй обычную рекламу готовых юнитов, мемы, оффтоп, повторы. " +
    "Для каждого события укажи (если есть): застройщик, проект, тип события, дата/время, место, и обязательно ссылку-источник. " +
    "Сгруппируй по типу события, объединяй дубли об одном и том же. Пиши по-русски, обычным текстом без markdown (без **, ##, ---). " +
    "Будь фактологичен: не выдумывай то, чего нет в сообщениях. Если значимых событий нет — напиши одну строку об этом.";
  const userMsg =
    `Дата: ${today}. Сообщения за сутки ниже. Сделай дайджест.\n\n` + blob +
    `\n\nФормат ответа:\nПервая строка: "📅 Дайджест Пхукет / новостройки — ${today}". ` +
    `Далее события с эмодзи-маркерами (🏗 презентация, 🔥 пресейл/старт продаж, 🆕 новый проект, 💸 цены/этап). ` +
    `Каждое событие 1–2 строки + строка "Источник: <ссылка>". Без воды.`;

  for (let attempt = 0; attempt < 3; attempt++) {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: ANTHROPIC_MODEL,
        max_tokens: 1800,
        system,
        messages: [{ role: "user", content: userMsg }],
      }),
    });
    if (res.ok) {
      const data = await res.json();
      return (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("").trim() ||
        `📅 Дайджест Пхукет / новостройки — ${today}\n\n(пустой ответ модели)`;
    }
    if (res.status === 429 || res.status >= 500) {
      await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
      continue;
    }
    const detail = await res.text().catch(() => "");
    throw new Error(`anthropic ${res.status}: ${detail.slice(0, 200)}`);
  }
  throw new Error("anthropic: retries exhausted");
}

async function sendTelegram(text) {
  const chunks = [];
  for (let i = 0; i < text.length; i += 3800) chunks.push(text.slice(i, i + 3800));
  for (const chunk of chunks) {
    const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: OWNER_CHAT_ID, text: chunk, disable_web_page_preview: true }),
    });
    if (!res.ok) console.error("telegram send failed:", res.status, await res.text().catch(() => ""));
  }
}
