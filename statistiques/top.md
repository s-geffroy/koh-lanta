---
layout: page
title: Le top des joueurs
permalink: /statistiques/top/
chapeau: >-
  Cinq facettes, aucune victoire dans le calcul, et deux découvertes : gagner
  les épreuves n’a **aucun rapport** avec bien jouer le conseil, et
  **quatre-vingt-quatorze joueurs** peuvent entrer dans ce top selon les poids
  qu’on choisit.
---

{% assign c = site.data.stats.classement %}
{% assign rb = c.robustesse %}
{% assign h = c.hasard %}
{% assign pl = c.palmares %}

Tout le monde a son classement, personne n’a le même, et aucun n’explique
comment il a été fait. Celui-ci est fabriqué devant vous, sur les
{{ c.joueurs_classes }} aventuriers du programme, à partir de cinq mesures
tirées des données — et il est publié **avec de quoi le démolir**.

Une règle a présidé à tout le reste : **le palmarès n’entre pas dans le
calcul**. Ni le titre, ni la place de finaliste. Un classement qui compte la
victoire parmi ses ingrédients remet les vainqueurs devant et appelle cela un
résultat ; c’est une tautologie déguisée. Ici, la victoire est la chose qu’on
regarde **après**, pour voir si le score la retrouve tout seul.

<ul class="chiffres">
  <li class="chiffre"><b>{{ c.joueurs_classes }}</b><span>aventuriers classés</span></li>
  <li class="chiffre"><b>{{ rb.candidats }}</b><span>entrent dans le top {{ c.taille }} selon les poids</span></li>
  <li class="chiffre"><b>{{ rb.socle }}</b><span>y sont sous plus de 99 % des pondérations</span></li>
</ul>

## Les cinq facettes, et leur dénominateur

Un chiffre ne veut rien dire sans ce qui le divise. Chaque facette porte donc
le sien, et il est publié à côté du classement.

<div class="tableau-large">
<table>
<thead><tr><th>Facette</th><th>Ce qu’elle mesure</th><th>Ce qu’on compte</th><th>Rapporté à</th><th class="nombre">Documentée pour</th></tr></thead>
<tbody>
{% for f in c.facettes %}
<tr><td><b>{{ f.libelle }}</b></td>
    <td>{{ f.question }}</td>
    <td>{{ f.mesure }}</td>
    <td>{{ f.denominateur }}</td>
    <td class="nombre">{{ f.documentes }} joueurs</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note"><strong>Aucun seuil n’exclut personne.</strong> Un taux sur
trois essais ne vaut rien, mais écarter celui qui n’a que trois essais
fabriquerait un classement de survivants. On <em>rétrécit</em> donc chaque taux
vers la moyenne de la population, d’autant plus fort que les essais sont rares.
La force de ce rétrécissement n’est pas choisie à la main : elle est estimée
sur les données elles-mêmes, par la méthode des moments. Faute de preuve, un
joueur vaut la moyenne — il ne vaut ni zéro, ni l’exclusion.</p>

<p class="note">Une précision sur le parcours : le rang final est donné en
clair par la source pour {{ c.rangs_attestes }} des
{{ c.participations_classees }} participations. Pour les
{{ c.rangs_deduits }} autres, il est reconstitué à partir du jour de sortie,
les ex æquo se partageant le rang. Rien n’est deviné, mais ce n’est pas la même
qualité de donnée, et c’est dit.</p>

<p class="note"><strong>Une conséquence à signaler, parce qu’elle décide de
la moitié du classement.</strong> Sur la facette du parcours, la dispersion
entre joueurs n’est pas décelable — ce que la section sur la stabilité mesure
plus bas — et le rétrécissement y part donc au plafond. La facette se comporte
alors comme un <em>cumul</em> : elle récompense d’être allé loin <em>et</em> de
l’avoir refait. Un vainqueur d’une seule saison y plafonne là où un habitué des
retours accumule. C’est assumé : « meilleur joueur » ne pose pas la même
question que « meilleure saison jouée », et la seconde a sa propre liste plus
bas.</p>

## Le top {{ c.taille }}

Le score est la moyenne des cinq facettes, ramenées chacune à une même échelle.
Poids égaux : c’est la seule pondération qui ne demande à personne de décider
que le physique compte plus que le vote.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th class="nombre">#</th><th>Aventurier</th><th class="nombre">Score</th>
  <th class="nombre">Saisons</th><th class="nombre">Titres</th>
  <th class="nombre">Dans le top selon les poids</th>
  <th class="nombre">Rang, du 5<sup>e</sup> au 95<sup>e</sup> centile</th>
