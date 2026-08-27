---
layout: page
title: Les aventuriers
permalink: /aventuriers/
---

{% assign g = site.data.stats.general %}

Les **{{ g.participations }} participations** relevées, toutes saisons
confondues. {{ g.personnes }} personnes différentes : la différence tient aux
{{ site.data.stats.records.nb_multi_participants }} aventuriers revenus jouer
une ou plusieurs fois.

<p class="note">Le tableau se trie en cliquant sur un en-tête de colonne. Sans
JavaScript, il reste entièrement lisible, dans l'ordre chronologique des
saisons puis de sortie.</p>

<div class="tableau-large">
<table id="tableau-aventuriers">
<thead><tr>
  <th>Aventurier</th><th>Saison</th><th class="nombre">Année</th>
  <th class="nombre">Âge</th><th>Sexe</th><th>Métier</th>
  <th>Tribu</th><th class="nombre">Jour de sortie</th><th>Sortie</th>
</tr></thead>
<tbody>
{% assign saisons = site.data.saisons %}
{% for p in site.data.participations %}
  {% assign sa = "" %}
  {% for x in saisons %}{% if x.id == p.saison %}{% assign sa = x %}{% endif %}{% endfor %}
<tr>
  <td>{{ p.nom_complet | default: p.nom }}</td>
  <td>{{ sa.titre }}</td>
  <td class="nombre">{{ sa.annee }}</td>
  <td class="nombre">{{ p.age }}</td>
  <td>{% if p.genre == "f" %}F{% elsif p.genre == "h" %}H{% endif %}</td>
  <td>{{ p.profession }}</td>
  <td>{% if p.couleur %}<span class="pastille" style="background: var(--tribu-{{ p.couleur }})"></span>{% endif %}{{ p.tribu }}</td>
  <td class="nombre">{{ p.jour_sortie }}</td>
  <td>{{ p.motif }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<script>
// Tri du tableau au clic sur un en-tete. La page reste entierement lisible
// sans ce script : il n'ajoute qu'un confort, il ne porte aucune donnee.
(function () {
  var table = document.getElementById('tableau-aventuriers');
  if (!table) return;
  var corps = table.tBodies[0];
  Array.prototype.forEach.call(table.tHead.rows[0].cells, function (entete, colonne) {
    entete.style.cursor = 'pointer';
    entete.setAttribute('title', 'Trier sur cette colonne');
    var croissant = true;
    entete.addEventListener('click', function () {
      var lignes = Array.prototype.slice.call(corps.rows);
      var numerique = entete.classList.contains('nombre');
      lignes.sort(function (a, b) {
        var x = a.cells[colonne].textContent.trim();
        var y = b.cells[colonne].textContent.trim();
        if (numerique) {
          var nx = parseFloat(x), ny = parseFloat(y);
          if (isNaN(nx)) nx = -Infinity;
          if (isNaN(ny)) ny = -Infinity;
          return croissant ? nx - ny : ny - nx;
        }
        return croissant ? x.localeCompare(y, 'fr') : y.localeCompare(x, 'fr');
      });
      lignes.forEach(function (l) { corps.appendChild(l); });
      croissant = !croissant;
    });
  });
})();
</script>
