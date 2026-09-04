---
layout: page
title: Sachant qui est autour du feu
permalink: /statistiques/autour-du-feu/
chapeau: >-
  On ne part pas au hasard, mais on ne part pas non plus pour ce qu’on croit.
  Six positions dans le camp, six probabilités — dont une qui vaut exactement
  zéro.
---

{% assign m = site.data.stats.modeles %}
{% assign f = m.autour_du_feu %}
{% assign reg = m.registre %}
{% assign tb = reg | where: "cle", "bandeau_minoritaire" | first %}
{% assign ts = reg | where: "cle", "sexe_minoritaire" | first %}
{% assign td = reg | where: "cle", "doyen_du_camp" | first %}
{% assign tc = reg | where: "cle", "confort_sortie" | first %}

[Sachant le conseil d’avant]({{ '/statistiques/conditionnelles/' | relative_url }})
conditionne sur le **passé** : les voix reçues la fois précédente. Cette
page-ci conditionne sur le **présent** — la place qu’on occupe dans le camp
assis autour du feu ce soir-là. Être du bandeau le moins représenté, du sexe le
moins représenté, le plus âgé, celui qui vient de gagner le confort : autant de
positions qui se lisent **avant** que le premier bulletin ne soit écrit.

<ul class="chiffres">
  <li class="chiffre"><b>{{ f.presences }}</b><span>présences à un conseil</span></li>
  <li class="chiffre"><b>{{ f.conseils }}</b><span>conseils, sur {{ f.saisons }} saisons</span></li>
  <li class="chiffre"><b>{{ f.hasard }} %</b><span>le hasard : une chance sur le nombre de présents</span></li>
</ul>

<p class="note"><strong>Le camp se connaît de deux façons, et l’une vaut mieux
que l’autre.</strong> Quand le dépouillement est complet, la liste des votants
<em>est</em> le camp : rien n’est reconstruit — {{ f.par_bulletins }} présences
sur {{ f.presences }}. Pour les {{ f.par_reconstruction }} autres, toutes
d’après la réunification et toutes des soirs à conseil unique, on rebâtit le
camp des encore-en-jeu : c’est exact aussi, puisqu’après la fusion tout le monde
vote au même feu. Avant la fusion, une reconstruction mélangerait les deux
tribus ; elle n’est donc jamais faite.</p>

## La seule probabilité du jeu qui vaut exactement zéro

{% assign imm = f.immunite | first %}
<div class="constat">
  <p>Sachant qu’on a gagné l’immunité individuelle du soir, la probabilité de
  partir vaut <b>{{ imm.probabilite }} %</b> — <b>{{ imm.cas }} sur
  {{ imm.effectif }}</b>. Le hasard en donnerait {{ imm.hasard }} %.</p>
  <p>C’est une règle du jeu, pas une découverte. Mais la voir sortir intacte de
  {{ imm.effectif }} présences reconstituées depuis les bulletins est le meilleur
  contrôle qu’on puisse faire sur ces données : si le rattachement des vainqueurs
  d’épreuve ou celui des éliminés était bancal, ce zéro ne serait pas zéro.</p>
</div>

<p class="note"><strong>Il a fallu s’y reprendre à deux fois, et le détour est
instructif.</strong> Rapproché naïvement des conseils par leur seul numéro
d’épisode, ce même contrôle sortait <strong>19 violations</strong> — des
immunisés apparemment éliminés. Toutes les dix-neuf tombaient sur un soir à
<em>plusieurs</em> conseils : dans un épisode qui en compte trois, l’immunité
gagnée avant le premier ne protège évidemment pas au troisième. Le rapprochement
était faux, pas la donnée. Les épreuves du soir ne sont donc lues que sur les
soirs à conseil unique.</p>

## Sachant la place qu’on occupe

{% include graphiques/feu-positions.svg %}

<p class="legende-figure">Probabilité d’être éliminé selon sa position parmi les
présents, comparée au tirage au sort. <strong>Chaque catégorie a son propre
hasard</strong> : on est plus souvent le doyen d’un camp de six que d’un camp de
douze.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Position dans le camp</th><th class="nombre">Présences</th>
  <th class="nombre">Éliminations</th><th class="nombre">Probabilité</th>
  <th class="nombre">Intervalle</th><th class="nombre">Le hasard</th>
