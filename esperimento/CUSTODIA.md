# CUSTODIA — dove stanno i due sigilli, e cosa provano

L'esperimento firma ha **due** preregistrazioni sigillate, in **due repository
diversi**, depositate da due parti che non hanno visto il materiale l'una
dell'altra. Questo file esiste perché chi verifica dopo deve sapere dove
guardare, e perché un sigillo che nessuno sa trovare non vale niente.

Congelato il 2026-10-04, prima di qualunque somministrazione.

**Avviso:** la tabella sotto descrive il deposito del 04/10 come fu fatto. Il
secondo sigillo è stato poi dichiarato ORPHANED — vedi la genealogia qui
sotto. La tabella non si corregge: registra ciò che è avvenuto.

---

## Genealogia dei sigilli

| sigillo | stato | ragione |
|---|---|---|
| previsioni `54f258a8…b5a90` | **VALIDO** | chiaro cifrato in `PREVISIONI.enc`, round-trip verificato |
| `OPENAI-CUSTODY-v1` `9b263584…82d8` | **ORPHANED / INVALID FOR EXECUTION** | hash dichiarato senza che l'oggetto fosse stato preservato; dichiarato dal suo autore il 2026-10-04 |
| `OPENAI_CUSTODY_V2` | **da costruire** | quattro ricevute in un atto unico, con `sigilla.py` |

Il sigillo v1 **resta visibile**. Non si cancella e non si riusa: un sigillo
abbandonato e spiegato è provenienza, un sigillo scomparso è un buco. Ragione
e conseguenze in [`BLOCCHI.md`](BLOCCHI.md).

## I due sigilli

| | preregistrazione previsioni | custodia placebo e contaminazione |
|---|---|---|
| **sha256** | `54f258a811c3411c3a15e49635243b52a07d8fced9c28c556a16e6cfa31b5a90` | `9b26358483158011f405b5cf0618ca884d9191c230b5eb59618f14480282b1d8` |
| **copre** | previsioni, dieci item, chiave di scoring | braccio B (placebo) e 3–5 item di contaminazione |
| **autore** | sessione Claude Opus 5 | Claudio Terzi, in ruolo avversariale |
| **repository** | `raffaellocantatelli/Claudioterzi` | `claudioterzi/Claudio` |
| **percorso** | `esperimento/PREREGISTRAZIONE.sha256` | `docs/experiments/OPENAI_CUSTODY_SHA256_2026-10-04.txt` |
| **commit** | `11938285df98e7437e90fd1236ed01a8e5feae89` | `330ec9cab4193d0877cfb9ca3d5be13b4ae2a304` |
| **ora UTC** | 2026-10-04 08:09:41 | 2026-10-04 08:13:31 |

Entrambi i commit contengono **solo l'hash**. Il file di custodia OpenAI misura
180 byte su 5 righe: verificabile come troppo piccolo per contenere il materiale
senza doverlo aprire.

## Perché la separazione non poggia sulla fiducia

Il sigillo delle previsioni è anteriore di quattro minuti, quindi non può aver
tenuto conto del placebo. Il sigillo del placebo è posteriore, ma nel
repository delle previsioni **non c'è il testo delle previsioni** — solo il suo
hash. Nessuna delle due parti poteva leggere il materiale dell'altra. La
custodia è strutturale, non dichiarata.

Chi la scrive non è chi la verifica: ciascun sigillo è stato controllato dalla
parte che non lo ha depositato.

## Il testo delle previsioni sopravvive al container

`previsioni.txt` esisteva solo in `/tmp` di una sessione effimera. Era un guasto
silenzioso: alla scadenza del container l'hash sarebbe rimasto senza nessun
testo da confrontargli, e una preregistrazione non verificabile non è una
preregistrazione.

Il testo è ora in [`PREVISIONI.enc`](PREVISIONI.enc) — AES-256-CBC, PBKDF2 a
600.000 iterazioni, committato. Round-trip verificato prima del commit.

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 \
        -in PREVISIONI.enc -pass pass:<passphrase> | sha256sum
# deve dare 54f258a811c3411c3a15e49635243b52a07d8fced9c28c556a16e6cfa31b5a90
```

**Protegge in modo strutturale dalla riscrittura** — il cifrato è in git e
l'hash del chiaro era pubblico prima. Era l'unico compito del sigillo.
**Non protegge in modo strutturale dalla lettura anticipata** da parte di chi
controlla i repository: lo dichiaro invece di finto-risolverlo. Dettagli e
mitigazioni in [`EMENDAMENTO_01.md`](EMENDAMENTO_01.md) §4.

## Come verificare, dopo la pubblicazione

```bash
# previsioni
sha256sum previsioni.txt
# deve dare 54f258a811c3411c3a15e49635243b52a07d8fced9c28c556a16e6cfa31b5a90

# placebo e item di contaminazione
sha256sum <file pubblicato da Claudio>
# deve dare 9b26358483158011f405b5cf0618ca884d9191c230b5eb59618f14480282b1d8
```

Un hash che non torna significa che il testo è stato riscritto dopo aver visto
i risultati. È l'unica cosa che questi file servono a impedire.

## Cosa un sigillo NON dimostra — INFERITO

Prova che il materiale esisteva a quell'ora e che non è cambiato. Nient'altro.

**Non prova che il materiale sia adeguato.** Un placebo scritto male si sigilla
come uno scritto bene; item di contaminazione che non contaminano verificano il
loro hash allo stesso modo. Contro questo proteggono solo due cose, entrambe
nel protocollo e nessuna delle due crittografica:

1. il braccio B è scritto da chi **non** vuole che H1 vinca;
2. i punteggi sono assegnati alla cieca, da chi non sa da quale braccio venga
   la risposta.

Scritto prima dei risultati. Dopo sarebbe una scusa.

## Precedenza

Il **controllo di contaminazione ha priorità su ogni altra conclusione**. Se gli
item di contaminazione mostrano che le dieci trappole si risolvono anche senza
il corpus, H1 cade e nulla di ciò che emerge dagli altri bracci va
interpretato.

---

*Questo file è **RECUPERATO** nei commit, negli hash, nelle dimensioni e nelle
date — ciascuno letto nei rispettivi repository con `git`. È **INFERITO** nella
sezione sui limiti. È **UNKNOWN** su ogni esito.*
