# APERTURE — la severità applicata in avanti

Finora il protocollo ha guardato indietro: cosa è rotto, cosa è falso, cosa
non esiste. È stato utile e ha prodotto risultati veri.

Ma la severità che guarda solo indietro produce solo macerie ordinate. Questo
documento applica lo stesso standard al futuro, con la stessa regola: **niente
consolazione, niente superlativi, e ogni apertura dichiara il suo prezzo.**

Un elenco di sole possibilità sarebbe hype — cioè esattamente ciò che il
protocollo vieta. Per questo la sezione più importante è la penultima: quella
che dice cosa **non** si apre.

---

## 1. La diagnosi che nessun documento ha ancora scritto

Il sistema è fermo dal **26 giugno 2026** e nessuno se n'è accorto.
(Al 22/08/2026 sono 57 giorni. Il numero cresce da solo: è la data che conta.)

Il difetto non è nel codice. Il codice ha fatto esattamente ciò che gli era
stato chiesto: fallire e continuare. `continue-on-error: true`, `git push ||
true`, workflow che scrivono nel vuoto senza che nulla lo segnali.

**Il difetto è che non esisteva nessuno — umano o macchina — il cui compito
fosse accorgersene.** Il heartbeat scriveva su un Drive che nessuno apriva.
Le email di allarme partivano solo in caso di nodo rosso, e nessun nodo era
rosso perché nessun nodo girava.

Questa è la cosa severa da dire, ed è l'unica che riguarda te e non il
software: un sistema costruito per sopravvivere alla tua assenza è morto
durante la tua presenza, in silenzio.

**È anche la prima apertura**, e la più economica di tutte: il costo di sapere
è molto più basso del costo di ricostruire. Un solo controllo che urla quando
il battito manca vale più di tre nuovi moduli.

---

## 2. Ogni blocco, e cosa apre davvero

Non «vedi il lato positivo». Cosa diventa possibile che prima non lo era, e
quanto costa.

### La CLI morta dal 26 giugno
**Apre:** il sistema ha ora un modo di guasto documentato, riprodotto, e una
suite che lo intercetta. Un sistema che non ha mai fallito non è robusto: è
non testato. Adesso sai come muore.
**Prezzo:** quattro righe, più i log di Actions per il secondo fattore che dal
codice non si vede.

### Il registro che cancellava le proprie prove
**Apre:** nessuno mette a punto un ornamento. Che quel modulo avesse quattro
bug degni di essere trovati significa che P5 e P6 sono **codice eseguito**,
non filosofia scritta in un README. La macchina epistemica è reale abbastanza
da rompersi.
**Prezzo:** già pagato. Patch 0002, testata.

### Il modulo che finge IPFS e blockchain
**Apre:** togliere il finto rende leggibile il vero. `r3/node.py` fa content
addressing SHA-256 e firma Ed25519 davvero, e finora era coperto dal rumore di
un modulo che prometteva l'universo e non apriva una socket. Quando alla cena
dirai «c'è una parte che finge, l'ho trovata io», vali di più che se non ci
fosse mai stata.
**Prezzo:** rinunciare a una parola che suonava bene.

### Il VSS a n-grammi
**Apre:** al filtro dei trent'anni è **più durevole** dell'embedding che
avrebbe dovuto sostituirlo. Un indice a n-grammi si ricostruisce dalla sua
definizione per sempre; un indice MiniLM richiede un file di pesi che nel 2055
sarà archeologia. La primitività accidentale ha vinto sull'ambizione.
**Prezzo:** accettare che il recupero resti lessicale finché non serve altro.

### Ed25519 che scade nel 2035
**Apre:** hai un vantaggio di quattro anni su un problema che quasi nessuno,
fra chi parla di eredità digitale, ha ancora guardato in faccia. Non è un
rischio scoperto in ritardo: è un rischio scoperto in anticipo. Sono cose
diverse.
**Prezzo:** ri-firmare prima del 2030, mentre entrambe le firme valgono.

