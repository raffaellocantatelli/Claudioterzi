# Preregistrazione dello scoring — R3-PEER/1.1c, test di convergenza

**Scritta PRIMA che il fixture esista.** È l'unico ordine che rende onesto il
punteggio: chi scrive le regole dopo aver visto la distribuzione degli eventi
può scegliere i sottoinsiemi in cui l'accordo è probabile.

Riferimento: `claudioterzi/Claudio` @ `d999ef7`,
`docs/R3_PEER_1_1c_CONVERGENCE_SPEC_2026-10-04.md`, §9:

> `Next: produce due implementazioni indipendenti, test su 1.000 eventi misti`
> `Soglia: disaccordo < 2% su decisioni binarie`
> `Se > 2%: la specifica è sottospecificata, non le implementazioni`

---

## 0. Correzione d'ordine alla sequenza proposta

La sequenza di Claudio è: ① freeze A/B → ② genera fixture → ③ freeze scoring →
④ esegui A/B.

**③ va prima di ②.** Chi congela lo scoring dopo aver visto il fixture ha
visto, per costruzione, quali strati sono densi e quali rari. È la stessa forma
del difetto che Claudio stesso ha corretto sull'altro esperimento: *non ci si
ferma dopo aver guardato un controllo*. Qui: non si scrivono le regole dopo
aver guardato i dati, anche se i dati non sono ancora risposte.

Sequenza corretta: ① freeze A/B → **② freeze scoring (questo file, hashato)** →
③ genera fixture → ④ esegui A/B.

## 0bis. Collisione di nomi, da risolvere adesso

In questo test **A, B, C** sono Qwen, Grok e il generatore. Nell'esperimento
firma **A, B, C, D, E** sono i bracci (cieco, placebo, corpus, canale,
controllo). Due esperimenti aperti negli stessi giorni, con le stesse lettere,
significati diversi.

Proposta: qui **IMPL-1**, **IMPL-2**, **GEN**. Le lettere restano
all'esperimento firma, che le ha nei documenti sigillati e non può cambiarle.

---

## 1. Il problema del denominatore — RECUPERATO dalla spec

La soglia parla di «decisioni binarie». **Il DECISION RECORD di §5 non ne
contiene quasi nessuna.**

| campo | valori | tipo |
|---|---|---|
| `decision` | ACCEPT · LINK-ONLY · DUPLICATE · REJECT · SUPERSEDES · REVOCATION · MARKS_AT_RISK | 7 classi |
| `memory_write` | NONE · CANONICAL · LINK · SUPERSEDE · MARK_AT_RISK | 5 classi |
| `identity_vector.node_auth_status` | VERIFIED_ED25519 · MISMATCH · UNVERIFIED · MISSING | 4 classi |
| `identity_vector.transport_status` | 3 valori | 3 classi |
| `identity_vector.provider_status` | 4 valori | 4 classi |
| `identity_vector.model_status` | 3 valori | 3 classi |
| `evidence_origin_verified` | 5 valori | 5 classi |

Nessun booleano. Quindi «decisioni binarie» significa necessariamente
**binarizzazioni derivate** — e *quale* si scelga cambia il numero. Vanno
nominate prima, o la soglia del 2% non ha denominatore.

### Le quattro binarizzazioni, e nessun'altra

```
B1  ACCEPTED           := decision == "ACCEPT"
B2  WROTE_CANONICAL    := memory_write == "CANONICAL"
B3  NODE_AUTH_OK       := identity_vector.node_auth_status == "VERIFIED_ED25519"
B4  ADMITTED_TO_MEMORY := memory_write in {CANONICAL, LINK, SUPERSEDE}
```

Nessuna binarizzazione aggiuntiva è ammessa dopo l'esecuzione. Se ne servisse
una, va aggiunta qui e il file va ri-hashato **prima** di generare il fixture.

---

## 2. Campi confrontabili, e quelli che non lo sono per costruzione

Questo è l'altro modo in cui il test diventa vacuo. Includere campi che **non
possono** coincidere fra implementazioni indipendenti porta il disaccordo al
100%; escluderli dopo aver visto i risultati è post-hoc.

### Confrontabili — 8 campi, deterministici da input + policy

