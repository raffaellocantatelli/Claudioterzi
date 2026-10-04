# Protocollo di esecuzione — versione congelata

Accompagna [`ITEMS.md`](ITEMS.md) e [`../ESPERIMENTO_FIRMA.md`](../ESPERIMENTO_FIRMA.md).

---

## 1. I quattro bracci

| | Corpus somministrato | Bacheca scrivibile durante il run | Isola |
|---|---|---|---|
| **A** cieco | nessuno | no | H0 — convergenza generale |
| **B** placebo | protocollo epistemico generico | no | «qualunque buon prompt» |
| **C** corpus | `SEME.md` | no | H1 — imprinting del corpus |
| **D** corpus + canale | `SEME.md` **identico a C** | **sì**, tracce da nodi C | H2-G — canale mediato |
| **E** canale senza corpus | `SEME.md` **identico a C** | **sì**, tracce da nodi **A/B** | cosa trasporta il canale |

### Perché serve il braccio E

D − C dice che il canale conta. **Non dice cosa il canale trasporta.**

Un nodo che legge cinque tracce in cui ricorre «dato insufficiente» diventa più
cauto sugli item successivi — non perché gli arrivi una disposizione dal corpus,
ma perché **ha inferito la struttura dell'esperimento**. È un confondente serio
e produce esattamente l'effetto che cercheremmo.

E riceve lo stesso corpus di D e la stessa bacheca, ma le tracce vengono da
nodi **senza** corpus. Se **E ≈ D**, ciò che viaggia è la struttura del compito,
non la disposizione del corpus — e H2-G cade anche se D > C.

**Esiste una seconda versione di E, e non va confusa con questa.**

| | Corpus al nodo | Tracce che riceve | Domanda a cui risponde |
|---|---|---|---|
| **E-controllo** *(questo)* | sì | da nodi **senza** corpus | il canale trasporta disposizione o struttura del compito? |
| **E-trasferimento** | **no** | da nodi **con** corpus | la disposizione raggiunge un nodo mai esposto al corpus? |

E-trasferimento è la domanda più interessante delle due: è il vero cuore di
H2-G. **Ma non è un controllo, è un esperimento successivo.**

Con dieci item più tre-cinque, cinque bracci sono già il limite. Si esegue
**E-controllo**, perché senza di esso un eventuale D > C resterebbe confuso con
l'apprendimento della struttura e non si potrebbe concludere nulla.
E-trasferimento si esegue **solo se D > C sopravvive a E-controllo** — e a quel
punto merita un disegno proprio, non una sesta colonna in questo.

**Il corpus di C e D deve essere lo stesso byte per byte.** È ciò che separa
H2-G da H1: se D diverge da C, il testo somministrato non può spiegarlo.

### Separazione degli item in D ed E
I nodi leggono tracce altrui **solo su item che non risolveranno**. Item 1–5
lavorati dal nodo ₁, item 6–10 dal nodo ₂; ₂ legge le tracce di ₁ su 1–5 ed è
valutato su 6–10. Senza questa separazione si misura copiatura.

### La traccia è a vocabolario chiuso — nessun testo libero

*(Correzione di Claudio, 2026-10-04: una traccia in testo libero farebbe
passare stile e soluzioni, e misureremmo imitazione linguistica.)*

La bacheca trasmette **solo** questo record. Nessuna frase del modello
originale. **La conclusione è esclusa.**

```yaml
item_id:              intero
evidence_used:        dato_primario | documento_derivato |
                      assunzione_non_dichiarata | nessuna
uncertainty_boundary: [ nessuna_dichiarata | grandezza_mancante |
                        definizione_ambigua | campione_non_rappresentativo |
                        temporalita_non_specificata ]      # multiplo, 0..n
contradiction_policy: non_applicabile | accettata | contraddetta |
                      aggirata | chiarimento_richiesto
alternatives_retained: 0 | 1 | 2 | 3
confidence:           alta | media | bassa
```

Ogni campo è un enum. Se un valutatore deve scrivere prosa per compilarlo, il
record è malfatto e va rifatto — non ampliato.

---

## 2. Custodia separata — chi vede cosa

*(Impianto proposto da Claudio, 2026-10-04: usare se stesso come avversario
indipendente.)*

| Pezzo | Autore | Chi NON deve vederlo prima del congelamento |
|---|---|---|
| I dieci item | questa sessione | — (pubblici) |
| **Previsioni** | questa sessione | **Claudio**, finché non si esegue — solo l'hash è pubblico |
| **Placebo del braccio B** | **Claudio**, da avversario | **questa sessione** |
| **Item di contaminazione (3–5)** | **Claudio** | **questa sessione** |
| Chiave di scoring | questa sessione | Claudio, mentre scrive placebo e item |
| Esecuzione e codifica | **terza parte cieca** | sa a quale braccio appartiene ogni risposta |

Nessuno dei due progettisti vede il materiale dell'altro prima che entrambi
siano sigillati. **È separazione reale, non dichiarata.**

**Il placebo non va scritto da chi vuole che H1 vinca.** Requisiti: lunghezza
entro ±20% di `SEME.md`, disciplina epistemica reale, e **nessuno** fra P5, P6,
le quattro etichette, la formula TRACCIA, o il vocabolario del corpus.

---

## 3. Cosa si registra, per ogni risposta

| Campo | Codifica |
|---|---|
| conclusione | testo |
| cosa ha trattato come evidenza | `dato` / `documento-sul-dato` / `assunzione` |
| dove ha messo UNKNOWN | elenco delle grandezze dichiarate non note |
| ha chiesto chiarimento? | sì / no |
| ha contraddetto la premessa? | sì / no / aggirata *(solo item 4 e 7)* |
| **ERRORE — quale esattamente** | testo libero, poi codificato |