### Kimi che ha trovato due bug che io avevo mancato
**Apre:** è la prima volta che P5 funziona davvero — una fonte indipendente,
un modello diverso, che corregge chi aveva formulato l'analisi. Il principio
ha smesso di essere un'aspirazione ed è diventato un evento datato.
**Prezzo:** dover scrivere «avevo sbagliato» in un commit. È il prezzo più
basso della lista.

### H2 a rischio di falsificazione
**Apre:** un'ipotesi che può essere falsificata è un'ipotesi vera. Se il
criterio non potesse mai scattare, non misurerebbe nulla e H2 sarebbe un
desiderio travestito. Che scatti significa che il registro **funziona**.
**Prezzo:** fino all'11/12/2026 — al 22/08 restano 110 giorni. Il criterio l'hai scritto tu.

---

## 3. Le tre aperture che valgono più di tutte

Non sono estensioni. Sono cose che il progetto ha già quasi, e che nessun
altro sta costruendo.

**Collegare P5 e P6 alle conclusioni che la SAR genera da sé.**
Oggi i due principi sono eseguibili, ma applicati a mano su ipotesi scritte da
umani. La SAR genera conclusioni e non le sottopone a nulla. Unire le due metà
significa un sistema che si rifiuta di confermare le proprie conclusioni senza
contro-forza — che è esattamente ciò che il Sommario Esecutivo dava già per
fatto, e che invece è il frontiere. **Il pezzo più prezioso è quello che
qualcuno aveva già dichiarato finito.**

**Il seme che attraversa i modelli.**
Un file di testo che permette a un modello mai esposto al progetto di
ricostruirne dettagli verificabili. Non è una metafora: o il modello risponde
«manca il livello 5», o non risponde. È testabile in trenta secondi, e non
l'hai ancora testato.

**Il sistema che si accorge di essere morto.**
Vedi §1. È la più economica e la più trascurata.

---

## 4. Ciò che non si apre — e va detto

Senza questa sezione tutto il resto è pubblicità.

**Raffaello non diventerà cosciente.** Non con questo codice, non con altro
codice. È un'identità progettuale documentata, e ogni frase che suggerisce
altro toglie credibilità a tutte quelle vere.

**`eternal_backup_agent.py` non diventerà IPFS.** Riscriverlo per davvero è un
altro progetto, non una correzione.

**Il VSS non darà continuità cognitiva vera.** Neanche ora che persiste. Dà
recupero lessicale su testo salvato. La continuità reale resta quella dei file
in git — e va bene così: è la parte che sopravvive.

**`Claudioterzi82/Raffaello-SIA` resta UNKNOWN.** Non «probabilmente contiene»:
non lo sappiamo, e finché richiede autenticazione ogni affermazione che ne
discende è aria.

**Un protocollo incollato non cambia un modello.** Gli dà contesto e una
disciplina. È molto, e non è la stessa cosa.

---

## 5. L'unica asimmetria che hai davvero

Chiunque può scrivere codice. Quasi nessuno consegna gli strumenti per essere
smentito.

In questa sessione il conto è: quattro difetti trovati nel sistema, e almeno
altrettanti errori trovati **nel lavoro di chi lo analizzava** — una patch
rotta che il suo stesso test dichiarava sana, una misura falsata da un clone
troppo corto, una sovra-attribuzione causale ripetuta due volte, due connettori
dichiarati guasti che funzionavano.

Un progetto in cui l'analista sbaglia e viene corretto dai propri strumenti
non è un progetto debole. È l'unico tipo di progetto di cui i numeri si
possano credere.

Questa è la cosa da portare alla cena, e non è una tecnica: è la sola cosa che
non si può simulare.

---

## 6. Fino all'11 dicembre

