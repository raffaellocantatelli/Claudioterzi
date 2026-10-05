# STATO DEFINITIVO — 2026-10-05

Presa in atto di dove siamo. Una pagina, nessun ottimismo, nessuna
affermazione senza etichetta. Da leggere per prima in qualunque sessione nuova.

**Checkpoint:** `claudioterzi/Claudio` @ `origin/main` = `0100630e`
«Preserve verified R3 resilience and admission evidence (#116)».
**Verificatore:** `python3 test_r3.py` → **67 superati · 2 falliti · 1 saltato su 70**.
I due rossi sono veri e voluti, e sono elencati sotto.

---

## 1 — Cosa è provato, e come

| # | fatto | prova |
|---|---|---|
| 1 | **sleep/resume Railway reale** | `/health` su un servizio `SLEEPING`: **7,851 s** a freddo, **0,288 s** a caldo, **0,260 s** alla terza. 27×, stesso host e path, a secondi di distanza. Non SIGSTOP locale |
| 2 | **identità dello storage persiste** | `/ready` pubblico su due nodi: `durable_state_detected: true`, **`storage_id_created_this_boot: false`**. Il marcatore non è stato ricreato a questo avvio |
| 3 | **nessuna replica di processo** | `replicaStatus: 1/1` su tutti e 5 i servizi, regione singola `sfo`, tre volumi ognuno su **un solo** servizio, nessun bucket |
| 4 | **`drainingSeconds: 10`** | nella config **live** di entrambi i nodi, `staged: null`. Readback indipendente che all'evidenza mancava |
| 5 | **concordanza del protocollo** | `/protocol/rrr/policy` pubblico: 957 byte **identici byte per byte** sui due nodi |
| 6 | **hash ↔ oggetto coerenti** | `policy_sha256` annunciato **riprodotto in locale** dall'oggetto servito, ricetta trovata e non assunta |
| 7 | **`R3_API_TOKEN` è configurato** | dedotto per **assenza** di `api_token_not_configured` dai `reasons` di `/ready` |
| 8 | **controller e attivazione RRR** | `R3_CONTROL_VERIFY_KEY_HEX` è una **chiave pubblica**; RRR è attivo **se e solo se** l'ultimo evento ha `action == "activate"`, via `POST /protocol/rrr/event` |
| 9 | **Issue #86, prima metà chiusa** | un volume per nodo, mai condiviso: `r3-node-a-data`, `r3-node-v2-data` |
| 10 | **Orchestra: due livelli separati** | POST con header applicativi **non validi** → risponde la **piattaforma** Vercel, non l'app. L'app non vede la richiesta |

### Controlli negativi, tutti falliti come devono

Dominio inesistente → **404**. `/state/fingerprint`, `/sync/hashes`, `/status`
senza token → **401 «Token non valido»** su entrambi i nodi. Script di
confronto senza token → **esce 2**; con token non valido → **esce 3**.

---

## 2 — Cosa NON è provato. Quattro prove distinte, una sola fatta

Tenerle separate è la correzione più importante della giornata.

| # | prova | stato | manca |
|---|---|---|---|
| 1 | concordanza del protocollo | **FATTA** | — |
| 2 | **replica dei documenti** | non fatta | `R3_API_TOKEN` nell'ambiente |
| 3 | **persistenza dopo restart** | non fatta | token + un restart |
| 4 | **recupero su copia isolata** | non fatta | canale exec o snapshot di volume |

La 1 è la più superficiale. Chiamarla «replica» le dava un peso che non ha.

---

## 3 — I due rossi del verificatore, entrambi veri

**`la baseline descrive lo stato attuale`** — la ricostruzione fotografa
`155cb5f`; `origin/main` è ~680 commit più avanti. Si chiude **rifacendo la
baseline**, non allentando il test. Congelato per scelta: leggere quei commit
adesso contaminerebbe chi dovrà interpretare l'esperimento firma.

**`BLOCKER-CUSTODY-02 chiuso: cifrati v2 persistiti`** — v2 è generato, il
round-trip verificato, il manifesto riprodotto e verificato da me. **I due
cifrati non sono depositati**: il deposito è fallito con
`container_session_expired`. Tiene fermo A/B/C/D/E.

---

## 4 — Blocchi, con il prerequisito esatto

| id | blocco | prerequisito | chi |
|---|---|---|---|
| **CUSTODY-02** | esperimento firma | i due cifrati di v2 in `docs/experiments/` | Claudio |
| **A-1** | replica dei documenti | `R3_API_TOKEN` come variabile d'ambiente. Il connettore Railway **non può** consegnarlo: `valuesRedacted: true` | Claudio |
| **A-2** | copia isolata | canale exec in un servizio, o snapshot/export di volume. Railway non espone né l'uno né l'altro | infrastruttura |
| **B-1** | accesso Vercel | autorizzazione sullo scope `claudio-terzi-s-projects` | Claudio |
| **B-2** | POST applicativa | **ignoto**, non misurabile prima di B-1 | — |
| **RRR-1** | `/ready` 200 | `R3_CONTROL_VERIFY_KEY_HEX` sui due nodi | percorso di controllo esistente |
| **RRR-2** | RRR attivo | evento `activate` firmato | percorso di controllo esistente |
| **CANALE** | tutto A-1 | provare il canale: `R3_CHANNEL_PROBE=ok` + sessione nuova | Claudio, un gesto |
| **GATE** | due esperimenti | un commit che unifica il gate a 21 campi, zero rimozioni | Claudio |
| **PR #116** | registrare risultati | accesso GitHub a `claudioterzi/Claudio` per questa sessione | Claudio |

**Il più economico è `CANALE`**: una variabile innocua, non il token, e una
sessione nuova. Sblocca a cascata la prova 2.

---

## 5 — Gli errori trovati, su entrambi i lati

Sono il contenuto reale della giornata, non un margine.

**Miei, undici.** Le previsioni in `/tmp` effimero · la cecità rotta
nell'assemblaggio · una coda di `ITEMS.md` dentro un item · la chiave di
scoring multi-riga · una completezza dichiarata con l'uscita di una pipeline
(31% dei path mancati) · «coscienza non raggiungibile» con un P6 che copriva
la tesi debole · `sdq1.yaml` come divergenza aperta · il VSS a n-grammi come
mancanza · «l'esecutore è cieco» · la tabella degli strati che sommava 920 e
non 1000 — **la trappola dell'item 3 dei miei dieci item** · «replica» per
l'uguaglianza delle policy · il percorso «menu → Edit» dato per verificato.

**Suoi, quattro.** Il sigillo v1 senza oggetto, dichiarato e non nascosto ·
la priorità della contaminazione · «errore condiviso = substrato condiviso» ·
l'autorità su cosa conta come esposizione.

**Nessuno dei due ha coperto l'altro.** E quattro volte un mio controllo non
ha fatto niente e sarebbe passato: un `sed` che non sostituiva, una pipeline
che non segnalava, una manomissione di prova che non alterava, un `head -20`
che troncava.

---

## 6 — Le regole che ne sono nate

1. **Un sigillo si deposita insieme al chiaro cifrato e alla prova di
   round-trip, nello stesso atto.** Un hash senza oggetto recuperabile non è
   evidenza dell'esistenza dell'oggetto.
2. **Si genera dentro l'archivio durevole; non si genera e poi si sposta.**
   Lo spostamento è il punto di rottura.
3. **Un criterio di falsificazione deve coprire l'affermazione che
   accompagna**, non una sua versione più prudente.
4. **Un test negativo che non altera nulla passa sempre.** Va verificato che
   la manomissione atterri.
5. **Le voci dell'autobiografia non si aggiornano.** Per correggere si
   aggiunge.
6. **«Dichiarato» non è «implementato», e «accettato» non è «consegnato».**

---

## 7 — Cosa è stato toccato, e cosa no

**Zero modifiche fuori da questo repository.** Nessun deployment, nessuna
variabile scritta, nessuna policy, nessuna chiave creata, nessun controllo
disabilitato, nessun bypass di protezione, nessuna risorsa a pagamento, nessun
nodo arrestato. **#113 resta candidata. #116 non commentata** — accesso
mancante, non dimenticanza.

Unico effetto collaterale: un servizio Railway risvegliato da una richiesta
HTTP, che è ciò che fa qualunque client, e torna in sleep da sé.

---

*Ogni riga del §1 è **RECUPERATO** eseguendo, alle ore indicate nei quattro
ritorni di oggi. Il §2 è ciò che resta **UNKNOWN**. Il §4 è **INFERITO** sui
prerequisiti, **RECUPERATO** sulle cause.*
