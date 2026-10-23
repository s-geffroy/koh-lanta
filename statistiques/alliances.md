---
layout: page
title: Les alliances
description: "Les alliances de Koh-Lanta existent-elles ailleurs que dans le récit ? Les bulletins de vote permettent de trancher, saison par saison."
permalink: /statistiques/alliances/
chapeau: >-
  Le programme raconte des alliances à chaque épisode. Rien n’oblige à ce
  qu’elles existent au-delà du récit. Les bulletins permettent de trancher.
---

{% assign m = site.data.stats.modeles %}
{% assign a = m.alliances %}
{% assign t = a.test %}

Un conseil où six personnes écrivent le même nom peut être une alliance — ou un
simple ralliement du moment, refait à neuf chaque semaine. La différence n’est
pas dans le montage, elle est dans la **suite** : une alliance, c’est ce qui
survit d’un conseil au suivant.

<p class="note"><strong>La mesure.</strong> On prend chaque paire d’aventuriers
présente à deux conseils consécutifs, et on compare deux probabilités : voter
ensemble <em>après</em> avoir voté ensemble, et voter ensemble après avoir voté
séparément. L’écart entre les deux est la persistance. À zéro, chaque conseil
repart de rien. Base : {{ a.bulletins }} bulletins, {{ a.conseils }} conseils au
dépouillement complet, {{ a.saisons }} saisons, {{ a.paires_suivies }} paires
suivies d’un conseil à l’autre.</p>

## Les alliances existent, et elles sont solides

{% include graphiques/alliances-persistance.svg %}

<p class="legende-figure">Écart entre les deux probabilités, en points. La
silhouette est ce que donnent {{ t.tirages_texte }} redistributions des bulletins à
l’intérieur de chaque conseil — chaque conseil gardant exactement sa
répartition de voix.</p>

<div class="constat">
  <p>Deux aventuriers qui ont voté ensemble votent encore ensemble au conseil
  suivant dans <b>{{ a.apres_ensemble }} %</b> des cas. Deux aventuriers qui ont
  voté séparément : <b>{{ a.apres_separes }} %</b>.</p>
  <p>{{ t.observe }} points d’écart, contre {{ t.attendu }} attendus si les
  bulletins n’étaient que du bruit — soit <b>{{ t.ecart_types }} {{ t.ecart_types_mot }}</b>.
  C’est de très loin le signal le plus fort de tout ce site.</p>
</div>

Le modèle nul mérite une phrase, parce que c’est lui qui donne son sens au
résultat. On ne compare pas à « personne ne vote pareil » : on rebat les
bulletins **à l’intérieur de chaque conseil**, en gardant intacte la répartition
des voix — quatre contre l’un, deux contre l’autre. Ce qui disparaît est le seul
lien entre conseils. Tout ce qui reste après ce brassage est donc de la
coordination qui traverse le temps.

## Ce que ça vaut, en jours de jeu

L’appartenance au camp majoritaire est une variable que le programme montre en
permanence sans jamais la mesurer. On peut la chiffrer : pour chaque aventurier,
la part de ses conseils passés du côté du nom qui sort.

{% include graphiques/alliances-majorite.svg %}

<p class="legende-figure">Points de saison gagnés ou perdus, le nombre de
conseils traversés tenu constant. Le bulletin écrit le soir de son élimination,
et les voix qui éliminent, sont retirés.</p>

{% assign v0 = a.majorite.variables[0] %}{% assign v1 = a.majorite.variables[1] %}

<div class="constat">
  <p>Passer de « jamais du bon côté » à « toujours du bon côté » vaut
  <b>{{ v0.estimation }} point{% if v0.estimation_pluriel %}s{% endif %} de saison</b> — intervalle
  {{ v0.bas }} à {{ v0.haut }}.</p>
  <p>Dans le même modèle, l’effet d’une voix de plus reçue par conseil vaut
  {{ v1.estimation }} point{% if v1.estimation_pluriel %}s{% endif %} ({{ v1.bas }} à {{ v1.haut }}) : rien de
  distinguable de zéro. <b>Être du bon côté compte ; être visé, une fois les
  voix qui éliminent retirées, ne se distingue pas.</b></p>
</div>

