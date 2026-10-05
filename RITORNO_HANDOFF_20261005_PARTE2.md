# Ritorno — handoff 2026-10-05, parte 2: verifica autenticata

Seguito di [`RITORNO_HANDOFF_20261005.md`](RITORNO_HANDOFF_20261005.md).
**UTC:** 2026-10-05T12:14Z–12:20Z. Checkpoint: `origin/main` = `0100630e`.

---

## 1 — Lettura del token: FERMATO, come disposto

Istruzione: *«Puoi usare il token esistente solo attraverso un canale che lo
mantenga riservato… Se il connettore lo espone nel testo della conversazione,
fermati.»*

Canali verificati, tutti negativi:

| canale | esito |
|---|---|
| CLI `railway` (permetterebbe `railway run` che inietta senza stampare) | **assente** |
| `R3_API_TOKEN` già nell'ambiente di sessione | **assente** |
| `RAILWAY_TOKEN` per autenticare una CLI | **assente** |
| `get-service-config` / `describe-service` | restituiscono **solo i nomi** delle variabili |
| `get-staged-changes` | valori **redatti** |
| `list-variables` | **restituisce i valori nel testo della conversazione** |

L'unico strumento che legge i valori li renderizza nella conversazione.
**Non l'ho chiamato.** Nessun fingerprint letto, nessun hash confrontato.

### Il canale che soddisfa il vincolo, e che non avevo considerato

Il token può entrare come **variabile d'ambiente della sessione**, non come
messaggio: si aggiunge dalle impostazioni dell'ambiente cloud — menu
dell'ambiente nella barra del titolo, poi *Edit* — con nome **`R3_API_TOKEN`**.

Lo leggo da `os.environ` e non compare mai in chat, nei log né nel repository.
**Lo raccoglie una sessione nuova**, non questa.

Con quello presente eseguo in una sola passata: `GET /state/fingerprint` su
entrambi i nodi, confronto di `document_hashes`, `document_set_sha256`,
`documents_missing_or_corrupt`, `storage_id`, `protocol_event_count`.

Il documento del progetto conferma che quell'endpoint **non restituisce
segreti** (`docs/R3_PERSISTENCE_RESTART_PROOF.md`): solo `verify_key`,
`storage_id` e hash.

---

## 2 — Controller RRR e protocollo di attivazione: TROVATI — FACT

Nessuna chiave creata, nessun controllo disabilitato: solo lettura del codice su
`origin/main`.

### Il controller

**`R3_CONTROL_VERIFY_KEY_HEX`** — letto da `r3/node.py` come
`CONTROL_VERIFY_KEY_HEX`. È la **chiave pubblica di verifica** del controller,
non un segreto: il materiale privato resta dove già sta.

`docs/R3_PERSISTENCE_RESTART_PROOF.md` lo dice alla lettera:

> «Il materiale di verifica del controller RRR (`R3_CONTROL_VERIFY_KEY_HEX`,
> chiave pubblica) va impostato tramite **il percorso di controllo autorizzato
> esistente**. Finché manca, `/ready` resta 503 con
> `rrr_controller_key_not_configured`: **è corretto**.»

Quindi il 503 che avevo riportato come reperto è **atteso e documentato**.
Correggo il tono del mio rapporto precedente: è una condizione dichiarata, non
un guasto scoperto.

### Il protocollo di attivazione

Da `r3/node.py`, `_readiness_state()`:

```python
latest = _rrr_latest()
active = bool(latest and latest["action"] == "activate")
```

RRR è attivo **se e solo se l'ultimo evento RRR ha `action == "activate"`**.
Gli eventi entrano da **`POST /protocol/rrr/event`** e sono verificati da
`verify_event` contro la chiave pubblica del controller.

**Non è un flag di configurazione: è un evento firmato dal controller esistente.**
Le rotte già presenti: `GET /protocol/rrr/policy`, `GET /protocol/rrr/status`,
`POST /protocol/rrr/event`.

### I quattro cancelli di `/ready`, e cosa dicono i reason osservati

```python
if not API_TOKEN or API_TOKEN == "changeme":  reasons.append("api_token_not_configured")
if not CONTROL_VERIFY_KEY_HEX:               reasons.append("rrr_controller_key_not_configured")
if REQUIRE_DURABLE_STATE and not durable:    reasons.append("durable_state_not_detected")
if REQUIRE_RRR_ACTIVE and not active:        reasons.append("rrr_not_active")
```

I `reasons` osservati alle 12:0xZ su entrambi i nodi erano **solo due**:
`rrr_controller_key_not_configured`, `rrr_not_active`. Da cui, per assenza:

| cancello | stato dedotto |
|---|---|
| `api_token_not_configured` | **assente dai reason → `R3_API_TOKEN` è configurato** su entrambi i nodi, e non è `changeme` |
| `durable_state_not_detected` | **assente → volume rilevato come mount** su entrambi |
| `rrr_controller_key_not_configured` | presente → chiave pubblica del controller **da impostare** |
| `rrr_not_active` | presente → **nessun evento `activate`** ancora |

