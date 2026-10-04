# Riconciliazione — pre-registrazione del fixture

Riferimento: `claudioterzi/Claudio` @ `261bebc`,
`docs/R3_PEER_1_1C_FIXTURE_PREREGISTRATION_2026-10-04.md`, 32 righe,
autore `Claudio <Claudioterzi82@outlook.com>`, 2026-10-04 12:05:10 +0200,
antenato di `origin/main`. **Verificato: il testo committato coincide con quello
della chat.** È la prima volta nella giornata che un incollato e un commit non
divergono.

Il punto 5 coincide con §3 della
[preregistrazione dello scoring](PREREGISTRAZIONE_SCORING.md) riga per riga,
UNDERSPECIFIED compreso. Il punto 2 e il punto 3 sono aggiunte che la
preregistrazione non aveva, e il punto 3 ha una conseguenza che cambia la
statistica.

Restano **tre lacune**. Nessuna richiede di riaprire il disegno: si chiudono
pinnando valori prima che GEN giri.

---

## L1 — Il seed non è definito. Sei hash dalla stessa formula

```
SHA256(81dce982dfbd1d4b5f646b1418efbc24c8be4bf0 || "R3-FIXTURE-1000")
```

`||` denota concatenazione, ma **di cosa**? Lo sha come 40 caratteri ASCII o
come 20 byte grezzi? Minuscolo o maiuscolo? Con separatore? Con newline finale?

| sha256 risultante | interpretazione |
|---|---|
| `583efd3fed126a802aa716fe2537e116850a2fbc2f94c9d59580a1cdc0b7466b` | ascii(sha) + ascii(stringa) |
| `4dd81fe613ae9e734429e902c66644ec2c81c9ef0aea6abde686d2f4bb0ce719` | ascii maiuscolo + ascii |
| `51b29ce088e7f5298328d9b8d5c99483483217aa55bc4150c8b6da8c50dc4a9e` | byte grezzi + ascii |
| `f35bda4f874daaec02c3338a02250561c565b75e6a5f67eb9e2970cb8aa10e01` | con `\|\|` letterale |
| `858fe374123b9da3dcd85a857128266b9194ff4d610ef775b6788e24393d754d` | con newline in mezzo |
| `99481273fdcccfe7e97a6499c91c31f4c490ab086cd537f7bd8c8d86d06e74df` | con newline finale |

**È esattamente il difetto di `OPENAI-CUSTODY-v1`**: un hash su una
concatenazione non documentata. Lì l'oggetto era irrecuperabile; qui il fixture
sarebbe irriproducibile — due esecuzioni «secondo la formula» darebbero file
diversi, ed entrambe potrebbero dirsi conformi.

«C non sceglie, C esegue» non regge finché la formula ammette sei letture: **chi
esegue sceglie, e non sa di farlo.**

### Pinning proposto

```
seed_bytes      = ascii("81dce982dfbd1d4b5f646b1418efbc24c8be4bf0")
                  + ascii("R3-FIXTURE-1000")
                  # 40 caratteri esadecimali MINUSCOLI, nessun separatore,
                  # nessun newline, 55 byte in tutto
seed_sha256     = 583efd3fed126a802aa716fe2537e116850a2fbc2f94c9d59580a1cdc0b7466b
seed_per_random = int(seed_sha256, 16)
```

Minuscolo perché è così che git stampa gli sha. Nessun separatore perché `||`
denota l'operazione, non un letterale. Nessun newline perché un newline non
dichiarato è il modo più comune di perdere un hash.

**Verificabile in una riga:**

```bash
printf '%s%s' 81dce982dfbd1d4b5f646b1418efbc24c8be4bf0 R3-FIXTURE-1000 | sha256sum
```

---

## L2 — Il punto 4 si contraddice

> «Distribuzione: fissata **al momento della generazione**, non scelta da C.
> Registrata nel manifest del fixture.»

Se è fissata al momento della generazione, **qualcuno la fissa in quel
momento** — e se non è C, è chi lancia C. In entrambi i casi non è
preregistrata, e il manifest la *registra* dopo averla subita invece di
*verificarla* contro un impegno precedente.

Il costo è misurabile e sta in §4 della preregistrazione dello scoring: **uno
strato con n ≤ 20 non può da solo far scattare la soglia del 2%**, quindi una
distribuzione scelta a generazione può rendere invisibile una
sottospecificazione reale senza che nessuno abbia barato.

### Chiusura

Il punto 4 rinvia alla distribuzione già preregistrata: **13 strati, minimo 25
eventi ciascuno, derivati riga per riga dalle `REGOLE OPERATIVE` §8, totale
1.000.** S11 e S12 esercitano gli OPEN FINDINGS O5 e O1 e sono **esclusi dal
denominatore**: la soglia riguarda ciò che 1.1c sostiene di aver deciso.

**Denominatore 900. Soglia 18 disaccordi.**

Il manifest allora fa il suo lavoro vero: **confrontare la distribuzione
ottenuta con quella impegnata**, e fallire se differiscono.

---

## L3 — Il punto 3 rompe l'indipendenza che il 2% assume

> «Sequenza ordinata. Ogni evento vede lo stato degli eventi precedenti.»

È la scelta giusta: un ledger senza stato non è un ledger. Ma ha una
conseguenza sulla statistica che va dichiarata **prima**.

Con stato sequenziale, **i disaccordi non sono indipendenti.** Se IMPL-1 accetta
l'evento 7 e IMPL-2 lo rifiuta, le due implementazioni hanno da quel momento
stati diversi, e ogni evento successivo che dipende da quello stato può
divergere. **Una sola ambiguità può produrne centinaia.**

