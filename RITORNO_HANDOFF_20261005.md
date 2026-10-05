# Ritorno — R3 handoff 2026-10-05

Formato richiesto dal documento
`docs/R3_PEER_EXECUTION_HANDOFF_20261005.md` @ `candidate/r3-peer-handoff-20261005`.

Checkpoint riletto: `origin/main` = `0100630e1a6b9e080bd291b8635bc0e53a7b8756`
«Preserve verified R3 resilience and admission evidence (#116)» — **verificato
antenato di main**.

---

## task_A — Railway: PARZIALE (FACT su 5 punti, BLOCKED su 2)

**UTC:** 2026-10-05T12:04Z–12:12Z
**Scope:** Railway workspace `raffaellocantatelli's Projects`, progetto
`deepseek-eval-temp-2026-09-15` (`2d6bff0c-b127-465d-99c4-fb7f70dc593d`),
ambiente `production` (`ae59a2c6-2c8c-453c-a7d4-a211040ceff3`).
**Repo dei servizi:** `claudioterzi/Claudio`, branch `main`.

### A.1 — FACT: sleep/resume Railway reale, misurato

Non SIGSTOP locale: inattività reale della piattaforma, su `r3-external-test`
che `describe-environment` riportava `SLEEPING`.

| chiamata | path | HTTP | tempo totale | TTFB |
|---|---|---|---|---|
| **1 — a freddo** | `/health` | 200 | **7,851 s** | 7,851 s |
| 2 — a caldo | `/health` | 200 | 0,288 s | 0,288 s |
| 3 — a caldo | `/health` | 200 | 0,260 s | 0,260 s |

**Atteso vs osservato:** atteso un primo accesso lento e i successivi rapidi se
lo sleep è reale. Osservato **27×** di differenza fra la prima e la seconda
chiamata, stesso host, stesso path, a secondi di distanza.

**Riscontro da fonte indipendente:** dopo le chiamate, `environment-status`
riporta `r3-external-test` `state: online`, deployment `1cda7d0c` `SUCCESS`,
`statusUpdatedAt: 2026-10-05T12:07:24.117Z` — l'istante delle chiamate.
*Limite dichiarato:* nello stesso intervallo anche `r3-typesafe-sister` risulta
aggiornato (`12:07:26.367Z`) **senza che io l'abbia contattato**. Non attribuisco
quel cambiamento alla mia azione: l'evidenza primaria è la misura dei tempi.

### A.2 — FACT: identità dello storage persiste fra i boot

Da `/ready`, endpoint **pubblico**, su entrambi i nodi con volume:

| campo | `r3-external-node-a` | `r3-external-node-v2` |
|---|---|---|
| `durable_state_required` | true | true |
| `durable_state_detected` | **true** | **true** |
| `storage_id_created_this_boot` | **false** | **false** |
| `signing_key_source` | `data_dir` | `data_dir` |
| `data_dir` | `/data` | `/data` |
| `policy_sha256` | `e6b45941ea9762dfbfd5d23919b9be03d76dc1eb0cfc042044ac374c53d44ded` | **identico** |

`storage_id_created_this_boot: false` è la continuità dell'identità di storage
**dichiarata dal nodo stesso**: il marcatore non è stato ricreato a questo
avvio. La chiave di firma Ed25519 vive sul volume, non in variabile d'ambiente.
Lo stesso `policy_sha256` su due nodi indipendenti.

### A.3 — FACT: nessuna replica

`environment-status` su tutti e 5 i servizi: `replicaStatus: {running: 1,
crashed: 0, total: 1}`, `servicesWithIssues: 0`, `pendingWork: []`.
`multiRegionConfig: {sfo: {numReplicas: 1}}` su ogni servizio.
Tre volumi da 500 MB, regione `sfo`, **ognuno montato su un solo servizio**;
nessun bucket.

**Qualunque affermazione di resilienza va letta entro questo limite: replica 1,
regione singola, nessuna copia.**

### A.4 — FACT: readback indipendente di `drainingSeconds`

L'evidenza `R3_RESILIENCE_COMPLETION_20261005.json` dichiara
`drainingSeconds.saved: 10, readback: true, effective: "next deployment"`.

`get-service-config` conferma `drainingSeconds: 10` **nella config live**, con
`staged: null`, su `r3-external-node-a` e `r3-external-node-v2`. **Confermato da
fonte diversa da chi l'ha scritto.**

### A.5 — FACT che corregge l'evidenza: `restartPolicy` maxRetries 10 non si trova

L'evidenza dichiara `restartPolicy: {type: ON_FAILURE, maxRetries: 10,
write_acknowledged: true}` con la giustificazione
`independent_readback: "default fields omitted by API"`.

Osservato:

| servizio | campo restituito dall'API |
|---|---|
| `r3-external-node-a` | **assente** |
| `r3-external-node-v2` | **assente** |
| `r3-external-test` | `restartPolicyMaxRetries: 5` |
| `r3-external-property-runner` | `restartPolicyMaxRetries: 3` |

**L'API non omette quel campo per default: lo restituisce per due servizi su
quattro.** Quindi «omesso per default» non spiega l'assenza sui due nodi dove il
10 sarebbe stato scritto. Le due letture possibili — il valore 10 coincide con
un default che Railway tace, oppure la scrittura non è atterrata su quei due
servizi — **non sono distinguibili da qui**. Non dichiaro PASS.

### A.6 — FACT non richiesto: i nodi di produzione non sono READY

`/health` → `200 {"status":"healthy"}`. Ma `/ready` → **`503`**:

```json
"ready": false,
"rrr_active": false,
"rrr_event_id": null,
"reasons": ["rrr_controller_key_not_configured", "rrr_not_active"]
```

Su **entrambi** i nodi. Il protocollo RRR non è attivo in produzione perché la
chiave del controller non è configurata — indipendentemente dal fatto che il
deployment sia `SUCCESS` e `/health` risponda 200.

### Controlli negativi — tutti falliti come devono

| controllo | atteso | osservato |
|---|---|---|
| dominio inesistente `bogus-r3-nodo-inesistente-production.up.railway.app/health` | fallire | **404** in 0,438 s |
| `/state/fingerprint` senza token, node-a | fallire | **401** `{"detail":"Token non valido"}` |
| `/state/fingerprint` senza token, node-v2 | fallire | **401** idem |
| `/sync/hashes` senza token | fallire | **401** idem |
| `/status` senza token | fallire | **401** idem |

*Errore mio, corretto prima di riportarlo:* al primo tentativo avevo usato
`/state-fingerprint` e ottenuto 404. La rotta reale è **`/state/fingerprint`**
(`r3/node.py` @ `origin/main`, riga 463). Il 404 era mio, non del nodo.

### changes + rollback

**Nessuna modifica.** Nessun deployment, nessuna variabile, nessuna policy,
nessuna risorsa creata o rimossa, nessun nodo arrestato. La patch staged del
progetto `r3-typesafe-sister` **non è stata applicata**.

Unico effetto collaterale: `r3-external-test` è stato **risvegliato da una
richiesta HTTP**, che è ciò che fa qualunque client. Torna in sleep da sé per
inattività; nessun rollback necessario e nessuna configurazione toccata.

### BLOCKED — e manca esattamente questo

**A-BLOCK-1 — confronto dei contenuti e SHA-256 prima/dopo.**
Serve `R3_API_TOKEN` dei nodi per `/state/fingerprint`, che restituisce
`document_hashes`, `document_set_sha256`, `documents_missing_or_corrupt`,
`storage_id`. Senza token: 401. **Non ho estratto il segreto** da
`list-variables`, pur avendone lo strumento: il handoff vieta di estrarre
segreti e non lo faccio senza autorizzazione esplicita.

**A-BLOCK-2 — recupero su copia isolata dello stato reale.**
Serve un canale di esecuzione dentro un servizio Railway, oppure uno snapshot
o export dei volumi. Il connettore Railway di questa sessione **non espone né
exec né snapshot di volume**: i tre volumi sono leggibili solo da dentro il
container che li monta. Senza quel canale non esiste copia isolata, quindi non
esiste confronto prima/dopo su copia.

---

## task_B — Orchestra autenticata: BLOCKED

**UTC:** 2026-10-05T12:04Z
**Scope canonico dal handoff:** `team_dO423fnEAekxtan0rF3u2CQt` /
`prj_NfWglC7AYRQs6W5pJBB6nf3lDqXN`.

### Osservato

| prova | risultato |
|---|---|
| `get_project` su `prj_NfWglC7…` con `teamId` canonico | **403** `Not authorized: Trying to access resource under scope "claudio-terzi-s-projects"` |
| `list_teams` del connettore | **0 team** |
| utente autenticato | `npn8km6jm7-3791` |
| `GET https://claudio-ebon.vercel.app/api/orchestra` | **302 → 401**, `Protected by Vercel Authentication` |
| `POST` stesso URL | **401**, `{"vercel_auth_enabled": true, "password_enabled": false}` |

