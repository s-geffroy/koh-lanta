/* Koh-Lanta en chiffres — le seul script du site.
 *
 * Rien de ce qu'il fait ne porte de donnee : sans lui, toutes les pages
 * restent completes et lisibles. Il ajoute trois conforts, et rien d'autre :
 * la bascule de theme, le tri des tableaux, le filtrage des aventuriers.
 * C'est pourquoi les commandes qu'il installe sont masquees tant qu'il n'a
 * pas tourne (classe `sans-js`, retiree tres tot dans <head>).
 */
(function () {
  "use strict";

  /* ------------------------------------------------------------- le theme */

  var bouton = document.getElementById("bascule-theme");
  if (bouton) {
    var etats = ["auto", "clair", "sombre"];
    var libelle = { auto: "Thème : auto", clair: "Thème : clair", sombre: "Thème : sombre" };

    var lire = function () {
      try {
        var t = localStorage.getItem("theme");
        return etats.indexOf(t) >= 0 ? t : "auto";
      } catch (e) { return "auto"; }
    };

    var poser = function (etat) {
      var r = document.documentElement;
      if (etat === "clair") r.setAttribute("data-theme", "light");
      else if (etat === "sombre") r.setAttribute("data-theme", "dark");
      else r.removeAttribute("data-theme");
      bouton.textContent = libelle[etat];
      try { localStorage.setItem("theme", etat); } catch (e) {}
    };

    poser(lire());
    bouton.addEventListener("click", function () {
      poser(etats[(etats.indexOf(lire()) + 1) % etats.length]);
    });
  }

  /* ------------------------------------------------------- tri des tableaux */

  var cle = function (cellule, numerique) {
    var brut = cellule.getAttribute("data-val");
    if (brut === null) brut = cellule.textContent;
    brut = brut.trim();
    if (!numerique) return brut;
    // Les nombres du site s'ecrivent avec une virgule decimale et parfois une
    // espace fine comme separateur de milliers ; le tiret marque l'absence.
    var n = parseFloat(brut.replace(/[\s\u00a0\u202f\u2009]/g, "").replace(",", "."));
    return isNaN(n) ? -Infinity : n;
  };

  Array.prototype.forEach.call(
    document.querySelectorAll("table[data-triable]"),
    function (table) {
      var corps = table.tBodies[0];
      if (!corps || !table.tHead) return;
      var entetes = Array.prototype.slice.call(table.tHead.rows[0].cells);

      entetes.forEach(function (entete, colonne) {
        entete.setAttribute("aria-sort", "none");
        entete.setAttribute("tabindex", "0");
        entete.setAttribute("title", "Trier sur cette colonne");

        var trier = function () {
          var sens = entete.getAttribute("aria-sort") === "ascending" ? -1 : 1;
          var numerique = entete.classList.contains("nombre");
          var lignes = Array.prototype.slice.call(corps.rows);

          lignes.sort(function (a, b) {
            var x = cle(a.cells[colonne], numerique);
            var y = cle(b.cells[colonne], numerique);
            if (numerique) return sens * (x - y);
            return sens * String(x).localeCompare(String(y), "fr");
          });

          var frag = document.createDocumentFragment();
          lignes.forEach(function (l) { frag.appendChild(l); });
          corps.appendChild(frag);

          entetes.forEach(function (h) { h.setAttribute("aria-sort", "none"); });
          entete.setAttribute("aria-sort", sens === 1 ? "ascending" : "descending");
        };

        entete.addEventListener("click", trier);
        entete.addEventListener("keydown", function (ev) {
          if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); trier(); }
        });
      });
    }
  );

  /* ------------------------------------------------------------- filtrage */

  var sansAccent = function (s) {
    return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  };

  Array.prototype.forEach.call(
    document.querySelectorAll("[data-filtre]"),
    function (bloc) {
      var table = document.getElementById(bloc.getAttribute("data-filtre"));
      if (!table || !table.tBodies[0]) return;

      var texte = bloc.querySelector("[data-role=texte]");
      var listes = Array.prototype.slice.call(bloc.querySelectorAll("[data-champ]"));
      var compte = bloc.querySelector("[data-role=compte]");
      var lignes = Array.prototype.slice.call(table.tBodies[0].rows);
      var total = lignes.length;

      // Le texte cherche est compare une seule fois par ligne, sans accents :
      // taper « teheiura » doit trouver « Teheiura ».
      lignes.forEach(function (l) { l._cherche = sansAccent(l.textContent); });

      var appliquer = function () {
        var q = texte ? sansAccent(texte.value.trim()) : "";
        var visibles = 0;

        lignes.forEach(function (l) {
          var garde = !q || l._cherche.indexOf(q) >= 0;
          if (garde) {
            for (var i = 0; i < listes.length; i++) {
              var v = listes[i].value;
              if (v && l.getAttribute("data-" + listes[i].getAttribute("data-champ")) !== v) {
                garde = false;
                break;
              }
            }
          }
          l.hidden = !garde;
          if (garde) visibles++;
        });

        if (compte) {
          compte.textContent = visibles === total
            ? total + " lignes"
            : visibles + " sur " + total;
        }
      };

      if (texte) texte.addEventListener("input", appliquer);
      listes.forEach(function (s) { s.addEventListener("change", appliquer); });

      var vider = bloc.querySelector("[data-role=vider]");
      if (vider) {
        vider.addEventListener("click", function () {
          if (texte) texte.value = "";
          listes.forEach(function (s) { s.value = ""; });
          appliquer();
        });
      }

      appliquer();
    }
  );
})();
