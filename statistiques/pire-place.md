---
layout: page
title: La pire place au conseil
permalink: /statistiques/pire-place/
chapeau: >-
  Deux signaux se lisent avant le vote : le nom qui est sorti la fois d’avant,
  et le nombre d’alliés encore assis autour du feu. Ensemble, ils font passer le
  risque de 11 % à 47 %.
---

{% assign m = site.data.stats.modeles %}
{% assign p = m.pire_place %}
{% assign reg = m.registre %}
{% assign ti = reg | where: "cle", "vote_isole" | first %}
{% assign tm = reg | where: "cle", "dos_au_mur" | first %}

Les deux pages précédentes prennent les signaux **un par un** :
[Sachant le conseil d’avant]({{ '/statistiques/conditionnelles/' | relative_url }})
pour le passé, [Sachant qui est autour du feu]({{ '/statistiques/autour-du-feu/' | relative_url }})
pour la place qu’on occupe. Celle-ci pose la question qui reste : **comptent-ils
ensemble, ou l’un n’est-il que l’ombre de l’autre ?**

## Un allié, ici, c’est quelqu’un avec qui on a écrit le même nom

L’alliance ne se déclare pas, elle se lit dans l’urne. Deux personnes qui ont
porté le même nom au même conseil ont voté ensemble ; c’est la définition
qu’emploie déjà [Les alliances]({{ '/statistiques/alliances/' | relative_url }}),
et elle ne se défait jamais dans ce calcul — on mesure « **a-t-il déjà été mon
allié** », pas « l’est-il encore ».

<ul class="chiffres">
  <li class="chiffre"><b>{{ p.presences }}</b><span>présences à un conseil</span></li>
  <li class="chiffre"><b>{{ p.conseils }}</b><span>conseils, sur {{ p.saisons }} saisons</span></li>
  <li class="chiffre"><b>{{ p.cumul[2].probabilite }} %</b><span>de risque quand les deux signaux sont réunis</span></li>
</ul>

## L’isolement, décomposé

{% include graphiques/pire-place-isolement.svg %}

<p class="legende-figure">Probabilité d’être éliminé selon le nombre de gens
avec qui on a déjà voté et qui sont encore présents, comparée au tirage au
sort.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Alliés encore présents</th><th class="nombre">Présences</th>
  <th class="nombre">Éliminations</th><th class="nombre">Probabilité</th>
  <th class="nombre">Intervalle</th><th class="nombre">Le hasard</th>
