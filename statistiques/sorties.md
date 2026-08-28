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

**Les ambassadeurs apparaissent puis refluent.** Absents des années 2000
({{ s.sorties.par_decennie[0].ambassadeurs }} %), ils culminent dans les années
2010 à {{ s.sorties.par_decennie[1].ambassadeurs }} % avant de redescendre. La
mécanique a été introduite, éprouvée, puis relativisée par les mécaniques plus
récentes — colliers, totems, duels.

**Le conseil, lui, gagne du terrain** : il fait sortir
{{ s.sorties.par_decennie[2].conseil }} % des aventuriers dans les années 2020
contre {{ s.sorties.par_decennie[0].conseil }} % dans les années 2000. Moins on
abandonne, plus on est éliminé par les autres.

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
