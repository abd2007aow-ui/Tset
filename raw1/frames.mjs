// node frames.mjs overlay.html outdir [--workers 3] [--only t1,t2,...] [--handle name]
import { createRequire } from "node:module"; const { chromium } = createRequire(import.meta.url)("/opt/node22/lib/node_modules/playwright");
import fs from "node:fs"; import path from "node:path"; import { pathToFileURL } from "node:url";
const [page_, out] = process.argv.slice(2);
const arg = (n, d) => { const i = process.argv.indexOf("--" + n); return i < 0 ? d : process.argv[i + 1]; };
const workers = +arg("workers", 3), only = arg("only", ""), handle = arg("handle", "");
fs.mkdirSync(out, { recursive: true });
const url = pathToFileURL(path.resolve(page_)).href + (handle ? "?handle=" + encodeURIComponent(handle) : "");
const browser = await chromium.launch({ args: ["--allow-file-access-from-files", "--font-render-hinting=none"] });
async function open() {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on("pageerror", e => console.error("page error:", e.message));
  await p.goto(url); await p.evaluate(() => reel.ready()); return p;
}
const probe = await open();
const { duration, fps } = await probe.evaluate(() => ({ duration: reel.duration, fps: reel.fps }));
const times = only ? only.split(",").map(Number) : Array.from({ length: Math.round(duration * fps) }, (_, i) => i / fps);
let next = 0;
async function run(p) {
  while (next < times.length) {
    const i = next++, t = times[i];
    await p.evaluate(t => reel.seek(t), t);
    await p.screenshot({ path: path.join(out, String(i).padStart(5, "0") + ".png"), omitBackground: true });
    if (i % 300 === 0) console.log(`${i}/${times.length}`);
  }
}
const pages = [probe, ...(await Promise.all(Array.from({ length: Math.max(0, workers - 1) }, open)))];
await Promise.all(pages.map(run));
await browser.close();
console.log("frames", times.length, "duration", duration);
