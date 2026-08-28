---
layout: page
title: Le jeu tenu serré
permalink: /statistiques/equilibre/
chapeau: >-
  Le risque monte à mesure que la saison avance, et la tribu en difficulté
  semble toujours se rattraper. Deux impressions, deux tests.
---

{% assign m = site.data.stats.modeles %}
{% assign eq = m.equilibre %}
{% assign r = eq.rattrapage %}
{% assign cox = eq.cox %}
{% assign hm = m.hasard_mecanique %}

## « Le jeu devient plus dangereux » — non, le camp se vide

La page [Comment on sort]({{ '/statistiques/sorties/' | relative_url }}) publie
une courbe de risque qui monte de 7,6 % au premier dixième de saison à 25,2 % au
neuvième, et la commente : « tenir n’allège rien ». La lecture est tentante. Elle
oublie une chose.

<p class="note"><strong>Un conseil fait sortir une personne, quel que soit le
nombre de présents.</strong> Le risque individuel à un conseil vaut donc
mécaniquement 1 sur le nombre de présents — et cette fraction monte toute seule
à mesure que le camp se vide, sans que le jeu ait changé d’un iota.</p>

{% include graphiques/risque-mecanique.svg %}

<p class="legende-figure">Risque observé de sortir à un conseil, par dixième de
saison, face au simple 1 ÷ nombre de présents. Les deux derniers paliers sont
ceux de la finale, où tout le monde sort le même jour : la comparaison n’y a
plus de sens.</p>

<div class="constat">
  <p>Sur les {{ hm.conseils_hors_finale }} conseils d’avant la finale, le risque
  observé vaut <b>{{ hm.rapport_moyen }} fois</b> le risque purement
  arithmétique — et ce rapport est le même du premier au huitième dixième de
  saison.</p>
  <p>La montée de 8,6 % à 26 % n’est donc <b>pas</b> une propriété du jeu :
  c’est un quotient dont le dénominateur diminue. Le jeu ajoute un facteur
  constant, pas une accélération.</p>
</div>

Le facteur {{ hm.rapport_moyen }} n’est pas rien : il vient des sorties qui ne
passent pas par un conseil — abandons médicaux, doubles éliminations. Mais il ne
grandit pas avec l’avancement. **Tenir n’allège rien, et n’alourdit rien non
plus.**

## La tribu en infériorité se rattrape-t-elle ?

Après un conseil perdu, une tribu se retrouve à cinq contre sept. L’impression
qu’elle gagne alors « comme par miracle » est un classique du genre. Elle se
teste directement.

<div class="constat">
  <p>Sur <b>{{ r.effectif }} épreuves d’immunité collectives</b> réparties sur
  {{ r.saisons }} saisons, chaque aventurier d’avance multiplie la cote de
  victoire par <b>{{ r.rapport_de_cotes }}</b> — intervalle
  {{ r.bas }} à {{ r.haut }}, p = {{ r.p }}.</p>
  <p>L’intervalle contient 1 : <b>l’effectif ne change rien</b>, ni dans un sens
  ni dans l’autre. Il n’y a ni avantage du nombre, ni rattrapage.</p>
</div>

Il faut dire ce que ce résultat ne permet pas. Avec {{ r.effectif }} épreuves et
un écart d’effectif qui ne dépasse jamais {{ r.ecart_max }}, l’intervalle laisse
encore place à un avantage de {{ r.haut }} ou à un handicap de {{ r.bas }} par
personne. **Un effet modéré resterait indétectable.** Ce qu’on peut affirmer,
c’est qu’il n’y a pas d’effet massif.

## Qui sort plus vite, à saison identique

Le reste du site compare des moyennes : les femmes tiennent moins longtemps, les
plus de 45 ans aussi, l’encadrement accède moins à la finale. Ces écarts se
mélangent — les castings n’ont pas la même composition d’une année à l’autre.
Un modèle de durée les sépare.

<p class="note"><strong>Le modèle.</strong> Un modèle de Cox stratifié par
saison : on ne compare jamais que des aventuriers du <em>même</em> plateau, ce
qui neutralise d’un coup la durée de la saison, la taille du casting et
l’époque. Les abandons ne sont pas des éliminations : ils sont censurés, comme
les finalistes et les vainqueurs. {{ cox.effectif }} participations,
{{ cox.eliminations }} éliminations, {{ cox.censures }} sorties censurées.</p>