</tr></thead>
<tbody>
{% assign rangs = f.immunite | concat: f.bandeau | concat: f.sexe | concat: f.age | concat: f.confort | concat: f.genre %}
{% for x in rangs %}
<tr>
  <td>{{ x.modalite | capitalize }}</td>
  <td class="nombre">{{ x.effectif }}</td>
  <td class="nombre">{{ x.cas }}</td>
  <td class="nombre" data-val="{{ x.probabilite }}"><b>{{ x.probabilite }} %</b></td>
  <td class="nombre">{{ x.bas }} – {{ x.haut }} %</td>
  <td class="nombre">{{ x.hasard }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Le bandeau d’origine décide qui part

{% assign bmin = f.bandeau | first %}
{% assign bmaj = f.bandeau | last %}

{% include graphiques/feu-bandeau.svg %}

<p class="legende-figure">Écart entre partir quand son bandeau de départ est le
moins représenté du camp et partir quand il est le plus représenté, contre
{{ tb.tirages }} tirages où l’éliminé est pris au hasard parmi les présents.</p>

<div class="constat">
  <p>Bandeau minoritaire : <b>{{ bmin.probabilite }} %</b>
  ({{ bmin.cas }} sur {{ bmin.effectif }}). Bandeau majoritaire :
  <b>{{ bmaj.probabilite }} %</b>.</p>
  <p>{{ tb.observe | round: 1 }} points d’écart, {{ tb.ecart_types }}
  écarts-types au-dessus du hasard, p ajustée {{ tb.p_ajustee }}.</p>
</div>

[Jaune contre rouge]({{ '/statistiques/tribus/' | relative_url }}) montre que la
couleur de départ ne décide **rien** du palmarès : douze victoires jaunes, douze
rouges. Les deux résultats ne se contredisent pas, ils se complètent — et
ensemble ils disent quelque chose de précis :

> **Le bandeau ne dit pas qui gagne. Il dit qui part, dès qu’on se retrouve du
> mauvais côté du compte.**

{% include graphiques/feu-bandeau-fusion.svg %}

<p class="legende-figure">Le même écart, de part et d’autre de la
réunification.</p>

{% assign amin = f.bandeau_avant | first %}
{% assign amaj = f.bandeau_avant | last %}
{% assign pmin = f.bandeau_apres | first %}
{% assign pmaj = f.bandeau_apres | last %}
<div class="tableau-large">
<table>
<thead><tr><th></th><th class="nombre">Bandeau minoritaire</th><th class="nombre">Bandeau majoritaire</th></tr></thead>
<tbody>
<tr><td>Avant la réunification</td>
    <td class="nombre"><b>{{ amin.probabilite }} %</b> <small>({{ amin.effectif }})</small></td>
    <td class="nombre">{{ amaj.probabilite }} % <small>({{ amaj.effectif }})</small></td></tr>
<tr><td>Après la réunification</td>
    <td class="nombre"><b>{{ pmin.probabilite }} %</b> <small>({{ pmin.effectif }})</small></td>
    <td class="nombre">{{ pmaj.probabilite }} % <small>({{ pmaj.effectif }})</small></td></tr>
</tbody>
</table>
</div>

L’effet est **plus fort avant la fusion qu’après**, ce qui n’allait pas de soi :
on attendait plutôt le contraire, la réunification étant le moment où les
anciennes tribus se comptent. L’explication est ailleurs — avant la fusion, un
bandeau ne devient minoritaire dans une tribu que par un **échange de
membres**. C’est donc la mesure du sort réservé au nouveau venu, et ce sort est
clair. [Qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}) montre
la même chose au niveau du bulletin : le bandeau est le seul trait qui guide
l’écriture d’un nom.

## Le sexe minoritaire, lui, protège

{% assign smin = f.sexe | first %}
{% assign smaj = f.sexe | last %}

{% include graphiques/feu-sexe.svg %}

<p class="legende-figure">Écart entre partir quand son sexe est le moins
représenté du camp et partir quand il est le plus représenté.</p>

<div class="constat">
  <p>Sexe minoritaire : <b>{{ smin.probabilite }} %</b>
  ({{ smin.cas }} sur {{ smin.effectif }}). Sexe majoritaire :
  <b>{{ smaj.probabilite }} %</b> ({{ smaj.cas }} sur {{ smaj.effectif }}).</p>
  <p>{{ ts.observe | round: 1 }} points, {{ ts.ecart_types }} écarts-types
  <b>sous</b> le hasard, p ajustée {{ ts.p_ajustee }}. C’est la <b>plus haute
  des p ajustées retenues de ce site</b>, et il faut le dire ainsi : une saison
  de plus pourrait la faire basculer dans un sens comme dans l’autre.</p>
</div>

C’est l’inverse du bandeau, et c’est l’inverse de l’intuition. La lecture la
plus économe est que **la majorité se mange elle-même** : quand un camp compte
six hommes et trois femmes, les bulletins des six se partagent entre eux. Rien
ici ne dit qu’il s’agit d’une stratégie ; le chiffre dit seulement où tombent
les voix.

<p class="note"><strong>Une seconde lecture, tout aussi compatible, et elle
oblige à la prudence.</strong> Un sexe devient minoritaire dans un camp <em>parce
que</em> les siens en sont déjà partis : ceux qui restent sont donc des
survivants, sélectionnés par tout ce qui précède. On mesurerait alors la
solidité de ces survivants, pas un effet de la minorité. Ces données ne
tranchent pas entre les deux lectures, et il n’y a aucune raison de faire
semblant.</p>

