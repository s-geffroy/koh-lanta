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

## Le jeu a changé — mais la date ne se laisse pas fixer

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
  <p><b>Une rupture existe</b> : {{ r.test.ecart_types }} écarts-types au-dessus
  de ce qu’une coupure au hasard obtiendrait, p ajustée
  {{ r.test.p_ajustee }}. Remettez les {{ r.saisons }} saisons dans le désordre
  et aucune coupure n’approche celle-ci.</p>
  <p><b>Mais sa date n’est pas identifiée.</b> La meilleure coupure tombe en
  {{ r.annee_rupture }} et ne devance la deuxième — {{ r.second.annee }} — que
  de <b>{{ r.avance }} %</b>. Et <b>{{ r.nb_proches }} dates</b> tiennent à
  10 % près, réparties sur <b>{{ r.fenetre.etendue }} ans</b>, de
  {{ r.fenetre.debut }} à {{ r.fenetre.fin }}.</p>
</div>

{% include graphiques/ruptures-profil.svg %}

<p class="legende-figure">Ce que chaque date de coupure envisageable sépare. Un
pic isolé désignerait une année ; ce profil-là est un plateau étalé sur
{{ r.fenetre.etendue }} ans.</p>

Il faut le dire dans ce sens, et pas dans l’autre : **le jeu d’avant n’est pas
le jeu d’après, et c’est solide** ; **l’année du basculement, elle, n’est pas
mesurable ici**. La lecture qui reste debout est celle d’une dérive étalée sur
une décennie, pas d’un changement de grille annoncé un vendredi soir.

<p class="note"><strong>Comment on le sait.</strong> Une version antérieure de
cette page datait la rupture de 2012 et l’affirmait sans réserve. Deux
compléments de données — les âges manquants, puis trois cents bulletins de
conseil retrouvés — ont déplacé le maximum, d’abord vers
{{ r.annee_rupture }}, puis en creusant son avance. Un critère qu’une révision
de données déplace de sept ans ne désigne pas une année : il désigne une
époque. C’est <a href="{{ '/statistiques/audience/' | relative_url }}">sur
l’audience</a> qu’on voit à quoi ressemble une date, elle, identifiée — trois
concurrentes serrées sur deux ans au lieu de six sur onze.</p>

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

{% assign objets = r.detail | where: "libelle", "Objets d'immunité en jeu" | first %}
{% assign casting = r.detail | where: "libelle", "Taille du casting" | first %}
{% assign abandon = r.detail | where: "libelle", "Taux d'abandon" | first %}
Le portrait est cohérent, et il ne se réduit à aucun de ses traits. **Les objets
d’immunité apparaissent** — ils étaient à zéro, ils sont à
{{ objets.apres }} par saison. **Le casting grossit**
({{ casting.avant }} → {{ casting.apres }}), **les conseils se multiplient**,
**le casting vieillit**, et **les abandons sont divisés par près de deux**
({{ abandon.avant }} % → {{ abandon.apres }} %).

Ce dernier point vaut d’être souligné : la page
[Comment on sort]({{ '/statistiques/sorties/' | relative_url }}) présente la
chute des abandons comme une évolution graduelle, décennie par décennie. Elle
l’est peut-être bien — la rupture, elle, ne sait pas dire l’année.

<p class="note">Ce que cette rupture ne dit pas. Elle ne dit pas <em>ce qui</em>
a changé en premier, ni pourquoi : six indicateurs qui bougent ensemble ne se
hiérarchisent pas. Elle ne dit pas non plus qu’il n’y en a qu’une — la méthode
en cherche une seule, et avec {{ r.saisons }} saisons il serait imprudent d’en
chercher deux. Et elle ne dit surtout pas l’année : le tableau ci-dessus compare
deux moyennes de part et d’autre d’une coupure qui aurait pu tomber sept ans
plus tôt sans presque rien perdre.</p>
