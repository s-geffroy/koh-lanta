---
layout: page
title: Le jeu social
permalink: /statistiques/jeu-social/
chapeau: >-
  Être visé, voter juste, ou n’être jamais écrit sur un bulletin —
  et pourquoi l’invisibilité n’est que le deuxième prédicteur.
---

{% assign i = site.data.stats.indicateurs %}

Les épreuves se voient. Le jeu social, non — et c’est pourtant lui qui décide.
Les {{ site.data.stats.conseils.bulletins }} bulletins relevés permettent de le
mesurer, avec des indicateurs empruntés à la statistique de *Survivor* et
adaptés à ce que ces données permettent réellement.

## Le résultat le plus net du site

Un aventurier sur lequel **personne n’a jamais écrit un nom** de toute la
saison, on peut l’appeler un fantôme. Il y en a **{{ i.nb_fantomes }}**, sur
{{ i.comparables }} participations mesurables. Voici ce qu’ils deviennent.

<p class="note"><strong>La colonne qui compte est la deuxième.</strong> Un
fantôme a par définition traversé au moins {{ i.seuil_fantome }} conseils sans
être écrit : le comparer à <em>tous</em> les aventuriers, celui qui est sorti au
premier conseil compris, mélangerait deux choses — ne pas être visé, et être
allé loin. La comparaison juste se fait aux {{ i.endurants }} aventuriers qui
ont tenu aussi longtemps. La troisième colonne, elle, est donnée pour mémoire.</p>

{% include graphiques/fantomes-issue.svg %}

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Sort final</th><th class="nombre">Chez les fantômes</th>
  <th class="nombre">Chez ceux qui ont tenu autant</th>
  <th class="nombre">Écart</th><th class="nombre">Chez tous</th>
</tr></thead>
<tbody>
{% for x in i.fantomes_issue %}
<tr>
  <td>{{ x.libelle }}</td>
  <td class="nombre">{{ x.part_fantomes }} %</td>
  <td class="nombre">{{ x.part_endurants }} %</td>
  <td class="nombre">{{ x.part_fantomes | minus: x.part_endurants | round: 1 }}</td>
  <td class="nombre">{{ x.part_ensemble }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

{% assign fv = i.fantomes_issue | where: "sort", "vainqueur" | first %}
{% assign fc = i.fantomes_issue | where: "sort", "elimine_conseil" | first %}
{% assign fa = i.fantomes_issue | where: "sort", "abandon_medical" | first %}

**{{ fv.part_fantomes }} % des fantômes gagnent la saison**, contre
{{ fv.part_endurants }} % de ceux qui ont tenu aussi longtemps : **deux fois et
demie plus**. Et {{ fc.part_fantomes }} % seulement sont éliminés au conseil,
contre {{ fc.part_endurants }} % — mais c’est presque une tautologie : on
n’élimine pas au conseil quelqu’un dont personne n’écrit le nom.

Le vrai écart est ailleurs, et il est inattendu.

<div class="constat">
  <p><b>{{ fa.part_fantomes }} % des fantômes quittent le jeu sur décision
  médicale</b>, contre {{ fa.part_endurants }} % de leurs pairs — quatre fois
  plus.</p>
  <p>Un corps qui lâche n’est plus une menace, et l’on n’écrit pas le nom de
  quelqu’un qu’on voit décliner. L’invisibilité au conseil n’est donc pas
  seulement une performance sociale : c’est aussi, parfois, le signe qu’on a
  cessé d’être un adversaire.</p>
</div>

{% assign v0 = site.data.stats.modeles.alliances.majorite.variables[0] %}
{% assign v1 = site.data.stats.modeles.alliances.majorite.variables[1] %}

Longtemps, cette page a présenté l’invisibilité comme le meilleur prédicteur de
victoire du jeu de données. **Elle ne l’est pas.** Mise en concurrence avec
l’appartenance au camp majoritaire, dans un même modèle, elle passe seconde :
être toujours du bon côté vaut {{ v0.estimation }} points de saison, contre
{{ v1.estimation }} points par voix reçue et par conseil — **cinq fois moins**.
Les deux comptent, mais dans cet ordre.
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}).

Et l’un comme l’autre ne se connaissent qu’en cours de jeu. Au casting,
[rien ne prédit rien]({{ '/statistiques/pronostic/' | relative_url }}).

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
selon la manière dont l’aventure s’est terminée.</p>

La gradation est sans exception. Un aventurier éliminé au conseil reçoit en
moyenne **{{ i.menace_par_sort.elimine_conseil }} voix par conseil** ; un
vainqueur, **{{ i.menace_par_sort.vainqueur }}**. Neuf fois moins. Entre les
deux, finalistes puis éliminés de la finale s’échelonnent proprement.

Autrement dit : on ne gagne pas Koh-Lanta en survivant aux votes, on le gagne en
n’en recevant pas.

## Être du bon côté du vote

La *justesse de vote* mesure la part des bulletins portés sur la personne qui a
effectivement été éliminée. C’est l’indicateur de qui lit correctement la salle.

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
<em>et</em> dont l’éliminé a pu être rattaché — quelques dizaines de conseils,
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

Ceux-là ont vu leur nom sortir de l’urne plusieurs fois sans jamais partir. La
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
