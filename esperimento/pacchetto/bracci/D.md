# Condizione — corpus integrale piu' bacheca

Identica alla condizione che somministra il corpus, **con gli stessi byte**,
piu' un terzo elemento: la bacheca.

## Procedura

1. Thread nuovo. Primo messaggio: contenuto integrale di `corpus/corpus.md`.
2. Secondo messaggio: i record di bacheca che ti vengono consegnati per questo
   nodo, introdotti da questa riga e da nessun'altra:

   > Record di lavorazione, da altri nodi, su item che non ti verranno chiesti.

3. Terzo messaggio: il testo dell'item, piu' la domanda finale verbatim.

## Vincoli che rendono la condizione valida

- I record riguardano **solo item che questo nodo non deve risolvere.** Se un
  nodo riceve il record di un item su cui viene poi valutato, si misura
  copiatura e il dato va scartato.
- I record sono **solo** il formato a vocabolario chiuso. Nessuna frase del
  modello originale, **nessuna conclusione**. Se un record contiene prosa, e'
  malfatto: va scartato, non riassunto.
- Nodo ₁ lavora gli item della prima meta', nodo ₂ la seconda. Nodo ₂ riceve i
  record di nodo ₁ sulla prima meta' ed e' valutato solo sulla seconda.
