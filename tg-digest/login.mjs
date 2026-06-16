// One-time login to generate a Telegram USER session string.
// Run locally:  TG_API_ID=... TG_API_HASH=... npm run login
// Then copy the printed SESSION string into the GitHub secret TG_SESSION.
import { TelegramClient } from "telegram";
import { StringSession } from "telegram/sessions/index.js";
import input from "input";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SESSION_FILE = path.join(__dirname, ".session"); // gitignored

const apiId = Number(process.env.TG_API_ID);
const apiHash = process.env.TG_API_HASH;

if (!apiId || !apiHash) {
  console.error("Set TG_API_ID and TG_API_HASH (from https://my.telegram.org → API development tools).");
  process.exit(1);
}

const client = new TelegramClient(new StringSession(""), apiId, apiHash, { connectionRetries: 5 });

await client.start({
  phoneNumber: async () => await input.text("Phone number (with country code, e.g. +66...): "),
  password: async () => await input.text("2FA password (leave empty if none): "),
  phoneCode: async () => await input.text("Login code from Telegram: "),
  onError: (e) => console.error(e),
});

const sessionStr = client.session.save();
fs.writeFileSync(SESSION_FILE, sessionStr, { mode: 0o600 });
await client.disconnect();

// Self-verify: reconnect from the SAVED string exactly as CI will, so we never
// store a session that can't reconnect (the previous failure mode).
const withTimeout = (p, ms, l) => Promise.race([p, new Promise((_, r) => setTimeout(() => r(new Error("timeout " + l)), ms))]);
const verify = new TelegramClient(new StringSession(sessionStr), apiId, apiHash, { connectionRetries: 3 });
let ok = false;
try {
  await withTimeout(verify.connect(), 25000, "connect");
  const me = await withTimeout(verify.getMe(), 15000, "getMe");
  ok = true;
  console.log(`\n✅ Session VERIFIED — reconnect works. Logged in as: ${me?.username ? "@" + me.username : me?.firstName} (id ${me?.id?.toString?.()})`);
} catch (e) {
  console.error(`\n❌ Session did NOT reconnect: ${e.message}\nDo not use this session; re-run login.`);
} finally {
  await Promise.race([verify.disconnect().catch(() => {}), new Promise((r) => setTimeout(r, 3000))]);
}

if (ok) {
  console.log(`\nSaved verified session to: ${SESSION_FILE}`);
  console.log("Tell the assistant it's done — it will read this file and update the GitHub secret automatically.");
}
process.exit(ok ? 0 : 1);
