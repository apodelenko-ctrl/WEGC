// Channel discovery: searches Telegram globally for Phuket-property channels,
// expands via "similar channels" recommendations, ranks by subscribers, and
// writes discovered.json + sends a numbered shortlist to your Telegram for review.
import { TelegramClient, Api } from "telegram";
import { StringSession } from "telegram/sessions/index.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_FILE = path.join(__dirname, "discovered.json");

const apiId = Number(process.env.TG_API_ID);
const apiHash = process.env.TG_API_HASH;
const session = process.env.TG_SESSION;
const BOT_TOKEN = process.env.TG_BOT_TOKEN;
const OWNER_CHAT_ID = process.env.OWNER_CHAT_ID;

function die(m) { console.error(m); process.exit(1); }
if (!apiId || !apiHash || !session) die("Missing TG_API_ID / TG_API_HASH / TG_SESSION.");

const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, "discover-queries.json"), "utf8"));
const queries = cfg.queries || [];
const relWords = (cfg.relevanceWords || []).map((w) => w.toLowerCase());
const TOP_TO_SEND = Number(process.env.TOP_TO_SEND || 40);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Fresh accounts get hit with long FLOOD_WAITs. Never block the whole run on
// one huge wait: skip calls whose required wait exceeds MAX_WAIT_S, and stop the
// expensive phases once the overall TIME_BUDGET is exhausted. We still write
// whatever was collected so the shortlist is always produced.
const MAX_WAIT_S = Number(process.env.MAX_WAIT_S || 45);
const TIME_BUDGET_MS = Number(process.env.TIME_BUDGET_MS || 5 * 60 * 1000);
const startedAt = Date.now();
const overBudget = () => Date.now() - startedAt > TIME_BUDGET_MS;
// Returns true if we slept (wait acceptable), false if the wait was skipped.
async function handleFlood(e) {
  if (e.seconds == null) return false;
  if (e.seconds > MAX_WAIT_S) {
    console.error(`flood wait ${e.seconds}s > ${MAX_WAIT_S}s — skipping call`);
    return false;
  }
  await sleep((e.seconds + 1) * 1000);
  return true;
}

const found = new Map(); // id -> {id, username, title, participants, about}

function relevant(title, about) {
  const t = (title + " " + (about || "")).toLowerCase();
  return relWords.some((w) => t.includes(w));
}
function addChannel(ch) {
  if (!ch || !(ch instanceof Api.Channel)) return;
  if (ch.broadcast === false && ch.megagroup !== true) { /* keep both broadcast & groups */ }
  const id = ch.id?.toString?.() || String(ch.id);
  if (found.has(id)) return;
  found.set(id, {
    id,
    username: ch.username || null,
    title: ch.title || "",
    participants: typeof ch.participantsCount === "number" ? ch.participantsCount : 0,
    about: "",
    _entity: ch,
  });
}

const client = new TelegramClient(new StringSession(session), apiId, apiHash, { connectionRetries: 5 });
await client.connect();

// 1) Global search by queries
for (const q of queries) {
  if (overBudget()) { console.error("time budget reached during search — stopping queries"); break; }
  try {
    const res = await client.invoke(new Api.contacts.Search({ q, limit: 50 }));
    (res.chats || []).forEach(addChannel);
    console.log(`search "${q}": +${(res.chats || []).length} chats (total ${found.size})`);
    await sleep(700);
  } catch (e) {
    console.error(`search "${q}" error: ${e.message}`);
    await handleFlood(e);
  }
}

// 2) Expand via "similar channels" for the strongest seeds (only those with username)
const seeds = [...found.values()].filter((c) => c.username).slice(0, 25);
for (const seed of seeds) {
  if (overBudget()) { console.error("time budget reached during recommendations — stopping"); break; }
  try {
    const rec = await client.invoke(new Api.channels.GetChannelRecommendations({ channel: seed._entity }));
    (rec.chats || []).forEach(addChannel);
    await sleep(700);
  } catch (e) {
    await handleFlood(e);
  }
}
console.log(`After recommendations: ${found.size} channels`);

// 3) Enrich top candidates with participants + about (cap calls to avoid flood)
const list = [...found.values()].filter((c) => c.username);
list.sort((a, b) => b.participants - a.participants);
const ENRICH_CAP = Number(process.env.ENRICH_CAP || 60);
const toEnrich = list.slice(0, ENRICH_CAP);
for (const c of toEnrich) {
  if (overBudget()) { console.error("time budget reached during enrichment — stopping"); break; }
  try {
    const full = await client.invoke(new Api.channels.GetFullChannel({ channel: c._entity }));
    const fc = full.fullChat;
    if (fc) {
      c.participants = fc.participantsCount || c.participants;
      c.about = (fc.about || "").slice(0, 200);
    }
    await sleep(350);
  } catch (e) {
    await handleFlood(e);
  }
}
// 4) Filter by relevance, sort, write file
const ranked = [...found.values()]
  .filter((c) => c.username && relevant(c.title, c.about))
  .map(({ _entity, ...rest }) => rest)
  .sort((a, b) => b.participants - a.participants);

fs.writeFileSync(OUT_FILE, JSON.stringify(ranked, null, 2));
console.log(`\nWrote ${ranked.length} relevant channels to discovered.json`);
console.log("Ready-to-paste usernames (top 40):");
console.log(ranked.slice(0, 40).map((c) => "@" + c.username).join(", "));

// 5) Send a numbered shortlist to Telegram for review (if bot configured)
if (BOT_TOKEN && OWNER_CHAT_ID && ranked.length) {
  const lines = ranked.slice(0, TOP_TO_SEND).map((c, i) =>
    `${i + 1}. @${c.username} — ${c.title} (${c.participants.toLocaleString("ru-RU")} подп.)` +
    (c.about ? `\n    ${c.about.replace(/\n/g, " ")}` : "")
  );
  const header = `🔎 Найдено каналов по теме Пхукет/недвижимость: ${ranked.length}. Топ-${Math.min(TOP_TO_SEND, ranked.length)} по подписчикам:\n\n`;
  const text = header + lines.join("\n") + `\n\nОтветь номерами нужных (например: 1,3,5,8) — добавлю их в мониторинг.`;
  for (let i = 0; i < text.length; i += 3800) {
    const chunk = text.slice(i, i + 3800);
    const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: OWNER_CHAT_ID, text: chunk, disable_web_page_preview: true }),
    });
    if (!res.ok) console.error("telegram send failed:", res.status, await res.text().catch(() => ""));
  }
  console.log(`Sent shortlist (top ${TOP_TO_SEND}) to Telegram.`);
}

// Disconnect can hang in CI (GramJS); never let it block the run. The file is
// already written and the shortlist already sent above.
await Promise.race([
  client.disconnect().catch(() => {}),
  sleep(5000),
]);
process.exit(0);
