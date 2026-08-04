# Claudio Terzi — sito

Quindici pagine tematiche, un'identità visiva: fondo `#0c0c0e`, oro `#c9a84c`,
Georgia serif, nav "La Costellazione" in cima. Deploy automatico su Vercel
a ogni commit.

## Stato di questo repo

Il repo era vuoto (solo README) quando questa versione è stata costruita.
Tutto qui dentro — struttura, codice, testi — è una **prima stesura**,
non un recupero di contenuti preesistenti. In particolare:

- **I testi dei Tarocchi Quantici** (`tarocchi_quantici_alpha.json`) sono
  generati da `scripts/genera-tarocchi.js` componendo carta + asse/ciclo +
  polarità, seguendo la regola fondativa "non assegnano significati,
  permettono ai significati di emergere" — **non sono i testi originali
  dell'autore**, che vanno inseriti sostituendo i contenuti dello script
  (la struttura del JSON prodotto resta compatibile con API e pagine).
- **Le API voli (`/api/flight/*`)** chiamano davvero
  `services-api.ryanair.com` (schema verificato con dati live in fase di
  sviluppo). Quel dominio applica una protezione anti-bot che può bloccare
  con un 403 il traffico da IP di datacenter/cloud — un limite noto e
  documentato di chi ha provato a integrare questa API da server, non un
  bug di questo codice. Quando il blocco scatta, l'endpoint lo dice
  chiaramente invece di inventare un prezzo.
- **I testi delle 15 pagine tematiche** sono una prima stesura scritta per
  rispettare l'identità e il tono del progetto — vanno rivisti e, dove
  serve, sostituiti con la voce autentica dell'autore.

## Struttura

```
public/              file statici serviti da Vercel
  css/style.css       design system condiviso
  css/nav.css         "La Costellazione" — nav responsive (flex-wrap)
  js/nav.js           costruisce la nav, 15 voci, testata 320–1280px
  js/soglia.js        soglia rituale (non sicurezza — documentato nel file)
  index.html          home / hub delle 15 pagine
  tarocchi.html        R³∞ — 78 carte
  alpha.html            Canone Alpha — 74 carte incorporate, collasso client-side
  parti.html · viaggi.html · flight.html · oracolo.html · parfums.html ·
  organo.html · dispensa.html · valigia.html · atelier.html · opera.html ·
  creazioni.html · opuscolo.html
  libro.html + libro/capitolo-1..5.html   indice + capitoli separati
  lettura.html          la stesa delle tre luci
  enzo.html             regalo per un amico — stesa a quattro assi

api/                  funzioni serverless Vercel
  mazzo.js (GET) · leggi.js (POST) · viaggi/pianifica.js (POST) ·
  flight/occasioni.js (POST) · flight/oracolo.js (POST)
  _lib/                helper condivisi (dati tarocchi, chiamata Ryanair)

tarocchi_quantici_alpha.json   dati dei due mazzi (radice del repo)
scripts/genera-tarocchi.js      rigenera il JSON sopra
scripts/dev-server.js           server locale per sviluppo/test (non usato in produzione)
tests/responsive.test.js        Playwright — overflow ed errori JS, 320–1280px
```

## Sviluppo locale

```bash
npm install          # scarica Playwright (serve solo per i test)
npm run dev           # server locale su http://localhost:3000
npm test              # test responsive (richiede il server locale attivo)
npm run genera-tarocchi   # rigenera tarocchi_quantici_alpha.json dallo script
```

## Regola fondativa dei Tarocchi Quantici

CARTA + ASSE (nord/est/sud/ovest) + POLARITÀ (luce/ombra) = SIGNIFICATO.
Luce e ombra sono due manifestazioni della stessa energia, non un bene e
un male. I significati non sono precalcolati per ogni combinazione: si
compongono a runtime — in `/api/leggi` per R³∞, interamente nel browser
in `alpha.html` per il Canone Alpha.
