#!/usr/bin/env node
"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const { URL } = require("url");

const catalogo = require("./lib/catalogo");
const { componiScheda, motivi, MODELLO } = require("./lib/scheda");

const PUBLIC = path.join(__dirname, "public");
const TIPI = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8"
};

function json(res, codice, corpo) {
  res.writeHead(codice, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(corpo));
}

function corpoRichiesta(req, limiteByte = 40 * 1024 * 1024) {
  return new Promise((risolvi, rifiuta) => {
    let dati = "";
    let dimensione = 0;
    req.on("data", (chunk) => {
      dimensione += chunk.length;
      if (dimensione > limiteByte) {
        rifiuta(new Error("richiesta troppo grande"));
        req.destroy();
        return;
      }
      dati += chunk;
    });
    req.on("end", () => {
      try {
        risolvi(dati ? JSON.parse(dati) : {});
      } catch (e) {
        rifiuta(new Error("JSON non valido"));
      }
    });
  });
}

async function api(req, res, pathname, url) {
  if (pathname === "/api/motivi" && req.method === "GET") {
    const conteggi = catalogo.conteggioPerMotivo();
    return json(res, 200, {
      motivi: motivi().map((m) => Object.assign({}, m, { quanti: conteggi[m.codice] || 0 }))
    });
  }

  if (pathname === "/api/oggetti" && req.method === "GET") {
    const motivo = url.searchParams.get("motivo");
    const q = url.searchParams.get("q");
    let elenco = motivo ? catalogo.perMotivo(motivo) : catalogo.leggi();
    if (q) {
      const cercati = new Set(catalogo.cerca(q).map((o) => o.id));
      elenco = elenco.filter((o) => cercati.has(o.id));
    }
    return json(res, 200, { oggetti: elenco });
  }

  const dettaglio = pathname.match(/^\/api\/oggetti\/([\w-]+)$/);
  if (dettaglio && req.method === "GET") {
    const oggetto = catalogo.trova(dettaglio[1]);
    if (!oggetto) return json(res, 404, { errore: "oggetto non trovato" });
    return json(res, 200, oggetto);
  }

  if (pathname === "/api/scheda" && req.method === "POST") {
    let corpo;
    try {
      corpo = await corpoRichiesta(req);
    } catch (e) {
      return json(res, 400, { errore: e.message });
    }
    if (!Array.isArray(corpo.immagini) || corpo.immagini.length === 0) {
      return json(res, 400, { errore: "servono una o più immagini" });
    }
    try {
      const esito = await componiScheda(corpo.immagini, corpo.nota);
      return json(res, 200, esito);
    } catch (errore) {
      const codice = errore.codice === "chiave_mancante" ? 503 : 500;
      return json(res, codice, { errore: errore.message, codice: errore.codice });
    }
  }

  if (pathname === "/api/oggetti" && req.method === "POST") {
    let corpo;
    try {
      corpo = await corpoRichiesta(req, 2 * 1024 * 1024);
    } catch (e) {
      return json(res, 400, { errore: e.message });
    }
    if (!corpo.titolo) return json(res, 400, { errore: "manca il titolo" });
    return json(res, 201, catalogo.aggiungi(corpo));
  }

  return json(res, 404, { errore: "endpoint non trovato" });
}

function statico(req, res, pathname) {
  let file = path.join(PUBLIC, decodeURIComponent(pathname));
  if (pathname === "/" || pathname === "") file = path.join(PUBLIC, "index.html");
  if (!path.resolve(file).startsWith(PUBLIC)) {
    res.writeHead(403);
    return res.end("Vietato");
  }
  fs.readFile(file, (errore, dati) => {
    if (errore) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      return res.end("Non trovato: " + pathname);
    }
    res.writeHead(200, { "Content-Type": TIPI[path.extname(file)] || "application/octet-stream" });
    res.end(dati);
  });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname.startsWith("/api/")) {
    api(req, res, url.pathname, url).catch((e) => json(res, 500, { errore: e.message }));
  } else {
    statico(req, res, url.pathname);
  }
});

if (require.main === module) {
  const porta = process.env.PORT || 3100;
  server.listen(porta, () => {
    console.log(`Galleria su http://localhost:${porta}`);
    console.log(`Modello: ${MODELLO}`);
    console.log(
      process.env.ANTHROPIC_API_KEY
        ? "Identificazione automatica: attiva."
        : "Identificazione automatica: disattivata (ANTHROPIC_API_KEY non impostata)."
    );
  });
}

module.exports = server;
