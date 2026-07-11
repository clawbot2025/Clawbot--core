#!/usr/bin/env node
/**
 * demo_recorder.mjs — scripted Playwright product-demo recorder (9:16 portrait).
 *
 * Reuses the proven capture rig from autotube/capture/capture.mjs (same wrapped
 * rootless Chromium EXE, UA, launch flags, settle/consent logic). Executes the
 * steps of a demo-spec JSON sequentially with recordVideo enabled and emits a
 * per-step timeline so the orchestrator can fit footage to narration.
 *
 * Usage:  node demo_recorder.mjs <spec.json> <workdir>
 * Output: <workdir>/raw.webm + <workdir>/timeline.json
 *
 * Spec: { product, url, viewport:{width,height}, steps:[
 *          {action: goto|click|type|scroll|wait|hover,
 *           selector?, text?, secs?, enter?, narration} ] }
 *
 * Human-feel rules: 150-300ms mouse settle before clicks, smooth eased mouse
 * moves, smooth multi-tick scrolls, typing at ~60ms/char.
 */
import { createRequire } from 'module'
import { mkdirSync, rmSync, readdirSync, copyFileSync, readFileSync, writeFileSync } from 'fs'
import { join } from 'path'

// playwright-core lives in the autotube capture rig — reuse, don't reinstall.
const require = createRequire('/config/workspace/autotube/capture/capture.mjs')
const { chromium } = require('playwright-core')

const EXE = '/config/.cache/ms-playwright/chromium-1229/chrome-linux64/chrome'
const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'

const [, , specPath, workdir] = process.argv
if (!specPath || !workdir) { console.error('usage: demo_recorder.mjs <spec.json> <workdir>'); process.exit(1) }
const spec = JSON.parse(readFileSync(specPath, 'utf8'))
const viewport = spec.viewport || { width: 608, height: 1080 }

const recDir = join(workdir, 'rec')
rmSync(recDir, { recursive: true, force: true })
mkdirSync(recDir, { recursive: true })

const rand = (a, b) => a + Math.random() * (b - a)

async function dismissConsent(page) {
  // best-effort: same common-banner sweep as capture.mjs settle()
  for (const sel of ['[aria-label*="accept" i]', 'button:has-text("Accept all")',
                     'button:has-text("Accept")', 'button:has-text("I agree")']) {
    try {
      const b = page.locator(sel).first()
      if (await b.isVisible({ timeout: 400 })) { await b.click({ timeout: 1000 }); return true }
    } catch {}
  }
  return false
}

async function smoothMoveTo(page, selector) {
  const loc = page.locator(selector).first()
  await loc.scrollIntoViewIfNeeded({ timeout: 8000 }).catch(() => {})
  const box = await loc.boundingBox({ timeout: 8000 })
  if (!box) throw new Error(`no bounding box for: ${selector}`)
  const tx = box.x + box.width / 2 + rand(-4, 4)
  const ty = box.y + box.height / 2 + rand(-3, 3)
  await page.mouse.move(tx, ty, { steps: 14 })          // eased-ish multi-step move
  await page.waitForTimeout(rand(150, 300))              // human settle before acting
  return loc
}

async function smoothScroll(page, totalPx, secs) {
  const ticks = Math.max(6, Math.round(secs * 8))
  const per = totalPx / ticks
  for (let i = 0; i < ticks; i++) {
    // gentle ease in/out on the wheel deltas
    const ease = 0.55 + 0.45 * Math.sin((Math.PI * (i + 0.5)) / ticks)
    await page.mouse.wheel(0, per * ease)
    await page.waitForTimeout((secs * 1000) / ticks)
  }
}

const browser = await chromium.launch({
  executablePath: EXE, headless: true,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
         '--disable-blink-features=AutomationControlled'],
})
const ctx = await browser.newContext({
  viewport, userAgent: UA, deviceScaleFactor: 2,        // crisp text at portrait size
  recordVideo: { dir: recDir, size: viewport },
})
const page = await ctx.newPage()
const t0 = Date.now()                                    // video time zero ~ page open
const now = () => (Date.now() - t0) / 1000

const timeline = []
try {
  for (const [i, step] of spec.steps.entries()) {
    const secs = step.secs ?? { goto: 3, click: 2.5, type: 2, scroll: 4, wait: 2, hover: 2 }[step.action] ?? 2
    let start

    if (step.action === 'goto') {
      // navigate + settle FIRST so the step's footage starts on a painted page
      await page.goto(step.url || spec.url, { waitUntil: 'domcontentloaded', timeout: 45000 })
      await page.waitForTimeout(2500)                    // fonts/lazy images/banners
      await dismissConsent(page)
      start = now()
      await page.mouse.move(viewport.width * 0.5, viewport.height * 0.4, { steps: 10 })
      await page.waitForTimeout(secs * 1000)             // on-page dwell = the footage
    } else if (step.action === 'click') {
      start = now()
      const loc = await smoothMoveTo(page, step.selector)
      await loc.click({ timeout: 8000 })
      await page.waitForTimeout(1200)                    // page reaction
      await dismissConsent(page)
      await page.waitForTimeout(secs * 1000)
    } else if (step.action === 'type') {
      start = now()
      const loc = await smoothMoveTo(page, step.selector)
      await loc.click({ timeout: 8000 })
      await page.waitForTimeout(rand(200, 350))
      await page.keyboard.type(step.text || '', { delay: 60 })
      if (step.enter) {
        await page.waitForTimeout(rand(300, 500))
        await page.keyboard.press('Enter')
        await page.waitForTimeout(1500)                  // results paint
        await dismissConsent(page)
      }
      await page.waitForTimeout(secs * 1000)
    } else if (step.action === 'scroll') {
      start = now()
      await smoothScroll(page, step.px ?? 900, secs)
      await page.waitForTimeout(400)
    } else if (step.action === 'hover') {
      start = now()
      await smoothMoveTo(page, step.selector)
      await page.waitForTimeout(secs * 1000)
    } else if (step.action === 'wait') {
      start = now()
      await page.waitForTimeout(secs * 1000)
    } else {
      throw new Error(`unknown action: ${step.action}`)
    }

    timeline.push({ index: i, action: step.action, narration: step.narration || '',
                    start: +start.toFixed(3), end: +now().toFixed(3) })
    console.error(`step ${i} ${step.action}: ${start.toFixed(2)}s -> ${now().toFixed(2)}s`)
  }
  await page.waitForTimeout(600)                         // tail so the last frame flushes
} catch (e) {
  console.error(`demo_recorder: step failed — ${e.message.split('\n')[0]}`)
  await ctx.close(); await browser.close()
  process.exit(1)
}
await ctx.close()
await browser.close()

const vids = readdirSync(recDir).filter(f => f.endsWith('.webm'))
if (!vids.length) { console.error('demo_recorder: no video produced'); process.exit(1) }
copyFileSync(join(recDir, vids[0]), join(workdir, 'raw.webm'))
rmSync(recDir, { recursive: true, force: true })
writeFileSync(join(workdir, 'timeline.json'), JSON.stringify({ product: spec.product, steps: timeline }, null, 2))
console.log(join(workdir, 'raw.webm'))
