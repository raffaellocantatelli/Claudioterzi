# Stato del progetto — claudioterzi (sito)

> Prima di lavorare su questo repo: leggi questo file.
> Prima di chiudere la sessione: aggiornalo — data, cosa hai fatto, cosa resta aperto.
>
> Non è un archivio filosofico, è un promemoria pratico. Se una voce qui sotto
> non è più vera, correggila invece di aggiungerne una nuova sopra.

## Ultimo aggiornamento

2026-08-05 — aggiunta `galleria/` (vedi sotto). Prima: sito costruito da zero,
P5/P6 integrati.

## galleria/ — progetto separato nella stessa repo

MVP di un'idea diversa dal sito: **da foto a scheda esperta**, e navigazione per
**motivo di interesse** (soppresso · primo · appartenuto a · tecnica perduta ·
interrotto · sopravvissuto · errore · quotidiano) invece che per categoria
merceologica. Gira in locale (`cd galleria && npm start`, porta 3100), non è
deployato su Vercel. Vedi `galleria/README.md` per cosa è deliberatamente fuori
da questa versione (VR, aste, logistica, valutazione automatica).

L'arricchimento da foto usa l'API Claude e richiede `ANTHROPIC_API_KEY`; senza
chiave tutto il resto funziona e le schede si compilano a mano. **Non è mai
stato eseguito con una chiave reale** — quel percorso va verificato al primo
uso con credenziali.

## Stato attuale

Il repo era vuoto (solo README) all'inizio di questa sessione. Ora contiene:

- 15 pagine tematiche + home, design system condiviso, nav responsive, soglia rituale.
- Tarocchi Quantici: `tarocchi_quantici_alpha.json` (78 carte R³∞ + Canone Alpha,
  74 carte/8 cicli/592 stati), generato da `scripts/genera-tarocchi.js`.
- API funzionanti: `/api/mazzo`, `/api/leggi`, `/api/viaggi/pianifica`,
  `/api/flight/occasioni`, `/api/flight/oracolo`.
- Test Playwright (`npm test`): 81/81 verifiche passate, overflow ed errori JS
  su tutte le pagine a 320/390/768/1280px.
- P5/P6 dal Protocollo Rosso Rosso Rosso integrati nel mazzo R³∞ (vedi sotto).

## Decisioni prese

- **I testi dei Tarocchi Quantici sono una bozza generativa v1, non i testi
  originali dell'autore** — il repo non ne conteneva. Vanno sostituiti quando
  pronti; la struttura del JSON resta compatibile. Dettagli in `README.md`.
- **Le API Ryanair funzionano** (schema verificato con dati live durante lo
  sviluppo) ma quel dominio può bloccare con 403 traffico da IP cloud/datacenter
  — limite noto dell'API, non un bug. L'endpoint lo segnala invece di inventare
  prezzi.
- **`libro.html` è indice + capitoli separati**, non una pagina unica, per
  restare leggibile da telefono.
- Nessuna pull request aperta finora — non richiesta esplicitamente.

## Aperto / prossimi passi

- Sostituire i testi generativi dei tarocchi con quelli reali dell'autore.
- Verificare in produzione (Vercel) se le chiamate Ryanair passano o vengono
  bloccate — il comportamento locale non garantisce quello in cloud.
- Nessun'altra richiesta pendente al momento di questo aggiornamento.

## Repo collegati

- **rosso-rosso-rosso** (privato) — https://github.com/raffaellocantatelli/rosso-rosso-rosso
  Contiene SDQ-1 (pipeline multi-agente) e il framework R³∞ originale (P5/P6,
  registro ipotesi). Da lì è stato esportato, in forma pubblica e generica, il
  principio P5/P6 verso `public/libro/capitolo-6.html` di questo repo — senza
  esporre le ipotesi private del registro originale.
