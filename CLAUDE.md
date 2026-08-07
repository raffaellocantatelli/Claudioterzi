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
| `SOLUZIONE_2055.md` | Il sistema passato al filtro dei trent'anni |
| `PROTOCOLLO_ROSSO.md` | Definizione canonica del protocollo, trasportabile fuori di qui |
| `patches/` | Due fix testati per i difetti bloccanti, da applicare con `git apply` |
| `test_r3.py` | Controllo eseguibile degli invarianti del protocollo |

---

## Prima di concludere un lavoro

```bash
python3 test_r3.py
```

Esce diverso da zero se la disciplina è decaduta: documenti canonici mancanti, etichette epistemiche assenti, o un'ipotesi senza criterio di falsificazione. Non è cerimoniale — ha già intercettato una violazione in questo stesso repository.

---

## Fatti verificati da non riscoprire

Costano tempo a ritrovare, e sono già RECUPERATO:

- Il codice del sistema è in `claudioterzi/Claudio`. Leggibile via clone pubblico; **non scrivibile** dalle sessioni legate a `raffaellocantatelli` — il git proxy non inietta credenziali fuori dal set autorizzato.
- `Claudioterzi82/Raffaello-SIA` richiede autenticazione: **UNKNOWN**, nessun contenuto verificato.
- La CLI `python -m sdq1` è rotta al commit `155cb5f`: legge `args.chat_telegram` e `args.briefing_operativo` mai dichiarati, prima di ogni dispatch. Fix in `patches/0001`.
- `registro_ipotesi.py` cancella H5 e H6 e azzera 4 delle 6 prove di H4 a ogni esecuzione. Fix in `patches/0002`. **Recuperare i dati da git history prima di rieseguirlo.**
- SAR V3 e SAR a 10 livelli **coesistono**, non sono versioni successive.
- Il VSS usa n-grammi di caratteri, non embedding, e non persiste.
- `r3/node.py` è reale; `eternal_backup_agent.py` simula IPFS e blockchain e non è importato da nessun modulo.
- La copia di lavoro sta in `.lavoro/` — dentro il workspace, così la cwd della shell non viene resettata.
