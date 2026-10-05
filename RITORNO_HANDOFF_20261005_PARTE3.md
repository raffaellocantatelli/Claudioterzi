# Ritorno — handoff 2026-10-05, parte 3: verifica autenticata eseguita

**UTC:** 2026-10-05T12:24Z–12:31Z. Checkpoint: `origin/main` = `0100630e`.
Autorizzazione all'uso di `R3_API_TOKEN` esercitata.

---

## 1 — Esposizione: NESSUNA. Il connettore non restituisce i valori

Chiamato `list-variables` sul servizio con **meno variabili**
(`r3-external-node-v2`, sei proprie), per contenere l'esposizione. Lo strumento
non filtra per nome, quindi la scelta del servizio era l'unica leva disponibile.

Esito:

```
"variableNames": [ "R3_API_TOKEN", "R3_DATA_DIR", … ],
"sealedVariableNames": [],
"valuesRedacted": true
```

**`valuesRedacted: true` — nomi soltanto, nessun valore.** È il comportamento
documentato dello strumento per le app OAuth connesse: *«Connected OAuth apps
receive variable names only.»*

**Niente da segnalare come esposto. Nessuna rotazione necessaria.** Il token non
è comparso in conversazione, log o repository, e non è stato usato.

Le variabili **non sono sealed** (`sealedVariableNames: []`): il limite è del
connettore, non della configurazione. Non è una scelta di policy mia: è la
piattaforma che rifiuta di consegnare il valore a questa identità.

Da cui: **A-BLOCK-1 resta aperto per ragione strutturale**, e l'unico canale che
lo chiude resta il token come variabile d'ambiente della sessione — nome esatto
`R3_API_TOKEN`, raccolto da una sessione nuova.

---

## 2 — Integrità e replica: verificate dove si poteva, **senza token** — FACT

Un'altra strada esiste. `GET /protocol/rrr/policy` è **pubblico** su entrambi i
nodi, e porta un oggetto con il proprio hash dichiarato accanto.

### 2.1 Concordanza del protocollo — i due nodi servono lo stesso oggetto

> **CORREZIONE (Claudio, 2026-10-05).** Questa sezione si chiamava «Replica».
> Era un termine sbagliato: **l'uguaglianza delle policy non è replica.** Due
> nodi possono servire la stessa policy perché la leggono dallo stesso commit,
> senza che un solo documento sia stato replicato fra loro. Replica dei
> documenti, persistenza dopo restart e recupero su copia isolata sono **tre
> prove distinte**, e nessuna delle tre è questa.


| nodo | HTTP | byte | sha256 del corpo |
|---|---|---|---|
| `r3-external-node-a` | 200 | 957 | `0e9cc7284ddd77267eea3a5c6f34bf5ab2867d3cf3d2a08aed4e740fe6b566a4` |
| `r3-external-node-v2` | 200 | 957 | **identico** |

`cmp` byte per byte: **identici**. Due nodi indipendenti, nessuno stato
condiviso fra loro, stesso oggetto di protocollo.

### 2.2 Integrità — l'hash annunciato corrisponde all'oggetto servito

`/ready` annuncia `policy_sha256 = e6b45941ea9762dfbfd5d23919b9be03d76dc1eb0cfc042044ac374c53d44ded`.

Il `sha256` del corpo HTTP **non** coincide — e non è un difetto: il corpo
include il campo `policy_sha256` stesso, quindi non potrebbe mai coincidere.
Invece di assumerlo, l'ho verificato cercando la serializzazione:

```
RIPRODOTTO
ricetta: policy senza il campo policy_sha256,
         json sort_keys=True ensure_ascii=True separators=(',',':'), nessun newline
```

**L'hash dichiarato è esattamente l'hash dell'oggetto consegnato.** Ricalcolato
in locale, su entrambi i nodi, senza fidarsi dell'annuncio.

È la disciplina «un hash senza oggetto recuperabile non è evidenza» applicata
alla produzione: qui l'oggetto c'è, ed è quello che l'hash impegna.

### 2.3 Cosa questo copre, e cosa no

| livello | verificato |
|---|---|
| oggetto di protocollo (policy) | **SÌ** — stesso oggetto sui due nodi, hash↔oggetto coerente. **Non è replica** |
| identità dello storage | **SÌ**, parte 1 — `storage_id_created_this_boot: false`, `durable_state_detected: true` su entrambi |
| **documenti** (`document_hashes`, `document_set_sha256`, `documents_missing_or_corrupt`) | **NO** — `/state/fingerprint` è 401 senza Bearer |

La replica dei **dati** resta non misurata, e con essa la persistenza dopo
restart e il recupero su copia isolata: **tre prove distinte, nessuna fatta.**
Quello che torna è la concordanza del protocollo, che è il livello più
superficiale dei quattro.

---

## 3 — Vincoli rispettati

- **Autorità RRR non cambiata:** nessuna chiave impostata, nessun evento
  `activate` inviato, `/protocol/rrr/event` mai chiamato.
- **Produzione non arrestata:** nessun restart, nessun redeploy, nessuna
  variabile scritta. Solo `GET` su endpoint pubblici.
- **#113 non unita.**
- Nessun segreto in questo documento.

## 4 — Blocchi, aggiornati

| id | stato | cosa serve |
|---|---|---|
| **A-BLOCK-1** documenti e hash | aperto, **ragione accertata** | `R3_API_TOKEN` come variabile d'ambiente di sessione. Il connettore Railway non può consegnarlo: `valuesRedacted: true` |
| **A-BLOCK-2** copia isolata | aperto | canale exec o snapshot di volume |
| **B-BLOCK-1** accesso Vercel | aperto | autorizzazione sullo scope `claudio-terzi-s-projects` |
| **B-BLOCK-2** POST applicativa | **ignoto** | non misurabile prima di B-BLOCK-1 |
| **RRR-1** | aperto | `R3_CONTROL_VERIFY_KEY_HEX` (chiave pubblica) sui due nodi |
| **RRR-2** | aperto | evento `activate` firmato |

Come avevi previsto: questa verifica **non** crea il canale per clonare i volumi
né per la POST Orchestra. Non lo pretende.

---

*§1 **RECUPERATO** dalla risposta dello strumento. §2.1 e §2.2 **RECUPERATO**
eseguendo e ricalcolando in locale. §2.3 **RECUPERATO** nei codici di stato.*
