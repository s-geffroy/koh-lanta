---
layout: page
title: La grille
permalink: /statistiques/grille/
chapeau: >-
  Deux décisions que la production ne commente jamais : le jour où elle réunit
  les tribus, et l’année où elle a changé de jeu.
---

{% assign m = site.data.stats.modeles %}
{% assign f = m.fusion %}
{% assign r = m.ruptures %}

## La réunification tombe à une date, pas à un nombre de joueurs

C’est le geste le plus lourd d’une saison. Deux logiques peuvent le commander :
réunir quand il reste assez peu de monde pour que le jeu individuel commence —
une règle **de jeu** — ou réunir à un épisode fixe pour que la seconde moitié
tienne dans la grille — une règle **de programme**.

Les deux se distinguent, parce que la taille des castings a changé : de
{{ f.casting_min }} aux premières saisons à {{ f.casting_max }} aux récentes.

<p class="note"><strong>Comment on repère la fusion sans la deviner.</strong>
Après elle, les immunités sont individuelles. Le dernier épisode portant une
immunité <em>collective</em> est donc le dernier épisode d’avant la
réunification. {{ f.saisons }} saisons classiques s’y prêtent.</p>

{% include graphiques/fusion-grille.svg %}

<p class="legende-figure">Chaque saison figure deux fois : par l’épisode où la
fusion tombe, et par le nombre de joueurs qu’elle laisse en jeu.</p>

<div class="constat">
  <p>Quand le casting gagne un membre, l’épisode de la fusion bouge de
  <b>{{ f.pente_episode.pente }}</b> — intervalle
  {{ f.pente_episode.bas }} à {{ f.pente_episode.haut }}, p =
  {{ f.pente_episode.p }}. Autrement dit : <b>il ne bouge pas</b>. La médiane
  est l’épisode {{ f.episode_median }}, de 2001 à 2026.</p>
  <p>Le nombre de joueurs restants, lui, bouge de
  <b>{{ f.pente_restants.pente }}</b> ({{ f.pente_restants.bas }} à
  {{ f.pente_restants.haut }}) — presque un pour un.</p>
  <p>La réunification est donc calée sur la <b>grille de diffusion</b>, pas sur
  l’état du jeu. Les castings ont grossi de huit personnes ; la fusion est
  restée à l’épisode {{ f.episode_median }}, et le plateau réuni est passé d’une
  dizaine de joueurs à une quinzaine.</p>
</div>

Cela se voit indirectement ailleurs sur ce site. Les
[petits multiples]({{ '/saisons/' | relative_url }}) montrent des courbes de
survie « remarquablement stables » : elles le sont parce que le calendrier, lui,
n’a pas bougé.

{% if f.ecartees %}
<p class="note">{{ f.ecartees | size }} saison est écartée du calcul :
{% for x in f.ecartees %}<b>{{ x.titre }}</b> porte une immunité collective à
l’épisode {{ x.episode }}, qui ne laisserait que {{ x.restants }} joueurs — ce
n’est pas une réunification mais une épreuve par équipes d’après-fusion. Le
repère y échoue, et on le dit plutôt que de le corriger à la main.{% endfor %}</p>
{% endif %}

## Le jeu a changé en {{ r.annee_rupture }}, sans que personne l’annonce

Une émission ne publie pas ses changements de format. Mais si le jeu a basculé,
plusieurs indicateurs doivent basculer **ensemble**, et à la même date.

<p class="note"><strong>La méthode.</strong> On cherche la coupure qui sépare le
mieux les {{ r.saisons }} saisons classiques en deux régimes, sur six
indicateurs à la fois — taille du casting, durée, âge moyen, taux d’abandon,
nombre de conseils, objets d’immunité. <strong>La date sort des données</strong>,
elle n’est pas choisie. Reste à savoir si cette coupure vaut mieux qu’une
coupure au hasard : on remet donc les saisons dans un ordre aléatoire, et on
recommence.</p>

{% include graphiques/ruptures-nulle.svg %}

<p class="legende-figure">Qualité de la meilleure coupure, face à la meilleure
coupure obtenue sur des saisons remises dans un ordre au hasard.</p>

<div class="constat">
  <p>La rupture tombe en <b>{{ r.annee_rupture }}</b>, entre
  <i>{{ r.derniere_avant.titre }}</i> ({{ r.derniere_avant.annee }}) et
  <i>{{ r.premiere_apres.titre }}</i> ({{ r.premiere_apres.annee }}).
  {{ r.avant }} saisons d’un côté, {{ r.apres }} de l’autre.</p>
  <p>{{ r.test.ecart_types }} écarts-types au-dessus de ce qu’une coupure au
  hasard obtiendrait, p ajustée {{ r.test.p_ajustee }}. Une coupure existe
  toujours ; celle-ci vaut nettement mieux que n’importe quelle autre.</p>
</div>

{% include graphiques/ruptures-serie.svg %}

<p class="legende-figure">Les deux séries qui basculent le plus franchement.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Indicateur</th><th class="nombre">Avant {{ r.annee_rupture }}</th>
  <th class="nombre">Après</th><th class="nombre">Écart, en écarts-types</th>
</tr></thead>
<tbody>
{% for d in r.detail %}
<tr>
  <td>{{ d.libelle }}</td>
  <td class="nombre">{{ d.avant }}</td>
  <td class="nombre">{{ d.apres }}</td>
  <td class="nombre" data-val="{{ d.ecart_types }}">{{ d.ecart_types }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Le portrait est cohérent, et il ne se réduit à aucun de ses traits. **Le casting
grossit** ({{ r.detail[0].avant }} → {{ r.detail[0].apres }}), **les conseils se
multiplient**, **le casting vieillit**, **les objets d’immunité apparaissent** —
ils étaient à zéro avant, ils sont à {{ r.detail[3].apres }} par saison après —
et **les abandons sont divisés par plus d’un tiers**
({{ r.detail[4].avant }} % → {{ r.detail[4].apres }} %).

Ce dernier point vaut d’être souligné : la page
[Comment on sort]({{ '/statistiques/sorties/' | relative_url }}) présente la
chute des abandons comme une évolution graduelle, décennie par décennie. Elle ne
l’est pas : elle fait partie d’une bascule datée.

<p class="note">Ce que cette date ne dit pas. Elle ne dit pas <em>ce qui</em> a
changé en premier, ni pourquoi : six indicateurs qui bougent ensemble ne se
hiérarchisent pas. Elle ne dit pas non plus qu’il n’y a qu’une rupture — la
méthode en cherche une seule, et avec {{ r.saisons }} saisons il serait
imprudent d’en chercher deux. Enfin la durée de la saison, elle, ne bouge
pratiquement pas : ce format-là n’a jamais été touché.</p>
