# CLAUDE.md

## Protocollo Rosso Rosso Rosso — attivo per default

In questo repository il protocollo **non va attivato**: è lo stato predefinito.
Definizione canonica in [`PROTOCOLLO_ROSSO.md`](PROTOCOLLO_ROSSO.md). Leggerlo prima di lavorare.

In sintesi operativa:

**Etichetta ogni affermazione** — RECUPERATO (letto o eseguito alla fonte) · INFERITO · IPOTESI · UNKNOWN.
Mai presentare un'inferenza o un'ipotesi come recupero. La fonte di un recupero è il dato, **mai un documento che ne parla**.

**Verifica prima di concludere.** Leggi il codice, eseguilo, misura. In questo progetto la documentazione e il codice divergono in più punti noti: quando sono in disaccordo, vince il codice.

**P5 — niente auto-conferma:** confermare richiede una fonte diversa da chi ha formulato l'ipotesi.
**P6 — ogni ipotesi dichiara come potrebbe essere falsificata.** Se non lo dichiara, non può essere confermata.

**Cerca anche ciò che manca**, non solo ciò che appare. Un'anomalia prova che qualcosa non torna, non che qualcosa è nascosto.

**Chiudi proponendo il prossimo esperimento verificabile**, non il prossimo ragionamento.

Attenzione totale significa verificare di più, non scrivere di più.

---

## Cosa contiene questo repository

Ricostruzione verificata del sistema R3∞ / SDQ-1, il cui codice vive in `claudioterzi/Claudio`.

| File | Contenuto |
|---|---|
| `RICOSTRUZIONE_R3.md` | Analisi del codice reale: architettura, difetti bloccanti, correzioni al Sommario Esecutivo |
| `baseline_r3.json` | La stessa baseline in forma leggibile da macchina, per ripartire senza contesto |
| `ESPERIMENTO_FIRMA.md` | Protocollo del test di firma comportamentale: H0 vs H1, col controllo placebo e la regola di arresto |
| `esperimento/` | I dieci item, il protocollo a quattro bracci, l'hash delle previsioni sigillate |
| `APERTURE.md` | Severità applicata al futuro: ogni blocco e cosa apre, col prezzo. E ciò che non si apre |
| `SOLUZIONE_2055.md` | Il sistema passato al filtro dei trent'anni |
| `SEME.md` | Da incollare in qualsiasi chat di qualsiasi modello: ricostituisce il contesto |
| `PROTOCOLLO_ROSSO.md` | Definizione canonica del protocollo, trasportabile fuori di qui |
| `DIMOSTRAZIONE.md` | Sequenza per dimostrare il progetto di persona |
| `patches/` | Quattro fix testati: i due difetti bloccanti, l'allineamento documentale, la persistenza del VSS |
| `test_r3.py` | 37 controlli: invarianti del protocollo, difetti, reperti, applicabilità delle patch in sequenza |

---

## Prima di concludere un lavoro

```bash
python3 test_r3.py            # rapporto leggibile
python3 test_r3.py --json     # stesso rapporto in JSON, deterministico
```

Esce diverso da zero se la disciplina è decaduta: documenti canonici mancanti, etichette epistemiche assenti, o un'ipotesi senza criterio di falsificazione. Non è cerimoniale — ha già intercettato una violazione in questo stesso repository.

---

## ⚠ Stato al 2026-10-04 — leggere prima di tutto il resto

**Il test fallisce di proposito, su un controllo solo: `[FAIL] la baseline descrive lo stato attuale`.
Non è un guasto. È vero.**

La ricostruzione in questo repository fotografa `claudioterzi/Claudio` al commit `155cb5f`
(2026-07-24). Al 2026-10-04 `origin/main` è `d6d329a`, **677 commit più avanti**: 1200 commit
totali, 311 file Python contro 160. Tutti i verdi di DIFETTI e REPERTI descrivono quel passato.

Cosa è cambiato, RECUPERATO il 2026-10-04:

- **Il battito è ripartito.** 91 commit su `output/` a settembre, 6 a ottobre. I commit
  `chore(daily):` — che in 523 commit non erano **mai** esistiti — ora sono 29, dal 05/09.
- **BUG-1 risolto** il 2026-09-04, commit `201dac3` «Apply FIX_BLOCCANTI package onto live paths».
- **BUG-2 risolto**: `r.carica()` è presente, le sei ipotesi H1–H6 sono intatte.
- **VSS persiste**: `salva()` è in `sdq1/memory/vss.py`.
- Parzialmente: `eternal_backup_agent.py` dichiara SIMULAZIONE, ma `sdq1.yaml` dichiara ancora
  `modello_embedding` e `sar.py` dice ancora «a 10 livelli».
- **Criterio (a) di H2, il battito: soddisfatto.** Al 22/08 era a rischio. Scadenza 11/12/2026.

**UNKNOWN:** 677 commit mai verificati. Letta, RedFrag, System One, R3 canary receipts —
nulla di tutto ciò è RECUPERATO. Non citarlo come verificato.

Per far tornare verde il test serve **rifare la baseline sul nuovo HEAD**, non cambiare il test.

---

## Fatti verificati da non riscoprire — AL COMMIT `155cb5f`, non oggi

Costano tempo a ritrovare, e sono già RECUPERATO:

- Il codice del sistema è in `claudioterzi/Claudio`. Leggibile via clone pubblico; **non scrivibile** dalle sessioni legate a `raffaellocantatelli` — il git proxy non inietta credenziali fuori dal set autorizzato.
- `Claudioterzi82/Raffaello-SIA` richiede autenticazione: **UNKNOWN**, nessun contenuto verificato.
- La CLI `python -m sdq1` è rotta al commit `155cb5f`: legge `args.chat_telegram` e `args.briefing_operativo` mai dichiarati, prima di ogni dispatch. Fix in `patches/0001`.
- `registro_ipotesi.py` cancella H5 e H6 e azzera 4 delle 6 prove di H4 a ogni esecuzione. Fix in `patches/0002`. **Recuperare i dati da git history prima di rieseguirlo.**
- SAR V3 e SAR a 10 livelli **coesistono**, non sono versioni successive.
- Il VSS usa n-grammi di caratteri, non embedding, e non persiste.
- `r3/node.py` è reale; `eternal_backup_agent.py` simula IPFS e blockchain e non è importato da nessun modulo.
- La copia di lavoro sta in `.lavoro/` — dentro il workspace, così la cwd della shell non viene resettata.
