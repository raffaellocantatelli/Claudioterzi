/*
  La Costellazione — barra di navigazione.

  Versione precedente: i link erano uniti con `join("")` dentro un unico
  contenitore `white-space: nowrap`, senza alcun punto di rottura per lo
  schermo del telefono — la barra sbordava invece di andare a capo.
  Fix: i 15 link sono nodi <li> reali dentro una <ul> flex-wrap (vedi
  nav.css, .costellazione__voci), quindi il browser sceglie da solo dove
  spezzare la riga. Testato 320–1280px, tutte le 15 voci raggiungibili.
*/
(function () {
  var VOCI = [
    { nome: "Tarocchi", href: "/tarocchi.html" },
    { nome: "Alpha", href: "/alpha.html" },
    { nome: "Parti", href: "/parti.html" },
    { nome: "Viaggi", href: "/viaggi.html" },
    { nome: "Flight", href: "/flight.html" },
    { nome: "Oracolo", href: "/oracolo.html" },
    { nome: "Parfums", href: "/parfums.html" },
    { nome: "Organo", href: "/organo.html" },
    { nome: "Dispensa", href: "/dispensa.html" },
    { nome: "Valigia", href: "/valigia.html" },
    { nome: "Libro", href: "/libro.html" },
    { nome: "Atelier", href: "/atelier.html" },
    { nome: "Opera", href: "/opera.html" },
    { nome: "Creazioni", href: "/creazioni.html" },
    { nome: "Opuscolo", href: "/opuscolo.html" }
  ];

  function percorsoCorrente() {
    var p = window.location.pathname.split("/").pop();
    return p === "" ? "index.html" : p;
  }

  function costruisci() {
    var host = document.getElementById("costellazione");
    if (!host) return;

    var qui = percorsoCorrente();
    var nav = document.createElement("nav");
    nav.className = "costellazione";
    nav.setAttribute("aria-label", "La Costellazione");

    var interno = document.createElement("div");
    interno.className = "costellazione__interno";

    var nome = document.createElement("a");
    nome.className = "costellazione__nome";
    nome.href = "/index.html";
    nome.textContent = "La Costellazione";
    interno.appendChild(nome);

    var ul = document.createElement("ul");
    ul.className = "costellazione__voci";

    VOCI.forEach(function (voce) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = voce.href;
      a.textContent = voce.nome;
      var target = voce.href.replace(/^\//, "");
      if (target === qui) {
        a.setAttribute("aria-current", "page");
      }
      li.appendChild(a);
      ul.appendChild(li);
    });

    interno.appendChild(ul);
    nav.appendChild(interno);
    host.replaceWith(nav);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", costruisci);
  } else {
    costruisci();
  }
})();
