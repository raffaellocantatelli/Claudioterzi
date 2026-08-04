"use strict";

const fs = require("fs");
const path = require("path");

let destCache = null;
function destinazioni() {
  if (!destCache) {
    const p = path.join(process.cwd(), "api", "_lib", "destinazioni.json");
    destCache = JSON.parse(fs.readFileSync(p, "utf8"));
  }
  return destCache;
}

function leggiCorpo(req) {
  if (req.body && typeof req.body === "object") return req.body;
  try {
    return JSON.parse(req.body || "{}");
  } catch (e) {
    return {};
  }
}

module.exports = (req, res) => {
  if (req.method !== "POST") {
    res.status(405).json({ errore: "usare POST" });
    return;
  }

  const corpo = leggiCorpo(req);
  const stile = corpo.stile ? String(corpo.stile).trim().toLowerCase() : null;
  const regione = corpo.regione ? String(corpo.regione).trim().toLowerCase() : null;
  const giorni = Number(corpo.giorni) || 4;

  let candidate = destinazioni();

  if (stile) {
    candidate = candidate.filter((d) => d.stile.includes(stile));
  }
  if (regione) {
    candidate = candidate.filter((d) => d.regione === regione);
  }

  if (candidate.length === 0) {
    res.status(200).json({
      trovate: 0,
      messaggio: "Nessuna destinazione corrisponde ai filtri richiesti — prova ad allargare stile o regione.",
      proposte: []
    });
    return;
  }

  const scelte = [...candidate].sort(() => Math.random() - 0.5).slice(0, 3);

  const proposte = scelte.map((d) => ({
    citta: d.citta,
    paese: d.paese,
    iata: d.iata,
    regione: d.regione,
    nota: d.note,
    itinerario: `${giorni} giorni: ${Math.max(1, Math.round(giorni * 0.4))} per orientarsi, ${Math.max(1, Math.round(giorni * 0.4))} per il resto — ${d.note.toLowerCase()}`
  }));

  res.status(200).json({
    trovate: candidate.length,
    filtri: { stile, regione, giorni },
    proposte
  });
};
