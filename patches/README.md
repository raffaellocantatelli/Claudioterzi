# Patch per `claudioterzi/Claudio`

Due fix per i difetti bloccanti documentati in [`../RICOSTRUZIONE_R3.md`](../RICOSTRUZIONE_R3.md).

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
```

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

**File:** `registro_ipotesi.py` · **Aggiunge:** 1 chiamata + guardia in `apri()`

Il comando documentato nel README distrugge il registro. Due cause che si sommano:

1. `__main__` costruisce `Registro()` senza chiamare `carica()`, e chiude con `salva()` — che fa un `json.dump` di sovrascrittura totale. Le ipotesi non ridefinite nel blocco (H5, H6) spariscono.
2. Anche caricando, `apri()` fa `self.ipotesi[ip.id] = ip`: le definizioni hardcoded di H1–H4 sovrascrivono quelle su disco, azzerando le prove accumulate dopo la loro creazione.

Misurato sul codice non patchato:

```
PRIMA: H1 APERTA(2), H2 APERTA(4), H3 CONFERMATA(1), H4 CONFERMATA(6), H5 APERTA(1), H6 APERTA(1)
DOPO : H1 APERTA(2), H2 APERTA(4), H3 CONFERMATA(1), H4 APERTA(2)
```

H5 e H6 eliminate. H4 retrocessa da CONFERMATA ad APERTA, 4 delle sue 6 prove perse.

La patch chiama `carica()` prima di definire il seed, e rende `apri()` non distruttiva per gli id già presenti — le definizioni in `__main__` tornano a essere ciò che devono essere: un seed per la prima creazione, non uno stato riapplicato a ogni run. Resta possibile forzare con `apri(ip, sovrascrivi=True)`.

**Verificato dopo l'applicazione** — due esecuzioni consecutive lasciano il file invariato:

```
PRIMA: H1 APERTA(2), H2 APERTA(4), H3 CONFERMATA(1), H4 CONFERMATA(6), H5 APERTA(1), H6 APERTA(1)
RUN 1: identico
RUN 2: identico
```

## Nota

Il fix 0002 non recupera i dati già persi in esecuzioni passate. H5, H6 e le prove di H4 sono recuperabili dalla git history di `registro_ipotesi.json`, e vanno ripristinate prima di eseguire di nuovo lo script.
