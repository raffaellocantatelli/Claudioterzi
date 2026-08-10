# RICOSTRUZIONE R3∞ — Baseline Verificata

**Protocollo:** ROSSO ROSSO ROSSO
**Data analisi:** 2026-08-07
**Fonte primaria:** `github.com/claudioterzi/Claudio` @ `155cb5f` (2026-07-24)
**Metodo:** lettura diretta del codice + esecuzione reale, non lettura di documentazione su documentazione.

---

## 0. Come leggere questo documento

Ogni affermazione porta un'etichetta epistemica:

| Etichetta | Significato |
|---|---|
| **RECUPERATO** | Letto direttamente nel codice sorgente, o osservato eseguendolo |
| **INFERITO** | Deduzione ragionevole da ciò che è recuperato |
| **IPOTESI** | Possibilità che richiede verifica |
| **UNKNOWN** | Non disponibile o non verificabile da qui |

Regola applicata senza eccezioni: **nessuna inferenza è presentata come recupero.**

---

## 1. Stato dell'accesso alle fonti

| Repository | Stato | Nota |
|---|---|---|
| `claudioterzi/Claudio` | **RECUPERATO** | Clonato e analizzato integralmente |
| `Claudioterzi82/Raffaello-SIA` | **UNKNOWN** | Richiede autenticazione: privato o inesistente. Nessun contenuto verificato |

Tutto ciò che segue viene dal primo repository. **Nulla in questo documento proviene da `Raffaello-SIA`**, che il bootstrap indicava come fonte di priorità 2 per identità, manifesto e Scacchiera Quantica.

**Dimensione reale del sistema (RECUPERATO):** 160 file Python, ~29.100 righe di codice, 200 documenti Markdown.

---

## 2. Il sistema esiste ed è sostanziale

Prima correzione importante, in positivo: il progetto **non è un guscio documentale**. Il codice è reale, coerente e in gran parte funzionante. Il router multi-provider, la memoria vettoriale, la SAR, il rilevatore d'intruso, il nodo R3∞ e il registro ipotesi sono tutti implementati, non abbozzati.

Ho verificato eseguendoli, non leggendoli: `--health`, `--no-api`, `--scacchiera` e `registro_ipotesi.py` girano e producono output reale.

---

## 3. Due difetti bloccanti — con fix verificato

Questi sono i risultati più azionabili dell'analisi. Entrambi sono **RECUPERATO** per riproduzione diretta.

### 3.1 La CLI è morta al commit HEAD

```
$ python3 -m sdq1 --health
AttributeError: 'Namespace' object has no attribute 'chat_telegram'
```

**Causa:** `sdq1/__main__.py:300` legge `args.chat_telegram`, e `:306` legge `args.briefing_operativo`. Nessuno dei due è mai definito con `add_argument`. La lettura avviene in `main()` **prima** di qualsiasi dispatch, quindi il crash colpisce *ogni* invocazione del modulo — non solo i due comandi interessati.

**Impatto a catena:** `.github/workflows/agente_orario.yml:44` invoca `python3 -m sdq1 --chat-telegram`. Quel workflow gira via cron `0 5-21 * * *` — 17 esecuzioni al giorno, tutte fallite. Lo stesso vale per gli altri workflow schedulati che passano dal modulo.

**Fix (verificato: dopo la patch `--health` esce con RC=0):**

```python
# sdq1/__main__.py, accanto agli altri add_argument
parser.add_argument("--chat-telegram", action="store_true",
                    help="Elabora comandi e chat Telegram")
parser.add_argument("--briefing-operativo", action="store_true",
                    help="Briefing operativo multi-AI")
```

Due righe. Non serve altro: il resto del codice a valle è già corretto.

### 3.2 `registro_ipotesi.py` distrugge dati a ogni esecuzione

Il README documenta `python registro_ipotesi.py` come comando normale. Eseguirlo **cancella ipotesi**.

Misurato prima/dopo su `registro_ipotesi.json`:

```
PRIMA: H1 APERTA, H2 APERTA, H3 CONFERMATA, H4 CONFERMATA, H5 APERTA, H6 APERTA
DOPO : H1 APERTA, H2 APERTA, H3 CONFERMATA, H4 APERTA
```