<p class="note">La même objection s’applique au bandeau — mais <strong>en sens
inverse</strong>, ce qui la rend rassurante : là aussi les minoritaires sont des
survivants, ce qui devrait les <em>protéger</em>. L’effet mesuré va contre cette
sélection ; il est donc, s’il faut choisir, plutôt sous-estimé que
surestimé.</p>

<p class="note">Ce résultat ne dit rien du sexe <em>en général</em> : toutes
positions confondues, une femme part dans {{ f.genre[0].probabilite }} % des cas
et un homme dans {{ f.genre[1].probabilite }} % — un écart que ces effectifs ne
permettent pas de distinguer du hasard. La question de la longévité, à âge et
métier égaux, est traitée par un modèle de durée sur
<a href="{{ '/statistiques/equilibre/' | relative_url }}">Le jeu tenu serré</a>,
et décrite sur
<a href="{{ '/statistiques/longevite/' | relative_url }}">Âge et longévité</a>.</p>

## Le doyen : l’exemple qui justifie toute la méthode

{% assign doyen = f.age | first %}
{% assign milieu = f.age[1] %}

Le plus âgé du camp est éliminé dans **{{ doyen.probabilite }} %** des cas,
contre {{ milieu.probabilite }} % pour ceux qui ne sont ni le plus âgé ni le
plus jeune. Lu ainsi, c’est un résultat : le doyen paierait son âge.

Il n’en est rien, et la raison tient en une ligne. **On est plus souvent le
doyen d’un camp de six que d’un camp de douze** — donc la catégorie « le plus
âgé » est surreprésentée dans les petits conseils, où chacun risque davantage.
Son hasard à elle vaut {{ doyen.hasard }} %, pas {{ f.hasard }} %.

Le test ci-dessous compare le doyen à **tous** les autres présents, benjamins
compris — c’est pourquoi son écart ({{ td.observe | round: 1 }} points) est un
peu plus petit que celui qu’on lit entre les deux lignes du tableau.

{% include graphiques/feu-doyen.svg %}

<p class="legende-figure">Écart entre partir quand on est le doyen et partir
quand on ne l’est pas. Le modèle nul absorbe l’effet de taille — et l’observé
n’en sort pas.</p>

<div class="constat">
  <p>{{ td.observe | round: 1 }} points d’écart, {{ td.ecart_types }}
  écarts-types, p brute {{ td.p }}, p ajustée {{ td.p_ajustee }}.
  <b>Non concluant.</b></p>
  <p>Sans le bon point de comparaison, on aurait publié près de cinq points
  d’écart comme un résultat. C’est exactement ce contre quoi cette page est
  construite.</p>
</div>

## Le confort maudit, mesuré comme une sortie

{% assign cw = f.confort | first %}
{% assign cn = f.confort | last %}

L’idée court depuis vingt-cinq ans : gagner le confort ferait de vous une cible
le soir même. [Les épreuves]({{ '/statistiques/epreuves/' | relative_url }}) la
testent sur les **bulletins**. Voici sa version en sortie.

{% include graphiques/feu-confort.svg %}

<p class="legende-figure">Écart entre partir quand on vient de gagner le confort
de l’épisode et partir quand on n’a rien gagné.</p>

<div class="constat">
  <p>A gagné le confort : <b>{{ cw.probabilite }} %</b>
  ({{ cw.cas }} sur {{ cw.effectif }}). N’a rien gagné :
  {{ cn.probabilite }} %.</p>
  <p>{{ tc.observe | round: 1 }} points, {{ tc.ecart_types }} écarts-types,
  p brute {{ tc.p }}, p ajustée {{ tc.p_ajustee }}. <b>Non concluant.</b></p>
  <p>L’écart va dans le sens de la légende et il est loin d’être petit. Mais à
  {{ cw.effectif }} présences, il reste compatible avec un tirage. Le dire
  autrement serait vendre une intuition pour une mesure.</p>
</div>

## Ce que cette page ne dit pas

<div class="constat">
  <p><b>Une position n’est pas une cause.</b> Le bandeau minoritaire ne fait
  partir personne : il décrit un rapport de force que le vote ne fait
  qu’enregistrer. La donnée ne sait pas séparer les deux.</p>
  <p><b>Le camp d’avant la fusion n’est connu que par les bulletins.</b> Sur les
  conseils tribaux au dépouillement incomplet, on ignore qui était là — ils sont
  écartés, et [la complétude]({{ '/completude/' | relative_url }}) montre que
  cela concerne surtout les saisons récentes.</p>
  <p><b>Quatre tests, deux retenus</b> — et l’un des deux de justesse. Les deux
  autres sont publiés comme non concluants, avec leur écart et leur intervalle :
  ils ne sont pas cachés, ils sont le prix de la liste déclarée d’avance. Le
  registre complet et la correction pour tests multiples sont sur
  [La méthode]({{ '/methode/' | relative_url }}).</p>
</div>
