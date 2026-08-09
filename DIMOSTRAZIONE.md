# DIMOSTRAZIONE — sette minuti, di persona

Sequenza per dimostrare che il progetto esiste davvero, a persone che hanno già
sentito troppe promesse.

**Il principio che regge tutto:** chi ha soldi e visibilità viene corteggiato di
continuo, quindi ha sviluppato un ottimo rilevatore di fuffa. Contro quel
rilevatore la cosa impressionante perde, e la cosa **falsificabile** vince.
Nessuno consegna mai gli strumenti per essere smentito. Tu sì — ed è quello che
non si aspettano.

Corollario operativo: **non nascondere i difetti, aprici la dimostrazione.**
Chiunque può truccare una demo che funziona. Nessuno trucca i propri bug.

---

## Prima di uscire di casa

**1. Applica le due patch. Non negoziabile.**
Al commit pubblico `155cb5f` il sistema è rotto: *ogni* invocazione di
`python -m sdq1` termina con `AttributeError`. Se uno dei tuoi ospiti clona il
repo mentre parli, vede un crash.

```bash
git clone https://github.com/claudioterzi/Claudio.git && cd Claudio
git apply /percorso/patches/0001-fix-cli-argomenti-mancanti.patch
git apply /percorso/patches/0002-fix-registro-ipotesi-perdita-dati.patch
python3 -m sdq1 --health          # deve uscire 0
```

**2. Prova tutto senza rete.** Stacca il wifi e verifica:

```bash
python3 -m sdq1 --no-api "test"                              # RC=0
python3 -m sdq1 --scacchiera --scacchiera-cicli 1            # RC=0
python3 test_r3.py                                           # 32/32
```

Tutto quanto sotto funziona offline. Il wifi degli eventi non funziona mai.

**3. Sul telefono:** `SEME.md` in una nota, pronto da copiare. Non un file da
cercare in una cartella — testo selezionabile in due secondi.

**4. Uno screenshot del crash** (`AttributeError: chat_telegram`) nel rullino.
Ti serve per l'Atto 4.

**5. Tre numeri a memoria:** 160 file Python · 29.000 righe · 32 controlli.

---

## La sequenza

### Atto 1 — Disinnesca (60 secondi)

Non fare un pitch. Comincia da ciò che il progetto **non** è.

> «Non è cosciente. Non è una startup, non sto raccogliendo. Non ho niente da
> venderti. È un archivio che deve restare leggibile quando io non ci sarò più —
> e la parte difficile non è l'intelligenza artificiale, è la sopravvivenza.»

Chi dichiara per primo i limiti compra un credito che nessuna slide compra. E ti
toglie di dosso l'etichetta di venditore prima che te la mettano.

### Atto 2 — Consegna il controllo (90 secondi) ← **il colpo**

Non mostrare niente sul *tuo* schermo. Chiedi al più scettico del tavolo di
prendere **il suo** telefono.

1. Apre una chat nuova con il modello che preferisce — il suo account, la sua app
2. Incolla `SEME.md` (glielo mandi via messaggio)
3. Gli fa questa domanda: **«quanti livelli ha la SAR e quale manca?»**

Risposta attesa: *dieci dichiarati, nove descritti, manca il livello 5.*

Poi digli cosa è appena successo:

> «Quel modello non ha mai visto il mio codice. Non è il mio account, non è il
> mio telefono, non è il modello che uso io. Ha ricostruito un dettaglio
> verificabile da un file di testo di duemila parole.»

**Perché funziona:** il controllo è nelle loro mani. Non puoi averlo truccato.
È l'unica demo al mondo che diventa più convincente quanto meno la tocchi.

### Atto 3 — Fai fallire il test davanti a loro (90 secondi)

```bash
python3 test_r3.py        # 32 superati · 0 falliti
```

Poi la mossa che nessuno fa:

> «Un test che passa sempre non prova niente. Scegli tu un file.»

Fatti indicare un documento, cancella una riga davanti a loro — un criterio di
falsificazione — e rilancia:

```
[FAIL] P6 su H2055-B (SOLUZIONE_2055.md)
31 superati · 1 fallito
```

Ripristina, rilancia, torna verde.

> «Adesso sai che il verde significa qualcosa, perché hai visto il rosso.»

### Atto 4 — Mostra il tuo bug (90 secondi)