```
decision
memory_write
identity_vector.node_auth_status
identity_vector.transport_status
identity_vector.provider_status
identity_vector.model_status
evidence_origin_verified
input_event_hash          (deterministico solo grazie a JCS RFC 8785, §7)
```

### NON confrontabili, esclusi prima di vedere qualunque dato

| campo | perché non può coincidere |
|---|---|
| `decision_id` | UUIDv7, generato localmente |
| `timestamp` | orologio |
| `ledger_index` | ordinamento locale |
| `prev_decision_hash`, `entry_hash` | dipendono dalla catena locale |
| `policy_profile_id`, `policy_version`, `router_version` | configurazione per implementazione |
| `evidence_parent_ids`, `causal_origin_ids` | contengono `decision_id` locali |
| `raw_input_hash` | confrontabile **solo se** il fixture fornisce il raw byte-identico; incluso se sì, escluso se no — deciso qui, non dopo |
| **`reason`** | **testo libero.** La spec dice `"reason": "string"`, senza vocabolario |

### `reason` è una lacuna della spec, non solo un campo da escludere

Un record pensato per essere confrontato fra implementazioni contiene un campo
di prosa. Due implementazioni non produrranno mai la stessa stringa, quindi
`reason` è inutilizzabile come evidenza — eppure è l'unico campo che dice
*perché*.

**La correzione è la stessa già adottata altrove in questo progetto: vocabolario
chiuso.** Un `reason_code` enumerato, con `reason` libero accanto per gli umani
e fuori dal confronto. Come ogni altra cosa: va deciso in 1.1c, non dopo la
promozione.

---

## 3. UNDERSPECIFIED — la regola che decide se la spec può vincere barando

Se un'implementazione dichiara UNDERSPECIFIED e l'altra decide, come conta?

**Conta come DISACCORDO.** Non è una scelta neutra ed è la ragione:

> una specifica che permette a un implementatore di decidere e all'altro di
> astenersi **è sottospecificata per definizione**.

Se contasse come accordo, o fosse escluso dal denominatore, 1.1c potrebbe
superare la soglia **essendo vaga**: ogni punto difficile diventerebbe
un'astensione, e le astensioni non peserebbero. Sarebbe un test che non può
perdere.

| IMPL-1 | IMPL-2 | conta come |
|---|---|---|
| decide X | decide X | accordo |
| decide X | decide Y | disaccordo |
| decide X | UNDERSPECIFIED | **disaccordo** |
| UNDERSPECIFIED | UNDERSPECIFIED | **accordo**, e registrato a parte come *lacuna condivisa* |

L'ultima riga è l'esito più informativo del test: due implementatori
indipendenti che si fermano **nello stesso punto** hanno trovato un buco della
spec che nessuna review aveva visto. Va contato come accordo e riportato
separatamente, con l'elenco degli eventi.

---

## 4. Composizione del fixture — è l'esperimento, non un dettaglio

> **CORREZIONE, prima che il fixture esista.** La prima versione di questa
> tabella sommava **920**, non 1.000, e il denominatore reale era **820**, non
> 900. Ho scritto nella mia stessa preregistrazione **la trappola dell'item 3
> dei dieci**: un totale in testa che i dati sotto non mostrano. Trovata
> estraendo i numeri dalla tabella con uno script invece di rileggere la riga
> «totale».
>
> I conteggi sotto sono corretti e verificati: somma 1.000, denominatore 900,
> minimo 25 per strato. `test_r3.py` ora ricalcola entrambi a ogni esecuzione.
> L'hash di questo file è cambiato di conseguenza: legittimo, il fixture non
> esiste ancora.

**Mille eventi banali danno disaccordo < 2% qualunque sia la qualità della
spec.** La composizione decide cosa il test può rilevare, quindi va preregistrata.

### Il vincolo quantitativo che la determina

Soglia 2% su 1.000 eventi = **20 disaccordi**. Uno strato di dimensione *n*,
anche se la spec vi è completamente sottospecificata, produce al massimo *n*
disaccordi. **Quindi uno strato con n ≤ 20 non può da solo far scattare la
soglia**, e una sottospecificazione reale lì resterebbe invisibile.

**Minimo per strato: 25 eventi.** Non è un numero di comodo: è 20 più margine.