**Divergenza dal handoff, da registrare:** il documento riporta «GET Orchestra
200». Da qui il GET dà 302/401. Quel 200 è stato ottenuto da una sessione
autorizzata; **non è riproducibile da questo esecutore**, e in ogni caso il
documento stesso dice che un GET 200 non prova inferenza.

### Perché non ho forzato

`web_fetch_vercel_url` e `get_access_to_vercel_url` esistono nel connettore, ma:
fanno **GET** (l'incarico richiede un **POST**), e creano un link di bypass
dell'autenticazione — che è una modifica della protezione, vietata dal handoff.
Non li ho usati.

### BLOCKED — manca esattamente questo

**B-BLOCK-1:** autorizzazione del connettore Vercel sullo scope
`claudio-terzi-s-projects` (`team_dO423fnEAekxtan0rF3u2CQt`). Oggi 403.
**B-BLOCK-2:** un modo di eseguire un **POST** autenticato oltre Vercel
Authentication, senza disattivare la protezione e senza estrarre segreti.

Con B-BLOCK-1 risolto, B è eseguibile in una chiamata.

---

## task_C — dispositivo Rizzo: NON TENTATO

Il handoff lo dichiara dipendente dal dispositivo online, visto offline 32 ore
prima. Nessun endpoint raggiungibile da questo esecutore. Nessuna prova
tentata, nessuna affermazione.

---

## Postcondizioni

- `origin/main` invariato; nessun push su `claudioterzi/Claudio` (questa
  sessione non ha scrittura su quel repository).
- PR #113 **non** toccata: le prove A non sono concluse.
- Nessun segreto in questo documento. `policy_sha256` è un hash pubblico
  restituito da un endpoint pubblico.

## Blocker residui, in ordine di costo

1. **B-BLOCK-1** — un'autorizzazione Vercel. Sblocca l'intero task_B.
2. **A-BLOCK-1** — `R3_API_TOKEN` in lettura. Sblocca il readback degli hash.
3. **A-BLOCK-2** — canale exec o snapshot di volume. È il più costoso e l'unico
   che richiede infrastruttura nuova.

---

*A.1–A.6 e i controlli negativi **RECUPERATO**, eseguiti alle UTC indicate.
A.5 **FACT** sulla discrepanza, **UNKNOWN** su quale delle due letture sia
vera. B **RECUPERATO** nei codici di stato. C **UNKNOWN**.*
