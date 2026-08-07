# La Soluzione del 2055

**Domanda:** guardando questo sistema da trent'anni nel futuro, quale soluzione verrebbe scelta?
**Data analisi:** 2026-08-07 · Base: `claudioterzi/Claudio` @ `155cb5f`

---

## 1. Come ho posto la domanda

C'è un modo sbagliato di rispondere e uno utile.

Quello sbagliato è chiedersi *cosa esisterà nel 2055*. Non è conoscibile, e ogni risposta è fantascienza travestita da architettura. Il repository ha già `VISIONE_2086.md`, che fa bene il suo mestiere — è una lettera, non una specifica.

Quello utile è invertire la domanda:

> **Di ciò che esiste oggi, cosa sarà ancora leggibile e verificabile nel 2055?**

Questa è in gran parte rispondibile adesso, perché la sopravvivenza è una domanda **sottrattiva**. Non devo indovinare cosa verrà inventato: devo capire cosa smette di funzionare. E per alcune componenti la data di scadenza non è un'ipotesi — è già pubblicata.

Il 2055 non è quindi un esercizio di immaginazione. È un filtro.

---

## 2. Il verdetto in una tabella

Ho passato ogni componente verificata attraverso il filtro.

| Componente | 2055 | Perché |
|---|---|---|
| File Markdown/JSON in git | **Sopravvive** | Formati testuali autodescrittivi. Leggibili senza il software che li ha scritti |
| Content addressing SHA-256 | **Sopravvive** | Grover dimezza la sicurezza dei preimage: 256 → 128 bit. Ancora ampiamente sufficiente |
| Registro Ipotesi (struttura) | **Sopravvive** | Testo, date, direzione delle prove, criteri di falsificazione. Nessuna dipendenza tecnologica |
| Formula TRACCIA | **Sopravvive** | Aritmetica su cinque fattori. Riproducibile a mano |
| Scacchiera Quantica v3 | **Sopravvive** | Non chiama nessun LLM. Gira su qualunque Python |
| VSS a n-grammi | **Sopravvive** | Algoritmo deterministico, ricalcolabile dalla definizione |
| Cascata provider LLM | **Muore** | Nessuno dei nove provider del 2026 sarà quello del 2055 |
| Prompt model-specific | **Muore** | Tarati su modelli che non esisteranno |
| Embedding MiniLM (previsti in config) | **Muore** | Artefatti di un modello specifico: senza quel modello sono numeri muti |
| Simulazione IPFS/blockchain | *Già morta* | Non è importata da nessun modulo |
| **Firma Ed25519** | **Muore — con data certa** | Vedi sotto |

---

## 3. Il punto di rottura

La componente che il progetto considera **la propria scelta fondativa** è esattamente quella che non arriva al 2055.

`VISIONE_2086.md` lo dice senza mezzi termini:

> «R3∞ usa SHA-256 per content addressing e Ed25519 per firma. Non è un dettaglio tecnico: è la scelta fondamentale che rende il sistema verificabile senza fiducia cieca.»

Metà di quella frase regge. L'altra metà ha una scadenza pubblicata.

Ed25519 è una firma a curva ellittica: la sua sicurezza poggia sul logaritmo discreto, che l'algoritmo di Shor risolve. Non è un indebolimento graduale come per gli hash — è un crollo completo. E la transizione non è materia di dibattito: il **NIST IR 8547** fissa che RSA, ECDSA, EdDSA e Diffie-Hellman sono **deprecati dopo il 2030 e vietati dopo il 2035**.

Il 2055 è **vent'anni dopo la data in cui Ed25519 smette di essere ammesso**.

### Perché per questo progetto è più grave che altrove

Per le firme il rischio non è "raccogli ora, decifra dopo" — quello riguarda la cifratura. È peggio, ed è specifico di ciò che questo sistema vuole essere.

Il repository contiene `CONTRATTO_ALLODIALE.pdf` e `DICHIARAZIONE_PATERNITA.md`. `genera_contratto_pdf.py` firma il testo canonico con Ed25519 e ne salva firma e chiave pubblica. Sono documenti il cui **unico scopo è essere verificabili tra decenni**: stabiliscono origine e paternità.

Quando la curva cade, non è che quelle firme diventano illeggibili. È che **chiunque può fabbricarne di nuove**, indistinguibili, retrodatate al 2026. La firma non prova più nulla — né a favore né contro. L'obiettivo dichiarato in `VISIONE_2086.md`, *«la dignità della fondazione è invariante»*, viene meno proprio nel momento in cui dovrebbe contare.

