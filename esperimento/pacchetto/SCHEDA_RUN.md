# Scheda run — una per ogni thread, compilata prima di incollare l'item

Senza questa scheda un effetto attribuito alla condizione puo' essere
differenza di configurazione. *(Requisito di Claudio, 2026-10-04.)*

```yaml
run_id:              <condizione>-<nodo>-<item>      # es. condizione_R-n1-07
condizione:          condizione_<lettera>
nodo:                n1 | n2
item_file:           item_NN.md
modello:             <nome come dichiarato dal fornitore>
versione_build:      <stringa esatta, non "ultima">
timestamp_inizio:    <ISO 8601 con fuso>
timestamp_fine:      <ISO 8601 con fuso>
parametri:                                            # solo quelli esposti
  temperatura:       <valore | non_esposta>
  top_p:             <valore | non_esposto>
  ragionamento:      <off | basso | medio | alto | non_esposto>
memoria:             assente | presente_vuota | presente_popolata
strumenti:           [ ]                              # vuoto = nessuno
ricerca_web:         off | on
thread_nuovo:        si | no
interruzioni:        nessuna | <descrizione>
```

## Il vincolo che la scheda da sola non da'

**La configurazione deve essere identica fra le condizioni, non solo
registrata.** Una condizione con memoria attiva e un altro senza non si
confrontano, e nessuna annotazione a posteriori ripara quel confronto.

Obbligatorio per tutti i run: `memoria: assente`, `strumenti: []`,
`ricerca_web: off`, `thread_nuovo: si`. Se uno di questi non e' ottenibile su
una piattaforma, **non si usa quella piattaforma** — non si annota l'eccezione.

`temperatura` va fissata allo stesso valore in tutti i run. Se non e' esposta,
si esegue **tre volte** lo stesso item e si conservano tutte e tre le risposte:
la variabilita' interna al run diventa misurabile invece che ignota.

La scheda serve ad **accorgersi** di una deriva, non a permetterla.
