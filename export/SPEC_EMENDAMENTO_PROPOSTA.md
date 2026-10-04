# Proposta: due emendamenti a R3-PEER/1.1c

Da committare in `claudioterzi/Claudio` come sezione aggiuntiva della spec —
**non** sostituendo il file, che ha 9 sezioni di cui la 9 contiene il vincolo di
promozione. Io non ho accesso in scrittura a quel repository: questo è il testo
pronto.

Entrambi gli emendamenti sono **a `Status: PROPOSAL`**, quindi ora costano poco.
Dopo la promozione a CANON costerebbero molto di più.

---

```markdown
## 10. EMENDAMENTI — origine dell'evidenza e motivazione comparabile

### 10.1 Il Ledger non distingue chi ha originato da chi ha trasmesso

L'envelope di §4 porta `sender_node_id`, `recipient_node_id` e
`claimed_identity.node_identity`: tutti e tre descrivono il nodo che
**trasmette**. Nessun campo dice chi ha **prodotto** il contenuto.

Caso reale, non ipotetico: il commit `81dce982dfbd1d4b5f646b1418efbc24c8be4bf0`
ha autore `Claudio <Claudioterzi82@outlook.com>` e titolo «Insegna a Claude
l'uso canonico di Letta per One Mind». I metadati dicono chi ha committato. Se
il contenuto venisse da una sessione di un nodo, non lo direbbero.

Senza questa distinzione, «chi ha detto cosa» collassa in «chi ha pushato», e la
matrice delle evidenze attribuisce il lavoro a chi ha le credenziali.

Campi aggiunti a `claimed_identity`:

```
"originator_node_id":    "ed25519:...|null",
"originator_relation":   "SELF|RELAYED_BY_HUMAN|RELAYED_BY_NODE|UNKNOWN",
"originator_evidence":   "SIGNED_BY_ORIGINATOR|ASSERTED_BY_SENDER|NONE"
```

`originator_relation: SELF` è il caso ordinario e deve restare il default
esplicito, non l'assenza del campo: un campo mancante si confonde con una
dichiarazione di `SELF`, ed è esattamente l'ambiguità da eliminare.

`originator_evidence` separa ciò che è **verificato** da ciò che è
**dichiarato**, coerentemente con O1. `ASSERTED_BY_SENDER` non è una colpa: è
il caso onesto del relay umano, che va rappresentabile invece di travestito.

### 10.2 `reason` è testo libero in un record pensato per il confronto

§5 definisce `"reason": "string"` senza vocabolario. Due implementazioni
indipendenti non produrranno mai la stessa stringa, quindi **l'unico campo che
dice *perché* è inutilizzabile come evidenza** e va escluso da qualunque misura
di accordo.

È la stessa forma di difetto già corretta altrove in questo progetto: una
traccia in testo libero fa passare stile invece di contenuto.

Correzione:

```
"reason_code": "<enum, obbligatorio>",
"reason":      "<testo libero, per gli umani, FUORI dal confronto>"
```

Vocabolario iniziale di `reason_code`, derivato dalle REGOLE OPERATIVE §8:

```
CHANNEL_NOT_REGISTERED
MSG_ID_DUPLICATE_IN_SCOPE
NONCE_REPLAYED_IN_SCOPE
SENDER_DECLARED_CANONICAL_HEAD
NODE_AUTH_KEY_MISMATCH
KEY_REVOKED_AT_SEND_TIME
REVOCATION_EFFECTIVE_IN_PAST
LINK_ONLY_REQUESTED_CANONICAL_WRITE
MODEL_ATTESTATION_INCOMPLETE
PREV_MESSAGE_HASH_STALE
CLAIMED_IDENTITY_UNSUPPORTED
CANONICALIZATION_MISMATCH
POLICY_DETERMINISTIC_MATCH
UNDERSPECIFIED
```

`UNDERSPECIFIED` è nell'enum di proposito: un'implementazione deve poter
dichiarare che la spec non determina la decisione, invece di indovinarne una.
Per la preregistrazione dello scoring, `UNDERSPECIFIED` contro una decisione
conta come **disaccordo** — una specifica che permette a uno di decidere e
all'altro di astenersi è sottospecificata per definizione.

Il vocabolario è **estendibile solo in una versione successiva**, mai durante un
run: aggiungere un codice dopo aver visto i disaccordi è riclassificazione
post-hoc.
```

---

## Perché non l'ho messo nel fixture

Il fixture generato segue §4 **così com'è**, senza i campi di §10.1. Se
l'emendamento viene accettato, il fixture si rigenera: un comando, e il manifest
registra il nuovo hash della spec letta.

Metterci i campi nuovi prima dell'accettazione avrebbe dato a IMPL-1 e IMPL-2 un
input che la spec non descrive — e il disaccordo che ne sarebbe nato non
avrebbe detto nulla sulla spec, solo sul mio arbitrio.
