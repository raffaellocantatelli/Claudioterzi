# Patch per `claudioterzi/Claudio`

Quattro patch per i difetti e i disallineamenti documentati in [`../RICOSTRUZIONE_R3.md`](../RICOSTRUZIONE_R3.md).

**Base:** `claudioterzi/Claudio` @ `155cb5f` (2026-07-24)
**Stato:** scritte, applicate e testate sul codice reale. Applicabilità su albero pulito verificata con `git apply --check`.

Stanno qui e non nel repository di destinazione perché questa sessione ha accesso in lettura a `claudioterzi/Claudio` ma non in scrittura: il git proxy non inietta credenziali per repository fuori dal set autorizzato della sessione.

## Come applicare

```bash
git clone https://github.com/claudioterzi/Claudio.git
cd Claudio
git checkout -b fix/cli-e-registro
git apply /percorso/patches/0001-fix-cli-argomenti-mancanti.patch
git apply /percorso/patches/0002-fix-registro-ipotesi-perdita-dati.patch
git apply /percorso/patches/0003-allinea-documentazione-e-config.patch
git apply /percorso/patches/0004-persistenza-vector-state-store.patch
```

**Vanno applicate in quest'ordine.** `test_r3.py` le verifica in sequenza su
un albero pulito estratto da `155cb5f`, non una per una su alberi separati:
applicarle a una a una nasconderebbe i conflitti fra patch.

Dopo tutte e quattro, verificato: `--health`, `--no-api`, `--scacchiera`,
`--sar-stato`, `python -m sdq1.voli` e `registro_ipotesi.py` escono tutti
con `RC=0`, e le sei ipotesi restano intatte.

## 0001 — Argomenti CLI mancanti

**File:** `sdq1/__main__.py` · **Aggiunge:** 4 righe

`main()` legge `args.chat_telegram` (riga 300) e `args.briefing_operativo` (riga 306) senza che esistano gli `add_argument` corrispondenti. La lettura avviene prima di ogni dispatch, quindi il crash colpisce **ogni** invocazione del modulo, non solo i due comandi interessati:

```
AttributeError: 'Namespace' object has no attribute 'chat_telegram'
```

Rompe a cascata `.github/workflows/agente_orario.yml:44`, che invoca `python3 -m sdq1 --chat-telegram` via cron `0 5-21 * * *`.

La patch dichiara i due flag. Il codice a valle era già corretto.

**Verificato dopo l'applicazione:**

| Comando | RC |
|---|---|
| `python3 -m sdq1 --health` | 0 |
| `python3 -m sdq1 --no-api "test"` | 0 |
| `python3 -m sdq1 --scacchiera --scacchiera-cicli 1 --scacchiera-livelli 2` | 0 |
| `python3 -m sdq1 --sar-stato` | 0 |
| `python3 -m sdq1 --chat-telegram` | 0 |

## 0002 — `registro_ipotesi.py` cancella ipotesi a ogni esecuzione

**File:** `registro_ipotesi.py` · **Corregge:** 4 difetti, non 2

Il comando documentato nel README distrugge il registro. **Quattro** cause che si sommano — le ultime due individuate da una revisione indipendente (Kimi, `SEME_v1.1`) e confermate eseguendo il codice:

1. `__main__` costruisce `Registro()` senza chiamare `carica()`, e chiude con `salva()` — che fa un `json.dump` di sovrascrittura totale. Le ipotesi non ridefinite nel blocco (H5, H6) spariscono.
2. Anche caricando, `apri()` fa `self.ipotesi[ip.id] = ip`: le definizioni hardcoded di H1–H4 sovrascrivono quelle su disco, azzerando le prove accumulate dopo la loro creazione.

Misurato sul codice non patchato:

```
PRIMA: H1 APERTA(2), H2 APERTA(4), H3 CONFERMATA(1), H4 CONFERMATA(6), H5 APERTA(1), H6 APERTA(1)
DOPO : H1 APERTA(2), H2 APERTA(4), H3 CONFERMATA(1), H4 APERTA(2)
```

H5 e H6 eliminate. H4 retrocessa da CONFERMATA ad APERTA, 4 delle sue 6 prove perse.

3. **`carica()` va in `TypeError`** sul JSON reale: `H4` contiene `note_convergenza`, campo assente dal dataclass. Chiamare `carica()` senza gestirlo fa morire lo script.
4. **`valuta()` mutava lo stato come effetto collaterale**: bastava stampare il registro per promuovere `H2` da APERTA a CONFERMATA, e `salva()` persisteva la promozione. Descrivere un'ipotesi non deve confermarla.

La patch chiama `carica()` prima di definire il seed, rende `apri()` non distruttiva sugli id già presenti, fa tollerare a `carica()` i campi extra preservandoli in `salva()`, e rende `valuta()` pura (la transizione richiede `applica=True`).

**Errore mio da non ripetere.** La prima versione di questa patch correggeva solo le cause 1 e 2, e il mio test la dichiarava idempotente. Il test era un falso positivo: confrontavo il JSON prima e dopo con l'output soppresso, e lo script moriva in `TypeError` *prima* di scrivere. File invariato per crash e file invariato per idempotenza sono indistinguibili se non si guarda l'exit code. Ora il test verifica `RC=0` **e** la stabilità del contenuto.

