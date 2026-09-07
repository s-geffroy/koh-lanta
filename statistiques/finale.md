---
layout: page
title: La fin de saison
permalink: /statistiques/finale/
chapeau: >-
  Gagner les poteaux ne fait pas gagner la saison. Mais arriver **dernier** à
  l’orientation, si : onze victoires sur dix-sept, contre une sur trois
  attendues.
---

{% assign f = site.data.stats.finale %}
{% assign cv = f.couverture %}
{% assign p = f.poteaux %}
{% assign r1 = f.par_rang[0] %}{% assign r2 = f.par_rang[1] %}{% assign r3 = f.par_rang[2] %}

Les trois derniers jours d’une saison suivent toujours la même mécanique :
l’**orientation** ne garde que trois aventuriers, les **poteaux** en désignent
un, et celui-là emmène en finale qui il veut. Le troisième est éliminé.

Trois décisions s’enchaînent donc, et aucune n’avait été mesurée ici — parce
qu’aucune n’était dans les données. `epreuves.yml` ne porte **aucun nom
d’épreuve** ; la dernière épreuve d’immunité individuelle relevée n’est pas les
poteaux, et pour huit saisons son vainqueur est justement la personne éliminée
dessus. Il a fallu aller lire les deux wikis.

<ul class="chiffres">
  <li class="chiffre"><b>{{ cv.vainqueur_des_poteaux_connu }}</b><span>saisons dont on connaît le vainqueur des poteaux</span></li>
  <li class="chiffre"><b>{{ cv.qualifies_connus }}</b><span>dont l’ordre d’arrivée à l’orientation</span></li>
  <li class="chiffre"><b>{{ r3.gagne_la_saison.probabilite }} %</b><span>de victoires pour le dernier qualifié</span></li>
</ul>

## Gagner les poteaux ne suffit pas

Le vainqueur des poteaux choisit son adversaire. On s’attend à ce qu’il choisisse
le plus facile à battre, donc à ce qu’il gagne plus souvent qu’une fois sur
deux.

{% include graphiques/finale-poteaux.svg %}

<p class="legende-figure">Part des saisons remportées par le vainqueur des
poteaux et par le finaliste qu’il emmène, sur les {{ p.effectif }} saisons dont
la source nomme le vainqueur des poteaux.</p>

<div class="constat">
  <p><b>{{ p.vainqueur_des_poteaux.cas }} fois sur {{ p.effectif }}</b>, soit
  {{ p.vainqueur_des_poteaux.probabilite }} %. L’intervalle va de
  {{ p.vainqueur_des_poteaux.bas }} à {{ p.vainqueur_des_poteaux.haut }} % et
  <b>contient 50 %</b> : sur ces effectifs, on ne peut pas distinguer ce
  résultat d’un tirage à pile ou face.</p>
  <p>Le privilège de choisir son adversaire ne se voit pas dans les chiffres.
  Il rapporte peut-être quelque chose ; il n’en rapporte pas assez pour se lire
  sur vingt saisons.</p>
</div>

<p class="note">Sur les {{ p.choix_atteste.effectif }} saisons où une source
énonce le choix noir sur blanc — « décide d’affronter », « n’est pas choisi par »
—, le vainqueur des poteaux l’emporte {{ p.choix_atteste.cas }} fois, soit
{{ p.choix_atteste.probabilite }} %. L’intervalle
({{ p.choix_atteste.bas }} – {{ p.choix_atteste.haut }} %) contient encore 50 %,
et il faudrait s’en méfier deux fois plutôt qu’une : ces neuf saisons sont les
plus récentes, pas un échantillon au hasard.</p>

## L’ordre d’arrivée à l’orientation

Voilà où le résultat se trouve. À l’orientation, les trois qualifiés le sont
dans l’ordre où ils ont trouvé leur poignard — et cet ordre annonce la suite,
mais **à l’envers de l’intuition**.

{% include graphiques/finale-rang.svg %}

<p class="legende-figure">Part des saisons remportées selon le rang d’arrivée à
l’orientation, sur {{ f.saisons_ordonnees }} saisons. Le trait horizontal est le
hasard : un qualifié sur trois gagne.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Rang à l’orientation</th><th class="nombre">Saisons</th>
  <th class="nombre">Gagne les poteaux</th><th class="nombre">Gagne la saison</th>
  <th class="nombre">Intervalle</th><th class="nombre">Éliminé aux poteaux</th>
