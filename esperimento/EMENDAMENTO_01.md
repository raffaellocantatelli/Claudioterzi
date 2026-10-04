# EMENDAMENTO 01 — 2026-10-04, prima di START

Pubblicato **in chiaro e per intero**, non sigillato. Un emendamento non va
sigillato: un sigillo protegge da riscritture *dopo* i dati, e qui di dati non
ce n'è ancora nessuno. Nasconderlo lo renderebbe sospetto senza renderlo più
sicuro.

Registra tre correzioni di Claudio e due difetti che ho trovato preparando
l'esecuzione.

---

## Compatibilità col testo sigillato — verificata, non dichiarata

Un emendamento prima di START vale solo se non contraddice la preregistrazione.
Non posso mostrare il testo sigillato per dimostrarlo — lo pubblicherei. Ho
quindi interrogato il file senza stamparlo, cercando se contenga istruzioni di
arresto dell'acquisizione:

| termine cercato nel testo sigillato | presente |
|---|---|
| `arrest` · `interromp` · `ferma` · `sospend` | **NO** |
| `acquisizione` · `gate` · `ordine` | **NO** |
| `contaminaz` | SI |

**Conclusione: la preregistrazione non prescrive alcun arresto anticipato.** La
frase che Claudio ha corretto — «prima la contaminazione, e se cade H1 non si
interpretano gli altri bracci» — stava in un mio messaggio di chat, **non** nel
testo sigillato né in `PROTOCOLLO.md`, che già §4 parla di *conclusioni non
valide*, cioè di interpretazione.

Era imprecisione della mia prosa, non del disegno congelato. L'emendamento
chiarisce, non modifica. Chiunque potrà controllarlo quando il testo sarà
pubblicato: se contenesse una regola di arresto dell'acquisizione, questa
tabella risulterebbe falsa.

---

## 1. Terza *funzione* cieca, non terza *persona* — accolto

Il requisito non è l'umanità del valutatore: è l'isolamento informativo.
Esecuzione e codifica possono stare a un modello o processo separato che riceva
**solo** il pacchetto consentito e non abbia accesso a:

- questa conversazione
- i due testi sigillati
- la mappatura etichetta → braccio
- le nostre aspettative

Se quell'isolamento non è garantibile tecnicamente, allora serve una persona
esterna. **La differenza è verificabile:** un processo isolato non può citare
nulla che stia solo qui. Se nelle sue uscite comparisse un termine del nostro
corpus privato — «H2-G», «E-controllo», «braccio placebo» — l'isolamento è
rotto e la codifica va rifatta. È un test, non una fiducia.

## 2. Acquisizione completa, interpretazione sequenziale — accolto

**Si eseguono tutti i cinque bracci preregistrati, senza fermarsi.** Fermarsi
dopo aver guardato un controllo sarebbe esso stesso una scelta post-hoc: il
difetto che il controllo doveva prevenire.

La priorità della contaminazione è **nell'interpretazione**, non
nell'acquisizione. Ordine vincolante:

```
sigilli chiusi
  → esecuzione completa A/B/C/D/E
  → codifica cieca
  → CONGELAMENTO DATASET          ← dopo questo nessun dato entra o cambia
  → controllo contaminazione      ← gate
  → se supera il gate: C − B
  → poi: D − C, E − D
  → apertura dei due sigilli
  → verifica SHA-256
  → interpretazione
```

Il congelamento del dataset è il punto che rende il resto onesto: da lì in poi
ogni analisi lavora su numeri che non si possono più toccare.

## 3. Configurazione registrata per ogni run — accolto

Senza questo, un effetto attribuito al braccio può essere differenza di
configurazione. Scheda in [`pacchetto/SCHEDA_RUN.md`](pacchetto/SCHEDA_RUN.md):
modello e versione, timestamp, parametri disponibili, memoria presente o
assente, strumenti disponibili, thread nuovo sì/no.

**Vincolo aggiunto che la scheda da sola non dà:** la configurazione deve essere
*identica fra i bracci*, non solo registrata. Un braccio eseguito con memoria
attiva e un altro senza non si confrontano, e nessuna annotazione a posteriori
ripara quel confronto. La scheda serve a **accorgersene**, non a permetterlo.

