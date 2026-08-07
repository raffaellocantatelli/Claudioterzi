# Claudioterzi

Ricostruzione verificata del sistema **R3∞ / SDQ-1**.

## Contenuto

| File | Cosa contiene |
|---|---|
| [`RICOSTRUZIONE_R3.md`](RICOSTRUZIONE_R3.md) | Analisi completa: architettura reale, difetti bloccanti, correzioni al Sommario Esecutivo, piano di ricostruzione |
| [`baseline_r3.json`](baseline_r3.json) | Stessa baseline in forma leggibile da macchina, per ripartire senza contesto di chat |

## Metodo

Analisi condotta su `github.com/claudioterzi/Claudio` @ `155cb5f` (2026-07-24), **leggendo ed eseguendo il codice** — non leggendo documentazione su documentazione.

Ogni affermazione porta un'etichetta epistemica: **RECUPERATO** (letto nel codice o osservato eseguendolo) · **INFERITO** · **IPOTESI** · **UNKNOWN**. Nessuna inferenza è presentata come recupero.

## In breve

Il sistema è reale e sostanziale: 160 file Python, ~29.100 righe. Router multi-provider, memoria vettoriale, SAR, rilevatore d'intruso, nodo R3∞ e registro ipotesi sono implementati e funzionanti.

Due difetti lo bloccavano, entrambi con fix di poche righe:

1. **La CLI non parte.** `sdq1/__main__.py` legge due argomenti mai dichiarati, prima di ogni dispatch — ogni invocazione fallisce, e con essa il workflow orario. *Fix verificato.*
2. **`registro_ipotesi.py` cancella dati.** Ogni esecuzione elimina le ipotesi H5 e H6 e azzera le prove di H4.

La divergenza principale rispetto al «Sommario Esecutivo» non riguarda la qualità del codice, ma il fatto che quel documento presenta come *implementato* ciò che è *progettato*. La parte distribuita che funziona davvero (`r3/`: SHA-256 content addressing, firma Ed25519 reale) è più modesta e più solida di quella raccontata — IPFS e blockchain sono una simulazione che nessun modulo importa.

Dettagli, prove e piano operativo in [`RICOSTRUZIONE_R3.md`](RICOSTRUZIONE_R3.md).