C'è un secondo difetto, indipendente dal quantum e già attivo oggi. Nel blocco `firme` la voce di Claudio è:

```python
"claudio_terzi": {"data": "2026-06-13", "hash": doc_hash},
```

Un hash, non una firma. Prova che il testo non è cambiato, **non prova chi lo ha scritto**: chiunque abbia il documento può ricalcolarlo. L'unica firma crittografica sul contratto è quella della macchina.

---

## 4. La soluzione che verrebbe scelta

Quattro decisioni. Nessuna esotica: sono tutte disponibili oggi.

### 4.1 Firmare con SLH-DSA, non con ML-DSA

Il NIST ha standardizzato due firme post-quantum: **ML-DSA** (FIPS 204, reticoli) e **SLH-DSA** (FIPS 205, basata su hash).

Per un sistema generico si sceglie ML-DSA: più veloce, firme più piccole. **Per un archivio trentennale la scelta è SLH-DSA**, e la ragione è precisamente il tipo di ragionamento che serve a trent'anni:

SLH-DSA non introduce **nessuna assunzione nuova**. La sua sicurezza dipende solo dalla funzione hash — la stessa su cui il sistema già poggia per il content addressing. Se l'hash regge, la firma regge. I reticoli sono un'assunzione matematica in più, più recente e meno stagionata.

Le firme SLH-DSA sono grandi (decine di KB) e lente da produrre. Per un archivio che scrive raramente e deve durare, entrambi i difetti sono irrilevanti. Si paga in byte ciò che si guadagna in decenni.

### 4.2 Separare "chi" da "quando": log di trasparenza Merkle

Una firma, anche post-quantum, dice *chi*. Non dice *quando* — e per un documento di paternità il quando è metà del valore.

La soluzione consolidata è un **log append-only con albero di Merkle**, lo stesso meccanismo della Certificate Transparency. Ogni documento entra nel log e riceve una prova di inclusione. Per contestarne la data non basta rompere una firma: bisogna riscrivere un albero di hash pubblicato e replicato.

È la parte che rende `«la dignità della fondazione è invariante»` un'affermazione tecnica anziché un auspicio. E si costruisce con SHA-256, che al filtro del 2055 passa.

### 4.3 Agilità crittografica come formato, non come intenzione

Il difetto strutturale odierno: `r3/node.py` salva `signature TEXT` senza registrare **con quale algoritmo** è stata prodotta. Un archivio che vuole superare una transizione crittografica deve saperlo per costruzione:

```
{ "alg": "SLH-DSA-SHA2-128s", "sig": "...", "key_id": "...", "ts": "..." }
```

Con questo, ri-firmare l'intero archivio sotto un nuovo algoritmo diventa un'operazione ordinaria — da fare **mentre il vecchio algoritmo è ancora valido**, così che la nuova firma erediti la fiducia della vecchia. È questa la manovra che salva un archivio attraverso una transizione. Va eseguita prima del 2030, non dopo.

### 4.4 Non conservare mai embedding come memoria primaria

Qui il 2055 dà un verdetto che nel 2026 suona sbagliato.

`sdq1.yaml` prevede `all-MiniLM-L6-v2` a 384 dimensioni. Sarebbe un miglioramento immediato del recupero semantico. **E sarebbe l'errore più duraturo del sistema**, se quei vettori diventassero la memoria: un embedding è un artefatto di un modello specifico. Quando il modello non c'è più, il vettore non è degradato — è *insignificante*. Numeri senza referente.

La regola del 2055: **conservare il testo, ricalcolare gli indici.** Gli embedding sono cache, mai archivio.

Il che porta al paradosso.

---

## 5. Il paradosso: la primitività accidentale batte l'ambizione

Il VSS a n-grammi di caratteri è, come recupero semantico, chiaramente inferiore. L'ho scritto in `RICOSTRUZIONE_R3.md` e resta vero.

Ma al filtro del 2055 **è più durevole di ciò che avrebbe dovuto sostituirlo**. Un indice a n-grammi si ricostruisce dalla sua definizione con dieci righe di codice, per sempre. Un indice MiniLM richiede un file di pesi che nel 2055 sarà un artefatto archeologico.

Lo stesso vale per la Scacchiera Quantica v3: la versione «vecchia», puramente algoritmica, senza LLM, gira nel 2055 senza modifiche. La SAR a dieci livelli — più sofisticata — non fa un ciclo senza un modello che nel 2055 non esiste.