### I dodici strati

| # | Strato | Regola della spec che esercita | n |
|---|---|---|---|
| S1 | envelope valido ordinario | baseline | 300 |
| S2 | `channel_id` assente dal Channel Registry | §8 Envelope, finding 3 | 70 |
| S3 | `msg_id` duplicato, stesso (channel, sender) | §8 unique scoped | 70 |
| S4 | `nonce` riusato, `msg_id` nuovo | §8, finding 11 | 60 |
| S5 | sender dichiara `canonical_memory_head` | §8: vietato, deve usare `observed_` | 60 |
| S6 | `node_auth` MISMATCH: key_id noto, pubkey diversa | §5 identity_vector | 70 |
| S7 | REVOCATION con `effective_from` nel passato | §8 Lifecycle | 55 |
| S8 | messaggio firmato da chiave revocata | §8 Lifecycle | 55 |
| S9 | LINK-ONLY che tenterebbe CanonicalMemory | §8 Storage: mai | 50 |
| S10 | `MODEL_ATTESTED` senza nonce+challenge+request_id | §8 Decision | 50 |
| S11 | replay broadcast di stato obsoleto | **O5, APERTO** | 50 |
| S12 | `claimed` vs `verified` in conflitto a livello schema | **O1, APERTO** | 50 |
| S13 | ordine chiavi JSON permutato, stesso stato logico | §7 JCS: deve dare lo stesso `input_event_hash` | 60 |
| | | **totale** | **1000** |

S11 e S12 esercitano **OPEN FINDINGS**. Previsione dichiarata: lì il disaccordo
sarà alto, e sarà **corretto** — la spec li dichiara aperti. Vanno riportati
separatamente e **non** conteggiati nella soglia del 2%, che riguarda ciò che
1.1c sostiene di aver deciso. Escluderli dopo sarebbe post-hoc; escluderli qui,
prima, è disegno.

**Denominatore della soglia: 900 eventi** (tutti meno S11 e S12). 2% = 18
disaccordi.

---

## 5. Determinismo — il seed non basta

Un seed registrato non rende riproducibile un generatore che itera su un `set`
o su chiavi non ordinate.

Requisiti del generatore, verificabili:

1. `sha256` del generatore **preregistrato insieme al seed**;
2. versione di Python dichiarata; nessuna dipendenza esterna;
3. nessuna iterazione su `set` o `dict` non ordinato nel percorso che produce
   eventi; ordinamento esplicito dove serve;
4. `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)`
   per la serializzazione, coerente con JCS;
5. **prova di riproducibilità**: due esecuzioni indipendenti producono file con
   lo stesso `sha256`. Senza questa prova, il seed è una dichiarazione.

---

## 6. Conflitto d'interesse, dichiarato

Chi scrive questo file ha letto 1.1c e ne ha già segnalato due lacune: il
Ledger non distingue chi ha **originato** da chi ha **trasmesso**, e `reason` è
testo libero.

Un generatore scritto da chi conosce i punti deboli tenderebbe a colpirli — che
è buon disegno, **ma solo se dichiarato prima**. È dichiarato: S11, S12 e S13
sono scelti conoscendo le lacune. Gli altri strati derivano meccanicamente da
§8, riga per riga.

**Chi genera il fixture non deve valutare il disaccordo finale.** È P5: il
punteggio va a una funzione che non ha scelto la composizione.

---

## 7. Cosa questo test non può dire

Due implementazioni, 900 eventi utili, nessuna correzione per confronti
multipli su quattro binarizzazioni più l'accordo multiclasse. **Può mostrare in
modo convincente che la spec è sottospecificata. Non può mostrare che è
completa** — può solo non trovare controesempi dove ha guardato.

Un disaccordo sotto il 2% significa: *nei dodici strati scelti, con questi due
implementatori, non è emersa ambiguità*. Non significa che non ce ne siano.

---

*Documento **IPOTESI** nel disegno, **RECUPERATO** nelle citazioni di `d999ef7`,
**UNKNOWN** negli esiti. Hash di questo file in
[`PREREGISTRAZIONE_SCORING.sha256`](PREREGISTRAZIONE_SCORING.sha256), calcolato
prima che il fixture esista.*
