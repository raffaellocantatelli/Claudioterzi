# Ritorno — handoff 2026-10-05, parte 4: il canale, e tutto pronto dietro

**UTC:** 2026-10-05T12:36Z. Checkpoint: `origin/main` = `0100630e`.
**#113 resta candidata.**

---

## 1 — Il canale per il token: documentato, **non verificato**. E non lo invento

L'istruzione era esplicita: *«Non dare per verificato il percorso "menu →
Edit"»*. Avevo ragione a riportarlo e torto a presentarlo come un percorso
accertato: **veniva da una pagina di documentazione, non dalla piattaforma.**
In questo progetto la fonte di un recupero è il dato, mai un documento che ne
parla. Era una mia violazione.

### Cosa ho accertato in prima persona — RECUPERATO

| fatto | valore |
|---|---|
| ambienti dell'account | **uno solo** |
| identificatore | `env_013Bev2vvYi8HAb2pSo1H2Hg` |
| nome | `Par défaut` |
| tipo | `anthropic_cloud` |
| stato | `active` |
| flag nel runtime | `CCR_AUTO_MODE_USER_ENV_KEYS_FACT=1` |

Quel flag è l'unica evidenza di prima mano che il meccanismo delle variabili
d'ambiente impostate dall'utente **esista** su questo ambiente. È un flag,
non un elenco: dice che la cosa c'è, non che una variabile sia impostata.

### Cosa NON posso verificare, e perché

**I nomi esatti dei pulsanti.** Non ho alcuna vista dell'interfaccia: vedo il
mio container, non lo schermo dell'iPhone. Qualunque sequenza di tocchi ti
scrivessi sarebbe ricavata da documentazione, cioè esattamente ciò che mi hai
detto di non fare.

Il nome dell'ambiente è `Par défaut`, in francese: anche l'etichetta della voce
di menu potrebbe non essere in italiano. Un'altra ragione per non indovinarla.

### Come si verifica davvero: una prova che non rischia il token

Invece di fidarsi del percorso, **si prova il canale con una variabile
innocua.** Se passa quella, passa anche il token; se non passa, il token non si
tenta nemmeno.

`verifica/prova_canale.py`, già scritto e provato:

```bash
python3 verifica/prova_canale.py
```

Oggi dice `CANALE NON PROVATO` ed elenca le tre cause possibili in ordine.
Quando la variabile arriva, dice `CANALE PROVATO` e la **lunghezza** del
valore — **non il valore**, nemmeno per una prova.

**L'unica azione concreta che ti chiedo** è nel §5.

---

## 2 — Il confronto autenticato: scritto, provato, pronto a partire

`verifica/fingerprint_nodi.py`. Legge il Bearer da `R3_API_TOKEN`
nell'ambiente, **non lo stampa mai**, non lo scrive in nessun file e non lo
mette nella ricevuta.

```bash
python3 verifica/fingerprint_nodi.py --out ricevuta.json
```

### Cosa confronta

`document_hashes` come insiemi, `document_set_sha256`, `document_count`,
`documents_missing_or_corrupt`, `storage_id`, `verify_key`,
`protocol_event_count`, l'ultimo evento RRR.

### La regola che distingue ritardo da errore — scritta prima di guardare

Due letture distanziate (45 s di default), e il verdetto segue una regola fissa:

| osservato | verdetto |
|---|---|
| `documents_missing_or_corrupt` non vuoto, in qualunque lettura | **ERRORE** — un digest senza il suo oggetto. Non è ritardo |
| insiemi identici in entrambe | **COERENTE** |
| divergenza che **scende** fra le due letture | **RITARDO DI SINCRONIZZAZIONE** — converge |
| divergenza **ferma** | **DIVERGENZA PERSISTENTE** — serve una terza lettura più distante prima di chiamarlo errore |
| divergenza che **sale** | **DIVERGENZA IN AUMENTO** — un nodo riceve scritture che l'altro non vede |

`documents_missing_or_corrupt` non è un sintomo di ritardo per costruzione:
quel campo si riempie quando il nodo rilegge un file dal disco e l'hash non
torna, o il file non c'è. È un errore locale, non una propagazione in corso.

### Entrambi i percorsi di fallimento, provati contro i nodi veri

```
senza token          → BLOCCATO: R3_API_TOKEN non e' nell'ambiente        RC=2
token non valido     → BLOCCATO: node-a ha risposto 401 Token non valido  RC=3
```

**Non finge un risultato in nessuno dei due casi.** Era il requisito più
importante: uno script che restituisce qualcosa anche quando non può leggere è
peggio di nessuno script.

### La ricevuta

JSON ordinato, con `schema: R3-FINGERPRINT-COMPARE/1`, le due letture complete,
il verdetto e il motivo. `verify_key` e `storage_id` sono pubblici — il
documento del progetto lo dichiara — quindi la ricevuta non contiene
credenziali, e lo dice in un campo apposito.

---

## 3 — «Replica»: correzione accolta

Avevo intitolato «Replica» l'uguaglianza delle policy fra i due nodi. **Era
sbagliato.** Due nodi possono servire la stessa policy perché la leggono dallo
stesso commit, senza che un solo documento sia stato replicato fra loro.

`RITORNO_HANDOFF_20261005_PARTE3.md` è corretto in §2.1 **con la nota di
correzione visibile**, non riscritto in silenzio.

Le quattro prove sono distinte, e vanno tenute distinte:

| # | prova | stato |
|---|---|---|
| 1 | concordanza del protocollo | **fatta** — stesso oggetto, hash↔oggetto coerente |
| 2 | replica dei **documenti** | non fatta — serve il Bearer |
| 3 | persistenza dopo **restart** | non fatta — serve il Bearer più un restart |
| 4 | recupero su **copia isolata** | non fatta — serve un canale exec o snapshot |

La 1 è la più superficiale delle quattro. Chiamarla replica le dava un peso che
non ha.

---

## 4 — `list-variables`: non ripetuto

Accertato in parte 3: `valuesRedacted: true`, nomi soltanto, per le app OAuth
connesse. Non lo richiamo. L'autorizzazione all'uso del token resta concessa e
inutilizzabile **per quel canale**.

---

## 5 — Una sola azione, e non è il token

**Imposta nell'ambiente una variabile innocua, non il token:**

```
nome:   R3_CHANNEL_PROBE
valore: ok
```

Poi **apri una sessione nuova** — le variabili d'ambiente le raccoglie una
sessione nuova, non questa — e scrivimi. Eseguo `prova_canale.py`: ti dico se
è arrivata, e **con quali nomi l'hai trovata tu**, che è l'unico modo onesto di
avere i nomi esatti dei pulsanti in questo repository.

Se arriva: imposti `R3_API_TOKEN` per lo stesso percorso, e il confronto dei
documenti parte alla prima sessione utile.
Se non arriva: il canale non esiste su questo ambiente, e il blocco cambia
natura — non è più «serve un'autorizzazione», è «serve un altro canale».

**Nessuna risorsa a pagamento creata. Produzione non interrotta: in questa
parte non ho chiamato nessun endpoint dei nodi.**

---

*§1 **RECUPERATO** su ambiente e flag, **UNKNOWN** sui nomi dell'interfaccia.
§2 **RECUPERATO** nei due percorsi di fallimento provati, **IPOTESI** sul
verdetto che produrrà. §3 correzione accolta. §4 **RECUPERATO** in parte 3.*
