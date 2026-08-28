---
layout: page
title: Comment on sort
permalink: /statistiques/sorties/
chapeau: >-
  Conseil, poteaux, orientation, abandon : neuf façons de quitter le jeu, et des proportions qui ont nettement bougé en vingt-cinq ans.
---

{% assign s = site.data.stats %}

On ne quitte pas Koh-Lanta d’une seule manière. Sur les saisons classiques, les
{{ s.general.participations }} participations se répartissent entre neuf façons
de partir — et leurs proportions ont changé.

{% include graphiques/sorties-repartition.svg %}

**Le conseil reste la voie principale** : {{ s.sorties.repartition[0].part }} %
des sorties. Vient ensuite, et c’est plus surprenant, l’**abandon médical**
({{ s.sorties.repartition[1].part }} %) — devant l’orientation, les poteaux et
les ambassadeurs.

## L’évolution

{% include graphiques/sorties-decennie.svg %}

<p class="legende-figure">Part de chaque motif de sortie, par décennie.</p>

Deux mouvements se lisent nettement :

**Les abandons reculent.** De {{ s.sorties.par_decennie[0].abandons }} % des
sorties dans les années 2000, ils tombent à
{{ s.sorties.par_decennie[2].abandons }} % dans les années 2020 — soit **moitié
moins**. Encadrement médical, sélection, préparation des candidats : le jeu
s’est professionnalisé.

<p class="note">Découpé par décennies, ce recul paraît graduel. Il ne l’est pas.
Une recherche de rupture menée sans a priori sur six indicateurs de saison le
date de <b>{{ site.data.stats.modeles.ruptures.annee_rupture }}</b>, en même
temps que l’agrandissement des castings et l’arrivée des objets d’immunité :
c’est une bascule, pas une pente.
<a href="{{ '/statistiques/grille/' | relative_url }}">La grille</a>.</p>

**Les ambassadeurs apparaissent puis refluent.** Absents des années 2000
({{ s.sorties.par_decennie[0].ambassadeurs }} %), ils culminent dans les années
2010 à {{ s.sorties.par_decennie[1].ambassadeurs }} % avant de redescendre. La
mécanique a été introduite, éprouvée, puis relativisée par les mécaniques plus
récentes — colliers, totems, duels.

**Le conseil, lui, gagne du terrain** : il fait sortir
{{ s.sorties.par_decennie[2].conseil }} % des aventuriers dans les années 2020
contre {{ s.sorties.par_decennie[0].conseil }} % dans les années 2000. Moins on
abandonne, plus on est éliminé par les autres.

## Le risque, à mesure que la saison avance

Une courbe de survie dit combien il en reste. Celle-ci dit tout autre chose :
**parmi ceux qui sont encore en jeu, quelle part s’en va maintenant.** C’est ce
que les statisticiens appellent un taux de hasard, et c’est la seule forme qui
montre que le jeu ne se contente pas de vider le camp — il devient plus
dangereux.

{% include graphiques/risque-courbe.svg %}

<p class="legende-figure">Part des aventuriers encore en jeu qui quittent
l’aventure à ce moment-là, par tranche de dix pour cent de la saison. La finale
est exclue : tout le monde en sort.</p>

{% assign q = site.data.stats.risque %}
Le risque part de **{{ q.tranches[1].risque }} %** au premier dixième de la
saison et atteint **{{ q.tranches[9].risque }} %** au neuvième. Tenir n’allège
donc rien : à mesure que le camp se vide, chaque conseil emporte une part plus
grande de ceux qui restent. Le calcul porte sur {{ q.effectif }} participations
aux saisons classiques.

### Les jours qui font le plus de sortants

{% include graphiques/risque-jours.svg %}

<p class="legende-figure">Nombre de départs par jour de jeu. Les premiers rangs
sont les jours de finale, où plusieurs personnes sortent d’un coup.</p>

Passé les jours de finale, c’est le **jour {{ q.jours_les_plus_meurtriers[2].jour }}**
qui a fait le plus de sortants : {{ q.jours_les_plus_meurtriers[2].sortants }}
départs. Le tout premier conseil est le plus meurtrier de la saison.

## Le détail

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Motif</th><th class="nombre">Aventuriers</th><th class="nombre">Part</th></tr></thead>
<tbody>
{% for x in s.sorties.repartition %}
<tr><td>{{ x.libelle }}</td><td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.part }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Cette courbe se lit moins vite qu’il n’y paraît. Un conseil
fait sortir une personne quel que soit le nombre de présents : le risque
individuel vaut donc mécaniquement 1 ÷ nombre de présents, et cette fraction
monte toute seule à mesure que le camp se vide.
<a href="{{ '/statistiques/equilibre/' | relative_url }}">Le jeu tenu serré</a>
compare les deux courbes : la montée est arithmétique, pas ludique.</p>