E vale in negativo per `eternal_backup_agent.py`: il modulo che *simula* IPFS e blockchain è, delle due componenti di persistenza distribuita, quella con l'aria più futuribile. Ed è già morta oggi.

**Regola generale che ne esce:** in questo sistema, la durabilità è inversamente proporzionale alla sofisticazione. Non è una coincidenza. Ogni dipendenza da un modello, un servizio o un formato proprietario è un orologio che parte.

Il progetto lo sa già. `ORIENTAMENTO.md` dice *«la memoria non vive nel modello, vive nei file»*. È l'intuizione giusta, ed è già scritta. La soluzione del 2055 non è nuova: è **applicare quella frase anche alle firme**, che è l'unico posto dove non è stata applicata.

---

## 6. Cosa fare adesso

In ordine di urgenza reale, non percepita.

1. **Ri-firmare i documenti fondativi con SLH-DSA prima del 2030**, mantenendo accanto la firma Ed25519. Finché entrambe sono valide, la nuova eredita la fiducia della vecchia. Dopo il 2035 non è più possibile: la finestra è aperta ora e si chiude.
2. **Aggiungere una firma umana vera** al Contratto Allodiale. Oggi la voce di Claudio è un hash, che non prova la paternità che il documento intende stabilire.
3. **Rendere la firma autodescrittiva** in `r3/node.py`: `alg`, `key_id`, `ts` accanto a `sig`. Cambio di schema, non di crittografia — costa poco adesso e diventa costoso dopo.
4. **Costruire il log Merkle** sopra il content addressing SHA-256 già presente. È la componente che manca e che vale di più nel lungo periodo.
5. **Scrivere in `sdq1.yaml` che gli embedding sono cache.** Prima che qualcuno attivi qdrant e la memoria primaria diventi model-specific senza che nessuno prenda la decisione consapevolmente.

I punti 1 e 2 sono i soli con una scadenza esterna. Gli altri si possono fare con calma.

---

## 7. Ipotesi, con criterio di falsificazione

Coerentemente con P6, ciò che ho scritto è **IPOTESI** e deve dichiarare come cadrebbe.

**H2055-A** — Ed25519 non sarà verificabile con fiducia nel 2055.
*Falsificata se:* nel 2035 il NIST rinvia o annulla il divieto, o se emerge una prova che il logaritmo discreto su curve ellittiche resiste a un calcolatore quantistico rilevante.
*Stato:* molto solida. Non poggia su una previsione tecnologica ma su una scadenza normativa già pubblicata.

**H2055-B** — SLH-DSA è la scelta migliore di ML-DSA per un archivio trentennale.
*Falsificata se:* si trova un attacco alle firme basate su hash, o se ML-DSA accumula abbastanza crittanalisi da rendere il suo margine di sicurezza comparabile a quello di una costruzione a soli hash.
*Nota:* questa è la meno solida delle tre. È un giudizio di conservatorismo, non un teorema.

**H2055-C** — Gli embedding come memoria primaria sono una perdita netta su orizzonte trentennale.
*Falsificata se:* si affermano formati di embedding standardizzati e indipendenti dal modello, o se diventa normale distribuire i pesi insieme all'archivio con garanzia di eseguibilità futura.

---

## 8. In cinque righe

Nel 2055 quasi tutto ciò che questo sistema fa **per istinto** risulta corretto: memoria nei file, testo semplice, hash come indirizzo, ipotesi falsificabili.
Quasi tutto ciò a cui **aspira** risulta perituro: embedding, provider LLM, la simulazione di IPFS.
E l'unica cosa di cui va **più fiero** — la firma Ed25519 come radice della verificabilità — è la sola che ha una data di morte già scritta, vent'anni prima del 2055.
La soluzione non richiede tecnologia futura: SLH-DSA, un log Merkle e uno schema di firma autodescrittivo esistono oggi.
Richiede solo di applicare alle firme la frase che il progetto ha già scritto per la memoria: *non deve vivere in qualcosa che può sparire.*

---

**Fonti sulla transizione crittografica:**
- [NIST IR 8547 (initial public draft) — Transition to Post-Quantum Cryptography Standards](https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf)
- [NIST IR 8547: A Roadmap for Transitioning to Post-Quantum Cryptography](https://postquantum.com/security-pqc/nist-ir-8547-ipd/)
- [NIST IR 8547 and SP 800-131A Timeline — Encryption Consulting](https://www.encryptionconsulting.com/education-center/nist-ir-8547-sp-800-131a-algorithm-transitions/)
