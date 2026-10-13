import { randomUUID } from 'node:crypto';

const SITE = 'https://bespoke-elf-196a9d1.netlify.app';
const FORM_NAME = 'wegc-agent-commission';
const PAGE = 'https://wegc.fund/7718426309/';
const ALLOWED_ORIGINS = new Set(['https://wegc.fund', 'https://www.wegc.fund', SITE]);
const MAX_BYTES = 16384;
const FIELDS = { name: 120, contact: 240, project: 240, commission: 120, comment: 2000 };
const CHOICES = {
  profile: ['Независимый агент-физлицо', 'Тайская компания / агентство', 'Иностранный агент / иностранная компания'],
  payout: ['Криптовалюта', 'Наличные', 'Обсудить варианты'],
  stage: ['Есть клиент / готов регистрировать', 'Клиент выбирает объект', 'Планирую следующие сделки'],
};

function reply(request, status, data) {
  const origin = request.headers.get('origin');
  const headers = { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', Vary: 'Origin' };
  if (ALLOWED_ORIGINS.has(origin)) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS';
    headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept';
  }
  if (status === 204) return new Response(null, { status, headers });
  if (request.headers.get('accept')?.includes('text/html')) {
    headers['Content-Type'] = 'text/html; charset=utf-8';
    headers['Content-Security-Policy'] = "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'";
    const title = data.ok ? 'Запрос передан' : 'Не удалось отправить запрос';
    const message = data.ok ? 'Заявка передана системе приёма. После проверки мы свяжемся с вами по указанному контакту.' : 'Приём заявки не подтверждён. Вернитесь к форме и проверьте данные. Если ошибка повторяется, напишите на post@wegc.fund.';
    return new Response(`<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title} · WEGC</title><style>body{max-width:640px;margin:10vh auto;padding:24px;font:18px/1.6 system-ui;color:#0f172a}a{color:#80603c}</style><h1>${title}</h1><p>${message}</p><a href="${PAGE}#lead">Вернуться к странице WEGC</a></html>`, { status, headers });
  }
  headers['Content-Type'] = 'application/json; charset=utf-8';
  return new Response(JSON.stringify(data), { status, headers });
}

async function readBody(request) {
  if (Number(request.headers.get('content-length')) > MAX_BYTES) throw new RangeError('size');
  const reader = request.body?.getReader();
  if (!reader) return '';
  const chunks = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > MAX_BYTES) { await reader.cancel(); throw new RangeError('size'); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return new TextDecoder('utf-8', { fatal: true }).decode(bytes);
}

export default async function handler(request) {
  const origin = request.headers.get('origin');
  if (!ALLOWED_ORIGINS.has(origin)) return reply(request, 403, { ok: false, error: 'origin' });
  if (request.method === 'OPTIONS') return reply(request, 204, {});
  if (request.method !== 'POST') return reply(request, 405, { ok: false, error: 'method' });
  const contentType = (request.headers.get('content-type') || '').split(';')[0].trim();
  if (contentType !== 'application/x-www-form-urlencoded') return reply(request, 415, { ok: false, error: 'content_type' });

  let params;
  try { params = new URLSearchParams(await readBody(request)); }
  catch (error) { return reply(request, error instanceof RangeError ? 413 : 400, { ok: false, error: 'payload' }); }
  const allowed = new Set([...Object.keys(FIELDS), ...Object.keys(CHOICES), 'form-name', 'bot-field']);
  for (const key of params.keys()) {
    if (!allowed.has(key) || params.getAll(key).length !== 1) return reply(request, 422, { ok: false, error: 'fields' });
  }
  if (params.get('bot-field') || params.get('form-name') !== FORM_NAME) return reply(request, 422, { ok: false, error: 'fields' });

  const clean = {};
  for (const [field, max] of Object.entries(FIELDS)) {
    const value = (params.get(field) || '').trim();
    const controls = field === 'comment' ? /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/ : /[\u0000-\u001f\u007f]/;
    if (value.length > max || controls.test(value) || (['name', 'contact', 'project'].includes(field) && !value)) {
      return reply(request, 422, { ok: false, error: 'validation', field });
    }
    clean[field] = value;
  }
  for (const [field, choices] of Object.entries(CHOICES)) {
    const value = params.get(field);
    if (!choices.includes(value)) return reply(request, 422, { ok: false, error: 'validation', field });
    clean[field] = value;
  }

  const reference = randomUUID();
  const payload = new URLSearchParams({
    'form-name': FORM_NAME, 'bot-field': '', ...clean,
    reference, source: PAGE, subject: `WEGC — заявка агента — ${reference}`,
  });
  try {
    const upstream = await fetch(`${SITE}/7718426309/lead-receiver.html`, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: payload.toString(), signal: AbortSignal.timeout(12000), redirect: 'manual',
    });
    if (!upstream.ok && ![302, 303].includes(upstream.status)) return reply(request, 502, { ok: false, error: 'receiver', reference });
    return reply(request, 200, { ok: true, status: 'submitted', reference });
  } catch {
    return reply(request, 503, { ok: false, error: 'unconfirmed', reference });
  }
}

export const config = {
  rateLimit: { action: 'rate_limit', aggregateBy: 'ip', windowSize: 60, windowLimit: 10 },
};
