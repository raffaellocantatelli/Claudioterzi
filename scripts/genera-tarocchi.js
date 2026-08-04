#!/usr/bin/env node
/*
  Genera tarocchi_quantici_alpha.json.

  Versione 1 — bozza generativa. Il repo era vuoto: questi testi non sono
  quelli originali dell'autore (che non esistevano ancora in questo repo),
  sono una prima stesura pensata per rispettare la regola fondativa:
  "non assegnano significati, permettono ai significati di emergere".

  Per questo entrambi i mazzi non salvano un significato per ogni
  combinazione — salvano ingredienti brevi (carta, asse/ciclo, polarità)
  che vengono composti a runtime da /api/leggi e da alpha.html. Sostituire
  le liste qui sotto con i testi reali dell'autore quando saranno pronti:
  la struttura del JSON prodotto resta la stessa, così le pagine e le API
  continuano a funzionare senza modifiche.

  Uso: node scripts/genera-tarocchi.js > tarocchi_quantici_alpha.json
*/
"use strict";

const ASSI = {
  nord: { nome: "Nord", tema: "la direzione della volontà — dove qualcosa vuole ancora arrivare" },
  est: { nome: "Est", tema: "la direzione dell'origine — dove qualcosa è appena nato, non ancora nominato" },
  sud: { nome: "Sud", tema: "la direzione del corpo — dove qualcosa si sente prima di capirlo" },
  ovest: { nome: "Ovest", tema: "la direzione della memoria — dove qualcosa si è già depositato" }
};

const POLARITA = {
  luce: { nome: "Luce", tono: "la stessa energia mostrata, riconosciuta, messa al lavoro alla luce del giorno" },
  ombra: { nome: "Ombra", tono: "la stessa energia non ancora vista, non per questo meno vera — ciò che agisce prima di essere capito" }
};

const MAGGIORI = [
  ["Il Vuoto Fertile", "Prima di ogni scelta, lo spazio che le contiene tutte."],
  ["L'Osservatore", "Guardare una cosa è già cominciare a cambiarla."],
  ["La Soglia", "Ciò che sa e non dice ancora, perché dirlo troppo presto lo altera."],
  ["Il Campo", "Ciò che nutre senza dover intervenire — la condizione che rende possibile."],
  ["La Struttura", "La forma che tiene, anche quando nessuno la guarda."],
  ["Il Codice", "La regola trasmessa — utile finché non diventa gabbia."],
  ["La Risonanza", "Due frequenze che si riconoscono e cominciano a vibrare insieme."],
  ["La Traiettoria", "La direzione presa nonostante le forze che tirano altrove."],
  ["La Tensione", "Ciò che si tiene insieme proprio nel punto dove vorrebbe rompersi."],
  ["Il Silenzio", "Il passo indietro necessario per sentire ciò che il rumore copriva."],
  ["La Ruota degli Stati", "Nulla resta nello stato in cui lo hai lasciato l'ultima volta."],
  ["L'Equilibrio", "Il punto esatto in cui il peso smette di pendere da un lato."],
  ["La Sospensione", "Fermarsi non per rinunciare, ma per guardare da un'angolazione che si vede solo da fermi."],
  ["Il Collasso", "Il momento in cui una possibilità smette di essere tutte le altre."],
  ["La Miscela", "Ciò che nasce quando due cose diverse si lasciano attraversare a vicenda."],
  ["Il Vincolo", "Il legame scelto così tante volte da dimenticare che si può ancora scegliere altro."],
  ["La Frattura", "Ciò che crolla perché era già cavo, non perché qualcuno lo ha spinto."],
  ["La Stella Fissa", "Il punto fermo a cui tornare a guardare quando tutto il resto si muove."],
  ["La Marea", "Ciò che sale e scende per una legge che non chiede il permesso."],
  ["L'Emersione", "Ciò che finalmente si vede per intero, alla luce, senza più bisogno di essere spiegato."],
  ["Il Richiamo", "La voce che chiede di fare i conti con ciò che si era messo da parte."],
  ["L'Intero", "Non la somma delle parti, ma ciò che le parti diventano quando smettono di essere separate."]
].map(([nome, essenza], i) => ({ numero: i, nome, essenza, tipo: "maggiore" }));

const SEMI = [
  { nome: "Onde", dominio: "ciò che scorre tra le persone" },
  { nome: "Particelle", dominio: "ciò che si può toccare e contare" },
  { nome: "Campi", dominio: "ciò che orienta senza essere visto" },
  { nome: "Nodi", dominio: "ciò che si decide e si fa" }
];

