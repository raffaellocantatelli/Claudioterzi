"use strict";

/*
  Verifica il contratto della scheda: che lo schema inviato all'API e le schede
  che scriviamo in catalogo vadano d'accordo.

  SCHEDA_ALLEGRO è stata composta seguendo alla lettera le istruzioni del
  curatore in lib/scheda.js, a partire dalle due foto reali del libro
  (copertina + pagina del copyright). Non è output di una chiamata registrata:
  la chiamata di rete resta l'unico anello non coperto da questi test.

  Uso: node --test tests/
*/

const test = require("node:test");
const assert = require("node:assert");

const { schemaScheda, motivi } = require("../lib/scheda");
const { valida } = require("../lib/valida");
const catalogo = require("../lib/catalogo");

const CODICI = motivi().map((m) => m.codice);
const SCHEMA = schemaScheda(CODICI);

const SCHEDA_ALLEGRO = require("./scheda-allegro.json");

test("la scheda composta dalle foto rispetta lo schema inviato all'API", () => {
  const errori = valida(SCHEDA_ALLEGRO, SCHEMA);
  assert.deepStrictEqual(errori, [], "violazioni:\n" + errori.join("\n"));
});

test("i codici dei motivi esistono nella tassonomia", () => {
  for (const m of SCHEDA_ALLEGRO.motivi) {
    assert.ok(CODICI.includes(m.codice), `codice sconosciuto: ${m.codice}`);
  }
});

test("il validatore prende un campo obbligatorio mancante", () => {
  const rotta = Object.assign({}, SCHEDA_ALLEGRO);
  delete rotta.condizione;
  const errori = valida(rotta, SCHEMA);
  assert.ok(errori.some((e) => e.includes("condizione")), errori.join("\n"));
});

test("il validatore prende un motivo inventato", () => {
  const rotta = JSON.parse(JSON.stringify(SCHEDA_ALLEGRO));
  rotta.motivi.push({ codice: "bellissimo", spiegazione: "perché sì" });
  const errori = valida(rotta, SCHEMA);
  assert.ok(errori.some((e) => e.includes("bellissimo")), errori.join("\n"));
});

test("il validatore prende una confidenza fuori enum", () => {
  const rotta = Object.assign({}, SCHEDA_ALLEGRO, { confidenza: "altissima" });
  const errori = valida(rotta, SCHEMA);
  assert.ok(errori.some((e) => e.includes("altissima")), errori.join("\n"));
});

test("il validatore prende un campo non previsto", () => {
  const rotta = Object.assign({}, SCHEDA_ALLEGRO, { prezzo_secco: "300 euro" });
  const errori = valida(rotta, SCHEMA);
  assert.ok(errori.some((e) => e.includes("prezzo_secco")), errori.join("\n"));
});

test("la tassonomia è coerente: codici unici e campi completi", () => {
  const elenco = motivi();
  assert.strictEqual(new Set(CODICI).size, elenco.length, "codici duplicati");
  for (const m of elenco) {
    for (const campo of ["codice", "nome", "domanda", "spiegazione"]) {
      assert.ok(m[campo] && m[campo].length > 0, `${m.codice}: manca ${campo}`);
    }
  }
});

test("il catalogo esistente è valido e interrogabile per motivo", () => {
  for (const oggetto of catalogo.leggi()) {
    for (const m of oggetto.motivi || []) {
      assert.ok(CODICI.includes(m.codice), `${oggetto.id}: motivo ignoto ${m.codice}`);
    }
  }
  const soppressi = catalogo.perMotivo("soppresso");
  assert.ok(soppressi.length >= 1, "atteso almeno un oggetto soppresso in catalogo");
  assert.strictEqual(catalogo.perMotivo("codice-inesistente").length, 0);
});
