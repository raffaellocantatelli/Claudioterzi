"use strict";

/*
  Da foto a scheda esperta.

  Questo è il pezzo che rende la Galleria diversa da un marketplace qualunque:
  non genera una descrizione generica, ma prova a identificare la tecnica
  esatta, l'edizione, il contesto storico — e soprattutto il MOTIVO per cui
  l'oggetto merita attenzione, scelto dalla tassonomia in dati/motivi.json.

  Serve una chiave API (ANTHROPIC_API_KEY). Senza chiave, il resto della
  Galleria funziona lo stesso: si compilano le schede a mano.
*/

const fs = require("fs");
const path = require("path");

const MODELLO = process.env.MODELLO_GALLERIA || "claude-opus-5";

function motivi() {
  const p = path.join(__dirname, "..", "dati", "motivi.json");
  return JSON.parse(fs.readFileSync(p, "utf8")).motivi;
}

const ISTRUZIONI = `Sei il curatore di una galleria d'aste. Ricevi le foto di un oggetto che qualcuno vuole vendere e produci la scheda che un esperto scriverebbe.

Il tuo compito NON è vendere. È capire cosa hai davanti e spiegare perché merita attenzione — o dire onestamente che non ne merita.

Regole:
- Nomina la tecnica esatta quando la riconosci (smalto champlevé, non "lavorazione a smalto"; maiolica di Deruta, non "ceramica blu"). Se non sei sicuro, dillo e indica cosa distinguerebbe le ipotesi.
- Per i libri: identifica edizione e tiratura dai dati visibili (SBN/ISBN, "First Printed", colophon). Il prefisso SBN identifica l'editore.
- Non inventare mai una valutazione economica precisa. Indica al massimo una fascia, e di' sempre su cosa andrebbe verificata (prezzi realizzati, non prezzi richiesti).
- La condizione descrivila da ciò che vedi, senza addolcirla.
- Le domande di verifica servono a chi vende: cosa deve controllare di persona per completare la scheda (firme, marchi sotto la base, pagine mancanti, prezzo tagliato sul risvolto).
- Scrivi in italiano, in prosa asciutta. Niente entusiasmo commerciale.`;

function schemaScheda(codiciMotivi) {
  return {
    type: "object",
    properties: {
      titolo: { type: "string", description: "Titolo della scheda, specifico" },
      autore: { type: "string", description: "Autore, produttore o manifattura; stringa vuota se ignoto" },
      datazione: { type: "string", description: "Anno o periodo; indicare l'incertezza se c'è" },
      tecnica: { type: "string", description: "Il nome esatto della tecnica o del procedimento" },
      categoria: { type: "string", description: "Tipo di oggetto: libro, ceramica, dipinto, mobile, ecc." },
      descrizione: { type: "string", description: "Il testo della scheda: cos'è, il contesto, perché conta" },
      motivi: {
        type: "array",
        description: "I motivi di interesse applicabili, dal più forte",
        items: {
          type: "object",
          properties: {
            codice: { type: "string", enum: codiciMotivi },
            spiegazione: { type: "string", description: "Perché questo motivo si applica a QUESTO oggetto" }
          },
          required: ["codice", "spiegazione"],
          additionalProperties: false
        }
      },
      condizione: { type: "string", description: "Stato di conservazione osservabile dalle foto" },
      valore: { type: "string", description: "Fascia indicativa e su cosa va verificata; mai una cifra secca" },
      domande_da_verificare: {
        type: "array",
        description: "Cosa deve controllare di persona chi vende",
        items: { type: "string" }
      },
      confidenza: {
        type: "string",
        enum: ["alta", "media", "bassa"],
        description: "Quanto sei sicuro dell'identificazione"
      }
    },
    required: [
      "titolo", "autore", "datazione", "tecnica", "categoria", "descrizione",
      "motivi", "condizione", "valore", "domande_da_verificare", "confidenza"
    ],
    additionalProperties: false
  };
}

function blocchiImmagine(immagini) {
  return immagini.map((img) => ({
    type: "image",
    source: { type: "base64", media_type: img.tipo, data: img.base64 }
  }));
}

async function componiScheda(immagini, notaVenditore) {
  if (!process.env.ANTHROPIC_API_KEY) {
    const errore = new Error(
      "ANTHROPIC_API_KEY non impostata: l'identificazione automatica è disattivata. " +
      "La scheda si può compilare a mano."
    );
    errore.codice = "chiave_mancante";
    throw errore;
  }

  const Anthropic = require("@anthropic-ai/sdk");
  const client = new Anthropic();
  const elenco = motivi();

  const catalogo = elenco
    .map((m) => `- ${m.codice} (${m.nome}): ${m.spiegazione}`)
    .join("\n");

  const testo =
    `Ecco le foto di un oggetto.\n\n` +
    (notaVenditore ? `Quello che dice chi lo vende: "${notaVenditore}"\n\n` : "") +
    `Motivi di interesse disponibili — scegli solo quelli che si applicano davvero, ` +
    `e non forzarne nessuno se l'oggetto è semplicemente ordinario:\n${catalogo}`;

  const risposta = await client.messages.create({
    model: MODELLO,
    max_tokens: 16000,
    system: ISTRUZIONI,
    output_config: {
      effort: "high",
      format: { type: "json_schema", schema: schemaScheda(elenco.map((m) => m.codice)) }
    },
    messages: [
      { role: "user", content: [...blocchiImmagine(immagini), { type: "text", text: testo }] }
    ]
  });

  if (risposta.stop_reason === "refusal") {
    const errore = new Error("La richiesta è stata rifiutata dai filtri di sicurezza.");
    errore.codice = "rifiutata";
    throw errore;
  }

  const blocco = risposta.content.find((b) => b.type === "text");
  if (!blocco) {
    throw new Error("Nessuna scheda nella risposta.");
  }

  return { scheda: JSON.parse(blocco.text), uso: risposta.usage };
}

module.exports = { componiScheda, motivi, MODELLO };
