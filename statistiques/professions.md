---
layout: page
title: Le métier
permalink: /statistiques/professions/
chapeau: >-
  Près de cinq cents métiers déclarés, regroupés en familles — pour répondre à une question simple : lequel mène le plus loin ?
---

{% assign s = site.data.stats %}

Les {{ s.general.participations }} aventuriers déclarent près de cinq cents
métiers différents. Regroupés en familles, ils dessinent un casting — et
permettent de répondre à une question simple : **quel métier mène le plus
loin ?**

## Qui part

{% include graphiques/metiers-casting.svg %}

L’encadrement domine largement le casting : cadres, dirigeants, gérants,
ingénieurs et consultants forment à eux seuls le cinquième des départs. Viennent
ensuite le commerce, puis le sport et le coaching.

## Qui arrive

{% include graphiques/metiers-finale.svg %}

<p class="legende-figure">Part des aventuriers de chaque famille ayant atteint
la finale. Seules les familles comptant au moins quinze aventuriers figurent
ici : en dessous, un seul finaliste suffirait à faire bouger le taux de dix
points.</p>

Le renversement est net. **L’encadrement, première famille du casting, est la
dernière en taux d’accès à la finale** : {{ s.metiers[0].taux_finale }} % contre
{{ s.metiers[1].taux_finale }} % pour le commerce et
{{ s.metiers[2].taux_finale }} % pour le sport. Être nombreux au départ ne
protège de rien.

## Le tableau complet

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Famille</th><th class="nombre">Aventuriers</th><th class="nombre">Part du casting</th>
  <th class="nombre">Survie moyenne</th><th class="nombre">Finales</th>
  <th class="nombre">Taux de finale</th><th class="nombre">Victoires</th>
</tr></thead>
<tbody>
{% for m in s.metiers %}
<tr>
  <td>{{ m.libelle }}</td>
  <td class="nombre">{{ m.effectif }}</td>
  <td class="nombre">{{ m.part_du_casting }} %</td>
  <td class="nombre">{{ m.survie_moyenne }} %</td>
  <td class="nombre">{{ m.finales }}</td>
  <td class="nombre">{{ m.taux_finale }} %</td>
  <td class="nombre">{{ m.victoires }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Le regroupement des métiers en familles est fait par mots-clés,
selon une table publique et relisible. Un intitulé comme « éducateur sportif »
rejoint le sport et non l’enseignement, « maître-nageur » rejoint l’action et le
secours et non le sport : l’ordre des règles tranche ces cas, et il est
documenté. Voir les <a href="{{ '/sources/' | relative_url }}">sources</a>.</p>

<p class="note">Ce renversement tient-il une fois l’âge, le sexe et la saison
tenus constants ? Oui : <a href="{{ '/statistiques/equilibre/' | relative_url }}">
un modèle de durée</a> donne aux métiers d’encadrement un rapport de risque
d’élimination de
{% assign cc = site.data.stats.modeles.equilibre.cox.coefficients | where: "variable", "Metier : encadrement" | first %}
{{ cc.rapport }}, intervalle {{ cc.bas }} à {{ cc.haut }}.</p>