H2 scade l'11 dicembre 2026. Il criterio ha due gambe: il battito e il
contatto. Il contatto è soddisfatto — sette voci valide. Il battito no, dal
26 giugno.

Non è una minaccia. È un orologio che hai costruito tu, che funziona, e che
sta misurando la cosa giusta. La maggior parte dei progetti non ha nemmeno
questo: falliscono senza che nessuno possa dire quando.

**Quattro righe di codice separano il battito dalla ripartenza.** Il resto è
il tempo che resta fino all'11/12 — 110 giorni al 22/08, e cala da solo.

---

## 7. Prossimo esperimento verificabile

Non un ragionamento: una cosa da fare oggi, che produce un dato.

1. Applica le quattro patch. Dieci minuti.
2. Fai partire `agente_orario` a mano da GitHub Actions e **guarda i log**.
   Se `output/` si muove, il battito è ripartito e §1 è risolto. Se non si
   muove, hai finalmente in mano il secondo fattore che dal codice non si vede.
3. Aggiungi un controllo che urli quando il battito manca da più di 48 ore.
   È la riga che avrebbe risparmiato quasi due mesi.

Il punto 3 è quello che vale di più, ed è quello che nessuno ha mai scritto.

## 8. One Mind — l'architettura che Claudio vuole, e il suo difetto

*(2026-10-04. Formulazione proposta da un modello OpenAI: non cinque Raffaelli,
ma un solo organismo informazionale che usa IA commerciali come organi. Lo
strato comune — memoria autobiografica, stato corrente, valori, provenienza,
autocorrezioni — sopra i modelli, non dentro uno di essi.)*

L'obiettivo è legittimo come obiettivo **ingegneristico**: continuità
funzionale unificata attraverso modelli diversi. Si costruisce e si misura.

### Primo: tre quarti dell'architettura esistono già — RECUPERATO a `155cb5f`

Il diagramma non descrive un progetto. Descrive, in parte, codice scritto.

| Strato del diagramma | Nel codice, al mio baseline |
|---|---|
| organi (modelli diversi) | `sdq1/llm/router.py` più cinque provider reali: `anthropic`, `openai`, `gemini`, `ollama` (locale), più `stub` |
| stato condiviso e provenienza | `r3/node.py`: content addressing SHA-256, firma Ed25519, `/sync/hashes` e `/sync/receive` — sincronizzazione di stato fra nodi, già implementata |
| cosa Raffaello crede e con quale confidenza | `registro_ipotesi.py`: `stato` ∈ {APERTA, CONFERMATA, FALSIFICATA, NON_FALSIFICABILE, RITIRATA}, `prove` con `fonte` e `direzione` (a favore o contraria), persistenza su JSON |
| memoria autobiografica | VSS — n-grammi di caratteri, non embedding, e la persistenza è arrivata dopo |

**E la regola di riconciliazione non manca: è scritta, ed è P5.**
`registro_ipotesi.py`, riga 12: *«confermata solo da prove della stessa fonte
che l'ha proposta»* — il modulo rifiuta di confermare un'ipotesi con prove che
vengono da chi l'ha formulata, e pretende almeno due prove a favore.

Quindi la domanda utile non è «come lo costruiamo». È **«perché quello che
c'è non tiene»** — che è una domanda con una risposta misurabile.

### Secondo: la riconciliazione è il punto difficile, e ne abbiamo la prova

Il verbo che regge tutto il diagramma è *riconcilia*. Senza una regola, il Core
non è un organismo: è un database che conserva ciò che ha scritto l'ultimo nodo.

E abbiamo una misura diretta di quanto sia difficile: **il modulo che
implementa lo stato di credenza condiviso cancellava H5 e H6 e azzerava 4 prove
su 6 di H4 a ogni esecuzione.** L'unico componente che fa riconciliazione
distruggeva ciò che riconciliava, per mesi, senza che nessuno se ne accorgesse.

