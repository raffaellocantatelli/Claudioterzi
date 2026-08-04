"use strict";

/*
  Vedi la nota in api/flight/occasioni.js: services-api.ryanair.com applica
  una protezione anti-bot che può bloccare traffico da IP di datacenter —
  questa funzione non finge mai un risultato quando la chiamata fallisce.
*/

const ORIGINE_DEFAULT = "CRL"; // Bruxelles Charleroi — base dell'autore

const PAESE_A_AEROPORTO = {
  BE: "CRL",
  FR: "BVA",
  IT: "BGY",
  ES: "MAD",
  DE: "NRN",
  NL: "EIN",
  PT: "OPO",
  IE: "DUB",
  PL: "KRK",
  UK: "STN",
  GB: "STN"
};

function autodetectaOrigine(req) {
  if (req.query && req.query.origine) return String(req.query.origine).toUpperCase();
  const paese = req.headers["x-vercel-ip-country"];
  if (paese && PAESE_A_AEROPORTO[paese]) return PAESE_A_AEROPORTO[paese];
  return ORIGINE_DEFAULT;
}

function dataISO(offsetGiorni) {
  const d = new Date();
  d.setDate(d.getDate() + offsetGiorni);
  return d.toISOString().slice(0, 10);
}

async function chiamaRyanair(origine, destinazione) {
  const url =
    `https://services-api.ryanair.com/farfnd/v4/oneWayFares` +
    `?departureAirportIataCode=${encodeURIComponent(origine)}` +
    (destinazione ? `&arrivalAirportIataCode=${encodeURIComponent(destinazione)}` : "") +
    `&language=en&market=en-gb&adultPaxCount=1&currency=EUR` +
    `&outboundDepartureDateFrom=${dataISO(1)}&outboundDepartureDateTo=${dataISO(60)}`;

  const controllo = new AbortController();
  const timeout = setTimeout(() => controllo.abort(), 8000);

  try {
    const risposta = await fetch(url, {
      signal: controllo.signal,
      headers: {
        Accept: "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; ClaudioTerziSito/1.0)"
      }
    });
    if (!risposta.ok) {
      return { ok: false, status: risposta.status };
    }
    const dati = await risposta.json();
    return { ok: true, dati };
  } catch (errore) {
    return { ok: false, status: null, errore: errore.message };
  } finally {
    clearTimeout(timeout);
  }
}

module.exports = { autodetectaOrigine, chiamaRyanair, dataISO };
