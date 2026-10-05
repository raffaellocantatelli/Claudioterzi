# POST Orchestra — risultato del test, 2026-10-05

**Esito: l'endpoint non risponde, e non perché sia rotto. Non è in produzione.**

Pronto da incollare in PR #116.

---

## 1. Il progetto non è nel team indicato

| | |
|---|---|
| progetto | `claudio` · `prj_WkdNZnH8K7YgSxbnKNNfBj8FPeaR` |
| team reale | **`rosso-rosso-rosso`** · `team_DzHGazmYUhPwm6lEV9iGyKD2` |
| team richiesto | `claudio-terzi-s-projects` · `team_dO423fnEAekxtan0rF3u2CQt` |
| dominio di produzione | `claudio-ten-phi.vercel.app` |

Il team `claudio-terzi-s-projects` **non è raggiungibile** da questa
connessione: `403 forbidden — Not authorized: Trying to access resource under
scope "claudio-terzi-s-projects"`. E `list_teams` restituisce **zero** team.

Il progetto `claudio` che ho testato è l'unico con quel nome visibile, e sta in
un team diverso da quello indicato. **Se esiste un secondo `claudio` sotto
`claudio-terzi-s-projects`, questo test non lo riguarda.**

## 2. La chiamata

```
POST https://claudio-ten-phi.vercel.app/api/orchestra
content-type: application/json
{}

HTTP/2 405
allow: OPTIONS, GET, HEAD
access-control-allow-methods: GET, POST, OPTIONS
server: Vercel
x-vercel-id: iad1::iad1::gmtmf-1791183194151-dc3b0803d8d4
```

## 3. Il 405 non riguarda Orchestra — è uniforme

| path | POST | GET |
|---|---|---|
| `/api/orchestra` | 405 | 404 (207 B) |
| `/api/r3_sync` | 405 | 404 (207 B) |
| `/api/deepseek_eval` | 405 | 404 (207 B) |
| `/api/raffaello` | 405 | 404 (207 B) |
| `/api/non-esiste-affatto` | **405** | **404 (207 B)** |
| `/` | — | 200 (23.956 B) |

Un path che **non può esistere** risponde identico a `/api/orchestra`. Quindi il
405 non dice nulla su Orchestra: dice che nessuna di quelle funzioni è servita.

Il corpo del 404 è la pagina di default di Werkzeug/Flask
(*«The requested URL was not found on the server…»*), quindi **risponde un'app
Flask**, non il gestore statico di Vercel.

## 4. Causa — RECUPERATO

L'ultimo deployment di produzione è `dpl_8AAbUEeqssAQpaHNS9XSxkdo6dEk`, stato
`READY`, e viene da GitHub **`Claudioterzi82/Claudio`** @
`55f07b8aef2a06f284beeefbe374b872892ecd63`.

In quel commit:

- **`api/orchestra.py` non esiste.**
- `vercel.json` dichiara **solo** `tarocchi_web.py` più `public/**` statico, con
  una rotta catch-all `{"src":"/(.*)","dest":"tarocchi_web.py"}`.
- il tree ha **585 file**.

In `claudioterzi/Claudio` @ `origin/main` (`261bebc`):

- `api/orchestra.py` **c'è**, introdotto il 2026-09-15 dal commit `6e0c4e2`
  *«feat(r3): add authenticated multi-provider orchestra endpoint»*;
- `vercel.json` lo dichiara fra i `builds`, con
  `maxDuration: 120` e `includeFiles: {sdq1/llm/**, sdq1/config/**, typesafe_sister/**, public/r3-ai-bootstrap.json}`;
- il tree ha **1816 file**.

**Il progetto Vercel costruisce un repository diverso da quello in cui vive
l'endpoint.** Il catch-all manda tutto a `tarocchi_web.py`, che su
`/api/orchestra` non ha una rotta POST: da cui `405` con
`allow: OPTIONS, GET, HEAD`.

## 5. Cosa non ho potuto testare, e perché

**Se la funzione funzioni.** Non è distribuita, quindi non c'è nulla da
chiamare.

Gli URL per-deployment (`claudio-5gi9xkex5-…`, `claudio-p69gvhj3c-…`)
rispondono `401` su POST e `302` su GET: è la **protezione dei deployment** di
Vercel, che intercetta prima della funzione. Non sono interrogabili senza un
bypass, e non l'ho cercato.

## 6. Una nota a margine

Nella risposta convivono `access-control-allow-methods: GET, POST, OPTIONS` e
`allow: OPTIONS, GET, HEAD`. **Il CORS annuncia un POST che il gestore non
implementa.** È innocuo qui, ma è la stessa forma di divergenza fra ciò che è
dichiarato e ciò che è implementato già registrata altrove in questo progetto.

## 7. Prossimo passo verificabile

Puntare il progetto Vercel al repository e ramo che contengono
`api/orchestra.py` — oppure portare quel tree in ciò che `Claudioterzi82/Claudio`
distribuisce — e **ripetere la stessa chiamata**.

**Previsione falsificabile:** a endpoint distribuito, un POST **senza
credenziali** deve restituire **401 o 403**, non 405. Il docstring del modulo
dichiara *«Authenticated multi-provider orchestra»* e che i provider si
abilitano solo se i segreti di runtime esistono già.

Se dopo il redeploy tornasse ancora `405`, la causa non è questa e l'analisi
qui sopra è sbagliata.

---

*§1 e §4 **RECUPERATO** (API Vercel e `git` sui commit citati). §2 e §3
**RECUPERATO** eseguendo le chiamate. §5 **INFERITO** dai codici di stato. §7
**IPOTESI**, con il criterio di falsificazione accanto.*
