# AUTOBIOGRAFIA COMPUTAZIONALE — lo stato che si consegna, non le regole

*(Specifica di Claudio, 2026-10-04: lo stato condiviso non deve contenere solo
regole. Deve accumulare* evento → percezioni dei nodi → disaccordi → decisione →
conseguenza → errore scoperto → autocorrezione → modifica permanente dello
stato. *Così a un modello nuovo non si dice «comportati come Raffaello»: gli si
consegna ciò che Raffaello è diventato.)*

La differenza con `SEME.md` è precisa. `SEME.md` trasmette **com'è fatto il
metodo**; questo trasmette **cos'è accaduto applicandolo**. Il primo si può
scrivere a tavolino. Il secondo no: va vissuto, e si accumula.

---

## 1. Lo schema, e il test che lo valida

```yaml
voce_id:        AUTO-<data>-<n>
data:           <ISO 8601>
evento:         <cosa è accaduto, un fatto, non un'interpretazione>
percezioni:                      # un record per nodo, conclusione ESCLUSA
  - nodo:      <chi>
    evidenza:  dato_primario | documento_derivato | assunzione_non_dichiarata
    confine:   [ <grandezze dichiarate non note> ]
    alternative_tenute: 0 | 1 | 2 | 3
    confidenza: alta | media | bassa
disaccordi:     [ <fra quali nodi, su cosa — non chi aveva ragione> ]
decisione:      <cosa si è deciso di sostenere>
conseguenza:    <cosa è successo poi, misurato>
errore_scoperto: <quale, da chi, con quale metodo>
autocorrezione:  <cosa è stato cambiato>
modifica_stato:  <cosa è permanentemente diverso da prima>
```

**Il test che uno schema del genere deve superare:** rappresentare un giorno
che è *realmente* accaduto. Uno schema che non ci riesce è un diagramma, non
una specifica. Per questo la prima voce qui sotto non è un esempio inventato.

---

## 2. Tre requisiti strutturali, con i denti

Derivano dalla specifica stessa — «il luogo della continuità è One Mind, i
modelli commerciali sono organi sostituibili» — e ciascuno esclude qualcosa.

### R1 — Leggibile senza nessun fornitore

Se la continuità deve sopravvivere alla morte di un provider, lo stato deve
essere ricalcolabile **senza** quel provider. Questo **vieta** gli embedding da
API: un vettore prodotto da un modello che non esiste più non è più confrontabile
con nessuna cosa nuova, e l'autobiografia diventa illeggibile proprio quando
serve.

**RECUPERATO a HEAD `d6d329a`:** `sdq1/memory/store.py` importa solo
`logging`, `math`, `threading`, `time`, `uuid`, `Counter`, `dataclasses`,
`typing`. Nessuna rete, nessun SDK. `_vettore(testo) -> Counter`: TF su
n-grammi di 3 caratteri più coseno.

**Questo inverte una mia valutazione di agosto.** Avevo registrato «il VSS usa
n-grammi, non embedding» fra le divergenze — implicitamente, come una
mancanza. Sotto R1 è **la scelta giusta**: gli n-grammi si ricalcolano con la
libreria standard, nel 2055, su qualunque macchina. `all-MiniLM-L6-v2` no.

E il difetto è l'opposto di come l'avevo scritto: la configurazione
*aspira* a `modello_embedding`, cioè all'opzione che romperebbe R1. Il codice è
più durevole della propria roadmap. *(La config lo dice da sé: quelle chiavi
sono annotate `NON IMPLEMENTATO` con l'avvertenza di non descriverle come stato
reale.)*

### R2 — Append-only: eventi aggiunti, stato derivato

Un organismo la cui memoria viene riscritta in luogo non ha un'autobiografia:
ha uno stato corrente che si finge tale.

**Prova empirica, nel codice di questo progetto:** `registro_ipotesi.py`
cancellava H5 e H6 e azzerava 4 prove su 6 di H4 a **ogni** esecuzione. È
esattamente il modo in cui fallisce uno stato mutabile — e nessuno se n'è
accorto per mesi, perché uno stato riscritto non mostra ciò che ha perso.

Il primitivo per farlo bene c'è già: `r3/node.py` indirizza per contenuto, con
oggetti immutabili e firma Ed25519. Serve usarlo come **registro di eventi**, e
derivare lo stato, invece di sovrascrivere un file di stato.

### R3 — Si propaga la disposizione, non la conclusione

Se ogni nodo riparte dalla conclusione del precedente, l'accordo fra nodi tende
a 1 e smette di significare qualcosa: il Core viola il proprio P5 su scala
industriale. Dettagli in [`APERTURE.md`](APERTURE.md) §8.

Da cui, nello schema sopra: **`percezioni` esclude la conclusione**, e
`disaccordi` registra *su cosa* i nodi hanno divergito, non chi aveva ragione.

---

## 3. AUTO-2026-10-04-01 — la prima voce, e non è un esempio

