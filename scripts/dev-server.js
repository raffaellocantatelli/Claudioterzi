#!/usr/bin/env node
/*
  Server locale minimale per sviluppo e test — non usato in produzione
  (in produzione è Vercel a servire /public come statico e /api come
  funzioni serverless). Riproduce lo stesso instradamento a livello
  locale così i test end-to-end possono girare senza dipendere da un
  deploy.
*/
"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const { URL } = require("url");

const ROOT = path.join(__dirname, "..");
const PUBLIC = path.join(ROOT, "public");

const TIPI = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8"
};

function leggiCorpo(req) {
  return new Promise((resolve) => {
    let dati = "";
    req.on("data", (chunk) => (dati += chunk));
    req.on("end", () => resolve(dati));
  });
}

async function gestisciApi(req, res, pathname) {
  const rel = pathname.replace(/^\/api\//, "");
  const file = path.join(ROOT, "api", rel + ".js");
  if (!fs.existsSync(file)) {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ errore: "endpoint non trovato" }));
    return;
  }

  delete require.cache[require.resolve(file)];
  const handler = require(file);

  const url = new URL(req.url, "http://localhost");
  req.query = Object.fromEntries(url.searchParams.entries());

  if (req.method === "POST") {
    const corpo = await leggiCorpo(req);
    try {
      req.body = corpo ? JSON.parse(corpo) : {};
    } catch (e) {
      req.body = {};
    }
  }

  const resWrapper = {
    statusCode: 200,
    status(codice) {
      this.statusCode = codice;
      return this;
    },
    json(oggetto) {
      res.writeHead(this.statusCode, { "Content-Type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(oggetto));
    }
  };

  try {
    await handler(req, resWrapper);
  } catch (errore) {
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ errore: "errore interno: " + errore.message }));
  }
}

function serviStatico(req, res, pathname) {
  let filePath = path.join(PUBLIC, decodeURIComponent(pathname));
  if (pathname === "/" || pathname === "") filePath = path.join(PUBLIC, "index.html");
  else if (!path.extname(filePath) && fs.existsSync(filePath + ".html")) filePath += ".html";

  if (!filePath.startsWith(PUBLIC)) {
    res.writeHead(403);
    res.end("Vietato");
    return;
  }

  fs.readFile(filePath, (errore, dati) => {
    if (errore) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Non trovato: " + pathname);
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { "Content-Type": TIPI[ext] || "application/octet-stream" });
    res.end(dati);
  });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname.startsWith("/api/")) {
    gestisciApi(req, res, url.pathname);
  } else {
    serviStatico(req, res, url.pathname);
  }
});

const PORTA = process.env.PORT || 3000;
server.listen(PORTA, () => {
  console.log("Server locale su http://localhost:" + PORTA);
});

module.exports = server;
