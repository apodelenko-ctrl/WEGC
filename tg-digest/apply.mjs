// Apply selected channels from discovered.json into channels.json.
// Usage: node apply.mjs 1,3,5,8   (1-based indices from the discovery shortlist)
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const arg = process.argv[2] || "";
const idxs = arg.split(/[,\s]+/).map((s) => parseInt(s.trim(), 10)).filter((n) => n > 0);
if (!idxs.length) { console.error('Usage: node apply.mjs "1,3,5,8"'); process.exit(1); }

const disc = JSON.parse(fs.readFileSync(path.join(__dirname, "discovered.json"), "utf8"));
const chPath = path.join(__dirname, "channels.json");
const ch = JSON.parse(fs.readFileSync(chPath, "utf8"));

const picked = idxs.map((i) => disc[i - 1]).filter(Boolean).map((c) => "@" + c.username);
const existing = (ch.channels || []).filter((c) => c && !c.startsWith("@example"));
ch.channels = [...new Set([...existing, ...picked])];

fs.writeFileSync(chPath, JSON.stringify(ch, null, 2));
console.log(`Added ${picked.length} channels. channels.json now monitors ${ch.channels.length}:`);
console.log(ch.channels.join(", "));
console.log("\nReminder: join these channels from the collector account before the next digest run.");
