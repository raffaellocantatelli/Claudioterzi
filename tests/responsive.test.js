/*
  Verifica automatica che colma il gap "nessun test automatico da nessuna
  parte": per ogni pagina pubblica, a quattro larghezze di riferimento
  (320, 390, 768, 1280px), controlla che non ci sia overflow orizzontale
  e che non compaiano errori JS in console.

  Uso: node --test tests/  (richiede il server locale attivo — vedi
  npm run test:avvia, che avvia server e test insieme).
*/
"use strict";

const test = require("node:test");
const assert = require("node:assert");
const { chromium } = require("playwright");

const BASE = process.env.BASE_URL || "http://localhost:3000";
const LARGHEZZE = [320, 390, 768, 1280];

const PAGINE = [
  "/index.html",
  "/tarocchi.html",
  "/alpha.html",
  "/parti.html",
  "/viaggi.html",
  "/flight.html",
  "/oracolo.html",
  "/parfums.html",
  "/organo.html",
  "/dispensa.html",
  "/valigia.html",
  "/libro.html",
  "/libro/capitolo-1.html",
  "/atelier.html",
  "/opera.html",
  "/creazioni.html",
  "/opuscolo.html",
  "/lettura.html",
  "/enzo.html"
];

test("nessun overflow orizzontale ed errori JS su tutte le pagine, 320-1280px", async (t) => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const erroriConsole = [];
  const erroriPagina = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") erroriConsole.push(msg.text());
  });
  page.on("pageerror", (err) => erroriPagina.push(String(err)));

  try {
    for (const percorso of PAGINE) {
      for (const larghezza of LARGHEZZE) {
        await t.test(`${percorso} @ ${larghezza}px`, async () => {
          erroriConsole.length = 0;
          erroriPagina.length = 0;
          await page.setViewportSize({ width: larghezza, height: 900 });
          await page.goto(BASE + percorso, { waitUntil: "networkidle" });

          const misure = await page.evaluate(() => ({
            scrollWidth: document.documentElement.scrollWidth,
            clientWidth: document.documentElement.clientWidth
          }));

          assert.ok(
            misure.scrollWidth <= misure.clientWidth + 1,
            `overflow orizzontale su ${percorso} a ${larghezza}px: scrollWidth ${misure.scrollWidth} > clientWidth ${misure.clientWidth}`
          );

          assert.deepStrictEqual(erroriPagina, [], `errori JS su ${percorso} a ${larghezza}px: ${erroriPagina.join(" | ")}`);
        });
      }
    }
  } finally {
    await browser.close();
  }
});
