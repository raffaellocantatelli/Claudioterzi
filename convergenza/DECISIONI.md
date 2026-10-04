# DECISIONI — pin congelati il 2026-10-04

Claudio: **«Accetta tutto.»** Tre delle quattro voci aperte sono decisioni e si
chiudono qui. La quarta non è una decisione: è un oggetto, e resta aperta.

**La distinzione non è formale.** «Accetto» chiude una scelta; non produce un
file. Trattare un'accettazione come una consegna sarebbe `OPENAI-CUSTODY-v1` di
nuovo, con un'altra faccia.

---

## D1 — Seed del fixture: PINNATO

```
seed_bytes  = ascii("81dce982dfbd1d4b5f646b1418efbc24c8be4bf0")
            + ascii("R3-FIXTURE-1000")
              # 40 esadecimali MINUSCOLI, nessun separatore, nessun newline,
              # 55 byte in tutto
seed_sha256 = 583efd3fed126a802aa716fe2537e116850a2fbc2f94c9d59580a1cdc0b7466b
```

```bash
printf '%s%s' 81dce982dfbd1d4b5f646b1418efbc24c8be4bf0 R3-FIXTURE-1000 | sha256sum
```

Le altre cinque letture della formula (byte grezzi, maiuscolo, `||` letterale,
newline in mezzo, newline finale) sono **escluse**. `genera_fixture.py`
ricalcola il seed a ogni esecuzione e si rifiuta di partire se non coincide.

## D2 — S13: righe permutate, §7 viene testato

Le 60 righe di S13 hanno le chiavi di primo livello permutate; le altre 940
sono JCS canoniche. Gli indici sono nel manifest, campo `righe_non_canoniche`.

**Conseguenza accettata:** il punto 2 della pre-registrazione («una riga per
evento, JCS canonico») vale per 940 righe su 1000, e l'eccezione è dichiarata
invece che nascosta. In cambio §7 è verificabile. Un fixture interamente
canonico non avrebbe potuto misurare la canonicalizzazione.

## D3 — Gate unificato: 21 campi, zero rimozioni

`f848f19` più `GIT_STATUS` e `REAL_POSTGRES_BACKEND`. La versione a 10 campi è
**superata**: toglieva `PATCH` tenendo `PATCH_SHA256` e toglieva `NODE_ID`.

Applicato nel codice:

- `export/verifica_export.py` richiede 21 campi e valida i valori ammessi dei
  due nuovi. Self-test su **nove** casi, otto dei quali devono essere respinti.
- `export/genera_export.py` emette i due campi; `GIT_STATUS` è calcolato da
  `git status --porcelain`, non dichiarato.
- Testo pronto da committare in `claudioterzi/Claudio`:
  [`export/GATE_UNIFICATO_PROPOSTA.md`](../export/GATE_UNIFICATO_PROPOSTA.md).

**Resta da fare in quel repository, e non posso farlo io**: il git proxy non
inietta credenziali fuori dal set autorizzato. Finché il commit non c'è, il
controllo anti-deriva confronta il validatore con `f848f19` — e passa, perché
il validatore è **più stretto** del gate committato, non più largo.

Nota da non perdere: `GIT_STATUS` ha trovato qualcosa al primo uso. Il mio
artefatto risultava `dirty` per un `.pyc` tracciato per sbaglio. Un campo che
costringe a dichiarare lo stato dell'albero di lavoro ha fatto in un minuto
quello per cui esiste.

---

## A1 — I cifrati di v2: APERTO, e non si chiude accettando

`BLOCKER-CUSTODY-02` resta **aperto**. Stato invariato:

```
V2_GENERATED_AND_ROUNDTRIP_VERIFIED / PERSISTENCE_NOT_YET_PROVEN / START BLOCKED
```

Le tre ricevute sono dichiarate e il manifesto è **riprodotto e verificato** da
questa sessione. I due cifrati no: il deposito è fallito con
`container_session_expired`.

Si chiude con un file che compare in `docs/experiments/` di
`claudioterzi/Claudio`, non con un'affermazione. `test_r3.py` lo cerca e resta
rosso finché non lo trova.

**La domanda che tiene fermo A/B/C/D/E è ancora una sola:** quei quattro file
esistono ancora in quel runtime? Se sì, un commit li salva. Se no, è v3 — e
questa volta `sigilla.py` scrive direttamente nella cartella di lavoro di un
repository, perché lo spostamento è il punto di rottura.

---

## Stato dei due esperimenti, dopo questi pin

| | stato | cosa manca |
|---|---|---|
| **Convergenza R3-PEER/1.1c** | fixture generato e verificabile, scoring preregistrato, pin chiusi | IMPL-1 e IMPL-2 freschi, che esportino secondo il gate a 21 campi |
| **Firma (A/B/C/D/E)** | disegno congelato, pacchetto cieco pronto, un sigillo valido | i due cifrati di v2 |

Il primo può partire. Il secondo no, e la differenza è un file.

---

*Decisioni **RECUPERATO** dal messaggio di accettazione. Pin D1 verificato
ricalcolando, D2 e D3 verificati eseguendo. A1 **UNKNOWN** sulla sopravvivenza
dei byte.*
