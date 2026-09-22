/**
 * Renders the vector card out to the raster and print files.
 *
 *   node render.mjs
 *
 * Writes into ./out:
 *   save-the-date-1200.png    for email and screens
 *   save-the-date-3000.png    for large prints and posters
 *   save-the-date-a5.pdf      A5, print ready, fonts embedded
 *   save-the-date-a6.pdf      A6, the usual postcard size
 *
 * The SVG carries its fonts inside it, so nothing needs installing.
 */
import { chromium } from "playwright";
import { mkdirSync, readFileSync } from "fs";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = resolve(HERE, "out");
mkdirSync(OUT, { recursive: true });

const CARD = resolve(HERE, "save-the-date.svg");
const W = 1000, H = 1414;                     // the card's own units

const browser = await chromium.launch({
  executablePath: "/opt/pw-browsers/chromium",
});

async function page(widthPx) {
  const svg = readFileSync(CARD, "utf8");
  const p = await browser.newPage({
    viewport: { width: widthPx, height: Math.round((widthPx * H) / W) },
    deviceScaleFactor: 1,
  });
  await p.setContent(
    `<style>html,body{margin:0;padding:0;background:#f8f6f2}
     svg{display:block;width:100vw;height:auto}</style>${svg}`,
    { waitUntil: "load" }
  );
  await p.waitForTimeout(1800);               // let the filters settle
  return p;
}

for (const px of [1200, 3000]) {
  const p = await page(px);
  await p.screenshot({ path: `${OUT}/save-the-date-${px}.png` });
  await p.close();
  console.log(`out/save-the-date-${px}.png  ${px}x${Math.round((px * H) / W)}`);
}

// Print: A-series, so the card's 1:1.414 fills the sheet edge to edge.
for (const [name, size] of [["a5", "148mm 210mm"], ["a6", "105mm 148mm"]]) {
  const p = await page(1200);
  await p.addStyleTag({
    content: `@page{size:${size};margin:0}
              @media print{html,body{width:100%;height:100%}
              svg{width:100%;height:100%}}`,
  });
  await p.pdf({
    path: `${OUT}/save-the-date-${name}.pdf`,
    width: size.split(" ")[0],
    height: size.split(" ")[1],
    printBackground: true,
    margin: { top: "0", bottom: "0", left: "0", right: "0" },
  });
  await p.close();
  console.log(`out/save-the-date-${name}.pdf  ${size}`);
}

await browser.close();
