---
layout: page
title: Comment on sort
description: "Comment on sort de Koh-Lanta : conseil, épreuve, poteaux, orientation, abandon — onze façons de quitter le jeu, et des proportions qui ont bougé."
permalink: /statistiques/sorties/
chapeau: >-
  Conseil, épreuve, poteaux, orientation, abandon : onze façons de quitter le jeu, et des proportions qui ont nettement bougé en vingt-cinq ans.
---

{% assign s = site.data.stats %}

On ne quitte pas Koh-Lanta d’une seule manière. Sur les saisons classiques, les
{{ s.sorties.effectif }} participations se répartissent entre
{{ s.sorties.repartition | size }} façons de partir — et leurs proportions ont changé.

{% include graphiques/sorties-repartition.svg %}

**Le conseil reste la voie principale** : {{ s.sorties.repartition[0].part }} %
des sorties. Vient ensuite, et c’est plus surprenant, l’**abandon médical**
({{ s.sorties.repartition[1].part }} %) — devant l’orientation, les poteaux et
les ambassadeurs.

## L’évolution

{% include graphiques/sorties-decennie.svg %}

<p class="legende-figure">Part de chaque motif de sortie, par décennie.</p>

Deux mouvements se lisent nettement :

**Les abandons reculent.** De {{ s.sorties.par_decennie[0].abandons }} % des
sorties dans les années 2000, ils tombent à
{{ s.sorties.par_decennie[2].abandons }} % dans les années 2020 — soit
**{{ s.sorties.abandons_rapport }} fois moins**. Encadrement médical, sélection, préparation des candidats, ou simple
changement de règles sur ce qui compte comme abandon : ces données ne disent
pas laquelle de ces raisons l’emporte.

<p class="note">Découpé par décennies, ce recul paraît graduel, et rien ne
permet de dire mieux. Une recherche de rupture menée sans a priori sur
{{ s.mots.indicateurs_rupture }} indicateurs de saison place sa meilleure
coupure en <b>{{ site.data.stats.modeles.ruptures.annee_rupture }}</b>, avec
l’agrandissement des castings et l’arrivée des objets d’immunité ; mais
<a href="{{ '/statistiques/grille/' | relative_url }}">la grille</a> montre
qu’une évolution régulière produit une coupure aussi nette. Bascule ou pente,
les données ne tranchent pas.</p>

**Les sorties aux ambassadeurs apparaissent puis refluent.** Absentes de ces
comptes dans les années 2000 ({{ s.sorties.par_decennie[0].ambassadeurs }} %),
elles culminent dans les années 2010 à {{ s.sorties.par_decennie[1].ambassadeurs }} %
avant de redescendre. La mécanique, elle, existe depuis le début : ce sont ses
règles qui ont changé. Ce n’est qu’à partir de *Palau* (2009) que les
ambassadeurs doivent éliminer eux-mêmes un aventurier, et la seule élimination
de cette saison-là, celle d’Alexandre, ne compte pas ici : il est revenu en jeu
avant de sortir pour de bon.

**Le conseil, lui, ne gagne pas de terrain** : il fait sortir
{{ s.sorties.par_decennie[2].conseil }} % des aventuriers dans les années 2020,
contre {{ s.sorties.par_decennie[0].conseil }} % dans les années 2000. La place
que laissent les abandons ne lui revient pas. Ce qui monte, ce sont les
**épreuves éliminatoires**, où le dernier quitte le jeu sans que personne ait
voté : {{ s.sorties.par_decennie[0].epreuve }} % des sorties dans les années
2000, {{ s.sorties.par_decennie[2].epreuve }} % dans les années 2020.

<p class="note"><strong>Cette page a longtemps écrit l’inverse.</strong>
Jusqu’au 21 octobre 2026, elle concluait que le conseil gagnait du terrain
(63,3 % des sorties dans les années 2000, 67 % dans les années 2020) et que,
moins on abandonnait, plus on était éliminé par les autres. Vingt-trois
sorties par épreuve éliminatoire y étaient comptées comme des éliminations
au conseil, et quinze datent des années 2020. Rendues à leur nature, elles
renversent la conclusion.</p>

## Le risque, à mesure que la saison avance

Une courbe de survie dit combien il en reste. Celle-ci dit tout autre chose :
**parmi ceux qui sont encore en jeu, quelle part s’en va maintenant.** C’est ce
que les statisticiens appellent un taux de risque instantané, et c’est la seule forme qui
montre que le risque, lui, monte à mesure que le camp se vide — et
[l’équilibre]({{ '/statistiques/equilibre/' | relative_url }}) montre que cette
montée est d’abord arithmétique.

{% include graphiques/risque-courbe.svg %}

<p class="legende-figure">Part des aventuriers encore en jeu qui quittent
l’aventure à ce moment-là, par tranche de dix pour cent de la saison. La finale
est exclue : tout le monde en sort.</p>

{% assign q = site.data.stats.risque %}
Le risque part de **{{ q.tranches[1].risque }} %** entre 10 et 20 % de la
saison et atteint **{{ q.tranches[9].risque }} %** dans le dernier dixième. Tenir n’allège
donc rien : à mesure que le camp se vide, chaque conseil emporte une part plus
grande de ceux qui restent. Le calcul porte sur {{ q.effectif }} participations
aux saisons classiques.

### Les jours qui font le plus de sortants

{% include graphiques/risque-jours.svg %}

<p class="legende-figure">Nombre de départs par jour de jeu. Les premiers rangs
sont les jours de finale, où plusieurs personnes sortent d’un coup.</p>

Passé les jours de finale, c’est le **jour {{ q.jours_les_plus_meurtriers[2].jour }}**
qui a fait le plus de sortants ({{ q.jours_les_plus_meurtriers[2].sortants }}
départs). Hors finale, c’est en tout début de saison qu’on sort le plus.

## Le détail

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Motif</th><th class="nombre">Aventuriers</th><th class="nombre">Part</th></tr></thead>
<tbody>
{% for x in s.sorties.repartition %}
<tr><td>{{ x.libelle }}</td><td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.part }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Cette courbe se lit moins vite qu’il n’y paraît. Un conseil
fait sortir une personne quel que soit le nombre de présents : le risque
individuel vaut donc mécaniquement 1 ÷ nombre de présents, et cette fraction
monte toute seule à mesure que le camp se vide.
<a href="{{ '/statistiques/equilibre/' | relative_url }}">Le jeu tenu serré</a>
compare les deux courbes : la montée est arithmétique, pas ludique.</p>
