---
layout: page
title: Le jeu social
permalink: /statistiques/jeu-social/
chapeau: >-
  Être visé, voter juste, ou n’être jamais écrit sur un bulletin. Le meilleur prédicteur de victoire de tout le jeu de données est ici.
---

{% assign i = site.data.stats.indicateurs %}

Les épreuves se voient. Le jeu social, non — et c'est pourtant lui qui décide.
Les {{ site.data.stats.conseils.bulletins }} bulletins relevés permettent de le
mesurer, avec des indicateurs empruntés à la statistique de *Survivor* et
adaptés à ce que ces données permettent réellement.

## Le résultat le plus net du site

Un aventurier sur lequel **personne n'a jamais écrit un nom** de toute la
saison, on peut l'appeler un fantôme. Il y en a **{{ i.nb_fantomes }}**, sur
{{ i.comparables }} participations mesurables. Voici ce qu'ils deviennent,
comparés à tout le monde :

{% include graphiques/fantomes-issue.svg %}

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Sort final</th><th class="nombre">Chez les fantômes</th>
  <th class="nombre">Chez tous</th><th class="nombre">Écart</th>
</tr></thead>
<tbody>
{% for x in i.fantomes_issue %}
<tr>
  <td>{{ x.libelle }}</td>
  <td class="nombre">{{ x.part_fantomes }} %</td>
  <td class="nombre">{{ x.part_ensemble }} %</td>
  <td class="nombre">{{ x.part_fantomes | minus: x.part_ensemble | round: 1 }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

**{{ i.fantomes_issue[0].part_fantomes }} % des fantômes gagnent la saison**,
contre {{ i.fantomes_issue[0].part_ensemble }} % de l'ensemble — **cinq fois et
demie plus**. Et seulement {{ i.fantomes_issue[1].part_fantomes }} % d'entre eux
sont éliminés au conseil, contre {{ i.fantomes_issue[1].part_ensemble }} %.

Ne jamais être écrit sur un bulletin est le meilleur prédicteur de victoire que
ces données contiennent — devant l'âge, devant le métier, devant les épreuves.

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Aventurier</th><th>Saison</th><th class="nombre">Conseils traversés</th><th>Sort</th></tr></thead>
<tbody>
{% for x in i.fantomes %}
<tr>
  <td><strong>{{ x.nom }}</strong></td>
  <td>{{ x.titre }} ({{ x.annee }})</td>
  <td class="nombre">{{ x.conseils }}</td>
  <td>{{ x.sort | replace: "_", " " | capitalize }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Être visé, et ce que ça coûte

{% include graphiques/menace-sort.svg %}

<p class="legende-figure">Nombre moyen de voix reçues par conseil assisté,
selon la manière dont l'aventure s'est terminée.</p>

La gradation est sans exception. Un aventurier éliminé au conseil reçoit en
moyenne **{{ i.menace_par_sort.elimine_conseil }} voix par conseil** ; un
vainqueur, **{{ i.menace_par_sort.vainqueur }}**. Neuf fois moins. Entre les
deux, finalistes puis éliminés de la finale s'échelonnent proprement.

Autrement dit : on ne gagne pas Koh-Lanta en survivant aux votes, on le gagne en
n'en recevant pas.

## Être du bon côté du vote

La *justesse de vote* mesure la part des bulletins portés sur la personne qui a
effectivement été éliminée. C'est l'indicateur de qui lit correctement la salle.

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Aventurier</th><th>Saison</th><th class="nombre">Justesse</th><th class="nombre">Bulletins</th></tr></thead>
<tbody>
{% for x in i.meilleure_justesse %}
<tr>
  <td>{{ x.nom }}</td><td>{{ x.titre }} ({{ x.annee }})</td>
  <td class="nombre">{{ x.valeur }} %</td><td class="nombre">{{ x.base }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Cet indicateur est le plus fragile du site, et il faut le dire :
il ne se calcule que sur les conseils dont le dépouillement est complet
<em>et</em> dont l'éliminé a pu être rattaché — quelques dizaines de conseils,
pas les {{ site.data.stats.conseils.conseils }}. Le classement ci-dessus est
donc indicatif, et penche mécaniquement vers les saisons les mieux documentées.
Un seuil de six bulletins écarte les cas où une seule bonne intuition
suffirait à afficher 100 %.</p>

## Survivre quand on est visé

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Aventurier</th><th>Saison</th><th class="nombre">Conseils où visé</th><th class="nombre">Survie</th><th>Sort</th></tr></thead>
<tbody>
{% for x in i.meilleure_evasion %}
<tr>
  <td>{{ x.nom }}</td><td>{{ x.titre }} ({{ x.annee }})</td>
  <td class="nombre">{{ x.base }}</td><td class="nombre">{{ x.valeur }} %</td>
  <td>{{ x.sort | replace: "_", " " }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Ceux-là ont vu leur nom sortir de l'urne plusieurs fois sans jamais partir. La
plupart finissent tout de même par tomber : échapper au vote se paie plus tard.

## Les plus visés

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Aventurier</th><th>Saison</th><th class="nombre">Voix par conseil</th><th class="nombre">Conseils</th><th>Sort</th></tr></thead>
<tbody>
{% for x in i.plus_menaces %}
<tr>
  <td>{{ x.nom }}</td><td>{{ x.titre }} ({{ x.annee }})</td>
  <td class="nombre">{{ x.valeur }}</td><td class="nombre">{{ x.base }}</td>
  <td>{{ x.sort | replace: "_", " " }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
