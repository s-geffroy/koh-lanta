---
layout: page
title: Sachant le conseil d’avant
permalink: /statistiques/conditionnelles/
chapeau: >-
  Mon nom est sorti deux fois la dernière fois. Qu’est-ce que cela change à mes
  chances de partir ce soir ? Sept probabilités conditionnelles, et un
  retournement.
---

{% assign m = site.data.stats.modeles %}
{% assign c = m.conditionnelles %}
{% assign reg = m.registre %}
{% assign t1 = reg | where: "cle", "menace_voix" | first %}
{% assign t2 = reg | where: "cle", "menace_sommet" | first %}
{% assign t3 = reg | where: "cle", "camp_perdant" | first %}
{% assign t4 = reg | where: "cle", "cible_persistante" | first %}
{% assign t5 = reg | where: "cle", "retour_de_baton" | first %}

Tout le monde autour du feu connaît le dépouillement précédent : il a été lu à
voix haute. C’est la seule information du jeu que personne ne peut cacher. La
question de cette page est celle d’un joueur assis sur son tronc, et elle est
exactement une probabilité conditionnelle : **sachant les voix que j’ai reçues
la dernière fois, quelles sont mes chances de partir ce soir ?**

## Le point de comparaison n’est pas zéro

Une probabilité de partir ne se lit jamais seule. À un conseil à six, on part
une fois sur six ; à un conseil à douze, une fois sur douze. La moitié des
écarts entre catégories que l’on croit lire dans ce genre de tableau ne sont que
cet effet de taille.

Le repère de toute cette page est donc **une chance sur n**, n étant le nombre
de personnes qui votent ce soir-là — {{ c.taille_moyenne }} en moyenne sur la
chaîne étudiée ici. Ce repère vaut **{{ c.hasard }} %**, et le taux observé,
toutes catégories confondues, vaut {{ c.globale }} %. Les deux sont égaux par
construction : il part exactement une personne par conseil. Tout l’intérêt est
donc dans la **répartition** de ce risque entre les présents, jamais dans son
niveau moyen.

<ul class="chiffres">
  <li class="chiffre"><b>{{ c.presences }}</b><span>présences à un conseil, dont on connaît le conseil précédent</span></li>
  <li class="chiffre"><b>{{ c.conseils }}</b><span>conseils enchaînés</span></li>
  <li class="chiffre"><b>{{ c.saisons }}</b><span>saisons</span></li>
  <li class="chiffre"><b>{{ c.hasard }} %</b><span>le hasard : une chance sur le nombre de présents</span></li>
</ul>

<p class="note"><strong>Comment la chaîne est construite, et ce qu’elle coûte.</strong>
« Le conseil précédent » d’un aventurier n’est pas le conseil précédent de la
saison : avant la réunification, deux tribus votent chacune de leur côté. C’est
donc le dernier conseil auquel <em>cette personne-là</em> a assisté. Un conseil
n’y entre que si son dépouillement est complet, c’est-à-dire si le nombre de
bulletins relevés égale le nombre de voix annoncées : c’est la seule garantie
que « zéro voix reçue » veuille dire zéro, et non « bulletin non lu ». Et la
remontée s’arrête au premier conseil manquant — faute de savoir qui y était, on
ne peut pas jurer que le conseil trouvé plus loin soit bien celui d’avant.
Cette prudence coûte cher : {{ c.presences }} présences retenues là où la
version qui enjambe les trous en compterait {{ c.presences_relachees }}. Les
deux versions donnent la même courbe ; c’est la stricte qui est publiée.
[La complétude]({{ '/completude/' | relative_url }}) montre pourquoi les
conseils sont la donnée la plus trouée du site.</p>

## Sachant les voix reçues la fois d’avant

{% include graphiques/conditionnelles-menace.svg %}

<p class="legende-figure">Probabilité d’être éliminé à un conseil selon le
nombre de voix reçues au conseil précédent. Le trait vertical est l’intervalle
de confiance à 95 % ; le trait tireté, le risque qu’un tirage au sort
donnerait.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Voix au conseil précédent</th>
  <th class="nombre">Présences</th><th class="nombre">Éliminations</th>
  <th class="nombre">Probabilité</th><th class="nombre">Intervalle</th>
  <th class="nombre">Le hasard</th>
