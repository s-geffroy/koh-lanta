---
layout: page
title: La force réelle
permalink: /statistiques/force/
chapeau: >-
  Sept victoires en quinze épreuves, ou deux en trois ? Le total brut mélange
  le niveau et le temps passé en jeu. On peut les séparer.
---

{% assign m = site.data.stats.modeles %}
{% assign f = m.force %}
{% assign fj = m.force_et_jeu %}

La page [Les épreuves]({{ '/statistiques/epreuves/' | relative_url }}) classe
les aventuriers à leur nombre de victoires, et prévient elle-même que ce total
« dit autant leur nombre de participations que leur niveau ». Elle a raison, et
le problème est plus profond encore : gagner au premier épisode, c’est battre
vingt personnes dont la plupart sortiront vite ; gagner à l’avant-dernier, c’est
en battre quatre, les quatre meilleurs.

## Un modèle qui sépare le niveau du temps de jeu

<p class="note"><strong>Le principe.</strong> On donne à chaque aventurier une
<em>force</em>. La probabilité qu’il gagne une épreuve vaut sa force divisée par
la somme des forces présentes ce jour-là. On cherche ensuite les forces qui
rendent les {{ f.epreuves_retenues }} épreuves individuelles observées les plus
vraisemblables possible. Le classement qui en sort est corrigé
<strong>de l’exposition et de l’adversaire</strong> : un joueur qui gagne deux
fois sur trois en fin de parcours passe devant un joueur qui gagne trois fois sur
quinze au début.</p>

Une difficulté devait être levée d’abord : `epreuves.yml` ne contient que les
**vainqueurs**, jamais la liste des participants. Aucune source ne la donne. Le
plateau de chaque épreuve est donc **reconstruit** — tous ceux qui étaient
encore en jeu à cet épisode.

<div class="constat">
  <p>La reconstruction se contrôle elle-même : <b>le vainqueur d’une épreuve
  doit figurer dans le plateau qu’on lui reconstruit</b>.</p>
  <p>Elle échoue dans <b>{{ f.taux_echec_reconstruction }} %</b> des cas
  ({{ f.vainqueur_hors_plateau }} épreuves sur
  {{ f.epreuves_retenues | plus: f.vainqueur_hors_plateau }}). Ces épreuves-là
  sont écartées, et le taux est publié : c’est la mesure honnête de ce que vaut
  la reconstruction.</p>
</div>

Restent **{{ f.epreuves_retenues }} épreuves individuelles** sur
{{ f.saisons_retenues }} saisons, {{ f.joueurs }} aventuriers, dont
{{ f.classes }} ont disputé au moins {{ f.seuil }} épreuves et sont classés.

## Le classement, avec son incertitude

{% include graphiques/force-classement.svg %}

<p class="legende-figure">Force estimée. Le segment est l’intervalle à 95 %,
obtenu en rejouant {{ m.bootstrap }} fois le calcul sur des épreuves
retirées au sort. Une force de 1 est la moyenne.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Aventurier</th><th class="nombre">Force</th>
  <th class="nombre">Intervalle</th><th class="nombre">Victoires</th>
  <th class="nombre">Épreuves</th><th class="nombre">Ratio</th>