</tr></thead>
<tbody>
{% for l in c.top %}
<tr><td class="nombre">{{ l.rang }}</td>
    <td>{{ l.nom }}<br><small>{{ l.saisons }}</small></td>
    <td class="nombre">{{ l.score }}</td>
    <td class="nombre">{{ l.participations }}</td>
    <td class="nombre">{{ l.titres }}</td>
    <td class="nombre">{{ l.part_top }} %</td>
    <td class="nombre">{{ l.rang_p05 }} – {{ l.rang_p95 }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

## Ce que les poids décident — et c’est presque tout

Voilà l’objection qu’on fait à tous les classements : *vos poids sont
arbitraires*. Elle est juste. Plutôt que de défendre les miens, je les ai tous
essayés — **{{ rb.tirages }} pondérations tirées au hasard** sur les cinq
facettes, sans aucune opinion sur leur importance relative, et le classement
refait à chaque fois.

{% include graphiques/top-rangs.svg %}

<p class="legende-figure">Pour chacun des {{ c.taille }} premiers : son rang
médian, et l’intervalle qui contient 90 % de ses rangs selon la pondération.</p>

<div class="constat">
  <p><b>{{ rb.candidats }} aventuriers différents entrent dans le top
  {{ c.taille }}</b> selon la pondération choisie. Pour {{ c.taille }} places.</p>
  <p>{% if rb.toujours == 0 %}<b>Aucun</b> n’y figure sous <em>toutes</em> les
  pondérations.{% elsif rb.toujours == 1 %}<b>Un seul</b> y figure sous
  <em>toutes</em> les pondérations.{% else %}<b>{{ rb.toujours }}</b> y figurent
  sous <em>toutes</em> les pondérations.{% endif %} Ils ne sont que
  <b>{{ rb.socle }}</b> à y être dans plus de 99 % des cas —
  {{ rb.socle_noms | join: " et " }} — et le moins solide du top actuel n’y
  tient que {{ rb.part_top_minimale_du_top }} % du temps.</p>
</div>

<div class="tableau-large">
<table>
<thead><tr><th>Présent dans le top {{ c.taille }} sous…</th><th class="nombre">Nombre de joueurs</th></tr></thead>
<tbody>
{% for p in rb.paliers %}
<tr><td>plus de {{ p.seuil }} % des pondérations</td>
    <td class="nombre">{{ p.effectif }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">La lecture juste de ce tableau : un classement des joueurs de
Koh-Lanta n’a pas un noyau dur de {{ c.taille }} noms, il en a
<strong>{{ rb.socle }}</strong> — et une longue zone grise où le rang dit
surtout ce que son auteur trouve important. Quand quelqu’un vous donne son
top 10, il vous parle de lui.</p>

## Le même classement, fabriqué par le hasard

Une deuxième objection, plus rude : est-ce que n’importe quelles données
donneraient un top d’apparence aussi convaincante ? On peut le vérifier. Chaque
joueur **garde exactement ses occasions** — son nombre de conseils, d’épreuves,
de bulletins — et ne perd que son talent : ses résultats lui sont retirés au
hasard, à la moyenne de la population. Puis le classement est refait à
l’identique.

{% include graphiques/top-hasard.svg %}

<p class="legende-figure">Score du premier au vingt-cinquième, pour le
classement réel et pour un classement où les résultats ont été tirés au sort.</p>

<div class="constat">
  <p>Le hasard produit un premier à <b>{{ h.premier }}</b>, un vingt-cinquième
  à {{ h.vingt_cinquieme }}, et un écart de {{ h.ecart }} entre les deux. Il
  produit aussi des noms — {{ h.noms | join: ", " }} — qu’on pourrait commenter
  avec le même aplomb.</p>
  <p><b>Le classement réel tient l’épreuve</b> : son premier est à
  {{ h.reel_premier }}, et l’écart du premier au vingt-cinquième vaut
  {{ h.reel_ecart }} — <b>{{ h.reel_ecart | divided_by: h.ecart | round: 1 }} fois</b>
  celui du hasard. La hiérarchie n’est donc pas fabriquée de toutes pièces. Mais
  un top tiré au sort a de l’allure, et c’est ce qu’il fallait montrer.</p>
</div>

## Les cinq facettes parlent-elles du même talent ?

Si « bon joueur » désigne quelque chose, les cinq facettes doivent aller
ensemble : celui qui gagne les épreuves devrait aussi voter juste. Sinon, le
score synthétique ne fait que moyenner cinq qualités sans rapport, et son
premier est celui que la moyenne a favorisé.

{% include graphiques/top-correlations.svg %}

<p class="legende-figure">Corrélation de rang entre chaque paire de facettes,
sur les {{ c.joueurs_classes }} joueurs classés. En clair, les quatre paires qui
font intervenir les épreuves.</p>

La corrélation moyenne vaut {{ c.correlation_moyenne }} — et c’est le chiffre à
ne pas retenir, parce qu’il moyenne deux régimes opposés.

{% assign sansEp = c.correlations | where_exp: "x", "x.a != 'epreuves'" | where_exp: "x", "x.b != 'epreuves'" | map: "rho" | sort %}
{% assign avecEp = c.correlations | where_exp: "x", "x.a == 'epreuves' or x.b == 'epreuves'" | map: "rho" | sort %}

<div class="constat">
  <p><b>Les quatre facettes du jeu social se tiennent</b> : parcours,
  discrétion, résistance et lecture s’accordent deux à deux entre
  {{ sansEp.first }} et {{ sansEp.last }}. Celui qui vote juste est aussi celui
  qu’on n’écrit pas, et il va plus loin.</p>
  <p><b>Les épreuves, elles, ne sont corrélées à rien.</b> Les
  {{ avecEp | size }} paires qui les font intervenir tiennent toutes entre
  {{ avecEp.first }} et {{ avecEp.last }} — c’est-à-dire <em>zéro</em>. Gagner
  les épreuves et bien jouer le conseil sont deux talents <b>sans aucun rapport
  mesurable</b> dans ces données.</p>
</div>

<p class="note">Conséquence directe sur la lecture du top : un classement qui
pèse plus le physique et un classement qui pèse plus le social ne sont pas deux
versions du même palmarès, ce sont <strong>deux palmarès différents</strong>.
C’est aussi ce qui explique l’ampleur du mouvement mesuré plus haut — quand les
facettes divergent à ce point, changer les poids change les noms. Une réserve
enfin, qui joue vers le haut : le rétrécissement ramène à la moyenne les joueurs
peu documentés <em>sur toutes les facettes à la fois</em>, ce qui crée à lui
seul un peu d’accord. Les corrélations sociales sont donc majorées ; celle des
épreuves, déjà nulle, ne peut que l’être aussi.</p>

## Un bon joueur l’est-il encore la fois suivante ?

C’est la question dont dépend tout le reste. Si la qualité est une propriété du
**joueur**, elle doit réapparaître quand il rejoue. Si elle est une propriété de
la **saison** — du tirage des tribus, du casting, de qui l’avait dans le nez —
elle ne réapparaît pas, et classer des personnes n’a pas d’objet.

{% assign t = site.data.stats.modeles.registre | where: "cle", "talent_stable" | first %}

{% include graphiques/top-stabilite.svg %}

<p class="legende-figure">Corrélation entre le score de la première
participation et la moyenne des suivantes, chez les {{ c.stabilite.effectif }}
aventuriers qui ont joué au moins deux fois, face à {{ t.tirages }} appariements
tirés au hasard.</p>

<div class="constat">
  <p><b>Rien.</b> La corrélation observée vaut {{ t.observe }}, contre
  {{ t.attendu }} attendu du hasard : {{ t.ecart_types }} écart-type,
  p = {{ t.p }} — et {{ t.p_ajustee }} après correction pour tests multiples.
  Le trait tombe au milieu de la masse.</p>
  <p>Sur ces données, <b>la performance d’un aventurier ne se reproduit pas</b>
  d’une saison à l’autre. Ce que ce classement mesure est donc, pour une part
  qu’on ne sait pas borner, ce qui lui est arrivé — et non ce qu’il est.</p>
</div>

<p>Une seconde mesure, indépendante de ce test, dit la même chose. Pour savoir
de combien rétrécir la facette du parcours, on compare ce qu’un même aventurier
fait varier d’une saison à l’autre à ce qui sépare les aventuriers entre eux.
<b>Le premier dépasse le second</b> : aucun écart stable entre joueurs n’y est
décelable, et le rétrécissement part au plafond. Deux calculs sans rapport,
une seule conclusion.</p>

<p class="note"><strong>Une réserve, et elle joue dans le sens inverse.</strong>
Ces {{ c.stabilite.effectif }} aventuriers ne sont pas un échantillon : ce sont
ceux que la production a <em>rappelés</em>, donc les meilleurs de leur saison.
Comparer des gens déjà triés sur le talent écrase mécaniquement la corrélation —
c’est le même effet qui fait qu’en ne regardant que les recrues d’une équipe
première, on ne trouve plus de lien entre taille et performance. L’absence de
lien mesurée ici est donc un plancher, pas une preuve que le talent n’existe
pas. Elle suffit néanmoins à dire qu’il ne <em>domine</em> pas.</p>

## Le score n’a jamais vu le palmarès — et il le retrouve

Le contrôle qui manquerait à n’importe quel autre top. Aucune des cinq facettes
ne sait qui a gagné. Où tombent les vainqueurs ?

<div class="constat">
  <p>Le rang médian des <b>{{ pl.vainqueurs_total }} vainqueurs</b> est
  <b>{{ pl.rang_median_vainqueurs }}</b> sur {{ c.joueurs_classes }}. Celui de
  tous les autres est {{ pl.rang_median_autres }}.</p>
  <p>Pris au hasard, un vainqueur est mieux classé qu’un non-vainqueur dans
  <b>{{ pl.auc | times: 100 | round: 1 }} %</b> des cas. Un score aveugle au
  palmarès reconstitue donc largement le palmarès — c’est la meilleure raison
  qu’on ait de le prendre au sérieux, et elle ne doit rien à la construction.</p>
</div>

<p class="note">{{ pl.vainqueurs_dans_le_top }} des
{{ pl.vainqueurs_total }} vainqueurs figurent dans le top {{ c.taille }}. Les
autres n’y sont pas, et ce n’est pas une anomalie : gagner une saison demande
d’aller au bout d’une seule, quand ce classement demande d’avoir bien joué
partout où l’on a joué.</p>

## Les meilleurs qui n’ont jamais gagné

La sous-liste la plus intéressante du lot, et celle qui justifie de ne pas avoir
mis la victoire dans le calcul.

<div class="tableau-large">
<table data-triable>
<thead><tr><th class="nombre">Rang général</th><th>Aventurier</th><th class="nombre">Score</th><th class="nombre">Dans le top selon les poids</th></tr></thead>
<tbody>
{% for l in c.sans_titre %}
<tr><td class="nombre">{{ l.rang }}</td><td>{{ l.nom }}</td>
    <td class="nombre">{{ l.score }}</td>
    <td class="nombre">{{ l.part_top }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

## Les cinq classements par facette

Le top synthétique cache ce qu’il moyenne. Voici les cinq classements séparés,
chacun sur sa mesure et avec le compte brut qui la fonde.

{% for f in c.facettes %}
### {{ f.libelle }} — {{ f.question | downcase }}

<p class="note">{{ f.mesure }}, rapporté à {{ f.denominateur }}. Moyenne du
programme : {{ f.moyenne }}{{ f.unite }}. {{ f.documentes }} joueurs ont au
moins une observation ; les autres valent la moyenne, faute de preuve.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr><th class="nombre">#</th><th>Aventurier</th><th class="nombre">Valeur</th><th class="nombre">Compte brut</th><th class="nombre">Rang général</th></tr></thead>
<tbody>
{% for l in f.top %}
<tr><td class="nombre">{{ l.rang }}</td><td>{{ l.nom }}</td>
    <td class="nombre">{{ l.valeur }}{{ f.unite }}</td>
    <td class="nombre">{{ l.brut }}</td>
    <td class="nombre">{{ l.rang_general }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>
{% endfor %}

## La meilleure saison jamais jouée

Autre question, autre liste. Ci-dessus, un joueur ; ici, **une saison** — une
participation, sur ses seules cinq facettes, sans rien cumuler.

<div class="tableau-large">
<table data-triable>
<thead><tr><th class="nombre">#</th><th>Aventurier</th><th>Saison</th><th class="nombre">Année</th><th>Fin de parcours</th><th class="nombre">Score</th></tr></thead>
<tbody>
{% for l in c.top_saisons %}
<tr><td class="nombre">{{ l.rang }}</td><td>{{ l.aventurier }}</td>
    <td>{{ l.saison }}</td><td class="nombre">{{ l.annee }}</td>
    <td>{{ l.sort }}</td><td class="nombre">{{ l.score }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

## Et sans les éditions de revenants ?

Les {{ c.joueurs_classes }} joueurs ci-dessus comprennent les éditions
spéciales, où le casting est trié sur le volet : on y affronte des adversaires
bien plus forts, ce que le classement ne sait pas corriger. Refait sur les
seules saisons classiques, sur {{ c.joueurs_classiques }} joueurs :

<div class="tableau-large">
<table data-triable>
<thead><tr><th class="nombre">#</th><th>Aventurier</th><th class="nombre">Score</th><th class="nombre">Rang toutes saisons</th></tr></thead>
<tbody>
{% for l in c.top_classique %}
<tr><td class="nombre">{{ l.rang }}</td><td>{{ l.nom }}</td>
    <td class="nombre">{{ l.score }}</td>
    <td class="nombre">{{ l.rang_general }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

## Le biais que ce classement ne sait pas réparer

{% assign be = c.biais_epoque %}

Trois facettes sur cinq — la discrétion, la résistance, la lecture — se lisent
sur les bulletins, et **le dépouillement des conseils s’effondre à l’époque
récente**. Les joueurs des dernières saisons sont donc, sur ces trois facettes,
ramenés à la moyenne faute d’observations. Ce n’est pas une opinion sur leur
niveau, c’est un trou dans la source.

<div class="tableau-large">
<table>
<thead><tr><th>Période</th><th class="nombre">Conseils</th><th class="nombre">Au dépouillement complet</th><th class="nombre">Part</th></tr></thead>
<tbody>
{% for d in be.depouillement %}
<tr><td>{{ d.periode }}</td>
    <td class="nombre">{{ d.conseils }}</td>
    <td class="nombre">{{ d.complets }}</td>
    <td class="nombre">{{ d.part }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

Standardiser chaque facette **à l’intérieur de sa période** ne répare pas la
donnée manquante, mais mesure de combien le classement bouge quand on l’y
contraint :

<div class="constat">
  <p><b>{{ be.communs }} des {{ be.taille }} noms restent les mêmes</b>, et le
  déplacement médian est de {{ be.deplacement_median }} rangs. Sortent :
  {{ be.sortants | join: ", " }}. Entrent : {{ be.entrants | join: ", " }}.</p>
  <p>Le biais existe donc, et il est réel — mais il ne renverse pas la table.
  Ce qui décide du top n’est pas l’époque.</p>
</div>

<p class="note">Les limites, en un bloc, parce qu’elles comptent autant que le
classement. <strong>Le test de stabilité ne trouve rien</strong> : la
performance ne se reproduit pas d’une saison à l’autre, et c’est le résultat le
plus gênant de cette page. <strong>Les poids sont arbitraires</strong> :
{{ rb.socle }} joueurs seulement tiennent dans plus de 99 % des pondérations,
et {{ rb.candidats }} peuvent entrer dans le top.
<strong>Trois facettes sur cinq dépendent d’un dépouillement inégal.</strong>
<strong>La discrétion est ambivalente</strong> : n’être jamais écrit peut aussi
vouloir dire qu’on ne menaçait personne — c’est exactement ce que
<a href="{{ '/statistiques/jeu-social/' | relative_url }}">le jeu social</a>
montre en ne la classant que deuxième.
<strong>Et deux dimensions entières manquent</strong> : les colliers d’immunité,
relevés sur {{ site.data.stats.colliers.saisons_couvertes }} saisons seulement,
et les objets qui les ont remplacés — armes secrètes, totem maudit, talisman —
dont
<a href="{{ '/sources/' | relative_url }}">les sources</a> ne donnent pas le
détail. Le seul test déclaré ici est celui de la stabilité, et il entre au
<a href="{{ '/methode/' | relative_url }}">registre corrigé</a> avec les autres :
un test qu’on tiendrait à l’écart de la liste serait un test gratuit.</p>

Pour aller voir les mesures une par une :
[le jeu social]({{ '/statistiques/jeu-social/' | relative_url }}),
[les épreuves]({{ '/statistiques/epreuves/' | relative_url }}),
[la force réelle]({{ '/statistiques/force/' | relative_url }}) et
[les revenants]({{ '/statistiques/revenants/' | relative_url }}).
