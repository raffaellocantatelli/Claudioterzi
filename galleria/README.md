# La Galleria

Da foto a scheda esperta, e navigazione per **motivo di interesse** invece che per
categoria merceologica.

## L'idea in una riga

Ogni marketplace dell'usato cataloga per *cosa* una cosa è (libri → storia →
anni '70). Qui si cataloga per **perché merita attenzione**: soppresso · primo ·
appartenuto a · tecnica perduta · interrotto · sopravvissuto per caso · errore ·
quotidiano scomparso.

Nessuno cerca «ceramica italiana XVI secolo». Si cerca «fammi vedere cose fatte
con una tecnica che oggi nessuno sa più fare» — e questa è la navigazione che i
marketplace per categoria non permettono.

## I due problemi che risolve

1. **Chi vende** si ferma al dodicesimo oggetto perché ogni annuncio richiede
   dieci minuti. Qui fotografi, e la scheda — tecnica esatta, edizione, contesto
   storico, cosa verificare di persona — si compone da sola. Poi la correggi.
2. **Chi compra** non riuscirà mai a guardare un milione di oggetti. La risorsa
   scarsa non sono le cose, è l'attenzione: serve qualcuno che dica *perché*
   guardare questo e non quello.

## Cosa c'è dentro

```
dati/motivi.json      la tassonomia dei motivi di interesse — il cuore dell'idea
dati/oggetti.json     il catalogo
lib/scheda.js         foto → scheda esperta (API Claude, structured outputs)
lib/catalogo.js       lettura, scrittura, interrogazione per motivo
server.js             API + statici
public/               galleria, scheda, aggiungi
```

## Avvio

```bash
npm install
export ANTHROPIC_API_KEY=...   # solo per l'identificazione automatica
npm start                       # http://localhost:3100
```

Senza chiave API tutto il resto funziona: le schede si compilano a mano.

## Cosa NON è (ancora)

Deliberatamente fuori da questa prima versione, perché sono anni di lavoro e
capitali, non un pomeriggio:

- **Realtà virtuale.** La galleria immersiva è la parte scenografica; questa è
  la parte che decide se l'idea vale qualcosa.
- **Aste vere** — pagamenti, escrow, contestazioni.
- **Logistica** — ritiro, spedizione, assicurazione, dogane.
- **Valutazione automatica affidabile.** Servirebbe un database di *prezzi
  realizzati* (non richiesti). È quello il vero asset di Catawiki, ed è ciò che
  rende il settore difficile da attaccare. Qui il campo `valore` indica una
  fascia e dice sempre su cosa va verificata — non inventa mai una cifra.
- **Profilo di gusto e aste su misura.** Il passo successivo naturale: gli
  oggetti che una persona possiede sono il segnale più ricco che esista su di
  lei, molto più dei click. Chi scansiona casa per vendere, senza volerlo,
  insegna alla rete chi è.

## Nota sull'onestà delle schede

Il prompt del curatore ha tre regole non negoziabili: nominare la tecnica esatta
o dichiarare l'incertezza; non inventare mai una valutazione precisa; descrivere
la condizione senza addolcirla. Ogni scheda porta un livello di **confidenza**
dichiarato, e un elenco di cose che chi vende deve verificare di persona.

Una scheda che esagera vende una volta. La fiducia è l'unica cosa che rende
possibile un mercato dove la gente compra oggetti che non ha in mano.
