#!/usr/bin/env bun
/**
 * Telegram intake bridge — persistent data pipe (NOT a Claude agent).
 *
 * Long-polls Telegram as the sole getUpdates consumer and routes everything the
 * Visionary sends from his phone into the right project's intake, so the cloud
 * agent reads it on its own schedule. Project tagging:
 *   - message starts with a tag (A/B/C, "Project C", "#B", "C:", etc.) -> that project
 *   - otherwise -> general operations
 * Acks each message with where it landed. Allowlisted to one chat.
 */
import { readFileSync, writeFileSync, appendFileSync, mkdirSync, existsSync } from 'fs'
import { join } from 'path'

const VAULT = '/config/workspace/operations/.secrets/.env'
const STATE_PID = '/config/.claude/channels/telegram/bot.pid'
const ROOT = '/config/workspace/operations/intake'
const MEDIA = join(ROOT, 'media')
const OFFSET_FILE = join(ROOT, '.offset')

const ROUTES: Record<string, { dir: string; label: string }> = {
  A:       { dir: join(ROOT, 'project-a'), label: 'Project A · AI News' },
  B:       { dir: join(ROOT, 'project-b'), label: 'Project B · Old Money' },
  C:       { dir: join(ROOT, 'project-c'), label: 'Project C · AI Agency' },
  GENERAL: { dir: join(ROOT, 'general'),   label: 'General Operations' },
}

function env(k: string): string {
  for (const line of readFileSync(VAULT, 'utf8').split('\n')) {
    const m = line.match(/^(\w+)=(.*)$/); if (m && m[1] === k) return m[2].trim()
  }
  throw new Error(`missing ${k}`)
}
const TOKEN = env('TELEGRAM_BOT_TOKEN'); const ALLOW = env('TELEGRAM_CHAT_ID')
const API = `https://api.telegram.org/bot${TOKEN}`

mkdirSync(MEDIA, { recursive: true })
for (const r of Object.values(ROUTES)) {
  mkdirSync(r.dir, { recursive: true })
  const f = join(r.dir, 'feed.md')
  if (!existsSync(f)) writeFileSync(f, `# ${r.label} — intake feed\n\nResources the Visionary sends from his phone for this project. Newest at the bottom.\n`)
}

// --- project routing -------------------------------------------------------
function routeFor(text: string): keyof typeof ROUTES {
  const t = text.trim()
  // explicit leading tag: [C]  #B  C:  C-  C)  project C  proj A  p:B
  const m = t.match(/^\s*(?:\[\s*([abc])\s*\]|#\s*([abc])\b|(?:project|proj|p)\s*:?\s*([abc])\b|([abc])\s*[:\-)–])/i)
  const tag = (m && (m[1] || m[2] || m[3] || m[4]))?.toUpperCase()
  if (tag && ROUTES[tag]) return tag as keyof typeof ROUTES
  // keyword fallback
  const l = t.toLowerCase()
  if (/\bai news\b|breaking news|trending ai/.test(l)) return 'A'
  if (/\bold money\b|edmund|tuxedo|private jet/.test(l)) return 'B'
  if (/\bagency\b|avatar|digital twin|prospect|outreach|client\b/.test(l)) return 'C'
  return 'GENERAL'
}

function readOffset(): number { try { return parseInt(readFileSync(OFFSET_FILE, 'utf8'), 10) || 0 } catch { return 0 } }
function writeOffset(n: number): void { writeFileSync(OFFSET_FILE, String(n)) }
function claimSlot(): void {
  try { const h = parseInt(readFileSync(STATE_PID, 'utf8'), 10); if (h > 1 && h !== process.pid) { try { process.kill(h, 'SIGTERM') } catch {} } } catch {}
  try { writeFileSync(STATE_PID, String(process.pid)) } catch {}
}
async function tg(method: string, params: Record<string, unknown>): Promise<any> {
  const res = await fetch(`${API}/${method}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(params) })
  return res.json()
}
async function download(fileId: string, label: string): Promise<string | null> {
  try {
    const f = await tg('getFile', { file_id: fileId }); const path = f?.result?.file_path; if (!path) return null
    const res = await fetch(`https://api.telegram.org/file/bot${TOKEN}/${path}`)
    const buf = Buffer.from(await res.arrayBuffer())
    const ext = (path.split('.').pop() || 'bin').replace(/[^a-z0-9]/gi, '') || 'bin'
    const out = join(MEDIA, `${Date.now()}-${label}.${ext}`); writeFileSync(out, buf); return out
  } catch { return null }
}

async function handle(msg: any): Promise<void> {
  const chatId = String(msg.chat?.id ?? ''); if (chatId !== ALLOW) return
  const text = msg.text ?? msg.caption ?? ''
  const route = routeFor(text); const dest = ROUTES[route]
  const ts = new Date((msg.date ?? 0) * 1000).toISOString()
  const lines: string[] = [`## ${ts}`]; if (text) lines.push(text)
  let saved: string | null = null
  if (msg.photo) saved = await download(msg.photo[msg.photo.length - 1].file_id, 'photo')
  else if (msg.document) saved = await download(msg.document.file_id, (msg.document.file_name || 'doc').replace(/[^a-z0-9._-]/gi, '_'))
  else if (msg.video) saved = await download(msg.video.file_id, 'video')
  else if (msg.voice) saved = await download(msg.voice.file_id, 'voice')
  if (saved) lines.push(`[media saved] ${saved}`)
  appendFileSync(join(dest.dir, 'feed.md'), `\n${lines.join('\n')}\n`)
  await tg('sendMessage', { chat_id: chatId, text: `✓ Filed to ${dest.label}. I'll pick it up.` })
}

async function main(): Promise<void> {
  claimSlot(); let offset = readOffset()
  process.stderr.write(`telegram-intake: polling (offset=${offset})\n`)
  for (;;) {
    try {
      const res = await fetch(`${API}/getUpdates?timeout=50&offset=${offset}`, { signal: AbortSignal.timeout(60000) })
      const data = await res.json()
      if (data?.error_code === 409) { claimSlot(); await new Promise(r => setTimeout(r, 1500)); continue }
      if (!data?.ok) { await new Promise(r => setTimeout(r, 2000)); continue }
      for (const u of data.result) {
        offset = u.update_id + 1
        const m = u.message ?? u.channel_post
        if (m) { try { await handle(m) } catch (e) { process.stderr.write(`handle err: ${e}\n`) } }
      }
      writeOffset(offset)
    } catch (e) { process.stderr.write(`poll err: ${e}\n`); await new Promise(r => setTimeout(r, 2000)) }
  }
}
main()