</tr></thead>
<tbody>
{% for x in c.par_voix %}
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

La lecture directe : **n’avoir reçu aucune voix la fois d’avant fait passer sous
le hasard** ({{ c.par_voix[0].probabilite }} % contre
{{ c.par_voix[0].hasard }} %), en recevoir une le double presque
({{ c.par_voix[1].probabilite }} %), en recevoir deux le triple
({{ c.par_voix[2].probabilite }} %).

{% include graphiques/conditionnelles-nulle.svg %}

<p class="legende-figure">Écart entre partir après avoir été visé et partir sans
l’avoir été. La silhouette est celle de {{ t1.tirages }} tirages où l’éliminé de
chaque conseil est pris au hasard parmi les présents.</p>

<div class="constat">
  <p>Avoir été visé au conseil précédent ajoute <b>{{ t1.observe | round: 1 }} points</b>
  de risque : {{ t1.ecart_types }} écarts-types au-dessus du hasard, p ajustée
  {{ t1.p_ajustee }}.</p>
  <p>Le modèle nul fait ici tout le travail. À chaque conseil, on tire l’éliminé
  <em>au hasard parmi les présents de ce soir-là</em> : la taille du conseil, la
  saison, l’époque et la composition du camp restent exactement ce qu’elles
  étaient. Ne bouge que la question posée.</p>
</div>

## Le retournement : trop visé pour partir

La courbe ne monte pas indéfiniment. Elle culmine à deux ou trois voix, puis
elle **redescend sous le hasard**.

{% include graphiques/conditionnelles-sommet.svg %}

<p class="legende-figure">Écart entre partir après une à trois voix et partir
après quatre voix ou plus, contre {{ t2.tirages }} tirages du même modèle
nul.</p>

<div class="constat">
  <p>Une à trois voix la fois d’avant : le risque monte. <b>Quatre voix ou
  plus</b> : il tombe à
  {% assign gros = c.par_voix | where: "modalite", "5 voix et plus" | first %}
  <b>{{ gros.probabilite }} %</b> pour cinq voix et plus — soit un cas sur
  {{ gros.effectif }}.</p>
  <p>L’écart vaut {{ t2.observe | round: 1 }} points, {{ t2.ecart_types }} écarts-types,
  p ajustée {{ t2.p_ajustee }}.</p>
</div>

L’explication tient en une phrase, et elle est de survie : **qui a encaissé
quatre bulletins et se trouve encore là au conseil suivant a nécessairement été
protégé** — par un collier, par un tour nul, par une majorité qui s’est
recomposée. Cette protection ne s’évapore pas entre deux conseils. Deux
bulletins, eux, ne déclenchent rien : ils désignent sans sauver.

{% assign sc = c.par_voix_sans_collier | where: "modalite", "5 voix et plus" | first %}
<p class="note"><strong>La vérification qui s’imposait.</strong> Si le
retournement n’était qu’un effet des colliers d’immunité, il devrait disparaître
en écartant les conseils où un objet a annulé des voix. Il ne disparaît pas : à
cinq voix et plus, sans ces conseils-là, la probabilité vaut
<b>{{ sc.probabilite }} %</b> sur {{ sc.effectif }} présences. L’objet n’est
qu’une des formes de la protection ; ce n’est pas la seule.
Voir <a href="{{ '/statistiques/colliers/' | relative_url }}">Les colliers</a>.</p>

<p class="note"><strong>Ce que ces effectifs autorisent, et rien de plus.</strong>
Les cases à quatre voix et plus tiennent en quelques dizaines de présences, et
leurs intervalles sont larges — c’est visible sur la figure, et c’est pour cela
qu’ils y sont dessinés. Le retournement est net, sa <em>hauteur</em> ne l’est
pas.</p>

### Ceux qui ont encaissé quatre voix et sont restés

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Aventurier</th><th>Saison</th>
  <th class="nombre">Voix reçues</th><th>Un objet a annulé des voix</th>
  <th>Au conseil suivant</th>
