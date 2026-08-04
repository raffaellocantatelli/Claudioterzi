"use strict";

const { carica, componiLetturaR3, componiStatoAlpha } = require("./_lib/tarocchi");

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
  const mazzo = String(corpo.mazzo || "r3").trim().toLowerCase();
  const dati = carica();

  if (corpo.carta === undefined || corpo.carta === null || corpo.carta === "") {
    res.status(400).json({ errore: "specificare 'carta' (numero o nome)" });
    return;
  }

  if (mazzo === "alpha") {
    if (corpo.ciclo === undefined) {
      res.status(400).json({ errore: "specificare 'ciclo' (numero da 1 a 8)" });
      return;
    }
    const risultato = componiStatoAlpha(dati, corpo.carta, corpo.ciclo);
    if (risultato.errore) {
      res.status(400).json(risultato);
      return;
    }
    res.status(200).json(risultato);
    return;
  }

  if (mazzo !== "r3") {
    res.status(400).json({ errore: "mazzo non valido — usare 'r3' oppure 'alpha'" });
    return;
  }

  if (!corpo.asse || !corpo.polarita) {
    res.status(400).json({ errore: "specificare 'asse' (nord/est/sud/ovest) e 'polarita' (luce/ombra)" });
    return;
  }

  const risultato = componiLetturaR3(dati, corpo.carta, corpo.asse, corpo.polarita);
  if (risultato.errore) {
    res.status(400).json(risultato);
    return;
  }
  res.status(200).json(risultato);
};