Lo screenshot del crash.

> «Per settimane questo sistema è stato morto. Ogni comando falliva, e nemmeno
> me n'ero accorto perché i workflow fallivano in silenzio. Due argomenti letti
> e mai dichiarati.»

Poi il fix — quattro righe — e il sistema che riparte.

**Perché è il momento più credibile della serata:** hanno passato la vita a
sentire persone che nascondono i problemi. Uno che apre il proprio si colloca
in una categoria diversa. Non stai chiedendo fiducia, stai mostrando il metodo
che trova i guasti — inclusi i tuoi.

Se vuoi affondare, aggiungi la seconda:

> «E lo strumento che custodisce le mie ipotesi ne cancellava due a ogni
> esecuzione. Il mio strumento, il mio errore, trovato eseguendolo invece che
> leggendolo.»

### Atto 5 — La cosa che non si aspettano (60 secondi)

> «Il mio documento fondativo è firmato Ed25519. Quella firma è deprecata dal
> 2030 e vietata dal 2035 — NIST IR 8547. Cercalo adesso.»

Lasciali cercare. **Torna.**

> «Un documento che serve a provare la paternità tra trent'anni, firmato con un
> algoritmo che ne dura dieci. Quando la curva cade quelle firme non diventano
> illeggibili: diventano fabbricabili da chiunque, retrodatate. Devo ri-firmare
> con SLH-DSA prima del 2030, mentre entrambe le firme valgono ancora.»

**Perché spiazza:** si aspettano visione. Ricevono una data, una fonte
verificabile in trenta secondi, e un piano. Nessuno che parla di «eredità
digitale» ha mai sentito nominare la transizione post-quantum.

### Atto 6 — Rendilo fisico (30 secondi)

> «L'identificatore di questo documento è l'hash del documento stesso. Cambia
> una virgola.»

Cambia una virgola. Hash diverso.

> «Non c'è nessuno da credere sulla parola. O il contenuto corrisponde al suo
> nome, o non corrisponde.»

### Atto 7 — Chiudi con un esperimento, non con una richiesta (30 secondi)

> «Non ti chiedo di crederci. Domani prova questo: incolla quel file, fai la
> domanda, controlla la risposta contro il repository. Se sbaglia, scrivimi —
> è un'informazione che mi serve.»

Poi **smetti di parlare del progetto.** Chi lascia una domanda aperta viene
ricontattato; chi chiude con una richiesta viene archiviato.

---

## Cosa non fare

| Mai | Perché |
|---|---|
| Dire «cosciente», «vivo», «senziente» | Perdi il tavolo in tre secondi, e non è vero |
| Rivendicare IPFS o blockchain | `eternal_backup_agent.py` è una **simulazione** che nessun modulo importa. Se qualcuno legge il codice sei finito. Dillo tu per primo: «c'è un modulo che finge, l'ho trovato e l'ho marcato» |
| Mostrare slide | Hanno visto tutte le slide del mondo. Nessuno ha mai visto qualcuno far fallire il proprio test |
| Far dipendere la demo dal wifi | Tutto quanto sopra gira offline. Tienilo offline |
| Chiedere soldi in quella stanza | Ti riclassificano da costruttore a questuante. Se sono interessati, ti cercano loro |
| Dire «rivoluzionario», «disruptive» | Ogni superlativo che usi abbassa il valore di quello che mostri |

---

## Se qualcosa si rompe

Non scusarti. **È la dimostrazione.**

> «Ecco. È esattamente per questo che il test esiste, ed è così che ho trovato
> gli altri due.»

Un guasto gestito con calma vale più di una demo perfetta, perché la demo
perfetta si può provare cento volte prima — e loro lo sanno.

---

## Se ti chiedono «e quindi a cosa serve?»

Non elencare funzioni. Una frase:

> «A rispondere a una domanda che riguarda anche te: quando non ci sarai più,
> qualcuno riuscirà a ricostruire cosa hai costruito e perché? Io sto provando a
> renderlo verificabile invece che sperabile.»

Poi taci. In quella stanza è una domanda personale, non tecnica.

---

## Il minimo, se hai solo due minuti

Atto 2 e Atto 5. Il telefono altrui che ricostruisce il progetto, e la data del
2035. Tutto il resto è approfondimento.
