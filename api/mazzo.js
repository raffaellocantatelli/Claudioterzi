"use strict";

const { carica } = require("./_lib/tarocchi");

module.exports = (req, res) => {
  if (req.method !== "GET") {
    res.status(405).json({ errore: "usare GET" });
    return;
  }

  const dati = carica();
  const quale = String(req.query.mazzo || "").trim().toLowerCase();

  if (quale === "r3") {
    res.status(200).json(dati.r3);
    return;
  }
  if (quale === "alpha") {
    res.status(200).json(dati.alpha);
    return;
  }

  res.status(200).json({
    r3: { nome: dati.r3.nome, numeroCarte: dati.r3.numeroCarte, assi: dati.r3.assi, polarita: dati.r3.polarita },
    alpha: { nome: dati.alpha.nome, numeroCarte: dati.alpha.numeroCarte, numeroCicli: dati.alpha.numeroCicli, numeroStati: dati.alpha.numeroStati },
    nota: "aggiungere ?mazzo=r3 oppure ?mazzo=alpha per l'elenco completo delle carte"
  });
};
