# export/ — l'artefatto di questo nodo, e il gate reso applicato

Il gate canonico sta in `claudioterzi/Claudio`, commit `f848f19`,
`docs/R3_EXPORT_GATE_EVERY_NODE_2026-10-04.md`. **Quello è la fonte.** Questa
cartella contiene l'artefatto conforme di questo nodo e gli strumenti che
rendono il gate un controllo invece di una dichiarazione.

| File | Cosa fa |
|---|---|
| `verifica_export.py` | valida l'artefatto di qualunque nodo: campi obbligatori, tipi ammessi, ogni claim etichettato, **coerenza interna** fra `PATCH`, `PATCH_SHA256` e `PATCH_BYTES` |
| `genera_export.py` | ricalcola l'artefatto di questo nodo dal repository, include l'output letterale dei test, e **si fa validare prima di scriversi** |
| `R3_EXPORT_claude-opus-5_2026-10-04.txt` | l'artefatto. `PASS/FAIL/SKIP: FAIL`, perché i test hanno due rossi veri |

Un artefatto scritto a mano è una dichiarazione. Uno generato dal repository e
validato prima di esistere è una misura.

---

## Deriva del gate — rilevata il 2026-10-04

In chat è circolata una seconda versione del formato, **più debole di quella
committata**. Confronto meccanico, non a occhio:

```
gate committato (f848f19): 19 campi
versione in chat:          10 campi
```

**Rimuove 11 campi su 19**, e tre rimozioni sono gravi per ragioni diverse:

| Campo rimosso | Perché la rimozione rompe qualcosa |
|---|---|
| **`PATCH`** (il testo) | tiene `PATCH_SHA256` ma butta l'oggetto che l'hash impegna. **È BLOCKER-CUSTODY-02 scritto nello standard**: un hash senza oggetto recuperabile non è evidenza dell'esistenza dell'oggetto |
| **`NODE_ID`** | senza, «chi ha detto cosa» non è rappresentabile. È il campo che fa del gate un ledger invece di una checklist |
| **`DESIGN_ONLY_DECLARATION`**, **`KNOWN_ISSUES`**, **`CLAIM_RETRACTIONS`** | sono i tre campi che costringono un nodo a dichiarare cosa non ha fatto, cosa è rotto e cosa ritira. Senza, l'artefatto può solo vantarsi |

Toglie anche `SESSION_DATE`, `ARTIFACT_TYPE`, `CHANGED_FILES`, `PATCH_BYTES`,
`REPRODUCIBILITY`, `PASS/FAIL/SKIP`. Aggiunge `GIT_STATUS` e
`REAL_POSTGRES_BACKEND`, che sono utili e vanno conservati — ma si aggiungono,
non si scambiano con quelli sopra.

**Quale vince:** quello committato. In questo progetto, dove un documento e il
dato divergono, vince il dato; e fra una chat e un commit, il commit è il dato.
Resta valido `f848f19` finché un commit successivo non lo sostituisce
dichiarando cosa cambia e perché.

### Il controllo che impedisce che ricapiti in silenzio

`test_r3.py`, gruppo `CUSTODIA`: legge la lista dei campi dal gate **pubblicato
su `origin/main`** — non dall'albero di lavoro, che potrebbe essere a qualunque
commit — e la confronta con quella che `verifica_export.py` applica davvero.

Se una versione futura del gate toglie campi, il controllo lo dice. Se qualcuno
allinea il validatore a una versione più debole, il controllo lo dice uguale.
**Un cancello che si può indebolire senza che nessuno veda non è un cancello.**