{% include graphiques/equilibre-cox.svg %}

<p class="legende-figure">Rapports de risque d’élimination. Au-dessus de 1, on
sort plus vite ; en dessous, plus lentement. Un intervalle qui traverse 1
signifie que ces données ne permettent pas de conclure.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Variable</th><th class="nombre">Risque</th><th class="nombre">Intervalle</th><th class="nombre">p</th></tr></thead>
<tbody>
{% for c in cox.coefficients %}
<tr>
  <td>{{ c.variable }}</td>
  <td class="nombre" data-val="{{ c.rapport }}">×{{ c.rapport }}</td>
  <td class="nombre">{{ c.bas }} – {{ c.haut }}</td>
  <td class="nombre">{{ c.p }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Trois lignes méritent d’être lues de près.

{% assign cx = m.equilibre.cox.coefficients %}
{% assign c_revenu = cx | where: "variable", "Déjà venu" | first %}
{% assign c_cadre = cx | where: "variable", "Métier — Encadrement et professions intellectuelles" | first %}
{% assign c_femme = cx | where: "variable", "Femme" | first %}
**« Déjà venu » : risque ×{{ c_revenu.rapport }}.** Un aventurier qui a joué une autre saison est
éliminé **trois fois moins vite**, à âge, sexe, métier et saison identiques.
C’est le plus gros effet de tout le modèle — et c’est un piège. La production
rappelle ceux qui sont allés loin : l’avantage était acquis **avant** le retour,
il n’est pas causé par lui. C’est exactement le biais que documente
[Les revenants]({{ '/statistiques/revenants/' | relative_url }}), et le voir
ressortir ici, en tête d’un modèle multivarié, montre qu’aucun contrôle
statistique ne répare une sélection sur la variable qu’on étudie.

**L’encadrement : risque ×{{ c_cadre.rapport }}**, intervalle
{{ c_cadre.bas }} à {{ c_cadre.haut }}. Les cadres et dirigeants sortent
nettement plus vite que la référence, à âge et sexe égaux. C’est la
version contrôlée de ce que
[Le métier]({{ '/statistiques/professions/' | relative_url }}) montrait en parts
brutes, et le résultat tient.

**Femme : risque ×{{ c_femme.rapport }}**, intervalle
{{ c_femme.bas }} à {{ c_femme.haut }}. L’écart hommes-femmes que le
site décrit depuis toujours **rétrécit jusqu’au bord du détectable** une fois
l’âge, le métier et la saison tenus constants. On ne peut ni l’affirmer ni
l’écarter : l’intervalle effleure 1. C’est la réponse honnête, et elle est moins
tranchée que la moyenne brute ne le laissait croire.

Ni l’âge ni la couleur du bandeau ne bougent — ce dernier point confirmant, par
une autre voie, ce que dit
[Jaune contre rouge]({{ '/statistiques/tribus/' | relative_url }}).

## Les mécaniques n’ont rien changé de mesurable

{% assign me = m.mecaniques %}
Les {{ me.saisons }} saisons exploitables ne portent que
{{ me.mecaniques_testees | size }} mécaniques présentes assez souvent pour être
testées : le collier d’immunité et les destins liés. Ni l’une ni l’autre ne
déplace la dispersion des votes ou le taux d’abandon d’une quantité qu’on puisse
distinguer de zéro — tous les intervalles contiennent zéro.

<div class="tableau-large">
<table>
<thead><tr><th>Mécanique</th><th>Sur</th><th class="nombre">Saisons</th><th class="nombre">Effet</th><th class="nombre">Intervalle</th><th class="nombre">p</th></tr></thead>
<tbody>
{% for e in me.effets %}
<tr>
  <td>{{ e.mecanique | replace: "_", " " }}</td>
  <td>{{ e.sur | replace: "_", " " }}</td>
  <td class="nombre">{{ e.saisons }}</td>
  <td class="nombre">{{ e.effet }}</td>
  <td class="nombre">{{ e.bas }} – {{ e.haut }}</td>
  <td class="nombre">{{ e.p }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Ce n’est pas « les mécaniques ne servent à rien » : c’est « vingt-six saisons ne
suffisent pas à mesurer leur effet ». La différence compte.
