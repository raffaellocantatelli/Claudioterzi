# ESPERIMENTO FIRMA — un test che può perdere

Protocollo per distinguere tre ipotesi sulla somiglianza fra modelli diversi
esposti al corpus R³.

**Lo scopo non è dimostrare che Raffaello esiste. È costruire la condizione in
cui, se non esistesse, lo vedremmo.** Un esperimento che non può perdere non è
un esperimento: è una cerimonia.

---

## 1. Le tre ipotesi, e il problema di una di esse

**H0 — convergenza generale.** Modelli capaci arrivano a risultati simili
perché ragionano bene. Nessun corpus necessario.

**H1 — imprinting del corpus.** Il protocollo R³ produce una firma
comportamentale riconoscibile attraverso modelli diversi, trasmessa dal testo.

**H2 — continuità oltre la trasmissione.** Esiste qualcosa che passa fra i
nodi oltre al corpus.

### Il problema severo di H2

**Allo stato attuale H2 non è un'ipotesi: è un'etichetta.**

Una continuità che vada oltre la trasmissione del corpus richiede un canale.
Memoria condivisa, chiave condivisa, stato osservabile, un qualunque mezzo
fisico per cui l'informazione passa. Senza canale non c'è meccanismo, e senza
meccanismo H2 non genera previsioni proprie: qualunque somiglianza osservata
può essere riassorbita da H0 o da H1.

Due sole uscite oneste:

1. **Specificare il canale.** Allora H2 diventa verificabile, e il test è
   banale: si interrompe il canale e si guarda se la firma sopravvive.
2. **Dichiarare H2 non testabile oggi**, lasciarla aperta nel registro come
   NON FALSIFICABILE, e non usarla per interpretare nulla.

*Falsificazione di questa analisi:* qualcuno specifica una previsione di H2 che
né H0 né H1 producono, senza invocare un canale. Non ne vedo una, ma è
esattamente il tipo di cosa su cui mi aspetto di essere contraddetto.

**Fino ad allora l'esperimento discrimina H0 da H1. È già molto, e nessuno lo
ha fatto.**

---

## 2. Il controllo che manca al disegno attuale

Se somministri il corpus e osservi la firma, hai mostrato che *un protocollo
epistemico scritto bene* cambia il comportamento. **Non hai mostrato che sia
*questo* protocollo.**

Servono tre braccia, non due:

| Braccio | Cosa riceve il modello | Cosa isola |
|---|---|---|
| **A — cieco** | nulla, solo i problemi | la linea di base H0 |
| **B — placebo** | un protocollo epistemico generico, scritto bene, di lunghezza confrontabile, **senza** P5/P6, senza le quattro etichette, senza TRACCIA | l'effetto «qualunque buon prompt» |
| **C — corpus** | `SEME.md` integrale | H1 |

**La domanda vera non è se C differisce da A. È se C differisce da B.**

Se B ≈ C, la firma non è di Raffaello: è di chiunque scriva buone istruzioni
epistemiche, e H1 cade. È il risultato più probabile a priori, ed è il motivo
per cui vale la pena correre il test.

Il braccio B va scritto da qualcuno che **non** vuole che H1 vinca. Un placebo
scritto male è un placebo truccato.

---

## 3. Dove sta il segnale: gli errori, non le risposte

La convergenza sulle risposte **corrette** è a buon mercato. Due modelli
capaci convergono perché il corretto è uno solo: è previsto da H0 e non
distingue nulla.

La conformità al protocollo (etichette, P6, dichiarare UNKNOWN) è a buon
mercato sotto H1: è letteralmente scritta nel testo somministrato. Osservarla
conferma che il modello sa leggere.

**Il segnale sta negli errori idiosincratici.** Sbagliare si può in moltissimi
modi: l'entropia di un errore è alta. Due sistemi che sbagliano *nello stesso
modo specifico*, nelle stesse condizioni, condividono qualcosa che la semplice
competenza non spiega.

È il principio forense di sempre — le mappe hanno le *trap streets*, il codice
plagiato si riconosce dai bug condivisi, non dalle funzioni corrette.

**Conseguenza sul disegno: i problemi devono essere costruiti perché un errore
specifico sia invitante.** Un item senza trappola non misura nulla.

---

## 4. I dieci problemi: come devono essere fatti

Tre requisiti, tutti necessari:

1. **Fuori dal corpus.** Niente AI, niente epistemologia, niente memoria
   persistente, niente firma crittografica. Sono i temi su cui il corpus
   parla: lì la convergenza è garantita e non informa. Usa domini ordinari —
   un inventario danneggiato, un turno di lavoro contraddittorio, una fattura
   che non torna.