**Verificato dopo l'applicazione**, su albero pulito estratto da `155cb5f`:

```
run 1  RC=0
run 2  RC=0
ipotesi: 6 — H1 APERTA · H2 APERTA · H3 CONFERMATA · H4 CONFERMATA · H5 APERTA · H6 APERTA
note_convergenza su H4: preservata
hash del JSON stabile fra run 1 e run 2
```

Il primo run riordina le chiavi del JSON: confrontato campo per campo contro
l'originale, **nessuna differenza semantica** — stesse chiavi, stessi valori,
solo ordine di serializzazione. Dal secondo run in poi il file è byte-stabile.

## Nota

Il fix 0002 non recupera i dati già persi in esecuzioni passate. H5, H6 e le prove di H4 sono recuperabili dalla git history di `registro_ipotesi.json`, e vanno ripristinate prima di eseguire di nuovo lo script.


## 0003 — Allineare documentazione e configurazione alla realtà

**File:** `README.md` · `sdq1/config/sdq1.yaml` · `sdq1/agents/eternal_backup_agent.py` · `sdq1/sar/sar.py` · `PROGETTO_RAFFAELLO.md`

Nessun cambiamento di comportamento: solo smettere di dichiarare cose che il
codice smentisce. Una documentazione che descrive un sistema diverso da quello
in esecuzione è un generatore di errori futuri — il «Sommario Esecutivo» ne è
la prova.

| Dove | Prima | Dopo |
|---|---|---|
| `README.md` | cascata `Anthropic → Gemini → DeepSeek → Ollama → Stub` | l'ordine reale di `sdq1.yaml`: `gemini → anthropic → grok → openai → deepseek → stub` |
| `README.md` | «Ipotesi attive» con tre voci | sei, con H4 CONFERMATA e H5/H6 aperte |
| `sdq1.yaml` | `modello_embedding: all-MiniLM-L6-v2`, `dimensione_vettori: 384`, blocco `qdrant` come config attiva | commentati, con la spiegazione che il VSS usa n-grammi e che nessun modulo legge quelle chiavi |
| `eternal_backup_agent.py` | intestazione «Blockchain + IPFS + Orbital Redundancy» | docstring che dichiara **SIMULAZIONE**, elenca cosa non fa, e rimanda a `r3/node.py` per la parte reale |
| `sar.py` | «Sistema a 10 livelli» | «9 livelli implementati su 10 dichiarati», con il livello 5 assente e il livello 10 che contiene `test_identita()`, non il loop |
| `PROGETTO_RAFFAELLO.md` | `[ ] raffaello.py implementato` | `[x]` — verificato: 486 righe, classi `RaffaelloIdentity`, `AnalisiGiornaliera`, `Raffaello`, importabile e istanziabile |

L'ultima riga va nella direzione opposta alle altre: il progetto **si
sottostimava**. La deriva documentale non è sistematicamente auto-elogiativa.

**Verificato:** `sdq1.yaml` resta YAML valido; i due file Python restano
sintatticamente corretti; il sistema gira invariato.

## 0004 — Persistenza del Vector State Store

**File:** `sdq1/memory/vss.py` · **Aggiunge:** `salva()`, `carica()`, e due parametri opzionali al costruttore

Il VSS era un `dict` in-process: moriva col processo. Riduceva il contesto
*dentro* un run, non forniva continuità *tra* sessioni — che è ciò per cui
esiste. Questo era il vero collo di bottiglia architetturale.

**Scelta di progetto: si salva solo il testo, mai i vettori.** L'indice si
ricalcola dalla definizione dell'algoritmo. Un vettore salvato resterebbe
legato all'implementazione che l'ha prodotto; il testo no. È la stessa
conclusione di [`../SOLUZIONE_2055.md`](../SOLUZIONE_2055.md): gli embedding
sono cache, mai archivio.

Scrittura atomica via file temporaneo e `replace()`: non esiste uno stato in
cui il file è mezzo scritto.

**Verificato con sei prove:**

| Prova | Esito |
|---|---|
| Sopravvive alla morte del processo — scrivi, distruggi l'oggetto, ricarica in uno nuovo | 3 voci su 3, lettura per pointer e ricerca semantica intatte |
| Idempotenza — `carica()` due volte | 0 voci duplicate |
| Determinismo — due `salva()` consecutivi | hash identico |
| Nessun vettore su disco | campi salvati: `agente_id`, `chiave`, `ptr`, `run_id`, `testo` |
| File assente o corrotto | 0 voci, nessuna eccezione |
| Retrocompatibilità — costruttore a un solo argomento | funziona come prima |

Percorso di default `output/vss_state.json`, sovrascrivibile con
`SDQ1_VSS_PATH`. La persistenza è **opt-in**: senza `autocarica=True` il
comportamento resta identico a prima, quindi la patch non cambia nulla per
chi non la usa.
