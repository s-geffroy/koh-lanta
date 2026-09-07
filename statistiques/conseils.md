---
layout: page
title: Les conseils
permalink: /statistiques/conseils/
chapeau: >-
  Le vote est presque toujours serré, l’unanimité n’existe pas — et les conseils ne se sont pas durcis avec les années, ils se sont divisés.
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

À l’autre bout, l’unanimité n’existe pas : sur ces
{{ c.conseils_avec_decompte }} conseils, **{% if c.conseils_unanimes == 0 %}aucun{% else %}{{ c.conseils_unanimes }}{% endif %}
n’a vu tous les bulletins porter le même nom**. L’image du camp entier se
retournant d’un bloc contre un aventurier est une image de fiction — dans les
faits, le vote se divise toujours.

## Peut-on croire ces bulletins ?

{% assign cv = site.data.croisement_votes %}

La question mérite d’être posée avant tout le reste, parce que quatre des
résultats les plus forts de ce site reposent entièrement sur ces
{{ c.bulletins }} lignes. Sur une partie des saisons, les deux wikis publient
**chacun** leur matrice des votes : on peut donc les confronter.

<div class="constat">
  <p>{{ cv.bulletins_communs }} bulletins sont relevés par les deux sources.
  <b>{{ cv.identiques }} sont identiques — {{ cv.part_identiques }} %.</b></p>
  <p>Les {{ cv.divergents }} divergences sont le même incident : deux Jérôme
  dans <i>La Revanche des 4 Terres</i>, que les deux wikis distinguent
  différemment. Aucune n’est un désaccord sur qui a voté contre qui.</p>
</div>

Ce n’est pas une garantie — deux wikis peuvent recopier la même erreur, et le
recouvrement ne couvre qu’une saison sur trois. C’est le meilleur contrôle
disponible, et il est bon.

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

## Il en faut plus qu’avant, et pourtant on s’accorde moins

{% assign per = c.par_periode %}
{% assign p0 = per | first %}{% assign p9 = per | last %}

{% include graphiques/conseils-epoques.svg %}

<p class="legende-figure">Moyennes par tranche de cinq ans : le nombre de
votants au conseil, et le nombre de voix portées sur celui qui part.</p>

Le nombre de voix qu’il faut pour sortir quelqu’un **monte** — de
{{ p0.voix_moyennes }} au début des années 2000 à {{ p9.voix_moyennes }}
aujourd’hui. Mais ce chiffre ne dit presque rien tout seul : le conseil compte
aussi plus de monde, de {{ p0.votants_moyens }} votants à
{{ p9.votants_moyens }}. Il en faut mécaniquement davantage.

La mesure de l’accord, c’est la **part** des votants qui écrivent le même nom.

{% include graphiques/conseils-accord.svg %}

<p class="legende-figure">Part des votants dont le bulletin porte le nom de
l’éliminé, par tranche de cinq ans.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Période</th><th class="nombre">Conseils</th>
  <th class="nombre">Votants</th><th class="nombre">Voix sur l’éliminé</th>
  <th class="nombre">Part d’accord</th>
</tr></thead>
<tbody>
{% for x in per %}
<tr>
  <td>{{ x.periode }}</td>
  <td class="nombre">{{ x.conseils }}</td>
  <td class="nombre">{{ x.votants_moyens }}</td>
  <td class="nombre">{{ x.voix_moyennes }}</td>
  <td class="nombre" data-val="{{ x.part_moyenne }}"><b>{{ x.part_moyenne }} %</b></td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p>Elle <b>baisse</b> : de {{ p0.part_moyenne }} % au début des années 2000 à
  {{ per[4].part_moyenne }} % au début des années 2020. Le camp est plus
  nombreux, il lui faut plus de voix, et il en donne <em>proportionnellement</em>
  moins à celui qu’il élimine.</p>
  <p>Autrement dit : <b>les conseils ne se sont pas durcis, ils se sont
  divisés.</b> L’image du bloc qui désigne sa victime appartient aux premières
  saisons, pas aux dernières.</p>
</div>

<p class="note">Deux réserves. La dernière tranche ne contient que
{{ p9.conseils }} conseils et remonte à {{ p9.part_moyenne }} % : une saison ou
deux suffisent à la faire bouger, et il faut la lire pour ce qu’elle est — un
début, pas un retournement. Et cette part n’est pas un test : aucune tendance
n’est déclarée au <a href="{{ '/methode/' | relative_url }}">registre</a>, ce
sont des moyennes par tranche, sans intervalle.</p>

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

Cette réciprocité-là est **sans ordre** : à un moment ou un autre. Sa version
datée — *celui dont j’ai écrit le nom la fois d’avant écrit-il le mien ce
soir ?* — vaut
{{ site.data.stats.modeles.conditionnelles.retour.probabilite }} %, contre
{% assign trb = site.data.stats.modeles.registre | where: "cle", "retour_de_baton" | first %}{{ trb.attendu | round: 1 }} %
si les bulletins étaient tirés au sort.
[Sachant le conseil d’avant]({{ '/statistiques/conditionnelles/' | relative_url }}).

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
Les sources en publient le détail pour **{{ j.effectif }} scrutins**, sur
{{ j.saisons }} saisons — le scrutin tient une colonne par finaliste, et cette
table ne montre que celle du lauréat. Ces scrutins sont tenus à l’écart de tous
les calculs de cette page.

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
  <td>{% if x.laureat %}{{ x.laureat }}{% else %}—{% endif %}</td>
  <td class="nombre">{% if x.voix_pour %}{{ x.voix_pour }}{% else %}—{% endif %}</td>
  <td class="nombre">{% if x.voix_exprimees %}{{ x.voix_exprimees }}{% else %}—{% endif %}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

{% if j.sans_nom > 0 %}
<p class="note">{% if j.sans_nom == 1 %}Un de ces scrutins n’affiche{% else %}{{ j.sans_nom }} de ces scrutins n’affichent{% endif %}
pas de nom : la cellule source y mêle une vignette et un prénom, et le libellé
qui en sort ne se rattache à personne. Plutôt que de deviner qui se cache
derrière, la case reste vide.</p>
{% endif %}

<p class="note"><strong>« Voix pour » compte les bulletins, pas les totaux de
la source.</strong> Un bulletin de jury appartient à la colonne de la personne
dont il porte le nom — c’est la définition du scrutin — et sur les
{{ j.effectif }} scrutins relevés, chaque voix annoncée par les sources est
aujourd’hui lue et attribuée. Là où le total de la source disait autre chose,
c’est lui qui avait tort : <i>Les Armes secrètes</i> attribuait à Maxine le
score de Lucie et réciproquement, et <i>Le Totem maudit</i> rangeait trois
jurés dans la colonne voisine — ce qui masquait l’égalité <b>4-4</b> d’où sont
sortis ses deux vainqueurs.</p>

<p class="note">Cette dernière analyse ne porte que sur les
{{ c.conseils_complets }} conseils dont le dépouillement est complet, c’est-à-dire
ceux où le nombre de bulletins lus dans les sources correspond exactement au
nombre de voix annoncé. Les autres conseils restent comptés dans les agrégats
— qui part, avec combien de voix — mais pas dans les analyses bulletin par
bulletin.</p>