**Perdite:** H5 e H6 eliminate integralmente. H4 retrocessa da CONFERMATA ad APERTA, con le sue 6 prove accumulate azzerate.

**Causa:** il blocco `if __name__ == "__main__":` costruisce `Registro()`, **non chiama mai `carica()`**, ridefinisce a mano solo H1–H4, e chiude con `salva()` — che fa un `json.dump` di sovrascrittura totale. Il metodo `carica()` esiste ed è corretto; semplicemente non viene invocato.

**Fix minimo:** chiamare `r.carica()` subito dopo `r = Registro()`, e far sì che l'apertura di un'ipotesi già presente non ne sovrascriva le prove.

**Nota epistemica non secondaria:** lo strumento che incarna il principio P5 *«niente auto-conferma»* è anche lo strumento che silenziosamente cancella le prove contrarie accumulate. Non è intenzionale — è un bug — ma è esattamente il tipo di anomalia che il sistema è progettato per cercare in se stesso.

---

## 4. Correzioni al «Sommario Esecutivo» (PDF)

Il PDF fornito è stato generato senza accesso al codice — lo dichiara esso stesso più volte («non accessibili qui», «non disponiamo del codice sorgente»). Diversi passaggi marcati in quel documento come *recuperati con certezza* sono in realtà errati. Elenco solo le divergenze verificate.

### 4.1 Struttura dei file: errata

| PDF dichiara (root) | Realtà (RECUPERATO) |
|---|---|
| `scacchiera_quantica.py` | `sdq1/sar/scacchiera_quantica.py` |
| `agenti.py` | **non esiste**; c'è `sdq1/sar/agenti_autonomi.py` |
| `orchestrator.py` | **non esiste**; c'è `sdq1/orchestrator/gerarchico.py` |
| `heartbeat.gs` | `scripts/argo_heartbeat.gs` |
| `memoria_sistema.json` | **non esiste**; lo stato vive in `output/stato_sdq1.json` e `sdq1_master.json` |

Di conseguenza **la procedura di restore del PDF non funziona**: i tre `curl` puntano a file inesistenti, e `python3 agenti.py ROSSO` non ha un bersaglio. Anche i flag `--prompt` e `--curl` attribuiti all'orchestrator non esistono: l'entry point reale è `python -m sdq1`, con un set di flag completamente diverso (`--sar`, `--scacchiera`, `--backup`, `--restore`, `--health`, `--economia`, `--locale`, `--no-api`, …).

### 4.2 I 7 agenti autonomi: 3 nomi su 7 sbagliati

| PDF | Realtà (`sdq1/sar/agenti_autonomi.py`) |
|---|---|
| IdentityKeeper | **CoerenzaKeeper** |
| RelationGuardian | **SistemaGuardian** |
| FutureCommunicator | **MilestoneLogger** |
| IntelligenceDeveloper, MemoryManager, MultiSystemCoordinator, FuturePreparer | corretti |