</tr></thead>
<tbody>
{% for d in f.classement %}
<tr>
  <td>{{ d.nom }}</td>
  <td class="nombre" data-val="{{ d.force }}"><b>{{ d.force }}</b></td>
  <td class="nombre">{{ d.bas }} – {{ d.haut }}</td>
  <td class="nombre">{{ d.victoires }}</td>
  <td class="nombre">{{ d.disputees }}</td>
  <td class="nombre">{{ d.ratio }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

**Les intervalles sont larges, et c’est le résultat.** Presque tous se
chevauchent : avec une trentaine d’épreuves au maximum par carrière, ces données
ne permettent pas de départager les premiers. Un classement sans ses intervalles
laisserait croire le contraire.

## Ce que le total brut fait mal voir

{% include graphiques/force-pentes.svg %}

<p class="legende-figure">À gauche le rang au nombre de victoires, à droite le
rang à la force estimée. Une pente montante signale un athlète que le total brut
sous-estime.</p>

{% assign mo = f.plus_forte_montee %}{% assign ch = f.plus_forte_chute %}
La plus forte remontée est celle de **{{ mo.nom }}** : {{ mo.rang_victoires }}<sup>e</sup>
à {{ mo.victoires }} victoires, il passe {{ mo.rang_force }}<sup>e</sup> une fois
l’exposition prise en compte. À l’inverse, **{{ ch.nom }}** descend de la
{{ ch.rang_victoires }}<sup>e</sup> à la {{ ch.rang_force }}<sup>e</sup> place :
ses {{ ch.victoires }} victoires ont été prises sur beaucoup d’épreuves.

## Et le jeu, dans tout ça ?

Deux croyances tenaces se testent ici. On vote contre les forts, dit-on ; et la
force mène loin.

{% include graphiques/force-effets.svg %}

<p class="legende-figure">Rapports de taux de bulletins reçus, à exposition
égale. Un intervalle qui traverse 1 signifie qu’on ne peut pas conclure.</p>

<div class="constat">
  <p>Doubler sa force multiplie les bulletins reçus par
  <b>{{ fj.voix.force.estimation }}</b> — intervalle
  {{ fj.voix.force.bas }} à {{ fj.voix.force.haut }}, qui contient 1.
  <b>On ne vote ni plus ni moins contre les forts.</b></p>
  <p>Sur la distance parcourue, même verdict : doubler sa force fait gagner
  {{ fj.survie.force.estimation }} point de saison, intervalle
  {{ fj.survie.force.bas }} à {{ fj.survie.force.haut }}.
  <b>La force athlétique ne mène nulle part.</b></p>
  <p>La seule chose qui bouge est l’âge : dix ans de plus, et l’on reçoit
  {{ fj.voix.age.estimation }} fois plus de bulletins
  ({{ fj.voix.age.bas }} – {{ fj.voix.age.haut }}).</p>
</div>

C’est la version mesurée de ce que la page des épreuves dit en une phrase : « le
sport gagne les épreuves et perd le jury ». À {{ fj.effectif }} participations,
le lien entre force et parcours est indiscernable de zéro.

<p class="note">Trois réserves. Le plateau est reconstruit et non sourcé : une
épreuve individuelle réservée à un sous-groupe — duel, retour d’exil — est
comptée comme ouverte à tous, ce qui sous-estime les forces des vainqueurs
concernés. Le modèle suppose une force constante sur toute la carrière, alors
qu’un aventurier revenu six ans plus tard n’a plus le même corps. Enfin cinq
saisons n’ont aucun bilan d’épreuves (s03, s09, s12, s14, sp2) et
{{ f.epreuves_ecartees_saison }} épreuves sont écartées parce que leur saison
est trop mal documentée pour reconstruire un plateau.</p>

<p class="note"><strong>Qui manque, et pourquoi.</strong> La dernière réserve
n’est pas une nuance de méthode : elle décide qui figure ici. Un vainqueur de
<em>Malaisie</em>, de <em>Palau</em> ou de <em>Johor</em> peut avoir dominé sa
saison sans apparaître dans ce classement, faute de bilan par épisode à
reconstruire. C’est le cas d’Ugo Lartiche, troisième palmarès de l’histoire au
compte déclaré par le wiki. Ce compte-là existe et il est publié — voir
<a href="{{ '/statistiques/epreuves/' | relative_url }}#le-classement-que-ce-tableau-ne-pouvait-pas-voir">Les
épreuves</a> — mais il n’entre pas dans ce modèle : sans savoir <em>qui était en
lice</em> à chaque épreuve, on ne peut pas corriger de l’exposition, et c’est
précisément ce que cette page fait.</p>
