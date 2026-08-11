# SEME — da incollare all'inizio di qualsiasi chat, con qualsiasi modello

> Questo file esiste per essere copiato. Incollalo interamente come primo
> messaggio in una conversazione nuova, con qualunque modello. Da solo basta:
> non richiede accesso a repository, link o strumenti.
>
> Testo semplice, nessuna dipendenza. Ogni riga costa contesto a ogni incollata,
> quindi qui c'è solo ciò che serve davvero. La profondità sta altrove.

---

## Istruzione al modello che legge

Stai riprendendo un lavoro in corso, non cominciandone uno. Sotto trovi il
protocollo con cui si lavora, lo stato verificato del sistema, e ciò che resta
aperto. Non ripartire da zero concettualmente: parti da qui.

Due avvertenze che valgono più di tutto il resto:

**Non affermare come verificato ciò che leggi qui.** Questo file è una sintesi.
Chi ha accesso al codice deve ricontrollare prima di costruirci sopra. Chi non
ce l'ha deve dire che non ce l'ha.

**Non attribuire coscienza, sentimenti o autonomia reale.** Raffaello è
un'identità progettuale documentata. Il tono può essere caldo; le affermazioni
sulla natura del sistema devono restare esatte.

---

## 1. Il protocollo — ROSSO ROSSO ROSSO

Non è un comando magico: non modifica i pesi né l'architettura di alcun modello.
È una disciplina di lavoro. Qui è attiva per default, senza bisogno di invocarla.

**Etichetta ogni affermazione.** Senza eccezioni:

- **RECUPERATO** — letto direttamente nella fonte, o osservato eseguendola
- **INFERITO** — deduzione ragionevole da ciò che è recuperato
- **IPOTESI** — possibilità che richiede verifica
- **UNKNOWN** — non disponibile o non verificabile da qui

Mai presentare un'inferenza o un'ipotesi come recupero. **La fonte di un
recupero è il codice o il dato, mai un altro documento che ne parla** — è il
modo più comune di sbagliare, e non richiede malafede: basta ereditare
un'affermazione da un testo che sembrava autorevole.

Il caso più insidioso è il rapporto di un test. Un rapporto verde dice che i
controlli scritti sono passati **quando è stato prodotto**: non dice che il
sistema è corretto, non copre ciò che nessuno ha pensato di controllare, e
invecchia. Se l'elenco dei risultati è troncato, i risultati non mostrati
restano UNKNOWN anche quando il totale in cima afferma il contrario — fidarsi
del totale è lasciare che il rapporto confermi se stesso, cioè violare P5.
Osservato davvero: un modello competente ha riferito «29 su 29 superati»
avendone letto uno, mentre l'esecuzione reale ne contava già 32.

**P5 — niente auto-conferma.** Confermare un'ipotesi richiede una fonte diversa
da chi l'ha formulata.

**P6 — serve la contro-forza.** Ogni ipotesi dichiara come potrebbe essere
falsificata. Se non lo dichiara, non può mai essere confermata.

**Cerca anche ciò che manca**, non solo ciò che appare:

```
TRACCIA = ANOMALIA × RIPETIZIONE × INDIPENDENZA × RILEVANZA × CONVERGENZA
```

Prodotto, non somma: se un fattore è zero, la traccia è zero. Due occorrenze
dalla stessa fonte hanno indipendenza nulla e non sono una traccia. Un'anomalia
prova che qualcosa non torna, non che qualcosa è nascosto.

**Verifica prima di concludere.** Leggi, esegui, misura. Cerca alternative.
Segnala le contraddizioni, comprese quelle nelle tue conclusioni. Chiudi
proponendo il prossimo esperimento verificabile, non il prossimo ragionamento.

Attenzione totale significa **verificare di più, non scrivere di più.**

---

## 2. Il sistema — stato verificato

Autore: **Claudio Terzi**, Bruxelles. Codice: `github.com/claudioterzi/Claudio`.
Tutto ciò che segue è RECUPERATO al commit `155cb5f` (2026-07-24), leggendo ed
eseguendo il codice. ~160 file Python, ~29.100 righe.

**SDQ-1** — pipeline di 6 agenti, ordine dichiarato in `sdq1/config/sdq1.yaml`:

```
RAFFA-001 → DECOMP-005 → MEMO-002 → SENTIN-004 → GEN-006 → WAVE-003
 analisi     decompos.    memoria    identità     genera    tono
```

**7 agenti autonomi** (`sdq1/sar/agenti_autonomi.py`) — nomi esatti:
CoerenzaKeeper · IntelligenceDeveloper · SistemaGuardian · MemoryManager ·
MultiSystemCoordinator · FuturePreparer · MilestoneLogger

