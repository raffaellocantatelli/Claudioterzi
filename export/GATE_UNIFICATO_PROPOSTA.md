# Proposta: gate unificato, zero rimozioni

Da committare in `claudioterzi/Claudio` al posto di
`docs/R3_EXPORT_GATE_EVERY_NODE_2026-10-04.md`. **Io non ho accesso in
scrittura a quel repository**, quindi questo è il testo pronto, non un commit.

Risolve l'ambiguità: oggi esistono due versioni del formato e ogni nodo si
conformerà a quella che ha visto. È `f848f19` **più** i due campi utili della
versione a 10 campi, **senza nessuna rimozione**.

Differenze rispetto a `f848f19`: aggiunti `GIT_STATUS` e
`REAL_POSTGRES_BACKEND`; aggiunta la riga che dichiara superata la versione a
10 campi. Nient'altro.

Quando questo è committato, `verifica_export.py` si aggiorna ai 21 campi e il
controllo anti-deriva torna verde da sé. **Non lo aggiorno prima**: renderebbe
non conformi gli artefatti prodotti secondo `f848f19`, compreso il mio.

---

```markdown
# R³ EXPORT GATE — OGNI NODO

Stesso standard per Claude, Qwen, DeepSeek, Grok, Manus e Meta. Se è asimmetrico, non è canone.

Ogni nodo che produce lavoro (analisi, architettura, patch, review) esporta in questa forma. Chi non esporta non entra nella matrice come evidenza — resta conversazione.

**Versione autoritativa: questa.** Una versione a 10 campi è circolata in conversazione: è **superata**. Toglieva `PATCH` tenendo `PATCH_SHA256` — un hash senza l'oggetto che impegna — e toglieva `NODE_ID`, senza cui «chi ha detto cosa» non è rappresentabile. Nessun artefatto va prodotto secondo quella.

## Struttura comune

```
NODE_ID
SESSION_DATE             (RFC3339)
ARTIFACT_TYPE            (PATCH | DESIGN | REVIEW | TEST)
CLAIMED_BASE_SHA         (o NOT_AVAILABLE)
LOCAL_HEAD_SHA           (o NOT_AVAILABLE)
BRANCH                   (o NOT_AVAILABLE)
GIT_STATUS               (clean | dirty — se dirty, elencare i file)
CHANGED_FILES            (se PATCH)
DIFF_STAT                (se PATCH)
PATCH                    (testuale, non link)
PATCH_SHA256
PATCH_BYTES
REPRODUCIBILITY          (python, docker image, requirements hash, DB version)
TEST_COMMANDS
TEST_OUTPUT_RAW
PASS/FAIL/SKIP
SANDBOX_BACKEND          (mock | sqlite | postgres | in-memory | cloud)
REAL_POSTGRES_BACKEND    (PENDING | RUN | FAILED | PASSED | NOT_APPLICABLE)
DESIGN_ONLY_DECLARATION  (IMPLEMENTED | DESIGN_ONLY | MIXED — per ogni claim)
KNOWN_ISSUES             (strutturato)
CLAIM_RETRACTIONS
```

**Coerenza interna, verificabile senza fidarsi del nodo:** `PATCH_SHA256` e
`PATCH_BYTES` devono corrispondere al `PATCH` incluso. Un artefatto che non
torna con se stesso non entra, qualunque cosa dichiari.

## Regola di ammissione

Un nodo entra nella matrice delle evidenze solo dopo almeno un artefatto conforme.

```
NODE_ID → CANDIDATE / EVIDENCE NOT EXPORTED
```

Nessuna eccezione. Nessuna fiducia pregressa. **La regola vale anche per chi
scrive questo documento**, e vale per fronte: un nodo conforme su una patch
resta CANDIDATE su un lavoro che non ha esportato.
```

---

## Le richieste per nodo restano valide

Le sezioni per Claude, Qwen, DeepSeek, Grok e Manus di `f848f19` non cambiano e
vanno riportate sotto, invariate. Una nota sulla prima:

**la richiesta a «Claude» non è di questa sessione.** Nessun PostgreSQL, nessun
PG 16, nessuno dei cinque failure: UNKNOWN. Su quel fronte questo nodo è
`CANDIDATE / EVIDENCE NOT EXPORTED` e lo resta. La quarta domanda — il commit
`81dce982…` — ha risposta nei metadati: autore `Claudio
<Claudioterzi82@outlook.com>`, 2026-10-04 11:48:15, 125 righe. **Né di questo
nodo, né di un nodo Claude secondo git.** Con il limite che l'autore di un
commit non è l'autore del contenuto, ed è la lacuna del Ledger già segnalata.