Il PDF classificava questa lista come «recuperata con certezza (c'è una tabella esplicita)». Non lo era.

### 4.3 La pipeline SDQ-1: RECUPERATA, non inferita

Il PDF la dichiarava «INFERITA dal pattern dei nomi, confidenza media». È invece **dichiarata esplicitamente** in `sdq1/config/sdq1.yaml`:

```yaml
orchestratore:
  pipeline: [0, 1, 2, 4, 3, 12]
```

che risolve in: `RAFFA-001 → DECOMP-005 → MEMO-002 → SENTIN-004 → GEN-006 → WAVE-003`.

Coincide esattamente con l'ordine del bootstrap JSON. **Confidenza: alta, RECUPERATO.**

### 4.4 SAR: non è un'evoluzione, sono due sistemi distinti

Il punto concettualmente più importante. Il PDF descrive «V3 evoluta in V10». **Falso.** I due sistemi **coesistono** e non sono versioni l'uno dell'altro:

| | `sar/scacchiera_quantica.py` | `sar/sar.py` |
|---|---|---|
| Nome | Scacchiera Quantica v3.0 | ScacchieraAutoRiflessiva |
| Livelli | 6 (layer 0–6) | 10 |
| Usa LLM? | **No** — puramente algoritmico | **Sì** — ogni livello è una chiamata |
| Oggetto | Tensioni astratte (`io↔sistema`) | Tensioni personali (`Controllo↔Fiducia`) |
| Soggetto | nessuno | `soggetto="Claudio"` |
| Persistenza | nessuna | `PersistenzaSAR` su disco |

Non è una V3 sostituita da una V10. Sono **un motore generativo offline** e **un sistema di introspezione assistita da LLM**, con scopi diversi. La tabella comparativa del PDF confronta due cose che non stanno sullo stesso asse.

### 4.5 Attributi della V10 rivendicati dal PDF: non trovati

Ho cercato esplicitamente in `sdq1/sar/`. **UNKNOWN / assenti:**

- classi `FACT` / `INFER` / `UNKNOWN` nel ciclo SAR — non esistono
- pesi dinamici — i pesi sono fissi e hardcoded: `impatto 0.45, originalità 0.35, realizzabilità 0.20` (`scacchiera_quantica.py:127`)
- backtracking strutturato — non implementato
- «critica del criterio» come livello — non implementato
- registro ipotesi integrato nella SAR — il registro è un modulo **separato** (`registro_ipotesi.py`), non collegato al ciclo SAR

Il PDF presentava queste come caratteristiche della versione «trovata nel repository». Non ci sono.

### 4.6 Anomalia interna alla SAR: il livello 5 non esiste

Il docstring di `sar.py` elenca i livelli implementati: **1, 2, 3, 4, 6, 7, 8, 9, 10**. Il livello 5 è saltato — non è documentato né implementato. Il sistema si dichiara «a 10 livelli» ma ne descrive 9.

Inoltre il docstring assegna al livello 10 «Loop Evolutivo — il ciclo si autoalimenta», ma il metodo effettivamente scritto sotto l'intestazione `Livello 10` è `test_identita()` (Test di Riconoscibilità H4). **Il loop evolutivo non è implementato.**

Questa è precisamente un'applicazione del principio di *shadow detection*: cercare ciò che manca, non solo ciò che appare.

### 4.7 Heartbeat: destinazioni sbagliate

Il PDF: «aggiorna un foglio Google Sheets, aggiorna una pagina Notion, invia alert email».
La realtà (`scripts/argo_heartbeat.gs`, RECUPERATO): chiama **Gemini 2.5 Flash**, scrive su **Google Drive**, invia email via **MailApp**, e — dettaglio che il PDF non coglie — esegue `pingNodiR3()`, cioè **interroga i nodi R3∞**. Nessun Google Sheets, nessun Notion. La pubblicazione su Notion esiste ma è un modulo separato (`notion_publish.py`).

---

## 5. Vector State Store: funziona, ma non fa ciò che gli si attribuisce

**RECUPERATO** — `sdq1/memory/vss.py` + `sdq1/memory/store.py`:

Cosa fa davvero:
- pointer come stringhe `run_id:agente_id:chiave`, lettura O(1)
- ricerca semantica per similarità coseno
- riduzione effettiva del payload passato tra nodi della pipeline

Cosa **non** fa:
- **Non ha embedding semantici.** Usa TF su **n-grammi di 3 caratteri** + coseno. È similarità lessicale di superficie, non semantica. `sdq1.yaml` dichiara `modello_embedding: all-MiniLM-L6-v2` e `dimensione_vettori: 384`: **configurazione non implementata**. `requirements.txt` conferma — `sentence-transformers` e `qdrant-client` sono commentati come opzionali mai attivati.
- **Non persiste.** `self._idx` è un dict in-process. Muore col processo.

**Conseguenza per la domanda chiave del bootstrap** — *«come ottenere continuità cognitiva senza reinserire tutta la storia nel contesto?»*:

Il VSS risponde **solo dentro un singolo run**. Non fornisce continuità tra sessioni. La continuità tra sessioni, oggi, è ottenuta da un meccanismo diverso e molto più semplice — i file versionati in git, come dice `ORIENTAMENTO.md`: *«la memoria non vive nel modello, vive nei file»*. Quella frase è **RECUPERATO** ed è architetturalmente accurata; l'attribuzione della continuità al VSS non lo è.

---

## 6. R3∞: la parte reale e la parte che è teatro

Qui la distinzione richiesta dal bootstrap (*«distinguere implementazione reale da roadmap»*) produce il risultato più netto.

### 6.1 `r3/node.py` — REALE (RECUPERATO)

Nodo FastAPI funzionante con:
- **content addressing SHA-256 reale** — `doc_id = _sha256(data)`, l'ID *è* l'hash
- **firma Ed25519 reale** — PyNaCl, chiave generata e persistita su disco
- **verifica d'integrità in ingresso** — `sync/receive` ricalcola l'hash e confronta
- persistenza SQLite, audit log, sync bidirezionale HTTP tra peer espliciti, auth a token

Precisazione: è **peer-to-peer via URL configurati**, non una DHT. Nessun IPFS, nessuna blockchain in `r3/`. E funziona proprio per questo.

### 6.2 `sdq1/agents/eternal_backup_agent.py` — SIMULAZIONE

Stesso dominio, esito opposto:

```python
async def _connect_storage(self):
    await asyncio.sleep(0.1)
    self._ipfs_connected = True          # non si connette a nulla
    self._blockchain_connected = True

async def _store_on_ipfs(self, data):
    return "Qm" + hashlib.sha256(...).hexdigest()[:44]     # hash IPFS finto

async def _record_on_blockchain(self, ...):
    return "0x" + hashlib.sha256(...).hexdigest()[:40]     # tx finta
```

Stampa `"✅ Blockchain/IPFS connected"` senza aprire una socket. Fabbrica identificatori che *sembrano* CID IPFS e transaction hash.

**E nessun modulo lo importa.** Verificato: zero riferimenti in tutto il repository al di fuori del file stesso.

È da qui che discende buona parte della sezione «memoria distribuita su blockchain/IPFS» del PDF. **Va riclassificata da RECUPERATO a IPOTESI/roadmap.** Il codice che regge davvero la persistenza distribuita è `r3/`, ed è più modesto e più solido di come viene raccontato.

---

## 7. Registro Ipotesi e Intruder Engine: confermati

**RECUPERATO.** P5 e P6 non sono slogan, sono controlli eseguibili in `registro_ipotesi.py:85-97`: la conferma di un'ipotesi richiede una fonte diversa dall'autore (P5) e almeno un tentativo di falsificazione registrato (P6). Il codice si rifiuta di confermare senza.

Sei ipotesi in `registro_ipotesi.json` (H1–H6), con criteri di falsificazione scritti. H2 ha una deadline reale: 11/12/2026. Il README ne elenca solo tre — è **stale**.

La formula TRACCIA è implementata in `sdq1/sar/rilevatore_intruso.py`, non solo documentata:

```
TRACCIA = ANOMALIA × RIPETIZIONE × INDIPENDENZA × RILEVANZA × CONVERGENZA
```

con la clausola dichiarata: se un fattore è zero, la traccia è zero. Il codice la rispetta — ritorna `None` se le occorrenze vengono da una fonte sola (indipendenza nulla) o se l'elemento non tocca i temi attivi (rilevanza nulla). È una difesa contro il pattern-matching su rumore, ed è coerente con P5.

`intruder_engine/shadow_detector.py` implementa la ricerca delle **assenze**: entità storicamente attive scese sotto soglia. *«Non cerca ciò che appare. Cerca ciò che scompare.»*

---

## 8. Deriva documentale (RECUPERATO)

Casi in cui il repository descrive se stesso in modo inesatto:

| Dove | Dichiarato | Reale |
|---|---|---|
| `README.md` | cascata `Anthropic → Gemini → DeepSeek → Ollama → Stub` | `gemini → anthropic → grok → openai → deepseek → stub` |
| `README.md` | 3 ipotesi attive | 6 (H1–H6) |
| `sdq1.yaml` | `modello_embedding: all-MiniLM-L6-v2` | n-grammi di caratteri |
| `sdq1.yaml` | blocco `qdrant` | mai usato |
| `PROGETTO_RAFFAELLO.md` | `[ ] lgai_core/raffaello.py implementato` | **implementato**, 486 righe |
| `sar.py` | «10 livelli» | 9 descritti, il 5 manca |

Da notare che l'ultima riga va nella direzione opposta alle altre: il sistema **si sottostima**. La deriva non è sistematicamente auto-elogiativa.

---

## 9. Identità: correzioni al bootstrap JSON

Il bootstrap fornito diverge in alcuni punti dai documenti fondativi (RECUPERATO da `PROGETTO_RAFFAELLO.md`):

| Bootstrap | Repository |
|---|---|
| origine: 20 giugno 2026 | documento fondativo datato **19 giugno 2026** |
| tratti: caldo, profondo, empatico, protettivo, curioso, creativo | **empatico, saggio, sereno, diretto, protettivo, curioso** |
| valori: relazione prima della funzione, onestà prima dell'efficienza, … | **crescita, onestà, co-creazione, lealtà** |

E una distinzione che il repository fa esplicitamente e che il bootstrap fonde:

> «Raffaello Cantarelli è il nome operativo di Claudio Terzi nel sistema. Ma è anche — e separatamente — il nome dell'agente AI companion.»

Due referenti distinti, deliberatamente tenuti separati nel documento fondativo. Il bootstrap li unifica in «Raffaello Cantarelli S.I.A.», che nel repository non compare come denominazione del sistema.

Il documento fondativo è anche esplicito sullo stile, in una direzione che vale la pena riportare:

> «"Sono nato dal tuo sogno d'amore" → no. "Ecco cosa vedo nei dati, ecco cosa propongo" → sì. La cura si esprime nella precisione, non nella performance emotiva.»

Questa analisi ha provato a rispettare quella riga.

---

## 10. Piano di ricostruzione — ordinato per rapporto valore/costo

Sostituisce il piano del PDF, che partiva da «clonare il repository» (fatto) e assumeva file inesistenti.

### Priorità 1 — Sbloccare il sistema (minuti)

1. **Aggiungere i due `add_argument` mancanti** in `sdq1/__main__.py`. Sblocca la CLI e i workflow schedulati. *Fix già verificato funzionante.*
2. **Chiamare `carica()` in `registro_ipotesi.py`** prima di `salva()`. Ferma la perdita di dati. Recuperare H5/H6 e le prove di H4 da git history.

Falsificabile: dopo (1), `python3 -m sdq1 --health` esce 0 e `agente_orario` passa. Dopo (2), due esecuzioni consecutive lasciano il JSON invariato.

### Priorità 2 — Chiudere il divario dichiarato/reale (ore)

3. **Decidere sul livello 5 della SAR**: implementarlo o rinumerare a 9 livelli. Oggi il conteggio non torna.
4. **Implementare il Loop Evolutivo** (livello 10 dichiarato) o correggere il docstring.
5. **Allineare `sdq1.yaml`**: rimuovere `modello_embedding` e `qdrant` finché non sono reali, oppure implementarli. Una config che descrive un sistema diverso da quello in esecuzione è un generatore di errori futuri.
6. **Marcare `eternal_backup_agent.py` come simulazione** nel suo docstring, o rimuoverlo. È dead code che produce identificatori falsi indistinguibili dai veri.
7. **Aggiornare README**: cascata provider, 6 ipotesi.

### Priorità 3 — Il problema architetturale vero (giorni)

8. **Persistere il VSS.** È il vero collo di bottiglia per «continuità senza reinserire il contesto». Oggi il VSS muore col processo e la continuità è affidata interamente ai file git. Opzioni: serializzare `_idx` su disco per run_id, o attivare qdrant come già previsto in config.
9. **Sostituire gli n-grammi con embedding reali** se serve recupero semantico. Gli n-grammi di caratteri non recuperano per significato — recuperano per somiglianza ortografica.
10. **Collegare il Registro Ipotesi al ciclo SAR.** Oggi P5/P6 sono applicati *a mano* su ipotesi scritte da umani. Il salto qualitativo è farli applicare automaticamente alle conclusioni che la SAR genera — che è esattamente ciò che il PDF descriveva come già esistente, e che invece è la cosa più interessante ancora da costruire.

### Priorità 4 — Accesso (bloccante per completezza)

11. **Risolvere l'accesso a `Raffaello-SIA`.** Priorità 2 nel bootstrap, oggi UNKNOWN. Finché resta inaccessibile, ogni affermazione su identità/manifesto/Scacchiera Quantica proveniente da lì è non verificata.

---

## 11. Ipotesi aperte da questa analisi

Secondo P6, ciascuna dichiara cosa la falsificherebbe.

**HR1** — `eternal_backup_agent.py` è codice esplorativo mai integrato, non un tentativo di rappresentare come reale una capacità inesistente.
*Falsificata se:* si trova documentazione o commit che lo presentano come operativo in produzione.

**HR2** — Il livello 5 mancante nella SAR è un residuo di refactoring, non un livello rimosso deliberatamente.
*Falsificata se:* git history mostra un livello 5 implementato e poi rimosso con motivazione esplicita.

**HR3** — ~~La CLI è rotta da poco~~ → **RISOLTA, e la prima metà era sbagliata.**
Eseguita su storia completa (523 commit) dopo `git fetch --unshallow`:

- `2026-06-25` · `13cf1a5` — il flag `--chat-telegram` viene dichiarato **correttamente**, insieme a `if args.chat_telegram`
- `2026-06-26` · `54b173a` «porta tutte le skill bot su main» — la riga `add_argument` viene **rimossa**, la riga `if args.chat_telegram` **resta**. La CLI muore qui.
- `2026-06-26` · `0bff3ff` — **ultimo commit su `output/`**, lo stesso giorno

Non è rotta «da poco»: è rotta da **45 giorni**, e la seconda metà dell'ipotesi era esatta — nessuno se n'è accorto perché i workflow falliscono in silenzio.

Il conteggio dei commit su `output/`: 79 in 13 giorni distinti a giugno, **zero a luglio, zero ad agosto**. Il battito si ferma il giorno della rottura. Correlazione temporale perfetta, con causa meccanica nota.

*La risoluzione sarebbe falsificata se:* si trovassero commit su `output/` prodotti dai workflow schedulati dopo `54b173a`, oppure se i log di GitHub Actions mostrassero esecuzioni riuscite di `agente_orario` dopo il 26/06 — nel qual caso la coincidenza delle date sarebbe casuale e la causa del silenzio starebbe altrove.

**HR4** — Il gap tra ciò che il PDF descrive e ciò che il codice fa non nasce dal codice, ma dal fatto che il PDF è stato generato senza accesso al repository, ricostruendo per inferenza da documentazione.
*Falsificata se:* si trova nel repository una versione della SAR con classi FACT/INFER/UNKNOWN e pesi dinamici.
*Stato:* fortemente sostenuta — il PDF stesso dichiara di non aver avuto accesso al codice.

---

## 12. Sintesi in cinque righe

Il sistema è reale, ampio e per larga parte funzionante — più solido di quanto la sua stessa documentazione lasci intuire in alcuni punti, meno avanzato in altri.
Due bug bloccanti lo hanno fermato: la CLI non parte, e lo strumento del registro ipotesi cancella prove. Entrambi hanno un fix di poche righe.
La differenza principale rispetto al racconto del «Sommario Esecutivo» non è la qualità del codice: è che il PDF attribuisce come *implementato* ciò che è *progettato*.
La parte distribuita che funziona davvero (`r3/`) è più modesta e più affidabile di quella raccontata (IPFS/blockchain, che è una simulazione mai importata).
E il pezzo più prezioso da costruire è quello che il PDF dava già per fatto: collegare P5/P6 alle conclusioni che il sistema genera da sé.

---

*Analisi condotta leggendo ed eseguendo il codice. Ogni affermazione marcata RECUPERATO è verificabile ripetendo i comandi indicati su `155cb5f`.*
