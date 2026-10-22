---
layout: page
title: La force réelle
description: "La force réelle des aventuriers de Koh-Lanta : le total d’épreuves gagnées mélange le niveau et le temps passé en jeu. On peut les séparer."
permalink: /statistiques/force/
chapeau: >-
  Sept victoires en quinze épreuves, ou deux en trois ? Le total brut mélange
  le niveau et le temps passé en jeu. On peut les séparer.
---

{% assign m = site.data.stats.modeles %}
{% assign f = m.force %}
{% assign fj = m.force_et_jeu %}

La page [Les épreuves]({{ '/statistiques/epreuves/' | relative_url }}) classe
les aventuriers à leur nombre de victoires, et prévient elle-même que ce total
« dit autant leur nombre de participations que leur niveau ». Elle a raison, et
le problème est plus profond encore : gagner au premier épisode, c’est battre
vingt personnes dont la plupart sortiront vite ; gagner à l’avant-dernier, c’est
en battre quatre, les quatre meilleurs.

## Un modèle qui sépare le niveau du temps de jeu

<p class="note"><strong>Le principe.</strong> On donne à chaque aventurier une
<em>force</em>. La probabilité qu’il gagne une épreuve vaut sa force divisée par
la somme des forces présentes ce jour-là. On cherche ensuite les forces qui
rendent les {{ f.epreuves_retenues }} épreuves individuelles observées les plus
vraisemblables possible. Le classement qui en sort est corrigé
<strong>de l’exposition et de l’adversaire</strong> : un joueur qui gagne deux
fois sur trois en fin de parcours passe devant un joueur qui gagne trois fois sur
quinze au début.</p>

Une difficulté devait être levée d’abord : `epreuves.yml` ne contient que les
**vainqueurs**, jamais la liste des participants. Aucune source ne la donne. Le
plateau de chaque épreuve est donc **reconstruit** — tous ceux qui étaient
encore en jeu à cet épisode.

<div class="constat">
  <p>La reconstruction se contrôle elle-même : <b>le vainqueur d’une épreuve
  doit figurer dans le plateau qu’on lui reconstruit</b>.</p>
  <p>Elle échoue dans <b>{{ f.taux_echec_reconstruction }} %</b> des cas
  ({{ f.vainqueur_hors_plateau }} épreuves sur
  {{ f.epreuves_tentees }}). Ces épreuves-là
  sont écartées, et le taux est publié : c’est la mesure honnête de ce que vaut
  la reconstruction.</p>
</div>

Restent **{{ f.epreuves_retenues }} épreuves individuelles** sur
{{ f.saisons_retenues }} saisons, {{ f.joueurs }} aventuriers, dont
{{ f.classes }} ont disputé au moins {{ f.seuil }} épreuves et sont classés.

## Le classement, avec son incertitude

{% include graphiques/force-classement.svg %}

<p class="legende-figure">Force estimée. Le segment est l’intervalle à 95 %,
obtenu en rejouant {{ f.bootstrap }} fois le calcul sur des épreuves
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
  <td>{% include lien-aventurier.html id=d.id nom=d.nom %}</td>
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
chevauchent : avec {{ f.disputees_max }} épreuves au plus par carrière, ces
données ne permettent pas de départager les premiers. Un classement sans ses intervalles
laisserait croire le contraire.

## Ce que le total brut fait mal voir

{% include graphiques/force-pentes.svg %}

<p class="legende-figure">À gauche le rang au nombre de victoires, à droite le
rang à la force estimée. Une pente montante signale un athlète que le total brut
sous-estime.</p>

{% assign mo = f.plus_forte_montee %}{% assign ch = f.plus_forte_chute %}
La plus forte remontée est celle de **{{ mo.nom }}** : {{ mo.rang_victoires }}<sup>e</sup>
à {{ mo.victoires }} victoires, puis {{ mo.rang_force }}<sup>e</sup> une fois
l’exposition prise en compte. À l’inverse, **{{ ch.nom }}** descend de la
{{ ch.rang_victoires }}<sup>e</sup> à la {{ ch.rang_force }}<sup>e</sup> place :
ses {{ ch.victoires }} victoires ont été prises sur beaucoup d’épreuves.

## Le tenant du titre : élan ou niveau ?

{% assign tt = site.data.stats.modeles.tenant_du_titre %}
{% assign ttt = site.data.stats.modeles.registre | where: "cle", "tenant_du_titre" | first %}

Voici le genre de chiffre qui se lit tout seul, et dont il faut se méfier quand
on le lit seul.

{% include graphiques/tenant-du-titre.svg %}

<p class="legende-figure">Probabilité de remporter l’épreuve d’immunité
individuelle selon qu’on a gagné la précédente ou non, sur
{{ tt.epreuves }} épreuves et {{ tt.saisons }} saisons.</p>

Celui qui a gagné la dernière immunité gagne la suivante dans
**{{ tt.tenant.probabilite }} %** des cas
({{ tt.tenant.cas }} sur {{ tt.tenant.effectif }}), contre
**{{ tt.autres.probabilite }} %** pour n’importe quel autre présent —
{{ tt.rapport }} fois plus. On y verrait volontiers un **élan** : la confiance, l’habitude du
parcours, l’adversaire qui doute.

### Ce que la force explique déjà

Deux modèles nuls répondent, et c’est leur écart qui est le résultat.

<div class="tableau-large">
<table>
<thead><tr><th>Modèle nul</th><th>Ce qu’il suppose</th><th class="nombre">Écart attendu</th></tr></thead>
<tbody>
<tr><td>uniforme</td><td>chacun gagne avec la même probabilité</td>
    <td class="nombre">{{ tt.attendu_uniforme }} points</td></tr>
