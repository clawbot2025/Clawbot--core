#!/usr/bin/env bun
/**
 * Prospect engine v1 — zero-capital lead sourcing for the cash-flow engine.
 *
 * Runs a Firecrawl web search WITH inline scrape, then mines each result for a
 * contact email + context. Outputs a clean lead list (markdown table + JSONL)
 * so outreach can target real people. Social profiles rarely expose an email on
 * scrape; personal sites / booking pages do — those are the gold.
 *
 * Usage:
 *   bun prospect_engine.ts "<search query>" [limit]
 * Output:
 *   operations/outputs/leads/<slug>.md   (human view)
 *   operations/outputs/leads/<slug>.jsonl (machine view, for the mailer)
 */
import { execFileSync } from 'child_process'
import { writeFileSync, mkdirSync, appendFileSync, existsSync } from 'fs'
import { join } from 'path'

const FIRECRAWL = '/config/.local/bin/firecrawl'
const OUTDIR = '/config/workspace/operations/outputs/leads'
const query = process.argv[2]
const limit = process.argv[3] ?? '20'
if (!query) { console.error('usage: bun prospect_engine.ts "<query>" [limit]'); process.exit(1) }

mkdirSync(OUTDIR, { recursive: true })
const slug = query.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '').slice(0, 50)

const EMAIL_RE = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g
// junk addresses that are never a real prospect contact
const JUNK = /(example|sentry|wix|squarespace|godaddy|\.png|\.jpg|@2x|domain\.com|email\.com|yourdomain|cloudflare|googleapis|gstatic|w3\.org|schema\.org)/i

function findEmails(s: string): string[] {
  const hits = (s.match(EMAIL_RE) ?? []).filter(e => !JUNK.test(e))
  return [...new Set(hits.map(e => e.toLowerCase()))]
}

console.error(`prospect-engine: searching "${query}" (limit ${limit}) with inline scrape...`)
let raw: string
try {
  raw = execFileSync(FIRECRAWL, [
    'search', query,
    '--limit', String(limit),
    '--scrape',
    '--scrape-formats', 'markdown,links',
    '--json',
  ], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, timeout: 180000 })
} catch (e: any) {
  console.error('search failed:', e?.message ?? e)
  // CLI sometimes writes partial JSON to stdout even on non-zero exit
  raw = e?.stdout?.toString?.() ?? ''
  if (!raw) process.exit(1)
}

let parsed: any
try { parsed = JSON.parse(raw) } catch { console.error('could not parse JSON; dumping raw'); writeFileSync(join(OUTDIR, `${slug}.raw.json`), raw); process.exit(1) }

// normalize to an array of result objects across possible shapes
const results: any[] =
  parsed?.web ?? parsed?.results ?? parsed?.data?.web ?? parsed?.data ?? (Array.isArray(parsed) ? parsed : [])

type Lead = { name: string; url: string; email: string; context: string }
const leads: Lead[] = []
for (const r of results) {
  const url = r?.url ?? r?.link ?? ''
  const title = (r?.title ?? r?.metadata?.title ?? '').toString().trim()
  const desc = (r?.description ?? r?.snippet ?? '').toString().trim()
  const md = (r?.markdown ?? r?.content ?? r?.scrape?.markdown ?? '').toString()
  const links = JSON.stringify(r?.links ?? r?.scrape?.links ?? '')
  const emails = findEmails(md + '\n' + links + '\n' + JSON.stringify(r ?? {}))
  const email = emails[0] ?? ''
  leads.push({ name: title || url, url, email, context: desc.slice(0, 160) })
}

const withEmail = leads.filter(l => l.email)
const without = leads.filter(l => !l.email)

// write JSONL (only leads we can actually email)
const jsonl = join(OUTDIR, `${slug}.jsonl`)
writeFileSync(jsonl, withEmail.map(l => JSON.stringify(l)).join('\n') + (withEmail.length ? '\n' : ''))

// write human markdown
const md: string[] = [
  `# Leads — "${query}"`, '',
  `Searched ${results.length} results · **${withEmail.length} with a contact email** · ${without.length} need email-finding follow-up.`, '',
  `## Contactable now (${withEmail.length})`, '',
  '| Name | Email | URL | Context |', '|---|---|---|---|',
  ...withEmail.map(l => `| ${l.name.replace(/\|/g, '/')} | ${l.email} | ${l.url} | ${l.context.replace(/\|/g, '/')} |`),
  '', `## No email yet — bio-link/site follow-up needed (${without.length})`, '',
  '| Name | URL | Context |', '|---|---|---|',
  ...without.map(l => `| ${l.name.replace(/\|/g, '/')} | ${l.url} | ${l.context.replace(/\|/g, '/')} |`),
]
writeFileSync(join(OUTDIR, `${slug}.md`), md.join('\n') + '\n')

console.error(`prospect-engine: ${results.length} results → ${withEmail.length} contactable, ${without.length} need follow-up`)
console.error(`  -> ${join(OUTDIR, slug + '.md')}`)
console.log(JSON.stringify({ query, results: results.length, contactable: withEmail.length, follow_up: without.length }))
