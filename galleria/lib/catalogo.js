"use strict";

const fs = require("fs");
const path = require("path");

const PERCORSO = path.join(__dirname, "..", "dati", "oggetti.json");

function leggi() {
  if (!fs.existsSync(PERCORSO)) return [];
  return JSON.parse(fs.readFileSync(PERCORSO, "utf8"));
}

function salva(oggetti) {
  fs.writeFileSync(PERCORSO, JSON.stringify(oggetti, null, 2) + "\n");
}

function generaId(titolo) {
  const base = String(titolo || "oggetto")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);
  const esistenti = new Set(leggi().map((o) => o.id));
  if (!esistenti.has(base)) return base;
  let n = 2;
  while (esistenti.has(`${base}-${n}`)) n++;
  return `${base}-${n}`;
}

function aggiungi(scheda) {
  const oggetti = leggi();
  const oggetto = Object.assign({}, scheda, {
    id: generaId(scheda.titolo),
    aggiunto: new Date().toISOString().slice(0, 10)
  });
  oggetti.push(oggetto);
  salva(oggetti);
  return oggetto;
}

function trova(id) {
  return leggi().find((o) => o.id === id) || null;
}

/*
  La query che conta: non "dammi i libri", ma "dammi le cose soppresse".
  È l'interrogazione per motivo di interesse — la navigazione che i
  marketplace per categoria merceologica non permettono.
*/
function perMotivo(codice) {
  return leggi().filter((o) => (o.motivi || []).some((m) => m.codice === codice));
}

function conteggioPerMotivo() {
  const conteggi = {};
  for (const oggetto of leggi()) {
    for (const m of oggetto.motivi || []) {
      conteggi[m.codice] = (conteggi[m.codice] || 0) + 1;
    }
  }
  return conteggi;
}

function cerca(testo) {
  const q = String(testo || "").trim().toLowerCase();
  if (!q) return leggi();
  return leggi().filter((o) =>
    [o.titolo, o.autore, o.tecnica, o.descrizione, o.categoria]
      .join(" ")
      .toLowerCase()
      .includes(q)
  );
}

module.exports = { leggi, aggiungi, trova, perMotivo, conteggioPerMotivo, cerca };