Ce résultat a été corrigé le 23 octobre 2026. Le modèle comptait jusque-là le
bulletin écrit le soir de son élimination — minoritaire par construction,
puisqu’on ne vote pas pour soi — et les voix reçues ce soir-là, celles qui
éliminent. Il mesurait donc en partie la sortie elle-même : le coefficient de
majorité était presque deux fois plus grand, et la page en tirait un rapport
(« 3,9 fois ») qui divisait un effet par part par un effet par voix, deux
unités différentes. Ni l’un ni l’autre ne tient.

<p class="note"><strong>Une réserve, dans les deux sens.</strong> Le modèle
tient constant le nombre de conseils traversés. C’est un contrôle sévère :
traverser beaucoup de conseils, c’est déjà avoir survécu, et une part de ce
qu’on cherche à expliquer est absorbée par lui. Sans ce contrôle on publierait
une tautologie déguisée. Rien ne permet de dire si le chiffre affiché est
au-dessus ou au-dessous de l’effet réel.</p>

## Ceux qui ne se sont jamais trompés de camp

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Aventurier</th><th>Saison</th><th class="nombre">Conseils</th>
  <th class="nombre">Du bon côté</th><th class="nombre">Voix reçues</th>
  <th class="nombre">Saison tenue</th>
</tr></thead>
<tbody>
{% for x in a.les_plus_souvent_du_bon_cote %}
<tr>
  <td><strong>{% include lien-aventurier.html id=x.id nom=x.nom %}</strong></td>
  <td>{{ x.saison }}</td>
  <td class="nombre">{{ x.conseils }}</td>
  <td class="nombre" data-val="{{ x.part }}">{{ x.part }} %</td>
  <td class="nombre">{{ x.voix }}</td>
  <td class="nombre">{{ x.survie }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Les duos qui n’ont jamais divergé

{% assign du = site.data.stats.indicateurs.duos %}

Tout ce qui précède mesure la persistance **en agrégat** : elle ne dit jamais
qui. Voici les paires elles-mêmes — celles qui, sur au moins
{{ du.seuil }} conseils traversés ensemble, ont écrit le même nom le plus souvent.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Le duo</th><th>Saison</th><th class="nombre">Année</th>
  <th class="nombre">Conseils ensemble</th><th class="nombre">Mêmes bulletins</th>
  <th class="nombre">Part</th>
</tr></thead>
<tbody>
{% for x in du.meilleures %}
<tr>
  <td><strong>{{ x.un }}</strong> et <strong>{{ x.deux }}</strong></td>
  <td>{{ x.titre }}</td><td class="nombre">{{ x.annee }}</td>
  <td class="nombre">{{ x.ensemble }}</td>
  <td class="nombre" data-val="{{ x.accord }}"><b>{{ x.accord }}</b></td>
  <td class="nombre">{{ x.part }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Le dénominateur est exigeant, et c’est lui qui fait la rareté de
ce tableau : deux personnes ne se comparent que sur les conseils où
<em>toutes deux</em> ont voté <em>et</em> dont le dépouillement est complet.
{{ du.paires }} paires seulement franchissent le seuil de {{ du.seuil }} conseils
communs, sur {{ site.data.stats.general.paires_possibles_texte }} possibles. Un duo absent d’ici n’est pas un duo
faible : c’est le plus souvent un duo qu’on ne peut pas mesurer.</p>

## L’alliance protège : la trahison est rare

{% assign tr = m.trahison %}{% assign tt = tr.test %}

Le programme met en scène le retournement à chaque saison. Il se compte : sur
les {{ tr.bulletins }} bulletins dont l’auteur avait déjà un allié à ce
moment-là, combien visent cet allié ?

{% include graphiques/trahison.svg %}

<p class="legende-figure">Part des bulletins visant quelqu’un avec qui l’auteur
avait déjà voté. La silhouette est le même brassage que plus haut, à jeu de
cibles constant.</p>

<div class="constat">
  <p><b>{{ tt.observe }} %</b> des bulletins visent un ancien allié — contre
  <b>{{ tt.attendu }} %</b> attendus. {{ tt.ecart_types }} {{ tt.ecart_types_mot }}.</p>
  <p>L’alliance ne se contente donc pas de faire voter ensemble : elle
  <b>protège</b>. À jeu de cibles identique, on écrit le nom d’un ancien allié
  nettement moins souvent qu’un partage au hasard des bulletins ne le ferait.</p>
</div>

{% assign ef = tr.effet %}
Et quand on trahit quand même ? **Rien.** Passer de « jamais » à « toujours »
viser un ancien allié vaut {{ ef.estimation }} point{% if ef.estimation_pluriel %}s{% endif %} de saison —
intervalle {{ ef.bas }} à {{ ef.haut }}, p = {{ ef.p }}. Sur
{{ ef.effectif }} participations, la trahison est **sans effet mesurable** :
on ne voit ni qu’elle paie, ni qu’elle coûte — l’intervalle n’exclut ni l’un
ni l’autre.

## Après la réunification, un camp tombe-t-il en série ?

{% assign de = m.decimation %}{% assign dt = de.test %}

Si les blocs survivent à la réunification, cela doit se voir dans **l’ordre** des
sorties : le camp majoritaire démonte l’autre un par un, au lieu que les
départs alternent.

{% include graphiques/decimation.svg %}

<p class="legende-figure">Nombre de fois où deux sorties consécutives viennent
de la même tribu initiale, sur {{ de.saisons }} saisons et {{ de.sorties }}
sorties d’après-réunification. La silhouette est ce que donne un ordre de sortie tiré
au sort, à composition de camps identique.</p>

<div class="constat">
  <p>{{ dt.observe }} enchaînements observés contre {{ dt.attendu }} attendus,
  <b>{{ dt.ecart_types }} {{ dt.ecart_types_mot }}</b>, p ajustée {{ dt.p_ajustee }}.</p>
  <p>L’écart va dans le sens d’un camp démonté un par un, mais <b>il ne passe
  pas la correction pour tests multiples</b> : on ne peut pas affirmer que les
  sorties d’après-réunification se suivent par tribu initiale.</p>
</div>

<p class="note"><strong>Ce résultat a basculé le 23 octobre 2026.</strong>
Plusieurs sorties tombent dans le même épisode — les finalistes, l’éliminé
aux poteaux et le vainqueur, notamment. Elles étaient rangées entre elles par
ordre alphabétique d’identifiant, ce qui fabriquait des enchaînements. Rangées
par jour de sortie puis par rang final, elles en donnent moins, et le test,
retenu jusque-là (p ajustée 0,0005), ne l’est plus.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Saison</th><th class="nombre">Année</th>
  <th class="nombre">Sorties après réunification</th>
  <th class="nombre">Plus longue série</th><th>Ordre des sorties</th>
</tr></thead>
<tbody>
{% for d in de.detail %}
<tr>
  <td>{{ d.titre }}</td>
  <td class="nombre">{{ d.annee }}</td>
  <td class="nombre">{{ d.joueurs }}</td>
  <td class="nombre">{{ d.plus_longue_serie }}</td>
  <td><code>{{ d.suite }}</code></td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Chaque lettre est la tribu initiale d’un sortant, dans
l’ordre : <code>J</code> pour jaune, <code>R</code> pour rouge.
{{ site.data.stats.mots.serie_decimation_maj }} sorties de la même tribu d’affilée en
{{ de.detail[0].annee }} ne prouvent rien à elles seules ; et, accumulées sur
{{ de.saisons }} saisons, ces séries ne suffisent pas à passer la correction.</p>

<p class="note"><strong>Ce que l’alliance vaut, en probabilité de survie.</strong>
Cette page mesure l’existence et la durée des alliances. Leur <em>rendement</em>
se lit ailleurs : sachant qu’il ne reste plus un seul des gens avec qui on a
déjà voté, le risque de partir au conseil monte à
{% assign pp = site.data.stats.modeles.pire_place %}{% assign ppa = pp.isolement | where: "modalite", "tous ses alliés sont partis" | first %}<b>{{ ppa.probabilite }} %</b>
pour qui a vu partir tous ses alliés, contre
{{ pp.isolement[3].probabilite }} % pour qui garde trois alliés ou plus
(<a href="{{ '/statistiques/pire-place/' | relative_url }}">la pire place au conseil</a>).</p>

<p class="note">Ce que cette page ne dit pas. Elle ne distingue pas <em>former</em>
une majorité de <em>la rejoindre</em> : les bulletins ne portent pas d’heure, et
rien dans ces données ne dit qui a proposé le nom. Un suiveur discipliné et un
meneur ont ici exactement le même score. Elle ne porte par ailleurs que sur les
{{ a.conseils }} conseils au dépouillement garanti complet, sur les
{{ site.data.stats.conseils.conseils }} relevés : les saisons les mieux
documentées y pèsent plus que les autres.</p>
