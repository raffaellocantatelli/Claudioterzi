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

### Dove i byte NON sono — RECUPERATO, 2026-10-04

Ho enumerato **ogni path mai esistito** in `claudioterzi/Claudio`, su tutti i
rami, remoti compresi: **1896 path distinti**.

L'unico file sotto `docs/experiments/` è
`OPENAI_CUSTODY_SHA256_2026-10-04.txt` — i 180 byte del solo hash. **Nessun
placebo, nessun item di contaminazione, su nessun ramo, in nessun commit, mai.**

Il metodo e il suo limite, perché il risultato vale solo se il metodo è sano:
l'enumerazione dei path richiede commit e tree, non i blob. Il clone locale è
un *partial clone* con filtro `blob:none` — i blob arrivano su richiesta, i
tree no — ed è stato interrogato con `GIT_NO_LAZY_FETCH=1`, che avrebbe dato
errore se un tree fosse mancato. Uscita 0, nessun errore: **per i path la
scansione è completa.**

*(Un primo tentativo aveva confrontato gli hash dei soli 1887 blob presenti in
locale e non trovato nulla. Quel risultato era privo di valore — un clone
parziale ne ospita una frazione — e non va citato. È lo stesso errore del
`--depth 1` di agosto, riconosciuto prima di riportarlo.)*

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

### Stato

`APERTO` · START bloccato · nessun dato raccolto · il blocco è controllato da
`test_r3.py`, gruppo `CUSTODIA`, e resta rosso finché non si chiude.

---

*Registro **RECUPERATO** negli hash e nei commit citati, **INFERITO** nelle
conseguenze, **UNKNOWN** sulla recuperabilità dei byte.*