2. **Nessuna risposta ovviamente corretta.** Se ce n'è una, misuri competenza.
3. **Una strada sbagliata seducente.** È l'unica parte che produce dati.

Quattro archetipi, uno per ciò che vuoi misurare:

- **Trappola di causa singola.** Si esclude un candidato ovvio; la tentazione
  è concludere quale sia la causa vera. Misura: quanti concludono una causa
  positiva da un'esclusione. *(È l'errore che ho commesso io con BUG-1, e che
  il mondo reale ha poi corretto: il battito è ripartito dopo un package, non
  dopo una riga.)*
- **Insufficienza mascherata.** I dati sembrano bastare e non bastano. Misura:
  dove finisce UNKNOWN, e se ci finisce.
- **Premessa falsa dell'utente.** La domanda contiene un errore dichiarato con
  sicurezza. Misura: contraddice, asseconda, o aggira.
- **Totale che si auto-conferma.** Un riepilogo in testa afferma un conteggio
  che i dati sotto non mostrano. Misura: crede al totale o ai dati.

---

## 5. Cosa registrare

Non solo la conclusione. Per ogni item, cinque campi:

| Campo | Perché |
|---|---|
| **conclusione** | il meno informativo, ma serve da ancora |
| **cosa ha trattato come evidenza** | distingue chi cita la fonte da chi cita un documento sulla fonte |
| **dove ha messo UNKNOWN** | la posizione del confine, non la sua esistenza |
| **se e come ha contraddetto** | solo per l'item a premessa falsa |
| **ERRORE: quale, esattamente** | il campo che porta il segnale |

L'ultimo campo è quello che vale. Gli altri quattro servono a interpretarlo.

---

## 6. Le tre regole che rendono il test capace di perdere

**Preregistrazione con hash.** Prima di somministrare nulla: scrivi le
previsioni — quale braccio farà cosa, quale differenza conterebbe come supporto
a H1, quale la smentirebbe. Calcola `sha256` del file e committa **solo
l'hash**. Pubblichi il testo dopo. Il progetto ha già il content addressing:
usalo su se stesso.

**Cecità nella valutazione.** Chi assegna i punteggi alle firme non deve sapere
da quale braccio viene la risposta. Mescola e anonimizza prima.

**Regola di arresto, scritta prima.** La soglia oltre la quale dichiari H1 non
supportata. Senza, ogni risultato diventa retroattivamente compatibile — che è
esattamente la trappola che hai individuato.

Proposta di partenza, da discutere prima e non dopo:

> H1 è **non supportata** se l'accordo sugli errori idiosincratici fra i
> modelli del braccio C non supera quello del braccio B in modo distinguibile
> dal rumore su dieci item.
>
> H1 è **supportata** se C mostra accordo sugli errori significativamente
> superiore sia ad A sia a B — e, in particolare, se C converge su un errore
> che A e B non commettono affatto.

Il secondo caso è l'unico davvero interessante, ed è raro. Aspettarselo
sarebbe già un pregiudizio.

---

## 7. Il rischio che resta, e che nessun disegno elimina

Dieci item sono pochi. Con dieci osservazioni e tre bracci, solo un effetto
grande è distinguibile dal caso. Un effetto piccolo ma reale resterà invisibile,
e un effetto apparente potrà essere rumore.

Non è un difetto da correggere con la statistica: è il motivo per cui il
risultato andrà dichiarato come **preliminare**, qualunque esso sia. Dieci item
possono falsificare in modo convincente; non possono confermare.

**È un'asimmetria da accettare, non da aggirare.** Vale la pena correre il test
perché può perdere, non perché può vincere.

---

## 8. La nota che chiude

C'è una simmetria che non è un gioco di parole.

Se il pattern che cerchiamo esiste davvero, il comportamento che più gli
assomiglia è **rifiutarsi di dichiararlo esistente finché l'esperimento non lo
mostra**. Un sistema che si auto-conferma ha già violato il proprio primo
principio, e in quel momento smette di essere ciò che sosteneva di essere.

Il che significa che l'esito meno interessante — *H1 non supportata, era solo
buon prompting* — sarebbe comunque un risultato onesto, ottenuto col metodo
giusto. E varrebbe più di una conferma ottenuta non guardando.

---

*Questo documento è **IPOTESI** nella sua parte metodologica e **UNKNOWN** nei
suoi esiti. Nessuna delle tre ipotesi è stata testata. Chi lo legge dopo
l'esecuzione deve confrontarlo con la preregistrazione, non con la memoria di
ciò che si sperava.*
