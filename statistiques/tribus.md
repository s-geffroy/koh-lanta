---
layout: page
title: Jaune contre rouge
permalink: /statistiques/tribus/
---

{% assign s = site.data.stats %}

C'est une question qui revient à chaque saison : vaut-il mieux commencer chez
les Jaunes ou chez les Rouges ? Sur {{ s.general.saisons_classiques }} saisons
classiques, la réponse tient en une ligne.

## Les victoires

{% include graphiques/tribus-victoires.svg %}

**{{ s.couleurs[0].victoires }} victoires pour le jaune, {{ s.couleurs[1].victoires }}
pour le rouge.** Égalité stricte. Les couleurs minoritaires — bleu, vert,
violet, orange — n'apparaissent que sur les saisons à trois ou quatre tribus, et
leurs effectifs sont trop faibles pour qu'on en tire quoi que ce soit.

## La survie

{% include graphiques/tribus-survie.svg %}

<p class="legende-figure">Part de la durée totale de la saison passée dans le
jeu, en moyenne, selon la couleur de la tribu de départ.</p>

L'écart entre jaune et rouge se compte en points, sur des effectifs de plus de
deux cents aventuriers chacun : il n'y a pas de signal.

## Le détail

<div class="tableau-large">
<table>
<thead><tr>
  <th>Couleur</th><th class="nombre">Aventuriers</th>
  <th class="nombre">Survie moyenne</th><th class="nombre">Finales</th>
  <th class="nombre">Taux de finale</th><th class="nombre">Victoires</th>
</tr></thead>
<tbody>
{% for c in s.couleurs %}
<tr>
  <td><span class="pastille" style="background: var(--tribu-{{ c.couleur }})"></span>{{ c.couleur | capitalize }}</td>
  <td class="nombre">{{ c.effectif }}</td>
  <td class="nombre">{{ c.survie_moyenne }} %</td>
  <td class="nombre">{{ c.finales }}</td>
  <td class="nombre">{{ c.taux_finale }} %</td>
  <td class="nombre">{{ c.victoires }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">La couleur noire correspond à la tribu maudite de 2024 et à
l'île des héros de 2020 : deux aventuriers seulement, aucune conclusion
possible.</p>