</tr></thead>
<tbody>
{% for x in p.isolement %}
<tr>
  <td>{{ x.modalite | capitalize }}</td>
  <td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.cas }}</td>
  <td class="nombre" data-val="{{ x.probabilite }}"><b>{{ x.probabilite }} %</b></td>
  <td class="nombre">{{ x.bas }} – {{ x.haut }} %</td>
  <td class="nombre">{{ x.hasard }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

{% include graphiques/pire-place-nulle.svg %}

<p class="legende-figure">Écart entre partir sans un seul allié présent et
partir quand il en reste au moins un, contre {{ ti.tirages }} tirages où
l’éliminé de chaque conseil est pris au hasard parmi les présents.</p>

<div class="constat">
  <p>N’avoir plus personne avec qui on ait déjà voté ajoute
  <b>{{ ti.observe | round: 1 }} points</b> de risque :
  {{ ti.ecart_types }} écarts-types au-dessus du hasard, p ajustée
  {{ ti.p_ajustee }}.</p>
  <p>Et les deux formes de l’isolement ne se valent pas. Avoir vu ses alliés
  partir mène à {{ p.isolement[1].probabilite }} % ; <b>n’avoir jamais voté avec
  personne</b>, à <b>{{ p.isolement[0].probabilite }} %</b> — près de trois fois
  le hasard. Le joueur qui n’a jamais réussi à faire coïncider son bulletin avec
  celui d’un autre est, de toutes les positions mesurées sur ce site, la plus
  exposée.</p>
</div>

## L’adversaire, encore là ou déjà parti

L’allié a un miroir : **celui qui a déjà écrit votre nom.** On s’attend à ce
qu’un adversaire encore assis là soit plus dangereux qu’un adversaire éliminé
depuis. Ce n’est pas le cas.

{% include graphiques/pire-place-adverse.svg %}

<p class="legende-figure">Probabilité d’être éliminé selon que ceux qui ont déjà
écrit votre nom sont encore présents ou non.</p>

<div class="tableau-large">
<table>
<thead><tr><th>Ceux qui ont déjà écrit mon nom</th><th class="nombre">Présences</th><th class="nombre">Éliminations</th><th class="nombre">Probabilité</th><th class="nombre">Le hasard</th></tr></thead>
<tbody>
{% for x in p.adverse %}
<tr><td>{{ x.modalite | capitalize }}</td>
    <td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.cas }}</td>
    <td class="nombre"><b>{{ x.probabilite }} %</b></td>
    <td class="nombre">{{ x.hasard }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

**La menace ne s’éteint pas avec son auteur.** Avoir été visé par des gens tous
partis depuis mène à {{ p.adverse[1].probabilite }} % ; en avoir au moins un
encore là, à {{ p.adverse[2].probabilite }} %. L’écart est dans le sens
inverse de l’intuition et bien trop petit pour compter. Ce qui compte est
d’avoir été visé **un jour** — le camp a désigné quelqu’un, et cette
désignation lui survit.

Aucun test n’est déclaré ici : la question est la même que celle du
[nom sorti la fois d’avant]({{ '/statistiques/conditionnelles/' | relative_url }}),
posée sous un autre angle. La compter deux fois dans la correction pour tests
multiples reviendrait à la payer deux fois.

## Les deux signaux ensemble

{% include graphiques/pire-place-cumul.svg %}

<p class="legende-figure">Probabilité d’être éliminé selon qu’on cumule zéro, un
ou deux signaux : avoir été visé au conseil précédent, et n’avoir plus aucun
allié parmi les présents.</p>

<div class="tableau-large">
<table>
<thead><tr><th>Signaux réunis</th><th class="nombre">Présences</th><th class="nombre">Éliminations</th><th class="nombre">Probabilité</th><th class="nombre">Intervalle</th></tr></thead>
<tbody>
{% for x in p.cumul %}
<tr>
  <td>{{ x.modalite | capitalize }}</td>
  <td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.cas }}</td>
  <td class="nombre"><b>{{ x.probabilite }} %</b></td>
  <td class="nombre">{{ x.bas }} – {{ x.haut }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

De **{{ p.cumul[0].probabilite }} %** à **{{ p.cumul[2].probabilite }} %** : le
risque est multiplié par plus de quatre entre la position la plus confortable et
la plus mauvaise. C’est, sur ce site, le plus grand écart qu’une condition
connue **avant le vote** parvienne à produire.

<p class="note">La dernière case ne tient qu’à {{ p.cumul[2].effectif }}
présences, et son intervalle le dit : de {{ p.cumul[2].bas }} à
{{ p.cumul[2].haut }} %. Cumuler les deux signaux est rare — c’est même la
raison pour laquelle il faut un modèle plutôt qu’un tableau croisé pour trancher
la question suivante.</p>

## Ombre l’un de l’autre, ou pas ?

Un tableau croisé ne peut pas répondre : les deux signaux vont souvent de pair,
et la case qui les réunit est trop petite. Le modèle ci-dessous les met dans le
**même** calcul, chaque conseil formant son propre groupe de comparaison.

{% include graphiques/pire-place-modele.svg %}

<p class="legende-figure">Rapports de cotes d’un logit conditionnel, sur
{{ p.modele.presences }} présences et {{ p.modele.conseils }} conseils.</p>

<div class="tableau-large">
<table>
<thead><tr><th>Signal</th><th class="nombre">Cote multipliée par</th><th class="nombre">Intervalle</th><th class="nombre">p</th></tr></thead>
<tbody>
{% for x in p.modele.coefficients %}
<tr><td>{{ x.libelle }}</td>
    <td class="nombre"><b>{{ x.rapport }}</b></td>
    <td class="nombre">{{ x.bas }} – {{ x.haut }}</td>
    <td class="nombre">{{ x.p }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p><b>Les deux survivent ensemble.</b> Le nom sorti la fois d’avant multiplie
  la cote par {{ p.modele.coefficients[0].rapport }}, l’isolement par
  {{ p.modele.coefficients[1].rapport }}, et aucun des deux intervalles ne
  contient 1.</p>
  <p>Ce ne sont donc pas deux façons de dire la même chose. Le bulletin d’hier
  mesure ce que le camp a <em>fait</em> ; l’isolement mesure ce dont on
  <em>dispose</em> pour y répondre. Un joueur visé mais entouré s’en sort ; un
  joueur seul mais jamais visé encore tient. Les deux à la fois, presque
  jamais.</p>
</div>

## Le dos au mur ne fait pas gagner

Une idée séduisante veut que le joueur menacé se surpasse : il sait qu’il doit
gagner l’immunité, donc il la gagne. Elle se teste, sur les
{{ p.conseils_immunite }} conseils où l’on connaît le vainqueur de l’épreuve
d’immunité individuelle du soir.

{% include graphiques/pire-place-mur.svg %}

<p class="legende-figure">Écart entre gagner l’immunité quand on vient d’être
visé et la gagner quand on ne l’a pas été. Le modèle nul tire le vainqueur au
hasard parmi les présents.</p>

<div class="tableau-large">
<table>
<thead><tr><th>Au conseil précédent</th><th class="nombre">Présences</th><th class="nombre">Immunités gagnées</th><th class="nombre">Probabilité</th><th class="nombre">Le hasard</th></tr></thead>
<tbody>
{% for x in p.dos_au_mur %}
<tr><td>{{ x.modalite | capitalize }}</td>
    <td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.cas }}</td>
    <td class="nombre"><b>{{ x.probabilite }} %</b></td>
    <td class="nombre">{{ x.hasard }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p>{{ tm.observe | round: 1 }} point d’écart, {{ tm.ecart_types }}
  écarts-types, p brute {{ tm.p }}. <b>Rien.</b> Et pour une fois le mot est
  mérité : l’observé tombe au milieu même de la distribution nulle.</p>
  <p>La menace change ce que les autres font de vous. Elle ne change pas ce que
  vous faites sur un parcours d’obstacles.</p>
</div>

## Le contrôle qui tombait sous le sens

Si l’immunité protège, personne ne devrait perdre son bulletin en écrivant le
nom de l’immunisé du soir.

<div class="constat">
  <p>Sur les <b>{{ p.bulletins_lus }} bulletins</b> lus à ces conseils-là,
  <b>{{ p.bulletins_perdus }}</b> visent le vainqueur de l’immunité —
  <b>{{ p.part_perdue }} %</b>.</p>
  <p>Ce n’est pas zéro, et c’est normal : un bulletin peut être écrit avant que
  l’immunité ne soit connue, ou volontairement perdu. Mais à ce niveau-là, la
  donnée confirme la règle plutôt qu’elle ne la contredit — c’est le second
  contrôle de ce type, après
  <a href="{{ '/statistiques/autour-du-feu/' | relative_url }}">les
  {{ site.data.stats.modeles.autour_du_feu.immunite[0].effectif }} présences
  d’immunisés dont aucun n’est parti</a>.</p>
</div>

## Ce que cette page ne dit pas

<div class="constat">
  <p><b>L’alliance est mesurée par le bulletin, pas par l’amitié.</b> Deux
  personnes qui écrivent le même nom peuvent le faire par accident, et deux
  alliés véritables peuvent se répartir les voix exprès. Ce qu’on mesure est une
  coïncidence de bulletins, rien de plus — et elle suffit à prédire.</p>
  <p><b>Aucun des deux signaux n’est une cause.</b> Le joueur isolé ne part pas
  <em>parce qu’</em>il est isolé : l’isolement et l’élimination sont deux effets
  du même rapport de force. Ces données ne savent pas les séparer.</p>
  <p><b>La chaîne exige deux conseils complets d’affilée.</b> D’où
  {{ p.conseils }} conseils seulement, et des cases finales à quelques dizaines
  d’observations. [La complétude]({{ '/completude/' | relative_url }}) dit
  pourquoi.</p>
</div>