Restano quindi **due** passi, entrambi sul percorso di controllo già esistente:
impostare la chiave pubblica, poi inviare l'evento `activate` firmato.

### Issue #86: la prima metà è ora soddisfatta

Il documento apre con: *«Stato: **APERTO** finché non esistono volumi Railway su
`/data` per entrambi i nodi e due prove di restart remoto PASS per nodo.»*

Verificato oggi: `r3-external-node-a` → volume `r3-node-a-data`;
`r3-external-node-v2` → volume `r3-node-v2-data`. **Un volume per nodo, mai
condiviso**, esattamente come il documento prescrive. La prima condizione è
chiusa.

Resta la seconda: due prove di restart per nodo con
`scripts/r3_restart_proof.py`, che richiede il Bearer — cioè il punto 1.

---

## 3 — Orchestra: i due livelli sono separati, e blocca il primo — FACT

Istruzione: *«verifica separatamente accesso Vercel e capacità di eseguire una
POST con autenticazione applicativa: il solo connettore autorizzato non basta.»*

Confermato, ed è dimostrabile.

### Livello 1 — piattaforma Vercel

`get_project` su `prj_NfWglC7AYRQs6W5pJBB6nf3lDqXN` con
`teamId=team_dO423fnEAekxtan0rF3u2CQt` → **403**
`Not authorized: Trying to access resource under scope "claudio-terzi-s-projects"`.
`list_teams` del connettore → **0 team**. Utente: `npn8km6jm7-3791`.

### Livello 2 — autenticazione applicativa: NON TESTABILE OGGI

POST con header applicativi presenti e **volutamente non validi**:

```
POST https://claudio-ebon.vercel.app/api/orchestra
authorization: Bearer non-valido-di-proposito
x-r3-token: non-valido-di-proposito

HTTP/2 401
{"protection":{"vercel_auth_enabled":true,"password_enabled":false,…},
 "error":{"message":"Protected deployment","code":"401"},
 "message":"Protected by Vercel Authentication"}
```

**Risponde la piattaforma, non l'applicazione.** La forma del corpo è quella
della protezione Vercel; l'app non vede la richiesta. Quindi l'autenticazione
applicativa non è *insoddisfatta*: è **non osservabile** finché il livello 1
blocca.

Conseguenza, che è esattamente il tuo punto: risolvere B-BLOCK-1 **non** chiude
task_B. Apre soltanto la possibilità di misurare B-BLOCK-2, che oggi è ignoto.

*Nota di etichetta:* che `claudio-ebon.vercel.app` sia il dominio di
`prj_NfWglC7…` è **INFERITO** — ricavato dai riferimenti nel repository, non
dall'API, che mi è chiusa. Se fosse un altro dominio, le misure del livello 1
restano valide e quelle del livello 2 vanno rifatte.

### Non ho usato i bypass

`web_fetch_vercel_url` e `get_access_to_vercel_url` sono disponibili ma: fanno
**GET** mentre l'incarico richiede **POST**, e il secondo **crea un link di
bypass della protezione** — modifica vietata dal handoff. Non chiamati.

---

## Postcondizioni

- **Nessuna modifica**: nessun segreto letto, nessuna chiave creata, nessun
  controllo disabilitato, nessun deployment, nessuna variabile scritta, nessun
  bypass creato.
- **#113 non unita.**
- Nessun segreto in questo documento.

## Blocchi precisi

| id | blocco | cosa serve |
|---|---|---|
| **A-BLOCK-1** | fingerprint e confronto hash | `R3_API_TOKEN` come **variabile d'ambiente della sessione** (nome esatto: `R3_API_TOKEN`), raccolta da una sessione nuova |
| **A-BLOCK-2** | recupero su copia isolata | canale exec dentro un servizio, o snapshot/export di volume: il connettore Railway non espone né l'uno né l'altro |
| **B-BLOCK-1** | accesso Vercel | autorizzazione del connettore sullo scope `claudio-terzi-s-projects` |
| **B-BLOCK-2** | POST con auth applicativa | **ignoto**, e non misurabile prima di B-BLOCK-1 |
| **RRR-1** | `/ready` 200 | `R3_CONTROL_VERIFY_KEY_HEX` sui due nodi, dal percorso di controllo esistente |
| **RRR-2** | RRR attivo | evento `activate` firmato su `POST /protocol/rrr/event` |

---

*§1 **RECUPERATO** (assenza dei canali verificata eseguendo). §2 **RECUPERATO**
dal codice e dal documento citati, con una deduzione per assenza etichettata
come tale. §3 **RECUPERATO** nei codici e nei corpi, **INFERITO** sulla
corrispondenza dominio↔progetto.*
