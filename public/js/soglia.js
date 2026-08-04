/*
  soglia.js — la soglia d'ingresso.

  Chiede una parola prima di mostrare la pagina. NON è un meccanismo di
  sicurezza: la parola è scritta in chiaro qui sotto, chiunque apra questo
  file la legge in tre secondi. È un rituale di passaggio, non un lucchetto
  — un gesto che dice "stai per entrare da qualche parte", non una barriera.
  Chi vuole entrare senza cerimonia può leggere il sorgente e saltarla.

  Superata una volta, resta valida per la sessione del browser
  (sessionStorage): non si ripete ad ogni pagina della Costellazione.
*/
(function () {
  var PAROLA = "varco";
  var CHIAVE = "soglia-superata";

  if (sessionStorage.getItem(CHIAVE) === "1") return;

  var velo = document.createElement("div");
  velo.className = "soglia";
  velo.innerHTML =
    '<div class="soglia__corpo">' +
    '<p class="soglia__testo">Una parola, prima di entrare.</p>' +
    '<form class="soglia__forma">' +
    '<input class="soglia__campo" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Parola d\'ingresso" />' +
    '<button class="bottone" type="submit">Varca</button>' +
    "</form>" +
    '<p class="soglia__errore" hidden>Non è questa la parola.</p>' +
    '<button type="button" class="soglia__salta">entra comunque</button>' +
    "</div>";

  var stile = document.createElement("style");
  stile.textContent =
    ".soglia{position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;" +
    "background:#0c0c0e;padding:1.5rem;}" +
    ".soglia__corpo{max-width:26rem;width:100%;text-align:center;font-family:Georgia,serif;color:#e9e6da;}" +
    ".soglia__testo{color:#a39d8a;font-style:italic;margin-bottom:1.5rem;}" +
    ".soglia__forma{display:flex;gap:0.6rem;flex-wrap:wrap;justify-content:center;}" +
    ".soglia__campo{flex:1 1 12rem;background:#131316;border:1px solid #2a2a2f;color:#e9e6da;" +
    "font-family:Georgia,serif;font-size:1rem;padding:0.6rem 0.8rem;border-radius:4px;}" +
    ".soglia__campo:focus{outline:1px solid #c9a84c;}" +
    ".soglia__errore{color:#c98a4c;margin-top:1rem;font-size:0.9rem;}" +
    ".soglia__salta{display:block;margin:1.5rem auto 0;background:none;border:none;" +
    "color:#5a564a;font-family:Georgia,serif;font-size:0.8rem;text-decoration:underline;cursor:pointer;}";

  document.head.appendChild(stile);
  document.documentElement.style.overflow = "hidden";
  document.body.appendChild(velo);

  var campo = velo.querySelector(".soglia__campo");
  var errore = velo.querySelector(".soglia__errore");

  function entra() {
    sessionStorage.setItem(CHIAVE, "1");
    document.documentElement.style.overflow = "";
    velo.remove();
    stile.remove();
  }

  velo.querySelector(".soglia__forma").addEventListener("submit", function (e) {
    e.preventDefault();
    var risposta = campo.value.trim().toLowerCase();
    if (risposta === PAROLA) {
      entra();
    } else {
      errore.hidden = false;
      campo.select();
    }
  });

  velo.querySelector(".soglia__salta").addEventListener("click", entra);

  campo.focus();
})();
