"use strict";

/*
  Validatore del sottoinsieme di JSON Schema usato da lib/scheda.js
  (type, required, enum, additionalProperties, array items, oggetti annidati).

  L'API applica già lo schema lato server con gli structured outputs — questo
  serve a due cose diverse: verificare in test che schema e schede vadano
  d'accordo, e non fidarsi ciecamente di una risposta prima di scriverla in
  catalogo.
*/

function tipoDi(valore) {
  if (Array.isArray(valore)) return "array";
  if (valore === null) return "null";
  return typeof valore;
}

function valida(valore, schema, percorso = "") {
  const errori = [];
  const dove = percorso || "(radice)";

  if (schema.type && tipoDi(valore) !== schema.type) {
    errori.push(`${dove}: atteso ${schema.type}, trovato ${tipoDi(valore)}`);
    return errori;
  }

  if (schema.enum && !schema.enum.includes(valore)) {
    errori.push(`${dove}: "${valore}" non è tra i valori ammessi (${schema.enum.join(", ")})`);
  }

  if (schema.type === "object") {
    for (const richiesto of schema.required || []) {
      if (!(richiesto in valore)) {
        errori.push(`${dove}: manca il campo obbligatorio "${richiesto}"`);
      }
    }
    if (schema.additionalProperties === false) {
      const ammessi = new Set(Object.keys(schema.properties || {}));
      for (const chiave of Object.keys(valore)) {
        if (!ammessi.has(chiave)) {
          errori.push(`${dove}: campo non previsto "${chiave}"`);
        }
      }
    }
    for (const [chiave, sottoSchema] of Object.entries(schema.properties || {})) {
      if (chiave in valore) {
        errori.push(...valida(valore[chiave], sottoSchema, percorso ? `${percorso}.${chiave}` : chiave));
      }
    }
  }

  if (schema.type === "array" && schema.items) {
    valore.forEach((elemento, i) => {
      errori.push(...valida(elemento, schema.items, `${dove}[${i}]`));
    });
  }

  return errori;
}

module.exports = { valida };
