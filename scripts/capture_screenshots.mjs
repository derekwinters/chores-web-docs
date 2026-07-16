#!/usr/bin/env node
/**
 * Capture documentation screenshots of each main sidebar page.
 *
 * Drives the running frontend (the published nginx image on :3000) with
 * Playwright + Chromium: logs in as the demo admin, forces the light colour
 * scheme, then screenshots each route listed in screenshots.config.json,
 * writing deterministic PNGs into docs/assets/screenshots/.
 *
 * Prereqs: the compose stack is up and healthy and seed_demo_data.py has run.
 *
 * Usage:
 *   node capture_screenshots.mjs
 *
 * Env overrides:
 *   FRONTEND_URL   base URL of the frontend (default from config)
 */
import { chromium } from "playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { dirname, resolve, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");

const config = JSON.parse(
  readFileSync(join(__dirname, "screenshots.config.json"), "utf8"),
);

const frontendUrl = process.env.FRONTEND_URL || config.frontendUrl;
const outputDir = resolve(repoRoot, config.outputDir);
const { width, height } = config.viewport;

/** Wait for the SPA to be past its loading/spinner states. */
async function waitForApp(page) {
  // The app renders "Loading..." / "Database initializing..." shells before
  // the router mounts. Wait until the sidebar nav (or any main content) is up.
  await page.waitForLoadState("networkidle");
  await page
    .waitForSelector(".app-sidebar, .app-main", { timeout: 30000 })
    .catch(() => {});
}

async function login(page) {
  await page.goto(frontendUrl + "/", { waitUntil: "domcontentloaded" });
  // The login form mounts once the DB status poll resolves.
  await page.waitForSelector("#username", { timeout: 60000 });
  await page.fill("#username", config.admin.username);
  await page.fill("#password", config.admin.password);
  await Promise.all([
    page.waitForNavigation({ waitUntil: "domcontentloaded" }).catch(() => {}),
    page.click('button[type="submit"]'),
  ]);
  await waitForApp(page);
}

async function main() {
  mkdirSync(outputDir, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width, height },
    deviceScaleFactor: 2, // crisp PNGs for docs
    colorScheme: "light", // force the light scheme
  });
  const page = await context.newPage();

  try {
    await login(page);

    for (const capture of config.captures) {
      const url = frontendUrl + capture.route;
      console.log(`Capturing ${capture.name} -> ${url}`);
      await page.goto(url, { waitUntil: "domcontentloaded" });
      await waitForApp(page);
      // Small settle for async data (queries, theme apply) before the shot.
      await page.waitForTimeout(1500);
      const outPath = join(outputDir, `${capture.name}.png`);
      await page.screenshot({ path: outPath, fullPage: true });
      console.log(`  wrote ${outPath}`);
    }
  } finally {
    await browser.close();
  }

  console.log("\nScreenshot capture complete.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