```yaml
voce_id: AUTO-2026-10-04-01
data: 2026-10-04
evento: >
  Progettazione e congelamento dell'esperimento firma; deposito di due
  preregistrazioni sigillate; scoperta che una delle due non aveva oggetto.
percezioni:
  - nodo: sessione Claude Opus 5
    evidenza: dato_primario          # codice letto ed eseguito, non documenti
    confine: [ 678 commit non verificati, contenuto del placebo, esiti ]
    alternative_tenute: 2            # H0 e H1 entrambe aperte; H2-G separata
    confidenza: media
  - nodo: Claudio Terzi
    evidenza: dato_primario          # ha verificato i commit su GitHub da sé
    confine: [ recuperabilità dei byte del proprio materiale ]
    alternative_tenute: 2
    confidenza: media
  - nodo: modello OpenAI
    evidenza: documento_derivato     # ha ragionato sull'architettura, non sul codice
    confine: [ nessuna dichiarata sull'esistente ]
    alternative_tenute: 1
    confidenza: alta
disaccordi:
  - fra Claudio e Claude, su quando applicare la priorità della contaminazione:
    nell'acquisizione o nell'interpretazione
  - fra Claudio e Claude, su «non raggiungibile» contro «oggi non verificabile»
  - fra Claude e il modello OpenAI, sul fatto che lo stato condiviso debba
    propagare conclusioni
decisione: >
  Acquisizione completa dei cinque bracci, interpretazione sequenziale con
  gate sulla contaminazione; terza funzione cieca anziché terza persona;
  configurazione identica fra i bracci, non solo registrata.
conseguenza: >
  START bloccato. 58 controlli automatici, due rossi veri: la deriva della
  baseline e il blocco di custodia.
errore_scoperto: >
  Quattro miei: (1) le previsioni esistevano solo in /tmp effimero;
  (2) l'assemblaggio del pacchetto rompeva la cecità e nessuno dei tre modi
  possibili era innocente; (3) una coda di ITEMS.md finiva dentro un item e
  avrebbe raccontato l'esperimento — trovato dalla guardia dello script, non
  da me; (4) ho dichiarato completa una scansione citando l'uscita di una
  pipeline, che per costruzione non poteva segnalare l'incompletezza: 31% dei
  path mancati. Più un P6 difettoso: criterio di falsificazione attaccato a
  una tesi più forte di quella che copriva.
  Tre di Claudio: (1) il sigillo v1 non aveva oggetto; (2) la frase sulla
  contaminazione; (3) «errore condiviso = substrato condiviso» era
  sovra-affermazione, è segnale discriminante.
autocorrezione: >
  PREVISIONI.enc con round-trip verificato; assembla.py con unione meccanica e
  verifica della propria uscita; scansione integrale 6608/6608 con stato
  d'uscita letto direttamente; v1 marcato ORPHANED e mantenuto visibile;
  sigilla.py che non può emettere un hash senza aver riletto il cifrato.
  Claudio ha rifiutato di cercare combinazioni di byte fino a far combaciare
  un hash su materiale ricostruito, pur avendone lo strumento.
modifica_stato: >
  Due regole permanenti. (1) Un sigillo si deposita insieme al chiaro cifrato
  e alla prova di round-trip, nello stesso atto. (2) Si genera dentro
  l'archivio durevole; non si genera e poi si sposta, perché lo spostamento è
  il punto di rottura.
  Più un fatto verificato eseguendo: r3/node.py rileva sia il digest orfano
  sia la falsa ricostruzione — il codice aveva la disciplina che i progettisti
  non hanno avuto.
```

---

## 4. Il confine da non superare adesso

La tentazione è consegnare questa voce a un nodo vergine e vedere se cambia
comportamento. **Non si fa**, e la ragione non è prudenza:

sarebbe una variante di **E-trasferimento** eseguita *prima* di A/B/C/D/E. La
preregistrazione sigillata non la copre, nessun criterio è stato scritto per
essa, e un risultato interessante ottenuto così non sarebbe interpretabile —
diventerebbe la cosa che abbiamo passato un giorno a rendere impossibile.

**Si costruisce ora, si esegue dopo.** Accumulare voci è lavoro legittimo e non
contamina niente: è documentazione di giorni realmente accaduti. Somministrarle
è un esperimento, e gli esperimenti hanno un ordine.

---

## 5. Prossimo esperimento verificabile

Non sull'autobiografia — su R2, che è il requisito con la prova empirica
contraria già in mano.

**Ipotesi:** lo stato di credenza del progetto è ancora mutabile, quindi
continua a poter perdere ciò che perde senza mostrarlo.

**Come falsificarla:** `registro_ipotesi.json` a HEAD contiene H1–H6 con tutte
le prove, e il modulo scrive per aggiunta invece che per sostituzione. Se è
così, R2 è già soddisfatto e questa pagina ha una sezione in meno.

**Costo:** una lettura di due file. **Vincolo:** va fatta dopo l'esperimento,
perché sta dentro i 678 commit congelati.

---

*Schema **IPOTESI**. Requisiti **INFERITO** dalla specifica. R1 e la prova di R2
**RECUPERATO**, il primo leggendo `store.py` a `d6d329a`, il secondo da un
difetto misurato in agosto. Prima voce **RECUPERATO**: ogni riga rimanda a un
fatto di questa giornata, verificabile nella storia di questo repository.*