</tr></thead>
<tbody>
{% for r in f.par_rang %}
<tr>
  <td>{{ r.libelle }}</td>
  <td class="nombre">{{ r.effectif }}</td>
  <td class="nombre">{{ r.gagne_les_poteaux.probabilite }} %</td>
  <td class="nombre" data-val="{{ r.gagne_la_saison.probabilite }}"><b>{{ r.gagne_la_saison.probabilite }} %</b></td>
  <td class="nombre">{{ r.gagne_la_saison.bas }} – {{ r.gagne_la_saison.haut }} %</td>
  <td class="nombre">{{ r.elimine_aux_poteaux.probabilite }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p><b>Le dernier des trois gagne la saison
  {{ r3.gagne_la_saison.cas }} fois sur {{ r3.effectif }}</b> —
  {{ r3.gagne_la_saison.probabilite }} %, intervalle
  {{ r3.gagne_la_saison.bas }} à {{ r3.gagne_la_saison.haut }} %. Il
  <b>ne contient pas</b> le {{ r3.gagne_la_saison.hasard }} % du hasard.</p>
  <p>Le premier arrivé, lui, gagne {{ r1.gagne_la_saison.cas }} fois
  ({{ r1.gagne_la_saison.probabilite }} %) et se fait sortir aux poteaux
  {{ r1.elimine_aux_poteaux.probabilite }} % du temps — presque une fois sur
  deux. <b>Finir premier à l’orientation est la pire des trois places.</b></p>
</div>

{% include graphiques/finale-poteaux-rang.svg %}

<p class="legende-figure">Le même rang, mais pour l’épreuve suivante : qui
remporte les poteaux.</p>

L’écart naît donc **avant** le vote final : le dernier qualifié gagne déjà les
poteaux {{ r3.gagne_les_poteaux.probabilite }} % du temps, contre
{{ r1.gagne_les_poteaux.probabilite }} % au premier. Ce n’est pas le jury qui
préfère les lents, c’est le poteau.

<p class="note">Une explication vient à l’esprit et ces données ne peuvent pas
la trancher : l’orientation récompense la course et la lecture de terrain, les
poteaux récompensent la légèreté et l’immobilité. Ce seraient deux épreuves qui
demandent des corps opposés. C’est une hypothèse, pas un résultat — rien ici ne
la teste.</p>

## Le tableau, saison par saison

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Saison</th><th class="nombre">Année</th>
  <th>Qualifiés à l’orientation, dans l’ordre</th>
  <th>Poteaux</th><th>Finaliste</th><th>Vainqueur</th>
</tr></thead>
<tbody>
{% for x in f.table %}
<tr>
  <td>{{ x.titre }}</td><td class="nombre">{{ x.annee }}</td>
  <td>{% if x.qualifies.size > 0 %}{{ x.qualifies | join: ", " }}{% else %}—{% endif %}</td>
  <td>{% if x.poteaux %}{{ x.poteaux }}{% else %}—{% endif %}</td>
  <td>{% if x.autre_finaliste %}{{ x.autre_finaliste }}{% else %}—{% endif %}</td>
  <td><b>{{ x.vainqueur }}</b></td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## D’où vient l’ordre, et pourquoi on peut s’y fier

Tout ce qui précède repose sur une affirmation qu’il faut prouver : **l’ordre
dans lequel les wikis écrivent les qualifiés est l’ordre où ils sont arrivés.**
Rien ne l’annonce dans les sources. Deux vérifications ont été faites, et
elles sont refaites à chaque régénération des données.

<div class="constat">
  <p><b>Le récit confirme, jamais il ne dément.</b> Sur
  {{ cv.saisons_ordre_teste }} saisons, la prose nomme un rang d’arrivée —
  « Loïc trouve le premier poignard », « le dernier poignard, finalement trouvé
  par Alexandra ». <b>{{ cv.rangs_confirmes }} rangs</b> sont ainsi vérifiables :
  {{ cv.rangs_confirmes }} coïncident avec la place que la cellule leur donne,
  <b>{{ cv.rangs_dementis }} la contredit</b>.</p>
  <p><b>Les deux wikis, écrits séparément, écrivent le même ordre.</b> Sur les
  {{ cv.ordre_croisable }} saisons que les deux sources détaillent,
  <b>{{ cv.ordre_concordant }} donnent le même ordre</b>. C’est l’épreuve
  croisée déjà employée pour les bulletins de vote sur
  <a href="{{ '/statistiques/conseils/' | relative_url }}">la page des
  conseils</a>.</p>
</div>

Le contrôle est câblé dans `verifie.py` : un seul rang démenti par la prose fait
échouer la vérification des données. Si l’ordre cesse d’être l’ordre d’arrivée,
cette page cesse d’être publiable, et on le saura.

## Ce que cette page ne dit pas

<div class="constat">
  <p><b>Aucun test n’est déclaré ici.</b> Les tests de ce site sont annoncés
  d’avance et corrigés ensemble par Benjamini-Hochberg
  (<a href="{{ '/methode/' | relative_url }}">la méthode</a>) : en ajouter
  déplacerait les p ajustées de tous les autres. Ce que vous lisez, ce sont des
  proportions, leurs intervalles de Wilson, et la ligne du hasard. Un intervalle
  qui ne contient pas le hasard dit déjà l’essentiel ; il ne dit pas la même
  chose qu’une p ajustée, et on ne le présente pas comme telle.</p>
  <p><b>{{ f.saisons_ordonnees }} saisons, c’est peu.</b> Le résultat sur le
  dernier qualifié tient à
  {{ r3.gagne_la_saison.cas }} victoires ; trois de moins et l’intervalle
  reprendrait le hasard. Il demande à être revu dans cinq ans.</p>
  <p><b>{{ cv.saisons_sans_poteaux.size }} saisons manquent</b> —
  {{ cv.saisons_sans_poteaux | join: ", " }} — parce qu’aucune des deux sources
  n’y nomme le vainqueur des poteaux. Ce sont surtout des saisons anciennes, et
  rien ne garantit qu’elles ressembleraient aux autres. Trois éditions de plus
  sont écartées d’office : leur fin ne suit pas le format à trois aux poteaux.</p>
</div>