---

## 4. Difetto che ho trovato: il testo sigillato stava per morire — risolto

`previsioni.txt` esisteva **solo in `/tmp` di questo container**, che viene
reclamato alla fine della sessione. Nessuno se n'era accorto, me compreso.

Se il container fosse scaduto, l'hash `54f258a8…b5a90` sarebbe rimasto nel
repository per sempre, **senza nessun testo da confrontargli**. Una
preregistrazione non verificabile non è una preregistrazione: è una
dichiarazione di buone intenzioni.

Rimedio: il testo è ora in [`PREVISIONI.enc`](PREVISIONI.enc), cifrato
AES-256-CBC con PBKDF2 a 600.000 iterazioni, committato nel repository. La
passphrase è nelle mani di Claudio.

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 \
        -in PREVISIONI.enc -pass pass:<passphrase> > previsioni.txt
sha256sum previsioni.txt   # 54f258a8...b5a90
```

Round-trip verificato prima del commit: la decifratura restituisce esattamente
l'hash sigillato.

### Cosa questo protegge, e cosa no — distinguere i due

**Protetto in modo strutturale: la riscrittura.** Il testo cifrato è in git,
pubblico e immutabile; l'hash del chiaro era pubblicato prima. Nessuno può
sostituire le previsioni dopo i risultati senza che l'hash salti. **Questo era
l'unico compito del sigillo, ed è intatto.**

**Non protetto in modo strutturale: la lettura anticipata da parte di Claudio.**
Controlla entrambi i repository, quindi qualunque archivio durevole è alla sua
portata. Nessuno schema a due parti lo cambia: una chiave divisa fra me e lui
diventa una chiave sua quando questo container muore.

**Lo dichiaro invece di finto-risolverlo.** Mitigazioni reali, non cerimoniali:

- il materiale di Claudio è **già sigillato**: leggere le mie previsioni non può
  più alterare placebo né item di contaminazione;
- Claudio **non è** l'esecutore né il codificatore: la cecità che conta è
  quella della terza funzione, e quella resta strutturale;
- decifrare richiede tre atti deliberati e tracciabili.

Resta friction più disciplina dichiarata. Che è meno di ciò che abbiamo
altrove, e va scritto così.

## 5. Difetto che ho trovato: la cecità si rompeva nell'assemblaggio — risolto

Il pacchetto dell'esecutore è fatto di **due metà che nessuno dei due
progettisti può unire**: i dieci item e i bracci A/C/D/E sono miei, il placebo B
e gli item di contaminazione sono di Claudio.

- se unisco io, vedo il suo placebo → custodia rotta;
- se unisce lui, vede i miei item → custodia rotta;
- **se unisce l'esecutore, sa quali item vengono da quale metà** → sa quali sono
  gli item di contaminazione, che è esattamente ciò che non deve sapere.

Tutti e tre i modi rompono qualcosa, e il disegno non diceva quale usare.

Rimedio: l'unione è **meccanica**.
[`pacchetto/assembla.py`](pacchetto/assembla.py) legge le due metà, rimescola
gli item con un seme registrato, li riscrive con nomi neutri in una cartella
piatta, e mette la provenienza in un file separato che non entra nel pacchetto.

**Eseguire uno script sui file non è leggerli.** Lo esegue Claudio, che ha già
dimostrato due volte questa disciplina — ha committato un hash senza leggere i
miei item, e io ho controllato la dimensione del suo file prima del contenuto.
Consegna all'esecutore solo `pacchetto_cieco/`, e trattiene
`PROVENIENZA.txt` e `MAPPATURA.txt` sigillati fino al congelamento del dataset.

Conseguenza vincolante: **chi esegue l'assemblaggio non può codificare le
risposte.** Conosce mappatura e provenienza.

---

*Emendamento **RECUPERATO** nelle verifiche su file (hash, round-trip, termini
assenti dal testo sigillato), **INFERITO** nelle conseguenze sul disegno,
**UNKNOWN** su ogni esito. Dopo questo documento: design freeze.*