<tr><td><b>par la force</b></td><td>chacun gagne selon son <i>θ</i> estimé plus haut</td>
    <td class="nombre"><b>{{ tt.attendu_force }} points</b></td></tr>
<tr><td>observé</td><td>—</td><td class="nombre"><b>{{ tt.brut }} points</b></td></tr>
</tbody>
</table>
</div>

{% include graphiques/tenant-du-titre-nulle.svg %}

<p class="legende-figure">L’écart observé, contre {{ ttt.tirages }} saisons
simulées où les vainqueurs sont tirés <strong>selon les forces estimées</strong>.
Un tirage uniforme, lui, ne produirait que {{ tt.attendu_uniforme }} points.</p>

<div class="constat">
  <p>Contre un tirage uniforme, l’enchaînement ressort :
  {{ tt.ecarts_types_uniforme }} {{ tt.ecarts_types_uniforme_mot }}. Contre un tirage <b>selon les
  forces</b>, il ne reste que {{ ttt.ecart_types }} {{ ttt.ecart_types_mot }}, p ajustée
  {{ ttt.p_ajustee }}. <b>Non concluant.</b></p>
  <p>Autrement dit : {% if tt.force_suffit %}<b>le simple fait que les forts
  sont forts suffit à produire tout l’enchaînement observé</b>{% else %}<b>{{ tt.part_expliquee }} % de l’enchaînement est déjà
  produit par le simple fait que les forts sont forts</b>, et ce qui dépasse
  n’est pas distinguable du hasard{% endif %}. Le tenant du titre ne rejoue pas mieux
  parce qu’il vient de gagner ; il regagne parce que c’était déjà lui le
  meilleur.</p>
</div>

<p class="note"><strong>Ce test est conservateur, et il faut le dire.</strong>
Les forces <i>θ</i> sont ajustées sur ces épreuves-là, enchaînements compris :
un élan réel serait donc en partie absorbé par la force estimée. Conclure
« rien au-delà de la force » est prudent ; conclure l’inverse ne le serait
pas.</p>

## Et le jeu, dans tout ça ?

Deux croyances tenaces se testent ici. On vote contre les forts, dit-on ; et la
force mène loin.

{% include graphiques/force-effets.svg %}

<p class="legende-figure">Rapports de taux de bulletins reçus, à exposition
égale. Un intervalle qui traverse 1 signifie qu’on ne peut pas conclure.</p>

<div class="constat">
  <p>Doubler sa force multiplie les bulletins reçus par
  <b>{{ fj.voix.force.estimation }}</b> — intervalle
  {{ fj.voix.force.bas }} à {{ fj.voix.force.haut }}, p ajustée
  {{ fj.voix.force.p_ajustee }}. L’intervalle touche 1 : <b>les forts ne
  reçoivent pas davantage de bulletins</b>, et peut-être un peu moins, sans
  qu’on puisse l’affirmer. Gagner l’immunité, ce qui fait la force, rend
  d’ailleurs inéligible au vote : une part de cet écart est mécanique.</p>
  <p>Sur la distance parcourue, rien : doubler sa force fait gagner
  {{ fj.survie.force.estimation }} point de saison, intervalle
  {{ fj.survie.force.bas }} à {{ fj.survie.force.haut }}.
  <b>La force athlétique ne mène pas plus loin.</b></p>
  <p>L’âge ne tranche pas non plus : dix ans de plus, et l’on reçoit
  {{ fj.voix.age.estimation }} fois les bulletins, intervalle
  {{ fj.voix.age.bas }} à {{ fj.voix.age.haut }}, qui contient 1.</p>
</div>

C’est la version mesurée de ce que la page des épreuves dit en une phrase : « le
sport gagne les épreuves et perd le jury ». À {{ fj.effectif }} participations,
le lien entre force et parcours est indiscernable de zéro.

<p class="note">Trois réserves. Le plateau est reconstruit et non sourcé : une
épreuve individuelle réservée à un sous-groupe — duel, retour de l’île des bannis ou de l’exil — est
comptée comme ouverte à tous, ce qui sous-estime les forces des vainqueurs
concernés. Le modèle suppose une force constante sur toute la carrière, alors
qu’un aventurier revenu six ans plus tard n’a plus le même corps. Enfin
{{ f.epreuves_ecartees_saison }} épreuves sont écartées parce que leur saison
est trop mal documentée pour reconstruire un plateau, et
{{ site.data.stats.mots.saisons_source_unique }} saisons ne sont relevées que
sur une seule source ({{ site.data.stats.epreuves.saisons_source_unique_texte }}).</p>

<p class="note"><strong>Qui manque, et pourquoi.</strong> La dernière réserve
n’est pas une nuance de méthode : elle décide qui figure ici. Jusqu’au
20 octobre 2026, un vainqueur de <em>Malaisie</em>, de <em>Palau</em> ou de
<em>Johor</em> ne pouvait pas apparaître dans ce classement, faute de bilan par
épisode à reconstruire. C’était le cas d’Ugo Lartiche, troisième palmarès de
l’histoire au compte déclaré par le wiki — voir
<a href="{{ '/statistiques/epreuves/' | relative_url }}#ce-que-disent-les-fiches-pour-comparer">Les
épreuves</a>. Ces saisons sont désormais relevées, sur la seule foi du guide
d’épisodes du wiki <em>Survivor</em>, et Ugo Lartiche figure dans ce
classement. Une source unique reste une réserve : sans recoupement, on sait
<em>qui était en lice</em>, mais une erreur du guide passerait inaperçue.</p>