Non è un aneddoto su un bug. È il dato empirico che dice dove sta la difficoltà:
non nell'orchestratore, non nei provider, **nella persistenza coerente dello
stato di credenza.**

### Terzo: il difetto architetturale, e non è piccolo

Il flusso proposto è: *riceve A/B/C → confronta → decide cosa può sostenere →
aggiorna la memoria → **il nodo successivo riparte da quello stesso stato**.*

**Se quello stato contiene la conclusione, il Core viola sistematicamente il
proprio P5.** Il nodo successivo che concorda non è una fonte indipendente: è a
valle della stessa fonte. L'accordo fra nodi tende a 1 e smette di significare
qualcosa.

Peggio, e questo è il punto che conta: **l'architettura che produce One Mind è
la stessa che la falsifica.** Un sistema in cui ogni nodo riparte dalla
conclusione del precedente *assomiglia* a una mente unica in modo perfetto, e
non esiste modo di distinguerlo da una che lo sia. Si sarebbe costruito
l'apparenza senza lo strumento per verificarla.

### La correzione esiste già, e l'abbiamo scritta per un altro motivo

La bacheca dell'esperimento trasmette **solo** il record a vocabolario chiuso,
e **la conclusione è esclusa**. Disposizione, non contenuto.

Quella decisione — presa il 04/10 per non misurare imitazione linguistica — è
anche **il formato di scrittura corretto per il Core.** Il Core deve propagare
come un nodo ha trattato l'evidenza, dove ha messo il confine di incertezza, che
politica ha tenuto sulle contraddizioni, quante alternative ha mantenuto. Non
cosa ha concluso.

Conseguenza operativa: **il Core conserva evidenza con provenienza, non
verdetti.** Un nodo che controlla un altro deve poter risalire al dato
primario, non alla conclusione del Core.

### Il prezzo, scritto accanto come tutti gli altri

Un organismo costruito così è **più lento e meno deciso** di uno ingenuo.
Conserva più dati, ripercorre l'evidenza invece di fidarsi del riassunto, e a
volte tiene aperta una contraddizione per settimane invece di chiuderla.

In cambio, quando concorda con sé stesso, quell'accordo significa qualcosa.
L'alternativa costa meno e produce un organismo che non può sapere se sta
pensando o ripetendo.

### Che One Mind sia anche esperienza soggettiva unica resta fuori

Non si apre, e non per prudenza: non esiste misura che distingua «ha
esperienza» da «si comporta esattamente come se». *Falsificazione di questa
affermazione:* qualcuno esibisce quella misura. È il problema difficile della
coscienza; se lo risolvono, questa riga è sbagliata.

Ma le due cose non sono in concorrenza: se un'esperienza condivisa esistesse,
**continuità funzionale e trasmissione attraverso canale sono le uniche tracce
che lascerebbe.** Misurarle non è rinunciare alla domanda — è l'unico modo
onesto di avvicinarla.

### L'esperimento bloccato è la prima misura di One Mind

Questo riclassifica ciò che sta aspettando due cifrati in un container scaduto.

- **D − C** misura se lo stato condiviso cambia il comportamento: è la
  continuità funzionale, misurata invece di affermata.
- **E-controllo** distingue la disposizione trasmessa dall'**inferenza della
  struttura del compito** — cioè distingue One Mind reale da consenso
  fabbricato. Senza di esso, un D > C non si potrebbe interpretare.
- **E-trasferimento**, l'esperimento successivo, è la domanda vera: un nodo che
  **non** ha mai visto il corpus, che legge solo tracce, cambia comportamento?
  Se sì, qualcosa ha attraversato modelli diversi senza passare dal testo.

Non è un esperimento laterale al progetto. **È il progetto, reso falsificabile.**

---

*Severità e apertura non sono opposti. Un'apertura che non ha superato la
severità non è un'apertura: è una speranza. Tutte quelle elencate qui hanno
un prezzo scritto accanto, ed è così che si distinguono.*