const RANGHI = [
  ["Asso", (d) => `Il primo impulso di ${d}, ancora senza forma.`],
  ["Due", (d) => `${d[0].toUpperCase()}${d.slice(1)} che comincia a cercare un altro simile a sé.`],
  ["Tre", (d) => `${d[0].toUpperCase()}${d.slice(1)} messo alla prova nel mondo, la prima volta fuori casa.`],
  ["Quattro", (d) => `${d[0].toUpperCase()}${d.slice(1)} che si ferma a consolidare quanto ha ottenuto.`],
  ["Cinque", (d) => `${d[0].toUpperCase()}${d.slice(1)} che perde qualcosa che credeva acquisito.`],
  ["Sei", (d) => `${d[0].toUpperCase()}${d.slice(1)} che trova un nuovo equilibrio dopo la perdita.`],
  ["Sette", (d) => `${d[0].toUpperCase()}${d.slice(1)} che valuta se la strada presa vale ancora lo sforzo.`],
  ["Otto", (d) => `${d[0].toUpperCase()}${d.slice(1)} messo al lavoro, con metodo, senza più lo slancio iniziale.`],
  ["Nove", (d) => `${d[0].toUpperCase()}${d.slice(1)} quasi maturo, ma ancora segnato dalla fatica per arrivarci.`],
  ["Dieci", (d) => `${d[0].toUpperCase()}${d.slice(1)} portato a compimento — e già in cerca del prossimo inizio.`],
  ["Fante", (d) => `${d[0].toUpperCase()}${d.slice(1)} osservato da chi lo sta ancora imparando.`],
  ["Cavaliere", (d) => `${d[0].toUpperCase()}${d.slice(1)} lanciato in una direzione, senza guardarsi troppo indietro.`],
  ["Regina", (d) => `${d[0].toUpperCase()}${d.slice(1)} accolto e reso proprio, con la calma di chi lo conosce da dentro.`],
  ["Re", (d) => `${d[0].toUpperCase()}${d.slice(1)} governato con responsabilità, messo al servizio di qualcosa di più grande di sé.`]
];

let numero = MAGGIORI.length;
const MINORI = [];
for (const seme of SEMI) {
  for (const [rango, essenzaFn] of RANGHI) {
    MINORI.push({
      numero: numero++,
      nome: `${rango} di ${seme.nome}`,
      essenza: essenzaFn(seme.dominio),
      tipo: "minore",
      seme: seme.nome
    });
  }
}

const CARTE_R3 = [...MAGGIORI, ...MINORI];

const CICLI_ALPHA = [
  { numero: 1, nome: "Origine", tema: "il punto prima del punto, quando ancora nulla si è mosso" },
  { numero: 2, nome: "Attrito", tema: "il primo contatto con una resistenza reale" },
  { numero: 3, nome: "Fessura", tema: "la crepa che lascia entrare qualcosa di nuovo" },
  { numero: 4, nome: "Fermento", tema: "il disordine necessario prima che qualcosa si organizzi" },
  { numero: 5, nome: "Forma", tema: "ciò che finalmente prende una figura riconoscibile" },
  { numero: 6, nome: "Prova", tema: "la forma messa alla prova dal mondo che non la conosce ancora" },
  { numero: 7, nome: "Radicamento", tema: "ciò che ha retto e ora mette radici" },
  { numero: 8, nome: "Soglia successiva", tema: "il compimento che è già l'inizio di qualcos'altro" }
];

const QUALITA = [
  ["Silente", "ciò che agisce senza far rumore"],
  ["Ardente", "ciò che brucia il passo prima ancora di deciderlo"],
  ["Sospesa", "ciò che non è ancora scesa da nessuna parte"],
  ["Lucida", "ciò che vede chiaro proprio mentre trema"],
  ["Cava", "ciò che ha uno spazio vuoto al centro, e lo sa"],
  ["Doppia", "ciò che è due cose vere insieme, non una a scelta"],
  ["Ferma", "ciò che ha smesso di cercare altrove"],
  ["Mobile", "ciò che non si lascia fissare in una sola forma"],
  ["Grezza", "ciò che non è stata ancora lavorata da nessuno"],
  ["Levigata", "ciò che il tempo ha reso liscia, forse troppo"]
];

const NUCLEI = [
  ["Soglia", "un passaggio, non un luogo dove restare"],
  ["Radice", "ciò che tiene anche quando non si vede"],
  ["Fessura", "una crepa che lascia entrare aria nuova"],
  ["Corrente", "una forza che porta senza chiedere il permesso"],
  ["Nodo", "un punto dove più fili si sono stretti insieme"],
  ["Eco", "ciò che ritorna, cambiato, di qualcosa già detto"],
  ["Deriva", "un moto lento lontano dal punto di partenza"],
  ["Innesto", "un elemento estraneo diventato parte viva"]
];

const CARTE_ALPHA = [];
let n = 0;
outer: for (let qi = 0; qi < QUALITA.length; qi++) {
  for (let ni = 0; ni < NUCLEI.length; ni++) {
    if (n >= 74) break outer;
    const [qNome, qClausola] = QUALITA[qi];
    const [nNome, nClausola] = NUCLEI[ni];
    const qClausolaCap = qClausola[0].toUpperCase() + qClausola.slice(1);
    CARTE_ALPHA.push({
      numero: n++,
      nome: `${qNome} ${nNome}`,
      essenza: `${qClausolaCap}. Qui si mostra come ${nClausola}.`
    });
  }
}

const dataset = {
  versione: 1,
  nota:
    "Bozza generativa v1 — sostituire con i testi originali dell'autore quando pronti. " +
    "I significati non sono precalcolati per ogni combinazione: emergono componendo carta + asse/ciclo + polarità a runtime.",
  r3: {
    nome: "R³∞",
    numeroCarte: CARTE_R3.length,
    assi: ASSI,
    polarita: POLARITA,
    carte: CARTE_R3
  },
  alpha: {
    nome: "Canone Alpha",
    numeroCarte: CARTE_ALPHA.length,
    numeroCicli: CICLI_ALPHA.length,
    numeroStati: CARTE_ALPHA.length * CICLI_ALPHA.length,
    cicli: CICLI_ALPHA,
    carte: CARTE_ALPHA
  }
};

process.stdout.write(JSON.stringify(dataset, null, 2) + "\n");
