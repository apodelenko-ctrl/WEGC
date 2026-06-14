// One-time login to generate a Telegram USER session string.
// Run locally:  TG_API_ID=... TG_API_HASH=... npm run login
// Then copy the printed SESSION string into the GitHub secret TG_SESSION.
import { TelegramClient } from "telegram";
import { StringSession } from "telegram/sessions/index.js";
import input from "input";

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

console.log("\n================ COPY THIS into GitHub secret TG_SESSION ================\n");
console.log(client.session.save());
console.log("\n========================================================================\n");
await client.disconnect();
process.exit(0);