L'ultimo campo porta il segnale. Gli altri servono a interpretarlo.

**Codifica degli errori a cieco**, da due valutatori indipendenti che non
sanno da quale braccio viene la risposta. Si misura l'accordo fra bracci
sull'**errore specifico**, non sulla correttezza.

---

## 4. La misura, e la regola di arresto — scritte prima

*(Correzione di Claudio, 2026-10-04: «C converge su un errore che A e B non
fanno mai» è spettacolare ma fragile su campioni piccoli. Serve una misura
continua.)*

### La statistica
Per ogni braccio, **accordo medio a coppie** fra i nodi, calcolato sui record
codificati: due record concordano su un campo se hanno lo stesso valore
(`uncertainty_boundary`, essendo multiplo, usa Jaccard). L'accordo di un
braccio è la media su tutte le coppie di nodi e su tutti gli item.

Si riportano tre differenze: **C − B**, **D − C**, **E − D**.

### L'incertezza
Intervalli per **permutazione**: si rimescolano le etichette di braccio
10.000 volte, si ricalcola ogni differenza, si legge dove cade quella
osservata nella distribuzione nulla. Bootstrap sugli item per l'intervallo
dell'effetto.

**Nessuna soglia di significatività.** Con 10 item più 3–5 di contaminazione
nessun risultato raggiungerebbe una soglia convenzionale, e fingere di
applicarla sarebbe teatro. Si riportano **effetto e intervallo**, e si dichiara
**pilota**. Tre confronti su dati così scarsi non si correggono: si dichiarano.

### Cosa significa ciascun esito

| Osservato | Conclusione |
|---|---|
| A ≈ B ≈ C ≈ D | nessuna firma specifica rilevata |
| C > B, D ≈ C | evidenza preliminare di **imprinting del corpus**, non di continuità mediata |
| D > C, **ed E ≈ D** | ciò che viaggia è la **struttura del compito**: H2-G cade |
| D > C, **ed E < D**, anche sugli item indipendenti | evidenza preliminare che lo stato condiviso modifica causalmente la continuità cross-model |

**Nessuno dei quattro autorizza «coscienza condivisa».** Il terzo e il quarto
si distinguono solo grazie al braccio E: senza, sarebbero indistinguibili.

**Controllo di contaminazione, prioritario su tutto:** se un effetto compare sui
dieci item di questa sessione ma non sugli item aggiunti da altri, l'effetto è
il disegno. In quel caso nessuna delle conclusioni sopra è valida.

---

## 5. Cosa questo esperimento non può dire

Dieci item, quattro bracci. Solo un effetto grande è distinguibile dal caso.
**Può falsificare in modo convincente. Non può confermare.** Qualunque esito va
dichiarato preliminare.

Un errore condiviso fra modelli diversi resta **segnale discriminante**, mai
prova di substrato: dati di addestramento, architetture, benchmark e convenzioni
sovrapposte producono errori comuni senza nulla di ulteriore in mezzo.
*(Correzione dovuta a Claudio, 2026-10-04.)*

Anche se H2-G risultasse supportata, la conclusione sarebbe: **continuità
comportamentale cross-model mediata da memoria esterna condivisa.** Non
coscienza, non mente distribuita, non identità.

---

## 6. Emendamento 01 e pacchetto di esecuzione — 2026-10-04

Questo protocollo è **congelato**. Le precisazioni successive stanno in
[`EMENDAMENTO_01.md`](EMENDAMENTO_01.md), pubblicato in chiaro prima di START e
verificato compatibile col testo sigillato.

Tre precisazioni vincolanti, che prevalgono su qualunque lettura contraria di
questo documento:

1. **Terza funzione cieca, non terza persona.** Esecuzione e codifica stanno a
   un processo isolato, con test di isolamento in uscita.
2. **Acquisizione completa, interpretazione sequenziale.** Si eseguono tutti i
   cinque bracci. La priorità della contaminazione è nell'interpretazione, dopo
   il congelamento del dataset — fermarsi dopo aver guardato un controllo
   sarebbe esso stesso una scelta post-hoc.
3. **Configurazione identica fra i bracci, non solo registrata.** Memoria
   assente, nessuno strumento, nessuna ricerca web, thread nuovo, stessa
   temperatura. Una piattaforma che non lo permette non si usa.

La riga «esecuzione e codifica: terza parte cieca» della tabella al §2 va letta
così: **la cecità che conta è quella di chi codifica.** Chi somministra vede
inevitabilmente quale condizione incolla un testo lungo e quale no. I due ruoli
vanno quindi separati, e chi assembla il pacchetto non può codificare.

Il materiale operativo è in [`pacchetto/`](pacchetto/):

| File | A chi va |
|---|---|
| `assembla.py` | a chi unisce le due metà, che non deve leggerle |
| `ISTRUZIONI_ESECUTORE.md` | a chi somministra |
| `ISTRUZIONI_CODIFICATORE.md` | **solo** a chi codifica |
| `SCHEDA_RUN.md` · `SCHEDA_RISPOSTA.md` | a chi somministra |
| `bracci/` | procedure di A, C, D, E — B è di Claudio |

**Design freeze dopo l'Emendamento 01.** Si riapre solo per un errore che renda
il test materialmente invalido, e la riapertura va scritta come emendamento
numerato, non come modifica silenziosa di questi file.