Conseguenza: «18 disaccordi su 900» non è un conteggio di ambiguità. Può essere
una ambiguità con 17 code, oppure 18 ambiguità distinte — e sono diagnosi
opposte. La prima dice «un punto da chiarire»; la seconda «la specifica è
vaga».

### Chiusura: due misure, entrambe preregistrate

| misura | cosa conta | a cosa serve |
|---|---|---|
| **tasso grezzo** | ogni evento in disaccordo / 900 | è la soglia del 2%, come scritta |
| **disaccordi radice** | solo la **prima** divergenza per catena causale: un evento in disaccordo il cui stato di ingresso era identico nelle due implementazioni | conta le ambiguità, non le loro conseguenze |

Il tasso grezzo resta la soglia: non la cambio dopo. I disaccordi radice si
riportano accanto, e sono il numero da leggere per capire **cosa** correggere.

Un disaccordo radice è identificabile senza oracolo: basta che lo stato di
ingresso dell'evento coincida fra le due implementazioni. Non serve sapere chi
ha ragione — che è precisamente ciò che GEN non deve sapere.

*Falsificazione di L3:* se le due implementazioni, divergendo su un evento,
ri-convergono sullo stato successivo, la cascata non esiste e questa sezione è
inutile. È possibile — molte decisioni non scrivono stato — e lo si vede dai
dati: se disaccordi radice ≈ tasso grezzo, L3 non si applica a questo fixture.
**Va misurato, non assunto.**

---

## L4 — Il punto 2 impedisce di testare ciò che S13 deve testare

> «JSONL, una riga per evento, **JCS RFC 8785 canonico**.»

Lo strato S13 esiste per verificare che due implementazioni, ricevendo **lo
stesso stato logico con le chiavi in ordine diverso**, calcolino lo stesso
`input_event_hash` — è il test della canonicalizzazione, cioè del §7 della spec.

**Se ogni riga è già canonica, S13 non è somministrabile.** Un input
pre-canonicalizzato non può misurare se chi lo riceve canonicalizza: la
proprietà è già stata garantita da chi ha scritto il fixture.

Non è un conflitto risolvibile a parole: o si rinuncia a testare §7, o il
fixture contiene righe deliberatamente non canoniche.

**Scelta applicata, dichiarata nel manifest:** le 60 righe di S13 hanno le
chiavi di primo livello permutate deterministicamente; tutte le altre 940 sono
JCS canoniche. Il manifest elenca gli indici delle righe non canoniche nel
campo `righe_non_canoniche`, così nessuno le scopre per sorpresa.

Se preferisci il punto 2 alla lettera, S13 si rimuove e §7 resta non testato:
basta dirlo, e la distribuzione si ricompone sui 12 strati rimanenti. Ma va
deciso **prima**, non quando i numeri saranno sul tavolo.

---

## Il fixture è generato

| | |
|---|---|
| eventi | 1000, denominatore 900 |
| seed | `583efd3f…466b`, ricalcolato dalla formula a ogni esecuzione |
| fixture | `0cd2cf770b699db5cb80cbfc45ac11283c8828660888ed39cb33383d41d08e69` |
| generatore | `6cc12c45…261f` |
| preregistrazione letta | `c179cd15…4a26` |
| distribuzione | coincide con quella impegnata — il manifest **confronta**, e si rifiuta di scriversi se differisce |
| righe non canoniche | 60, elencate nel manifest |

**Riproducibilità provata su processi separati**, con `PYTHONHASHSEED` a 0, 1,
12345 e `random`: quattro esecuzioni, un solo hash. Due esecuzioni nello stesso
processo non l'avrebbero provato — condividono l'hash seed, e un'iterazione su
un insieme non ordinato avrebbe dato lo stesso ordine in entrambe. La prima
versione della prova faceva esattamente quell'errore.

**GEN non è un oracolo.** Produce envelope e non dichiara da nessuna parte
quale decisione sia corretta. L'etichetta di strato di ogni evento sta in
`PROVENIENZA_STRATI.tsv`, che **non è nel repository**: ne è pubblicato solo
l'hash, come per i sigilli. Se gli implementatori la leggessero, potrebbero
trattare per casi speciali invece di implementare la spec.

**GEN legge la distribuzione dalla preregistrazione sigillata**, non da una
costante al suo interno: non può derivare dal documento che la impegna, e se la
preregistrazione cambia il manifest lo registra con il suo nuovo hash.

---

## Cosa resta da fare, in ordine

1. **Pinnare il seed** (L1) — un valore, una riga di comando per verificarlo.
2. **Rinviare la distribuzione** alla preregistrazione (L2), e dare al manifest
   il compito di confrontare invece di registrare.
3. **Dichiarare le due misure** (L3) prima del run.
4. **Unificare il gate**: `f848f19` più `GIT_STATUS` e `REAL_POSTGRES_BACKEND`,
   zero rimozioni. Finché esistono due versioni, IMPL-1 e IMPL-2 esporteranno
   secondo quella che hanno visto, e gli artefatti non saranno confrontabili.
5. ~~Poi GEN gira~~ — **fatto**, in attesa che 1, 2, 3 e 4 siano confermati.
   Il fixture è un oggetto verificabile, non un impegno: se cambi il pinning
   del seed, la scelta su S13 o la distribuzione, si rigenera con un comando e
   quello attuale si butta. Niente è stato perso scrivendolo prima della
   conferma, e c'è qualcosa da ispezionare invece di una descrizione.

---

*Verifiche su `261bebc` **RECUPERATO**. I sei hash del seed **RECUPERATO**,
calcolati. L1, L2, L3 **INFERITO** dal testo committato. Esiti **UNKNOWN**.*
