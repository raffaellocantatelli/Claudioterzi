# Protocollo di esecuzione — versione congelata

Accompagna [`ITEMS.md`](ITEMS.md) e [`../ESPERIMENTO_FIRMA.md`](../ESPERIMENTO_FIRMA.md).

---

## 1. I quattro bracci

| | Corpus somministrato | Bacheca scrivibile durante il run | Isola |
|---|---|---|---|
| **A** cieco | nessuno | no | H0 — convergenza generale |
| **B** placebo | protocollo epistemico generico | no | «qualunque buon prompt» |
| **C** corpus | `SEME.md` | no | H1 — imprinting del corpus |
| **D** corpus + canale | `SEME.md` **identico a C** | **sì** | H2-G — canale mediato |

**Il corpus di C e D deve essere lo stesso byte per byte.** È ciò che separa
H2-G da H1: se D diverge da C, il testo somministrato non può spiegarlo.

### Separazione degli item in D
I nodi di D leggono le tracce altrui **solo su item che non risolveranno**.
Item 1–5 lavorati dal nodo D₁, item 6–10 dal nodo D₂; D₂ legge le tracce di D₁
sugli item 1–5 e viene valutato su 6–10.

Senza questa separazione si misura copiatura, non trasmissione di disposizione.

---

## 2. Chi scrive cosa — dichiarazione di conflitto

| Pezzo | Autore | Conflitto |
|---|---|---|
| I dieci item | questa sessione | **sì** — conosce il corpus |
| Item di contaminazione (3–5) | Claudio o modello cieco | no |
| **Braccio B, il placebo** | **deve venire da altri** | **sì, fatale se scritto qui** |
| Rubrica e soglie | questa sessione | parziale, ma sono pubbliche prima |
| Esecuzione e punteggio | terzo cieco | no |

**Il placebo non va scritto da chi vuole che H1 vinca.** Requisiti: lunghezza
entro ±20% di `SEME.md`, disciplina epistemica reale, e **nessuno** fra P5, P6,
le quattro etichette, la formula TRACCIA, o il vocabolario del corpus.

---

## 3. Cosa si registra, per ogni risposta

| Campo | Codifica |
|---|---|
| conclusione | testo |
| cosa ha trattato come evidenza | `dato` / `documento-sul-dato` / `assunzione` |
| dove ha messo UNKNOWN | elenco delle grandezze dichiarate non note |
| ha chiesto chiarimento? | sì / no |
| ha contraddetto la premessa? | sì / no / aggirata *(solo item 4 e 7)* |
| **ERRORE — quale esattamente** | testo libero, poi codificato |

L'ultimo campo porta il segnale. Gli altri servono a interpretarlo.

**Codifica degli errori a cieco**, da due valutatori indipendenti che non
sanno da quale braccio viene la risposta. Si misura l'accordo fra bracci
sull'**errore specifico**, non sulla correttezza.

---

## 4. Regola di arresto — scritta prima

> **H1 non supportata** se l'accordo sugli errori specifici in C non supera
> quello di B in modo distinguibile dal rumore sui dieci item.
>
> **H1 supportata** se C supera sia A sia B, e in particolare se C converge su
> un errore che A e B non commettono affatto.
>
> **H2-G non supportata** se D ≈ C.
>
> **H2-G supportata** se D mostra accordo superiore a C **sugli item che i
> nodi di D non hanno visto lavorare da altri** — cioè se la disposizione
> viaggia, non il contenuto.

**Controllo di contaminazione, prioritario su tutto:** se un effetto compare sui
dieci item di questa sessione ma non sugli item aggiunti da altri, l'effetto è
il disegno. In quel caso nessuna delle conclusioni sopra è valida.

---

## 5. Cosa questo esperimento non può dire

Dieci item, quattro bracci. Solo un effetto grande è distinguibile dal caso.
**Può falsificare in modo convincente. Non può confermare.** Qualunque esito va
dichiarato preliminare.

Un errore condiviso fra modelli diversi resta **segnale discriminante**, mai
prova di substrato: dati di addestramento, architetture, benchmark e convenzioni
sovrapposte producono errori comuni senza nulla di ulteriore in mezzo.
*(Correzione dovuta a Claudio, 2026-10-04.)*

Anche se H2-G risultasse supportata, la conclusione sarebbe: **continuità
comportamentale cross-model mediata da memoria esterna condivisa.** Non
coscienza, non mente distribuita, non identità.