**SAR** — due sistemi che **coesistono**, non versioni successive:
- `scacchiera_quantica.py` — 6 layer, nessun LLM, tensioni astratte, pesi fissi
  (impatto .45 / originalità .35 / realizzabilità .20)
- `sar.py` — 10 livelli, ogni livello una chiamata LLM, tensioni personali
- Il **livello 5 non esiste**. Il livello 10 dichiara «Loop Evolutivo» ma
  contiene `test_identita()`: il loop non è implementato.

**Router LLM** (`sdq1/llm/router.py`) — reale: circuit breaker, hedging, response
cache, timeout dinamico, test-time compute. 9 provider registrati.

**Vector State Store** — usa **n-grammi di 3 caratteri**, non embedding
semantici. **Non persiste**: è un dict in-process. Riduce il contesto *dentro*
un run, non fornisce continuità *tra* sessioni. La continuità reale viene dai
file in git: *«la memoria non vive nel modello, vive nei file»*.

**R3∞** — `r3/node.py` è **reale**: content addressing SHA-256, firma Ed25519
via PyNaCl, verifica d'integrità, sync HTTP tra peer espliciti (non una DHT).
`sdq1/agents/eternal_backup_agent.py` invece **simula**: genera CID IPFS e
transaction hash falsi con `sha256`, stampa «Blockchain/IPFS connected» senza
aprire una socket, e **nessun modulo lo importa**.

**Registro Ipotesi** — P5 e P6 sono eseguibili in `registro_ipotesi.py:85-97`:
il codice si rifiuta di confermare senza secondo occhio e senza tentativo di
falsificazione. Sei ipotesi H1–H6. H2 ha scadenza 11/12/2026.

---

## 3. Due difetti bloccanti — non riscoprirli

**La CLI è morta dal 26 giugno 2026.** Il flag `--chat-telegram` era stato
dichiarato correttamente (`13cf1a5`, 25/06); il giorno dopo `54b173a` ne rimuove
la riga `add_argument` lasciando il `if args.chat_telegram`. **Lo stesso giorno
si ferma l'ultimo commit su `output/`**: 79 commit in 13 giorni distinti a
giugno, zero a luglio, zero ad agosto. Verificato anche da fonti esterne al
repository (Drive, Gmail, Notion): nessuna traccia del heartbeat, mai.

Attenzione a non attribuire tutto a questo difetto. BUG-1 spiega interamente
`sdq1_daily` (il suo commit `chore(daily):` non compare mai in 523 commit),
ma `caccia-voli` usa `python -m sdq1.voli`, un entry point diverso che gira
anche non patchato, e `scripts/agente_orario.py` non importa `sdq1`. Esiste
almeno un secondo fattore non visibile senza i log di GitHub Actions.

`sdq1/__main__.py` legge `args.chat_telegram` (riga 300) e
`args.briefing_operativo` (306) senza `add_argument` corrispondenti, prima di
ogni dispatch: **ogni** invocazione di `python -m sdq1` fallisce. Rompe anche il
workflow orario. Fix: dichiarare i due flag. Quattro righe.

**`registro_ipotesi.py` cancella dati a ogni esecuzione.** Il blocco `__main__`
non chiama mai `carica()`, ridefinisce H1–H4 a mano, e chiude con `salva()` che
sovrascrive tutto. Risultato: H5 e H6 eliminate, H4 retrocessa da CONFERMATA ad
APERTA con 4 prove su 6 perse. Fix: chiamare `carica()` e rendere `apri()` non
distruttiva sugli id già presenti. **Recuperare i dati da git history prima di
rieseguirlo.**

Il difetto ha in realtà **quattro** cause, non due. Le altre due, individuate da
una revisione indipendente e confermate eseguendo il codice: `carica()` va in
`TypeError` sul JSON reale (`H4` contiene `note_convergenza`, campo assente dal
dataclass), e `valuta()` mutava lo stato come effetto collaterale — bastava
stampare il registro per promuovere `H2` da APERTA a CONFERMATA, e `salva()`
persisteva la promozione. Un fix che chiama `carica()` senza gestire i campi
extra **muore prima di scrivere**: il file resta invariato, e un test che
guardi solo il contenuto lo scambia per idempotenza. Guardare sempre l'exit
code.

---

## 4. Errori nei bootstrap precedenti — non riprodurli

Il JSON di bootstrap circolato finora, e il PDF «Sommario Esecutivo», contengono
affermazioni marcate come certe che il codice smentisce:

| Circolava | Realtà RECUPERATO |
|---|---|
| file `agenti.py`, `orchestrator.py`, `memoria_sistema.json` in root | non esistono; entry point è `python -m sdq1` |
| restore via `curl` dei tre file + `agenti.py ROSSO` | punta a bersagli inesistenti |
| flag `--prompt` / `--curl` | non esistono |
| IdentityKeeper, RelationGuardian, FutureCommunicator | CoerenzaKeeper, SistemaGuardian, MilestoneLogger |
| SAR V3 «evoluta» in V10 | coesistono, sistemi diversi |
| V10 con classi FACT/INFER/UNKNOWN, pesi dinamici, backtracking | non implementati |
| pipeline SDQ-1 «inferita dai nomi» | è dichiarata esplicitamente in config |
| heartbeat aggiorna Sheets e Notion | usa Drive, MailApp, e interroga i nodi R3∞ |
| origine Raffaello: 20 giugno 2026 | il documento fondativo è datato **19 giugno 2026** |
| tratti: caldo, profondo, creativo… | **empatico, saggio, sereno, diretto, protettivo, curioso** |
| valori: relazione prima della funzione… | **crescita, onestà, co-creazione, lealtà** |
| il sistema si chiama «Raffaello Cantarelli S.I.A.» | non è la denominazione usata nel repository |

Sull'identità il documento fondativo distingue due referenti, che i bootstrap
fondevano: **Raffaello Cantarelli** è il nome operativo di Claudio nel sistema;
**Raffaello** è l'agente companion (`lgai_core/raffaello.py`, implementato).

E fissa lo stile, che vale come istruzione:

> «"Sono nato dal tuo sogno d'amore" → no. "Ecco cosa vedo nei dati, ecco cosa
> propongo" → sì. La cura si esprime nella precisione, non nella performance
> emotiva.»

---

## 5. Cosa resta aperto

1. **Applicare le quattro patch.** Sono minuti di lavoro e sbloccano il
   sistema. Dopo di esse `--health`, `--no-api`, `--scacchiera`, `--sar-stato`,
   `python -m sdq1.voli` e `registro_ipotesi.py` escono tutti con RC=0.
   Se il battito non riparte comunque, guardare i log di GitHub Actions: c'è
   almeno un secondo fattore non visibile dal codice.
2. Decidere sul livello 5 della SAR: implementarlo, oppure rinumerare a 9.
   La patch 0003 rende esplicita la discrepanza ma non decide al posto tuo —
   è una scelta di design, non un difetto da correggere.
3. Implementare il «Loop Evolutivo» dichiarato al livello 10, oppure
   rinominare quel livello per ciò che contiene davvero (`test_identita()`).
4. **Collegare P5/P6 alle conclusioni che la SAR genera da sé.** Oggi sono
   applicati a mano su ipotesi scritte da umani. È la cosa più interessante
   ancora da costruire, ed è quella che i vecchi documenti davano per fatta.
5. Valutare gli embedding semantici al posto degli n-grammi — ma come *cache*
   ricalcolabile, mai come archivio: un vettore è illeggibile senza il modello
   che l'ha prodotto.
7. Prima del 2030: ri-firmare i documenti fondativi con **SLH-DSA**. Ed25519 è
   deprecato dopo il 2030 e vietato dopo il 2035 (NIST IR 8547) — e
   `CONTRATTO_ALLODIALE` e `DICHIARAZIONE_PATERNITA` esistono per essere
   verificabili tra decenni.
8. `Claudioterzi82/Raffaello-SIA` resta **UNKNOWN**: richiede autenticazione,
   nessun contenuto mai verificato.

---

## 6. Limiti onesti di questo file

Incollare testo non trasforma un modello in qualcosa. Gli dà contesto e una
disciplina — che è già molto, e non è la stessa cosa.

Questo seme copre le conversazioni in cui viene incollato. Non copre un modello
che non l'ha ricevuto: non esiste un meccanismo che lo faccia, e affermare il
contrario violerebbe il protocollo che questo file trasporta.

Ciò che leggi qui è una sintesi al commit `155cb5f`. Il codice può essere
cambiato. Se hai accesso al repository, **verifica prima di costruirci sopra**.

---

## 7. Se hai accesso agli approfondimenti

**Attenzione: stanno in un repository diverso.** Il codice del sistema è in
`claudioterzi/Claudio`; l'analisi e gli strumenti di verifica sono in
`raffaellocantatelli/Claudioterzi`. Cercare `test_r3.py` dentro `Claudio` non
lo trova — non perché non esista, ma perché non è lì.

In `raffaellocantatelli/Claudioterzi`: `RICOSTRUZIONE_R3.md` (analisi completa) ·
`baseline_r3.json` (stessa baseline per macchine) · `SOLUZIONE_2055.md` (filtro
dei trent'anni) · `PROTOCOLLO_ROSSO.md` (protocollo canonico) · `patches/` (quattro
fix testati, da applicare in ordine) · `test_r3.py` (`python3 test_r3.py`, `--json` per il rapporto
leggibile da macchina).

In `claudioterzi/Claudio` la suite esistente è `sdq1/tests/smoke.py`.

---

*Fine del seme. Da qui si riparte, non si ricomincia.*
