"use strict";

const fs = require("fs");
const path = require("path");

let cache = null;

function carica() {
  if (cache) return cache;
  const p = path.join(process.cwd(), "tarocchi_quantici_alpha.json");
  cache = JSON.parse(fs.readFileSync(p, "utf8"));
  return cache;
}

function trovaCartaR3(dati, riferimento) {
  const carte = dati.r3.carte;
  if (typeof riferimento === "number") {
    return carte.find((c) => c.numero === riferimento) || null;
  }
  const s = String(riferimento).trim().toLowerCase();
  return (
    carte.find((c) => String(c.numero) === s) ||
    carte.find((c) => c.nome.toLowerCase() === s) ||
    null
  );
}

function trovaCartaAlpha(dati, riferimento) {
  const carte = dati.alpha.carte;
  if (typeof riferimento === "number") {
    return carte.find((c) => c.numero === riferimento) || null;
  }
  const s = String(riferimento).trim().toLowerCase();
  return (
    carte.find((c) => String(c.numero) === s) ||
    carte.find((c) => c.nome.toLowerCase() === s) ||
    null
  );
}

function componiLetturaR3(dati, cartaRif, asseRif, polaritaRif) {
  const carta = trovaCartaR3(dati, cartaRif);
  if (!carta) return { errore: "carta non trovata nel mazzo R³∞" };

  const asseChiave = String(asseRif || "").trim().toLowerCase();
  const asse = dati.r3.assi[asseChiave];
  if (!asse) return { errore: "asse non valido — usare nord, est, sud oppure ovest" };

  const polaritaChiave = String(polaritaRif || "").trim().toLowerCase();
  const polarita = dati.r3.polarita[polaritaChiave];
  if (!polarita) return { errore: "polarità non valida — usare luce oppure ombra" };

  const significato =
    `${carta.nome}, sull'asse ${asse.nome.toLowerCase()} — ${asse.tema}. ` +
    `${carta.essenza} ` +
    `In ${polarita.nome.toLowerCase()}: ${polarita.tono}.`;

  return {
    mazzo: "r3",
    carta: { numero: carta.numero, nome: carta.nome },
    asse: asse.nome,
    polarita: polarita.nome,
    significato
  };
}

function componiStatoAlpha(dati, cartaRif, cicloRif) {
  const carta = trovaCartaAlpha(dati, cartaRif);
  if (!carta) return { errore: "carta non trovata nel Canone Alpha" };

  const numeroCiclo = Number(cicloRif);
  const ciclo = dati.alpha.cicli.find((c) => c.numero === numeroCiclo);
  if (!ciclo) return { errore: "ciclo non valido — usare un numero da 1 a 8" };

  const significato =
    `${carta.nome}, nel ciclo ${ciclo.numero} — ${ciclo.nome} (${ciclo.tema}). ${carta.essenza}`;

  return {
    mazzo: "alpha",
    carta: { numero: carta.numero, nome: carta.nome },
    ciclo: { numero: ciclo.numero, nome: ciclo.nome },
    significato
  };
}

module.exports = { carica, trovaCartaR3, trovaCartaAlpha, componiLetturaR3, componiStatoAlpha };
