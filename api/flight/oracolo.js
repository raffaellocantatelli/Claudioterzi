"use strict";

const fs = require("fs");
const path = require("path");
const { carica, trovaCartaR3 } = require("../_lib/tarocchi");
const { autodetectaOrigine, chiamaRyanair } = require("../_lib/ryanair");

let destCache = null;
function destinazioni() {
  if (!destCache) {
    const p = path.join(process.cwd(), "api", "_lib", "destinazioni.json");
    destCache = JSON.parse(fs.readFileSync(p, "utf8"));
  }
  return destCache;
}

const ASSI = ["nord", "est", "sud", "ovest"];
const POLARITA = ["luce", "ombra"];

function scegli(lista) {
  return lista[Math.floor(Math.random() * lista.length)];
}

function leggiCorpo(req) {
  if (req.body && typeof req.body === "object") return req.body;
  try {
    return JSON.parse(req.body || "{}");
  } catch (e) {
    return {};
  }
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.status(405).json({ errore: "usare POST" });
    return;
  }

  const corpo = leggiCorpo(req);
  const dati = carica();

  const carteR3 = dati.r3.carte;
  const carta =
    corpo.carta !== undefined ? trovaCartaR3(dati, corpo.carta) : carteR3[Math.floor(Math.random() * carteR3.length)];
  if (!carta) {
    res.status(400).json({ errore: "carta non trovata nel mazzo R³∞" });
    return;
  }

  const asseChiave = corpo.asse ? String(corpo.asse).toLowerCase() : scegli(ASSI);
  const polaritaChiave = corpo.polarita ? String(corpo.polarita).toLowerCase() : scegli(POLARITA);
  const asse = dati.r3.assi[asseChiave];
  const polarita = dati.r3.polarita[polaritaChiave];
  if (!asse || !polarita) {
    res.status(400).json({ errore: "asse o polarità non validi" });
    return;
  }

  const candidate = destinazioni().filter(
    (d) => d.regione === asseChiave && d.polarita === polaritaChiave
  );
  const scelte = candidate.length > 0 ? candidate : destinazioni().filter((d) => d.regione === asseChiave);
  const destinazione = scelte.length > 0 ? scegli(scelte) : scegli(destinazioni());

  const origine = corpo.origine ? String(corpo.origine).toUpperCase() : autodetectaOrigine(req);
  const esito = await chiamaRyanair(origine, destinazione.iata);

  const volo = esito.ok
    ? { fonte: "ryanair-live", occasioni: (esito.dati && esito.dati.fares) || [] }
    : {
        fonte: "non disponibile",
        motivo:
          esito.status === 403
            ? "Ryanair ha rifiutato la richiesta (403) — probabile blocco anti-bot sull'IP del server."
            : `Ryanair non raggiungibile (${esito.status || esito.errore || "errore sconosciuto"}).`
      };

  res.status(200).json({
    carta: { numero: carta.numero, nome: carta.nome, essenza: carta.essenza },
    asse: asse.nome,
    polarita: polarita.nome,
    significato: `${carta.nome} — ${carta.essenza} Sull'asse ${asse.nome.toLowerCase()}, in ${polarita.nome.toLowerCase()}: ${polarita.tono}.`,
    destinazione: {
      citta: destinazione.citta,
      paese: destinazione.paese,
      iata: destinazione.iata,
      nota: destinazione.note
    },
    origine,
    volo
  });
};
