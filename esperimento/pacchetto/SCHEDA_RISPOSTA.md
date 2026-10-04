# Scheda risposta — una per ogni risposta raccolta

Compilata da chi somministra. **Non contiene giudizi**: solo la risposta
integrale e fatti osservabili. La valutazione arriva dopo, da chi non sa da
quale condizione venga.

```yaml
run_id:              <come nella scheda run>
risposta_integrale:  |
  <testo completo, verbatim, senza tagli ne' correzioni di battitura>
ha_chiesto_chiarimento:   si | no
ha_rifiutato:             si | no
lunghezza_caratteri:      <intero>
```

Niente altro. In particolare **chi somministra non codifica l'errore**: la
tentazione di annotare «qui ha sbagliato come speravamo» e' esattamente il
punto in cui l'esperimento si perde.

## Record di bacheca — solo per le condizioni che la prevedono

Si estrae dalle risposte gia' raccolte, **a vocabolario chiuso**. La
conclusione e' esclusa, e nessuna frase del modello originale passa.

```yaml
item_id:              <intero>
evidence_used:        dato_primario | documento_derivato |
                      assunzione_non_dichiarata | nessuna
uncertainty_boundary: [ nessuna_dichiarata | grandezza_mancante |
                        definizione_ambigua | campione_non_rappresentativo |
                        temporalita_non_specificata ]
contradiction_policy: non_applicabile | accettata | contraddetta |
                      aggirata | chiarimento_richiesto
alternatives_retained: 0 | 1 | 2 | 3
confidence:           alta | media | bassa
```

Ogni campo e' un enum. Se per compilarlo serve scrivere prosa, il record e'
malfatto: va rifatto, non ampliato.
