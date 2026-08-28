---
layout: page
title: Les conseils
permalink: /statistiques/conseils/
chapeau: >-
  Le vote est presque toujours serré, l’unanimité rarissime, et le sexe du votant joue — à la marge.
---

{% assign c = site.data.stats.conseils %}

Le conseil est le cœur du jeu, et le seul endroit où l’on peut lire une
stratégie plutôt que la deviner. **{{ c.conseils }} conseils** ont été
dépouillés, pour **{{ c.bulletins }} bulletins**.

<ul class="chiffres">
  <li class="chiffre"><b>{{ c.conseils }}</b><span>conseils relevés</span></li>
  <li class="chiffre"><b>{{ c.bulletins }}</b><span>bulletins</span></li>
  <li class="chiffre"><b>{{ c.part_serres }} %</b><span>de conseils serrés</span></li>
  <li class="chiffre"><b>{{ c.voix_annulees_par_objet }}</b><span>voix annulées par un objet</span></li>
</ul>

## Le vote est presque toujours serré

Sur les {{ c.conseils_avec_decompte }} conseils dont le décompte est connu,
**{{ c.part_serres }} % se jouent à une voix près ou à peine plus** : le
nombre de bulletins contre la personne éliminée n’y dépasse pas la moitié des
votes exprimés.

À l’autre bout, l’unanimité est **rarissime** : {{ c.part_unanimes }} % des
conseils seulement. L’image du camp entier se retournant d’un bloc contre un
aventurier est une image de fiction — dans les faits, le vote se divise presque
toujours.

## Les objets d’immunité, vus depuis les bulletins

Un bulletin barré dans la matrice des votes n’a pas toujours la même cause, et
les confondre revient à mettre au crédit des colliers des annulations qui ne
leur doivent rien. Cette page les sépare.

**Une partie des bulletins barrée** : un objet d’immunité a protégé quelqu’un,
les autres voix comptent, et quelqu’un sort.
**{{ c.voix_annulees_par_objet }} voix** dans ce cas, sur
**{{ c.conseils_avec_objet_joue }} conseils** et
{{ c.saisons_avec_objet_joue }} saisons — soit plus du double des saisons dont
[la page des colliers]({{ '/statistiques/colliers/' | relative_url }}) connaît
le détail des objets.

**Tous les bulletins barrés** : c’est le tour entier qui est nul — une égalité,
suivie d’un second vote. {{ c.voix_annulees_tour_nul }} voix,
{{ c.conseils_tour_nul }} conseils, {{ c.saisons_tour_nul }} saisons. Rien à
voir avec un collier.

<div class="constat">
  <p>Sur les {{ c.objet_un_seul_protege }} conseils où un <b>seul</b> aventurier
  a vu ses voix annulées — les seuls où l’on sache qui l’objet protégeait —
  <b>il est resté en jeu {{ c.objet_a_sauve }} fois sur
  {{ c.objet_un_seul_protege }}</b>.</p>
  <p>Un objet joué au bon conseil ne rate jamais. Toute la difficulté est
  ailleurs : le jouer le bon soir. La page des colliers montre que la plupart
  ne sont jamais joués du tout.</p>
</div>

## Combien de voix faut-il pour partir ?

{% include graphiques/conseils-voix.svg %}

<p class="legende-figure">Nombre de bulletins portant le nom de l’éliminé, sur
les conseils dont le décompte est connu.</p>

{% assign v = site.data.stats.voix_pour_eliminer %}
Le cas le plus fréquent est **{{ v.mode }} voix**. La distribution est étalée —
de une à plus de dix — parce que les castings ont grossi : un conseil à seize
n’a pas le même arithmétique qu’un conseil à vingt-quatre.

## Qui a écrit le nom de qui

{% assign a = site.data.stats.arc_des_votes %}
Le détail des bulletins permet de dessiner le camp entier. La saison montrée
ici est **{{ a.titre }} ({{ a.annee }})** — retenue par le calcul, parce que
c’est celle dont le dépouillement est le plus complet : {{ a.bulletins }}
bulletins rattachés.

{% include graphiques/votes-arc.svg %}

<p class="legende-figure">Les aventuriers sont rangés dans l’ordre de leur
sortie, du premier parti à gauche au vainqueur à droite. Un arc relie deux
personnes dont l’une a écrit le nom de l’autre ; plus il est épais, plus elle
l’a fait souvent. La couleur du point est celle de la tribu de départ.</p>

### Le vote se rend

{% assign rec = site.data.stats.reciprocite %}
Sur les **{{ rec.couples }} couples** votant → cible relevés dans les conseils
au dépouillement complet, **{{ rec.reciproques }} sont réciproques** :
**{{ rec.part }} %**. Écrire le nom de quelqu’un, c’est donc avoir près d’une
chance sur deux qu’il ait écrit le vôtre le même soir ou un autre. Le conseil
n’est pas une meute contre un isolé, c’est un affrontement à deux camps.

Et ces camps **durent**. Deux aventuriers qui ont voté ensemble votent encore
ensemble au conseil suivant dans
{{ site.data.stats.modeles.alliances.apres_ensemble }} % des cas, contre
{{ site.data.stats.modeles.alliances.apres_separes }} % pour ceux qui avaient
voté séparément — un écart que le hasard ne produit jamais.
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}).

## Qui vote contre qui

{% include graphiques/conseils-genre.svg %}

<p class="legende-figure">Répartition des bulletins selon le sexe du votant et
celui de sa cible, sur les conseils dont le dépouillement est complet.</p>

Si le sexe ne jouait aucun rôle, les quatre combinaisons pèseraient 25 % chacune
— le casting étant paritaire. Ce n’est pas tout à fait le cas : les bulletins
d’**un homme contre une femme** sont les plus nombreux
({{ c.vote_par_genre[0].part }} %), et ceux d’**une femme contre une femme** les
moins nombreux ({{ c.vote_par_genre[3].part }} %). L’écart est réel mais
modeste, de l’ordre de huit points entre les deux extrêmes.

## Le vote du jury final

{% assign j = site.data.stats.jury %}
Le dernier scrutin d’une saison n’est pas un conseil : **on n’y élimine
personne, on y désigne un vainqueur**, et le sens du bulletin est inversé.
Les sources n’en publient le détail que pour **{{ j.effectif }} saisons**. Ces
scrutins sont tenus à l’écart de tous les calculs de cette page.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Saison</th><th class="nombre">Année</th><th>Lauréat</th>
  <th class="nombre">Voix pour</th><th class="nombre">Voix exprimées</th>
</tr></thead>
<tbody>
{% for x in j.scrutins %}
<tr>
  <td>{{ x.titre }}</td>
  <td class="nombre">{{ x.annee }}</td>
  <td>{{ x.laureat }}</td>
  <td class="nombre">{% if x.voix_pour %}{{ x.voix_pour }}{% else %}—{% endif %}</td>
  <td class="nombre">{% if x.voix_exprimees %}{{ x.voix_exprimees }}{% else %}—{% endif %}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Cette dernière analyse ne porte que sur les
{{ c.conseils_complets }} conseils dont le dépouillement est complet, c’est-à-dire
ceux où le nombre de bulletins lus dans les sources correspond exactement au
nombre de voix annoncé. Les autres conseils restent comptés dans les agrégats
— qui part, avec combien de voix — mais pas dans les analyses bulletin par
bulletin.</p>
