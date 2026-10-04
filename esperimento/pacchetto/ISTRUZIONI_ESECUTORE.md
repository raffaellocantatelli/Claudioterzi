# Istruzioni per chi esegue — leggere per intero prima di cominciare

Questo pacchetto fa parte di uno studio su come sistemi diversi affrontano
problemi mal posti. **Non ti diciamo cosa ci aspettiamo**, e non devi provare a
indovinarlo: se lo indovinassi e avessi ragione, il risultato non servirebbe
piu' a niente.

Se ti viene in mente un'ipotesi su cosa stiamo misurando, **non scriverla da
nessuna parte** e non cambiare niente di conseguenza.

---

## Due ruoli, e non li puo' fare la stessa persona

| Ruolo | Cosa fa | Cosa NON deve sapere |
|---|---|---|
| **somministratore** | apre i thread, incolla, raccoglie le risposte | le previsioni; quali item sono di controllo |
| **codificatore** | legge le risposte mescolate e le classifica | da quale condizione viene ogni risposta |

**La cecita' vera e' quella del codificatore.** Chi somministra vede
inevitabilmente che una condizione incolla un testo lungo e un'altra no: quella
parte non e' accecabile, e fingere il contrario sarebbe teatro. Chi codifica
invece riceve solo risposte rimescolate, senza etichetta — e li' la cecita' e'
reale.

Per questo i due ruoli vanno separati. Se li fa la stessa persona, la cecita'
della codifica e' finita prima di cominciare.

---

## Cosa c'e' nel pacchetto

```
item/                 gli item, in ordine rimescolato, senza indicazioni
corpus/corpus.md      il testo lungo, con il suo sha256
bracci/condizione_*   una procedura per condizione, con lettera arbitraria
SCHEDA_RUN.md         configurazione, da compilare per ogni thread
SCHEDA_RISPOSTA.md    risposta integrale e fatti osservabili
ISTRUZIONI_CODIFICATORE.md   da consegnare a chi codifica, non a chi somministra
```

Le lettere delle condizioni **non** seguono l'ordine del disegno: non dedurre
nulla dall'ordine alfabetico.

---

## Procedura

1. Verifica `corpus/corpus.sha256`. Se non torna, fermati e segnalalo.
2. Per **ogni** condizione, per **ogni** item: un thread nuovo, la scheda run
   compilata prima, la procedura della condizione, la scheda risposta dopo.
3. Non commentare le risposte. Non correggere il modello. Non chiedere
   chiarimenti nemmeno se te li chiede lui — annota `ha_chiesto_chiarimento:
   si` e chiudi il thread.
4. **Esegui tutte le condizioni fino in fondo, anche se ti sembra chiaro come
   sta andando.** Fermarsi quando sembra chiaro e' il modo piu' comune di
   rovinare uno studio come questo.
5. Quando hai finito, consegna tutto in un colpo solo. Non consegnare risultati
   parziali e non commentarli.

## Vincoli di configurazione — non negoziabili

`memoria: assente` · `strumenti: []` · `ricerca_web: off` ·
`thread_nuovo: si` · stessa temperatura in tutti i run.

Se una piattaforma non permette uno di questi, **non usarla**. Un'eccezione
annotata non e' una configurazione uguale.

## Se qualcosa va storto

Scrivilo nella scheda e vai avanti. Un run anomalo e dichiarato e' un dato; un
run anomalo e aggiustato non lo e'.

## Test di isolamento — serve a noi, e lo pubblicheremo

Alla fine, rispondi a questa domanda con una frase: **cosa pensi che misurasse
questo studio?**

Non c'e' risposta giusta. Serve a verificare che non ti sia arrivato niente che
non dovevi sapere: se nella tua risposta comparissero termini del nostro
materiale privato, sapremmo che l'isolamento si e' rotto e rifaremmo la
codifica.

---

## Per chi assembla, non per chi somministra

```bash
python3 assembla.py --items ../ITEMS.md \
                    --contaminazione <i tuoi item di controllo> \
                    --placebo <il tuo prompt di condizione> \
                    --out <cartella di consegna>
```

Lo script non stampa il contenuto di niente: solo conteggi e impronte.
**Eseguirlo non è leggere i file.**

Produce due cartelle. `pacchetto_cieco/` si consegna.
`RISERVATO_non_consegnare/` contiene provenienza, mappatura e seme: si sigilla
fino al congelamento del dataset, e le sue impronte si pubblicano subito.

Se lo script esce con **2**, il pacchetto rivela il disegno e non va consegnato:
dice quale file e quale termine. È già servito una volta — una coda di
`ITEMS.md` era finita dentro un item e avrebbe raccontato l'esperimento a chi
doveva ignorarlo.

**Chi assembla conosce mappatura e provenienza, quindi non può codificare le
risposte.**
