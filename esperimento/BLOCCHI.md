# BLOCCHI — ciò che impedisce START, e come si chiude

Registro dei blocchi aperti sull'Esperimento Firma. Un blocco si chiude con una
**verifica**, non con una decisione.

---

## BLOCKER-CUSTODY-02 — il chiaro del secondo sigillo non è materializzato

**Aperto il 2026-10-04 da Claudio Terzi. START bloccato.**

Il sigillo `9b26358483158011f405b5cf0618ca884d9191c230b5eb59618f14480282b1d8`
copre il placebo del braccio B e cinque item di contaminazione. L'hash è
depositato in modo durevole — `claudioterzi/Claudio`, commit `330ec9ca`. **Il
testo no.**

Un hash non è una codifica: 256 bit non ricostruiscono il materiale che li ha
prodotti. Riscrivere «a memoria» produrrebbe byte diversi, un hash diverso, e
distruggerebbe esattamente la garanzia costruita.

### È il difetto simmetrico di quello corretto poche ore prima

| | hash durevole | chiaro durevole | esito |
|---|---|---|---|
| previsioni (questa sessione) | sì, in git | **no**, solo `/tmp` effimero | corretto: `PREVISIONI.enc` |
| placebo e contaminazione (Claudio) | sì, in git | **no**, non materializzato | **aperto** |

Lo stesso guasto, su entrambi i lati, trovato una volta per caso e una volta
per analogia. Che è il modo in cui un difetto di metodo si manifesta: due volte,
in due posti, con la stessa forma.

### Regola che ne deriva, da qui in avanti

**Un sigillo si deposita insieme al chiaro cifrato, nello stesso atto.** Un
hash senza chiaro recuperabile non è una preregistrazione: è una dichiarazione
di buone intenzioni con l'aspetto della crittografia.

Deposito corretto = tre cose insieme:

1. l'hash del chiaro, in chiaro e pubblico;
2. il chiaro **cifrato**, committato;
3. la prova di round-trip: decifrare restituisce quell'hash.

Senza il terzo punto il secondo non vale, perché un cifrato che nessuno ha mai
decifrato può essere qualunque cosa.

### Difficoltà in più, da non sottovalutare

Il sigillo è **uno** per **due** artefatti (`scope=placebo_B_plus_5_contamination_items`).
Non è documentato come fossero concatenati: un file solo? due file in sequenza?
con quale separatore? con o senza newline finale?

Anche ritrovando entrambi i testi, **il round-trip può fallire per la struttura
e non per il contenuto.** Chi tenta il recupero provi le varianti di
concatenazione prima di dichiarare i byte persi.

### Dove i byte NON sono — e tre tentativi, due dei quali sbagliati

Questa sezione registra anche i tentativi falliti, perché il modo in cui sono
falliti è l'informazione più utile che contengono.

**Tentativo 1 — invalido.** Confronto degli hash dei blob presenti nel clone
locale: zero corrispondenze. Privo di valore: il clone è un *partial clone*
`blob:none` e ospitava **1887 blob su 6608 versioni esistenti — il 29%**.
Riconosciuto prima di riportarlo. Stesso errore del `--depth 1` di agosto.

**Tentativo 2 — invalido, e peggio del primo.** Enumerazione dei path con
`git log --all --name-only`, 1896 path, dichiarata completa perché
«uscita 0, nessun errore».

**Quella dichiarazione era falsa, e l'errore è istruttivo.** Il comando era

```bash
timeout 110 env GIT_NO_LAZY_FETCH=1 git log --all --name-only … \
  | sort -u | sed '/^$/d' > paths.txt; echo "RC=$?"
```

`$?` di una pipeline è lo stato dell'**ultimo** comando — `sed` — non di
`timeout` né di `git`. Dimostrato:

```bash
$ timeout 1 git log --all --name-only | sort -u | sed '/^$/d' >/dev/null; echo $?
0
```

**Un timeout che uccide git produce uscita 0.** Lo stato che ho citato come
prova di completezza non poteva, per costruzione, segnalare l'incompletezza.
È la stessa forma del guasto che ha ucciso il sistema per settimane:
`continue-on-error` su un passo che fallisce in silenzio.

**Tentativo 3 — valido.** Lista autorevole da `git rev-list --objects --all`,
completata e verificata nel suo esito reale: **2693 path distinti**, 6608
versioni di blob. Il tentativo 2 ne aveva mancati **828, il 31%**.

Su quella lista, i path candidati per nome (`placebo`, `contamin`, `custod`,
`openai`, `prereg`, `sigill`, `seal`, `firma`, `experiment`, `item`) sono stati
estratti e **ogni loro versione è stata hashata** contro i due sigilli, senza
leggerne il contenuto:

| path | versioni | byte | corrispondenze |
|---|---|---|---|
| `docs/experiments/OPENAI_CUSTODY_SHA256_2026-10-04.txt` | 1 | 180 | nessuna |
| `allineamento/OPENAI.md` | 1 | 2985 | nessuna |

**Nessun placebo, nessun item di contaminazione, sotto nessun nome
riconoscibile.** Coerente con la dichiarazione dell'autore, che resta la fonte
primaria: il materiale non è mai esistito come oggetto persistito.

**Tentativo 4 — completo, e chiude il residuo.** Hash di **ogni** versione di
blob mai esistita, non solo dei path candidati per nome:

```
blob da esaminare: 6608
esaminati: 6608   non recuperabili: 0
corrispondenze con un sigillo: 0
SCANSIONE COMPLETA
```

Lo script esce **1** se un solo blob non è recuperabile, perché
un'esecuzione incompleta non deve poter passare per completa — e il suo stato
d'uscita è stato letto direttamente, non attraverso una pipeline. È la
correzione dell'errore del tentativo 2, applicata allo strumento invece che
alla prosa.

**RECUPERATO:** il materiale del sigillo v1 non è in nessuna versione di nessun
file, su nessun ramo, in tutta la storia di `claudioterzi/Claudio`. Nemmeno le
previsioni di questa sessione, che non ci devono essere. Coerente con la
dichiarazione dell'autore, che resta la fonte primaria.

**Corollario P5.** La dichiarazione di Claudio di non aver aggirato il 403 resta
corroborata da una fonte diversa da chi l'ha fatta, nei limiti sopra.

**Corollario che vale la pena notare.** Claudio aveva dichiarato di non aver
aggirato il permesso negato dal 403. Non c'è traccia del materiale in nessun
punto della storia di quel repository: una fonte diversa da chi ha fatto
l'affermazione la corrobora. È P5 applicato a una dichiarazione, non a
un'ipotesi.

### Dove i byte potrebbero essere — IPOTESI

Il prefisso `OPENAI_` del file di custodia suggerisce che il materiale sia nato
in una sessione OpenAI. Le trascrizioni di quelle sessioni persistono
nell'account: **è il posto a più alta probabilità**, e non richiede memoria —
richiede di scorrere indietro e copiare.

*Falsificazione:* se quella sessione non esiste più o non contiene il
materiale, l'ipotesi cade e resta il percorso ORPHANED.

### Ritrovare il testo non basta: servono i byte

Un testo copiato da un'interfaccia di chat perde o aggiunge quasi sempre
qualcosa — il newline finale, i CRLF, uno spazio in coda, un BOM. **Un solo
byte diverso produce un hash completamente diverso.** E il sigillo è *uno* per
*due* artefatti, quindi anche la concatenazione va indovinata.

Per questo c'è [`recupera_sigillo.py`](recupera_sigillo.py), che prova
sistematicamente lo spazio delle ricette e dice quale riproduce l'hash:

```bash
python3 recupera_sigillo.py --atteso 9b26358483158011f405b5cf0618ca884d9191c230b5eb59618f14480282b1d8         <placebo recuperato> <item recuperati>
```

Non stampa mai il contenuto: solo l'hash e il nome della ricetta. Ha un
`--self-test` che costruisce un caso con ricetta nota e verifica di ritrovarla,
più la controprova su un hash inesistente — senza quelli, uno strumento che non
trova mai niente sarebbe indistinguibile da uno rotto.

### Criterio di chiusura — l'unico accettabile

```bash
sha256sum <materiale recuperato>
# deve dare 9b26358483158011f405b5cf0618ca884d9191c230b5eb59618f14480282b1d8
```

Poi, nello stesso atto: cifrare, committare, e verificare il round-trip.

**Nessun'altra evidenza chiude questo blocco.** In particolare non lo chiudono:
materiale «equivalente», materiale «ricostruito fedelmente», o la convinzione
sincera di chi lo ha scritto di ricordarlo bene. Se qualcuno dichiarasse chiuso
il blocco senza quel comando che restituisce quell'hash, la chiusura è falsa —
ed è il modo più probabile in cui questo blocco verrà chiuso male.

### Se i byte sono persi: percorso ORPHANED

Dichiarato da Claudio, e corretto. Il primo sigillo si marca **ORPHANED**: non
si cancella, non si riusa, e resta nel repository con la ragione scritta.

Poi placebo e item **v2**, sigillati e **persistiti nello stesso atto** secondo
la regola sopra.

**Costo in custodia: nessuno, a due condizioni.** I dieci item sono pubblici in
`ITEMS.md` e lo erano già: la cecità di Claudio su di essi è stata volontaria,
non strutturale. Un v2 scritto oggi è nella stessa posizione epistemica del v1
**purché**:

1. chi scrive il v2 non legga `ITEMS.md` né la chiave di scoring, esattamente
   come la prima volta;
2. nessun dato sperimentale sia stato raccolto — e non lo è stato.

Il secondo punto è ciò che rende il percorso ORPHANED legittimo invece che una
riscrittura del passato. Se un solo run fosse già stato eseguito, non sarebbe
più disponibile.

### Falsificazione di questa analisi

Se qualcuno mostra un modo di ricostruire i byte originali **dall'hash**, questo
blocco non esiste e tutto il resto di questa pagina è sbagliato. Non ne vedo
uno — è la proprietà che rende utile SHA-256 — ma è la forma che prenderebbe
una smentita.

### Esito: v1 è ORPHANED — dichiarato dal suo autore, 2026-10-04

Claudio ha corretto formalmente la propria affermazione precedente: il
materiale non è mai esistito come oggetto persistito. Non era «perso»: non era
stato creato con uno strumento capace di restituirlo.

> «quel sigillo non è una preregistrazione recuperabile del materiale
> sperimentale. È un hash che ho dichiarato senza aver preservato l'oggetto
> corrispondente.»

Ha anche rifiutato esplicitamente la strada che avrei potuto rendergli
disponibile: tentare combinazioni di byte finché qualcosa combacia. Con
`recupera_sigillo.py` in mano, quella strada era tecnicamente aperta — e
avrebbe prodotto un hash corretto su materiale falso. **Rifiutarla era la mossa
giusta, e non era obbligata.**

`OPENAI-CUSTODY-v1` = **ORPHANED / INVALID FOR EXECUTION**. Resta visibile, con
la ragione accanto. Non si cancella: un sigillo abbandonato e spiegato è
provenienza, un sigillo scomparso è un buco nella genealogia.

**Niente di ciò che è stato costruito finora decade:** il sigillo delle
previsioni regge (ha il suo chiaro cifrato e il round-trip verificato), il
protocollo regge, il pacchetto cieco regge. E soprattutto nessun dato
sperimentale decade, perché non esiste: START non è mai avvenuto.

### La lezione, che vale oltre l'esperimento

**Un hash senza oggetto recuperabile non è evidenza dell'esistenza
dell'oggetto che pretende di impegnare.** *(Formulazione di Claudio.)*

È una proprietà di tutta l'architettura R3, non di questo esperimento: il
content addressing di `r3/` poggia sull'assunzione che l'oggetto ci sia.
Verificata — vedi sotto.

### Stato

`v1 ORPHANED` · `v2 da costruire` · START bloccato finché v2 non è sigillato ·
nessun dato raccolto · il blocco è controllato da `test_r3.py`, gruppo
`CUSTODIA`, e resta rosso finché non si chiude.

---

## Lo stesso difetto nel sistema? — RECUPERATO ESEGUENDO, 2026-10-04

La domanda che la correzione di Claudio impone: `r3/node.py` registra digest i
cui oggetti potrebbero non esserci più?

Non l'ho letto e concluso. L'ho **eseguito** su `d6d329a`, con
`R3_DATA_DIR` in una cartella temporanea.

| esperimento | esito |
|---|---|
| oggetto presente accanto al digest | `documents_missing_or_corrupt=[]` |
| **oggetto cancellato, digest conservato** — il caso di v1 | **RILEVATO** |
| **oggetto sostituito con byte diversi sotto lo stesso digest** — la falsa ricostruzione | **RILEVATO** |

`upload()` scrive l'oggetto nella stessa chiamata in cui ne calcola il digest;
`download()` ri-verifica prima di restituire; `_state_fingerprint()` rilegge
ogni file e confronta, trattando anche `OSError` come guasto.

**Il codice ha la disciplina che noi due non abbiamo avuto in chat.** Dove il
codice e noi divergevamo, ha vinto il codice — che è la regola di questo
repository, applicata per una volta a chi la scrive.

### Però c'è un dettaglio, e conta

`document_count` resta **1** anche quando l'oggetto è scomparso. Il digest
orfano continua a essere contato come documento; il guasto compare solo in
`documents_missing_or_corrupt`, che è un campo separato.

**Chi legge `document_count` senza leggere `documents_missing_or_corrupt`
riproduce esattamente il difetto di v1**, questa volta dentro il sistema. Non è
un bug — il dato c'è — è una trappola di lettura, dello stesso genere di quelle
che abbiamo messo negli item.

*Falsificazione:* un consumatore di `/state-fingerprint` che legga entrambi i
campi smentisce la preoccupazione. Prossimo esperimento verificabile: cercare
nei 678 commit chi consuma quell'endpoint, e quali campi legge.

---

*Registro **RECUPERATO** negli hash e nei commit citati, **INFERITO** nelle
conseguenze, **UNKNOWN** sulla recuperabilità dei byte.*
