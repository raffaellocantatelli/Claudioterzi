"use strict";

const { autodetectaOrigine, chiamaRyanair } = require("../_lib/ryanair");

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
  const origine = corpo.origine ? String(corpo.origine).toUpperCase() : autodetectaOrigine(req);
  const budget = corpo.budget ? Number(corpo.budget) : null;

  const esito = await chiamaRyanair(origine);

  if (!esito.ok) {
    res.status(200).json({
      fonte: "non disponibile",
      origine,
      motivo:
        esito.status === 403
          ? "Ryanair ha rifiutato la richiesta (403) — probabile blocco anti-bot sull'IP del server."
          : `Ryanair non raggiungibile (${esito.status || esito.errore || "errore sconosciuto"}).`,
      occasioni: []
    });
    return;
  }

  let voli = Array.isArray(esito.dati && esito.dati.fares) ? esito.dati.fares : [];
  if (budget) {
    voli = voli.filter((v) => {
      const prezzo = v && v.outbound && v.outbound.price && v.outbound.price.value;
      return typeof prezzo === "number" ? prezzo <= budget : true;
    });
  }

  res.status(200).json({
    fonte: "ryanair-live",
    origine,
    budget,
    occasioni: voli.slice(0, 20)
  });
};