</tr></thead>
<tbody>
{% for x in c.survivants limit: 15 %}
<tr>
  <td>{{ x.nom }}</td>
  <td>{% assign s = site.data.saisons | where: "id", x.saison | first %}{{ s.titre }} ({{ s.annee }})</td>
  <td class="nombre">{{ x.voix }}</td>
  <td>{% if x.collier %}oui{% else %}non{% endif %}</td>
  <td>{% if x.sorti %}éliminé{% else %}encore là{% endif %}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## La menace s’éteint-elle ?

Si le nom sorti la fois d’avant compte, celui sorti **deux** conseils plus tôt
compte-t-il encore ?

<div class="tableau-large">
<table>
<thead><tr><th>Voix à l’avant-dernier conseil</th><th class="nombre">Présences</th><th class="nombre">Éliminations</th><th class="nombre">Probabilité</th><th class="nombre">Le hasard</th></tr></thead>
<tbody>
{% for x in c.par_voix_deux_pas %}
<tr>
  <td>{{ x.modalite | capitalize }}</td>
  <td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.cas }}</td>
  <td class="nombre"><b>{{ x.probabilite }} %</b></td>
  <td class="nombre">{{ x.hasard }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

{% assign t6 = reg | where: "cle", "menace_deux_pas" | first %}
{% include graphiques/conditionnelles-deux-pas.svg %}

<p class="legende-figure">Écart entre partir quand on avait été visé deux
conseils plus tôt et partir quand on ne l’avait pas été.</p>

<div class="constat">
  <p>{{ t6.observe | round: 1 }} points d’écart — presque autant qu’au conseil
  précédent — mais sur {{ c.par_voix_deux_pas[1].effectif | plus: c.par_voix_deux_pas[2].effectif }}
  présences seulement : {{ t6.ecart_types }} écarts-types, p brute {{ t6.p }},
  p ajustée {{ t6.p_ajustee }}. <b>Non concluant.</b></p>
  <p>La chaîne se raccourcit vite : exiger deux conseils complets d’affilée
  derrière soi ne laisse que {{ c.par_voix_deux_pas[0].effectif | plus: c.par_voix_deux_pas[1].effectif | plus: c.par_voix_deux_pas[2].effectif }}
  présences. Ce qu’on peut dire : rien n’indique que la menace s’éteigne au
  conseil suivant, et l’écart mesuré va dans le sens contraire.</p>
</div>

## À conseil égal

Le tableau ci-dessus compare des soirées entre elles. Le modèle ci-dessous ne
compare jamais deux soirées : chaque conseil forme son propre groupe, et le
calcul ne porte que sur les présents d’un même feu. La taille du conseil, la
saison, l’époque et la composition du camp disparaissent donc **sans qu’on ait à
les mesurer**.

{% include graphiques/conditionnelles-modele.svg %}

<p class="legende-figure">Rapports de cotes d’un logit conditionnel, sur
{{ c.modele.presences }} présences et {{ c.modele.conseils }} conseils.
Référence : aucune voix au conseil précédent.</p>

<div class="tableau-large">
<table>
<thead><tr><th>Voix au conseil précédent</th><th class="nombre">Cote multipliée par</th><th class="nombre">Intervalle</th><th class="nombre">p</th></tr></thead>
<tbody>
{% for x in c.modele.coefficients %}
<tr>
  <td>{{ x.libelle | capitalize }}</td>
  <td class="nombre"><b>{{ x.rapport }}</b></td>
  <td class="nombre">{{ x.bas }} – {{ x.haut }}</td>
  <td class="nombre">{{ x.p }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Le modèle dit la même chose que le tableau brut, ce qui est la meilleure des
nouvelles : l’effet ne venait pas de la taille des conseils.

## La même information, retournée

Une probabilité conditionnelle se lit dans les deux sens, et les deux sens ne
disent pas la même chose. C’est le second qu’on voit à l’écran : on ne regarde
le passé d’un éliminé **qu’une fois qu’il est éliminé**.

<div class="tableau-large">
<table>
<thead><tr><th></th><th class="nombre">Avaient été visés la fois d’avant</th><th class="nombre">Voix reçues en moyenne</th></tr></thead>
<tbody>
<tr><td>Ceux qui sont partis ({{ c.inverse.sortis }})</td>
    <td class="nombre"><b>{{ c.inverse.vise_si_sorti }} %</b></td>
    <td class="nombre">{{ c.inverse.voix_si_sorti }}</td></tr>
<tr><td>Ceux qui sont restés ({{ c.inverse.restes }})</td>
    <td class="nombre">{{ c.inverse.vise_si_reste }} %</td>
    <td class="nombre">{{ c.inverse.voix_si_reste }}</td></tr>
</tbody>
</table>
</div>

**{{ c.inverse.vise_si_sorti }} % de ceux qui partent avaient été visés la fois
d’avant — mais {{ c.inverse.vise_si_reste }} % de ceux qui restent aussi.** Le
signe annonciateur est réel et il est faible : la majorité des éliminations
frappe quelqu’un dont le nom n’était jamais sorti. Confondre les deux sens de
lecture est l’erreur ordinaire sur ce genre de chiffre, et le tableau est là
pour la rendre impossible.

## Sachant tout ce qui précède, et non la seule fois d’avant

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Histoire des voix reçues</th><th class="nombre">Présences</th><th class="nombre">Éliminations</th><th class="nombre">Probabilité</th><th class="nombre">Intervalle</th></tr></thead>
<tbody>
{% for x in c.par_histoire %}
<tr>
  <td>{{ x.modalite | capitalize }}</td>
  <td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.cas }}</td>
  <td class="nombre" data-val="{{ x.probabilite }}"><b>{{ x.probabilite }} %</b></td>
  <td class="nombre">{{ x.bas }} – {{ x.haut }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

{% assign jamais = c.par_histoire | where: "modalite", "jamais visé" | first %}
Le partage utile n’est pas entre « un peu visé » et « beaucoup visé » : il est
entre **{{ jamais.probabilite }} % pour ceux dont le nom n’est jamais sorti** et
une vingtaine de pour cent pour tous les autres. Une fois le nom sorti une
première fois, l’ancienneté de la menace ne change plus grand-chose.

## Sachant de quel côté on a voté

<div class="tableau-large">
<table>
<thead><tr><th>Au conseil précédent, j’ai voté…</th><th class="nombre">Présences</th><th class="nombre">Probabilité de partir</th><th class="nombre">Intervalle</th></tr></thead>
<tbody>
{% for x in c.par_camp %}
<tr><td>{{ x.modalite | capitalize }}</td><td class="nombre">{{ x.effectif }}</td>
    <td class="nombre"><b>{{ x.probabilite }} %</b></td>
    <td class="nombre">{{ x.bas }} – {{ x.haut }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p>{{ t3.observe | round: 1 }} points d’écart, {{ t3.ecart_types }} écarts-types, p brute
  {{ t3.p }}, p ajustée {{ t3.p_ajustee }}. <b>Non concluant.</b></p>
  <p>S’être trompé de cible expose peut-être un peu, mais à
  {{ c.par_camp[1].effectif }} présences du côté de la minorité, un écart de
  trois points ne se distingue pas d’un tirage. On ne peut ni l’affirmer ni
  l’écarter — et l’écrire ainsi vaut mieux que de le publier comme un
  résultat.</p>
</div>

## Une autre question : le nom ressort-il ?

Jusqu’ici la question était « part-il ? ». Celle-ci est différente et se mesure
sur bien plus de monde, puisqu’elle ne demande pas de savoir qui est parti :
**son nom ressort-il de l’urne ?**

{% include graphiques/conditionnelles-cible.svg %}

<p class="legende-figure">Probabilité de recevoir au moins une voix ce soir,
selon le nombre de voix reçues au conseil précédent.</p>

{% include graphiques/conditionnelles-cible-nulle.svg %}

<p class="legende-figure">Écart entre revoir son nom sortir quand il était déjà
sorti et le voir sortir quand il ne l’était pas, contre {{ t4.tirages }}
tirages.</p>

<div class="constat">
  <p>Sans voix la fois d’avant, le nom ressort dans
  {{ c.persistance[0].probabilite }} % des cas. Avec deux voix,
  <b>{{ c.persistance[2].probabilite }} %</b>.</p>
  <p>{{ t4.observe | round: 1 }} points d’écart, {{ t4.ecart_types }} écarts-types,
  p ajustée {{ t4.p_ajustee }}. <b>La cible reste la cible</b>, et c’est le
  résultat le plus net de cette page.</p>
</div>

<p class="note"><strong>Ce modèle nul n’est pas le même que les précédents, et
il fallait en changer.</strong> Rebattre les bulletins à l’intérieur d’un
conseil — le nul employé pour <a href="{{ '/statistiques/alliances/' | relative_url }}">les
alliances</a> — ne convient pas ici : la permutation change qui a écrit, jamais
combien de voix chacun reçoit. Le nombre de voix d’une personne y serait
rigoureusement le même avant et après, et le test ne testerait rien. Celui-ci
redistribue les <em>comptes</em> entre les présents, l’éliminé gardant le sien :
chaque conseil garde sa forme de dépouillement — cinq voix, deux voix, une — et
son résultat, et seule l’identité de ceux qui les reçoivent est tirée au
sort.</p>

## Le retour de bâton

Dernière conditionnelle, et elle ne porte plus sur les sorties mais sur les
bulletins : **celui dont j’ai écrit le nom la fois d’avant écrit-il le mien ce
soir ?**

{% include graphiques/conditionnelles-retour.svg %}

<p class="legende-figure">Part des couples où la cible de la dernière fois rend
le bulletin, tous deux étant présents et votants. Le hasard est ici une
redistribution des bulletins à l’intérieur de chaque conseil.</p>

<div class="constat">
  <p><b>{{ c.retour.probabilite }} %</b> — {{ c.retour.rendus }} couples sur
  {{ c.retour.couples }}, intervalle {{ c.retour.bas }} à {{ c.retour.haut }} %.
  Le hasard en donnerait {{ t5.attendu | round: 1 }} %.</p>
  <p>{{ t5.ecart_types }} écarts-types, p ajustée {{ t5.p_ajustee }}. Écrire un
  nom, c’est donc bien s’exposer à le voir revenir — mais quatre fois sur cinq,
  il ne revient pas.</p>
</div>

[Les conseils]({{ '/statistiques/conseils/' | relative_url }}) mesurent la
réciprocité **sans ordre** : deux personnes qui se sont écrites l’une l’autre à
un moment ou un autre. Celle-ci est datée et orientée, ce qui la rend beaucoup
plus rare — et beaucoup plus lisible.

## Ce que cette page ne dit pas

<div class="constat">
  <p><b>Ce n’est pas une prédiction.</b> Toutes ces probabilités sont mesurées
  après coup, sur des conseils dont on connaît déjà l’issue. Elles décrivent une
  régularité du jeu ; elles ne donnent pas un pronostic à un joueur en
  particulier.</p>
  <p><b>Ce n’est pas une cause.</b> Recevoir deux voix n’envoie personne dehors :
  c’est le même rapport de force qui produit les deux voix d’hier et
  l’élimination d’aujourd’hui. La donnée ne sait pas les séparer, et rien ici ne
  prétend le contraire.</p>
  <p><b>C’est un conseil sur six.</b> {{ c.conseils }} conseils enchaînés sur
  les {{ site.data.stats.conseils.conseils }} du jeu, parce que
  l’exigence de dépouillement complet est sévère et que la chaîne se rompt au
  premier trou. Les saisons les mieux documentées y pèsent plus que les
  autres.</p>
</div>

La question inverse — non plus « sachant mon passé », mais **« sachant qui est
assis autour du feu ce soir »** — est traitée sur
[Sachant qui est autour du feu]({{ '/statistiques/autour-du-feu/' | relative_url }}) :
le bandeau minoritaire, le sexe minoritaire, le doyen, le gagnant du confort, et
la seule probabilité conditionnelle du jeu qui vaut exactement zéro.

La liste complète des tests de ce site, leur correction pour tests multiples et
ce que chaque modèle ne peut pas établir sont sur
[La méthode]({{ '/methode/' | relative_url }}).
