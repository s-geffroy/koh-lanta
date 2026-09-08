---
layout: page
title: Le top des joueurs de Koh-Lanta
description: "Le top des joueurs de Koh-Lanta : quatre façons de bien jouer, mesurées sans jamais regarder qui a gagné, et le classement des 531 aventuriers."
permalink: /statistiques/top/
chapeau: >-
  Quatre façons de bien jouer, mesurées sans jamais regarder qui a gagné.
  **Aucune ne prédit les autres** — et une cinquième a dû être retirée parce
  qu’elle ne mesurait qu’une chose : le soir où l’on part.
---

{% assign c = site.data.stats.classement %}
{% assign rb = c.robustesse %}
{% assign h = c.hasard %}
{% assign pl = c.palmares %}
{% assign ar = c.artefacts %}

Tout le monde a son classement, personne n’a le même, et aucun n’explique
comment il a été fait. Celui-ci est fabriqué devant vous, sur les
{{ c.joueurs_classes }} aventuriers du programme, et il est publié **avec de
quoi le démolir**.

Une règle a présidé à tout le reste : **le palmarès n’entre pas dans le
calcul**. Ni le titre, ni la place de finaliste. Un classement qui compte la
victoire parmi ses ingrédients remet les vainqueurs devant et appelle cela un
résultat ; c’est une tautologie déguisée. Ici, la victoire est la chose qu’on
regarde **après**, pour voir si le score la retrouve tout seul.

<ul class="chiffres">
  <li class="chiffre"><b>{{ c.joueurs_classes }}</b><span>aventuriers classés</span></li>
  <li class="chiffre"><b>{{ rb.candidats }}</b><span>entrent dans le top {{ c.taille }} selon les poids</span></li>
  <li class="chiffre"><b>{{ c.correlations[0].rho }}</b><span>corrélation la plus forte entre deux facettes</span></li>
</ul>

## Les quatre facettes, et leur dénominateur

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
joueur vaut la moyenne — il ne vaut ni zéro, ni l’exclusion.
<a href="{{ '/methode/' | relative_url }}">La méthode</a> le détaille.</p>

{% assign ce = c.couverture_epreuves %}

<p class="note"><strong>Ce que la facette des épreuves ne peut pas voir.</strong>
Deux sources comptent les victoires individuelles, et elles ne disent pas la
même chose. Le <em>tableau de saison</em> date chaque épreuve : lui seul fournit
un dénominateur, donc lui seul sert ici. La <em>fiche individuelle</em> donne un
total par saison, sans dates. Là où les deux se comparent, elles s’accordent
sur <b>{{ ce.part_accord }} %</b> des {{ ce.comparables }} participations.
Surtout, la fiche attribue <b>{{ ce.victoires_invisibles }} victoires</b> à
{{ ce.participations_invisibles }} participations pour lesquelles le tableau ne
fournit aucun dénominateur — les cinq saisons sans relevé d’épreuves, pour
l’essentiel. Ces victoires-là sont <strong>invisibles au classement</strong>.
Un aventurier dont deux saisons sur trois sont dans ce cas est donc jugé sur la
troisième, et il faut le savoir avant de lire son rang.</p>

<p class="note">Une précision sur le parcours : le rang final est donné en
clair par la source pour {{ c.rangs_attestes }} des
{{ c.participations_classees }} participations. Pour les
{{ c.rangs_deduits }} autres, il est reconstitué à partir du jour de sortie,
les ex æquo se partageant le rang. Rien n’est deviné, mais ce n’est pas la même
qualité de donnée, et c’est dit.</p>

## La cinquième facette, et pourquoi elle n’existe pas

Il y en avait cinq. La cinquième s’appelait **la résistance** : s’en sortir
quand le nom écrit au conseil est le vôtre. C’est la qualité que tout le monde
cite en premier pour désigner un grand joueur. Elle a été construite, publiée,
puis retirée.

<div class="constat">
  <p>Sur les <b>{{ ar.resistance.occasions }} occasions</b> où quelqu’un est
  visé à un conseil dépouillé, <b>{{ ar.resistance.dont_le_soir_du_depart }}</b>
  — soit {{ ar.resistance.part }} % — <b>sont le conseil qui l’élimine</b>.
  C’est un échec que personne ne peut éviter, et il était compté comme un
  échec.</p>
  <p>Retirez-les : il ne reste que des survies, et le taux monte à
  <b>100 % pour tout le monde</b>. La facette n’avait pas d’autre signal que
  cet échec obligatoire. Elle ne mesurait pas l’art de s’en sortir — elle
  mesurait <em>combien de fois on nous a vu partir</em>.</p>
</div>

Le coup est plus dur encore sur ceux qu’on observe peu :
**{{ ar.resistance.une_seule_occasion }} participations** n’ont qu’une seule
occasion mesurée, et pour **{{ ar.resistance.une_seule_et_fatale }} d’entre
elles** — {{ ar.resistance.part_une_seule }} % — cette unique occasion *est*
l’élimination. Leur résistance valait zéro par construction.

### Le même piège, désamorcé sur les deux facettes qui restent

<div class="constat">
  <p><b>Un aventurier ne vote jamais pour lui-même.</b> Le bulletin qu’il émet
  le soir de son élimination est donc faux par construction :
  <b>{{ ar.lecture.justes_du_partant }} juste sur
  {{ ar.lecture.bulletins_du_partant }}</b>. Les autres soirs, la justesse est
  de {{ ar.lecture.taux_des_autres_soirs }} % — contre
  {{ ar.lecture.taux_tout_compris }} % si l’on garde tout. Ce bulletin-là est
  écarté.</p>
  <p><b>Les voix qui vous sortent ne mesurent pas votre discrétion.</b> Elles
  pèsent <b>{{ ar.discretion.part }} %</b> de toutes les voix relevées, et elles
  séparent les <em>manières de sortir</em> bien plus que les joueurs : 1,35 voix
  par conseil pour un éliminé au conseil, 0,14 pour un vainqueur. Les compter
  revient à redemander « a-t-il été éliminé au conseil ? », ce que le parcours
  dit déjà. Le soir du départ est écarté des deux côtés.</p>
</div>

<p class="note">Ces trois corrections ne sont pas des ajustements de confort :
elles ont <strong>renversé le résultat principal de cette page</strong>. Dans sa
première version, les quatre facettes non physiques s’accordaient entre 0,349 et
0,507, et la page en concluait qu’il existait un « jeu social » cohérent. Cet
accord était fabriqué par le soir du départ, présent dans les trois à la fois.
Retiré, il ne reste rien — la section suivante le montre.
<a href="{{ '/sources/' | relative_url }}">Les sources</a> racontent la revue.</p>

## Le top {{ c.taille }}

Le score est la moyenne des quatre facettes, ramenées chacune à une même
échelle. Poids égaux : c’est la seule pondération qui ne demande à personne de
décider que le physique compte plus que le vote.

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

## Et les visages qu’on connaît ?

C’est la question qu’on pose en premier devant un classement — *« et untel ? »*
— et la réponse est souvent plus instructive que le top lui-même. Voici, sans
tri d’auteur, **tous les aventuriers d’au moins trois saisons achevées**, et où
ils tombent.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th class="nombre">Rang</th><th>Aventurier</th>
  <th class="nombre">Saisons</th><th class="nombre">Titres</th>
  <th class="nombre">Score</th>
  {% for f in c.facettes %}<th class="nombre">{{ f.libelle | remove: "Le " | remove: "La " | remove: "Les " }}</th>{% endfor %}
  <th class="nombre">Rang, 5<sup>e</sup>–95<sup>e</sup> centile</th>
</tr></thead>
<tbody>
{% for l in c.carrieres %}
<tr><td class="nombre">{{ l.rang }}</td><td>{% include lien-aventurier.html id=l.id nom=l.nom %}</td>
    <td class="nombre">{{ l.participations }}</td>
    <td class="nombre">{{ l.titres }}</td>
    <td class="nombre">{{ l.score }}</td>
    {% for f in c.facettes %}<td class="nombre">{{ l.facettes[f.cle] }}</td>{% endfor %}
    <td class="nombre" data-val="{{ l.rang_p95 | minus: l.rang_p05 }}">{{ l.rang_p05 }} – {{ l.rang_p95 }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="legende-figure">Les quatre colonnes de facettes sont des écarts à la
moyenne, en écarts-types : 0 est la moyenne du programme, positif est meilleur.
La dernière donne l’étendue des rangs sous les
{{ rb.tirages }} pondérations tirées — plus elle est large, moins le rang
affiché veut dire quelque chose.</p>

{% assign cr = c.carrieres %}

<div class="constat">
  <p><b>{{ cr[0].nom }} est {{ cr[0].rang }}<sup>e</sup>,
  {{ cr[1].nom }} est {{ cr[1].rang }}<sup>e</sup></b> — et tous deux ont joué
  {{ cr[0].participations }} saisons. Le nombre de participations ne dit donc
  rien du niveau : il dit qui la production redemande, ce que
  <a href="{{ '/statistiques/revenants/' | relative_url }}">les revenants</a>
  mesurent à part.</p>
  <p>Ce qui les sépare tient en une colonne. {{ cr[0].nom }} est à
  <b>{{ cr[0].facettes.epreuves }}</b> sur les épreuves — le deuxième meilleur
  du programme. {{ cr[1].nom }} est à <b>{{ cr[1].facettes.lecture }}</b> sur la
  lecture : sur les {{ cr[1].preuve.lecture }} bulletins qu’on peut lire de sa
  carrière, il a rarement écrit le nom de celui qui partait.</p>
</div>

<p class="note">Un nom que tout le monde connaît n’est pas un nom que les
données distinguent, et c’est le plus utile de ce tableau. La notoriété se
construit à l’écran — sur une phrase, un caractère, une scène. Ce classement ne
voit ni l’écran ni le montage : il voit des bulletins, des épreuves et des jours
tenus. <strong>Les deux ne se recouvrent pas, et rien n’oblige à préférer
celui-ci.</strong></p>

## Les quatre facettes parlent-elles du même talent ?

Si « bon joueur » désignait quelque chose, les facettes iraient ensemble : celui
qui gagne les épreuves devrait aussi voter juste. On peut le vérifier
directement.

{% include graphiques/top-correlations.svg %}

<p class="legende-figure">Corrélation de rang entre chaque paire de facettes,
en valeur absolue, sur les {{ c.joueurs_classes }} joueurs classés. En clair,
les paires dont la corrélation est négative.</p>

<div class="constat">
  <p><b>Rien ne va avec rien.</b> Sur les six paires possibles, la plus forte
  vaut <b>{{ c.correlations[0].rho }}</b> et la plus faible
  {{ c.correlations[5].rho }}. La moyenne des six est
  {{ c.correlation_moyenne }}.</p>
  <p>Il n’existe donc pas de « bon joueur » au singulier. Être bon quelque part
  ne dit rien de ce qu’on vaut ailleurs, et un score synthétique ne fait
  qu’<em>additionner quatre qualités sans rapport</em>. Son premier est celui
  que la moyenne a favorisé.</p>
</div>

{% assign menees = 0 %}{% for f in c.facettes %}{% if f.top[0].id == c.top[0].id %}{% assign menees = menees | plus: 1 %}{% endif %}{% endfor %}

<p>La démonstration tient en un nom. <b>{{ c.top[0].nom }}</b>, premier du
classement général, n’est en tête que de <b>{{ menees }} facettes sur
{{ c.facettes | size }}</b>. Qui mène sur chacune :
{% for f in c.facettes %}{{ f.libelle | downcase }} — <b>{{ f.top[0].nom }}</b>{% unless forloop.last %} ; {% endunless %}{% endfor %}.
Le premier d’un classement composite n’est donc pas le meilleur partout : c’est
celui qui est excellent <b>là où l’écart-type est le plus large</b>, et qui se
contente d’être moyen ailleurs.</p>

### Un exemple que tout le monde croit connaître

« Être fort aux épreuves fait de vous une cible » : la phrase est dans toutes
les bouches. Voici les meilleurs aux épreuves, et leur rang en discrétion.

{% assign fe = c.facettes | where: "cle", "epreuves" | first %}
{% assign fd = c.facettes | where: "cle", "discretion" | first %}

<div class="tableau-large">
<table>
<thead><tr><th class="nombre">#</th><th>Aventurier</th><th class="nombre">{{ fe.mesure }}</th><th class="nombre">Rang en {{ fd.libelle | downcase }}</th></tr></thead>
<tbody>
{% for l in fe.top %}
<tr><td class="nombre">{{ l.rang }}</td><td>{% include lien-aventurier.html id=l.id nom=l.nom %}</td>
    <td class="nombre">{{ l.brut }}</td>
    <td class="nombre">{{ l.rangs.discretion }}<sup>e</sup></td></tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p><b>Aucun motif.</b> Les meilleurs aux épreuves s’étalent sur toute la
  largeur du classement de la discrétion. La corrélation entre les deux vaut
  {% for x in c.correlations %}{% if x.a == "epreuves" and x.b == "discretion" %}<b>{{ x.rho }}</b>{% endif %}{% endfor %}
  — et si elle penche, c’est du mauvais côté pour la légende : les forts sont
  très légèrement <em>moins</em> visés, pas plus.</p>
</div>

<p class="note"><strong>Sans contradiction avec
<a href="{{ '/statistiques/fusion/' | relative_url }}">« on élimine le fort
avant la fusion »</a></strong>, qui est un résultat retenu. Les deux ne parlent
pas de la même chose : cette page-là mesure <em>qui</em> sort à un moment donné,
celle-ci compte les voix reçues <em>hors du soir où l’on part</em>. Être sorti
parce qu’on est fort et être écrit toute la saison sont deux faits distincts —
et le second n’a pas lieu.</p>

<p class="note">C’est ce qui explique l’ampleur du mouvement mesuré plus bas :
quand les composantes divergent à ce point, changer les poids change les noms.
Et c’est aussi ce qui rend la première version de cette page fausse : elle
lisait un accord de 0,35 à 0,51 entre les facettes du conseil, mais cet accord
venait du soir du départ, compté trois fois. Une corrélation qui disparaît
quand on retire un artefact commun n’était pas une corrélation.</p>

## Ce que les poids décident — et c’est presque tout

Voilà l’objection qu’on fait à tous les classements : *vos poids sont
arbitraires*. Elle est juste. Plutôt que de défendre les miens, je les ai tous
essayés — **{{ rb.tirages }} pondérations tirées au hasard** sur les quatre
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
  sous <em>toutes</em> les pondérations.{% endif %}
  {% if rb.socle == 1 %}Un seul y est dans plus de 99 % des cas
  — <b>{{ rb.socle_noms | join: " et " }}</b>{% else %}Ils ne sont que
  <b>{{ rb.socle }}</b> à y être dans plus de 99 % des cas —
  {{ rb.socle_noms | join: " et " }}{% endif %} — et le moins solide du top
  actuel n’y tient que {{ rb.part_top_minimale_du_top }} % du temps.</p>
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
  produit surtout une liste de noms — {{ h.noms | join: ", " }} — que rien ne
  distingue, à la lecture, d’un vrai palmarès.</p>
  <p><b>Le classement réel tient l’épreuve</b> : son premier est à
  {{ h.reel_premier }}, et l’écart du premier au vingt-cinquième vaut
  {{ h.reel_ecart }} — <b>{{ h.reel_ecart | divided_by: h.ecart | round: 1 }} fois</b>
  celui du hasard. La hiérarchie n’est donc pas fabriquée de toutes pièces. Mais
  un top tiré au sort a de l’allure, et c’est ce qu’il fallait montrer.</p>
</div>

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
  <p>La corrélation observée vaut <b>{{ t.observe }}</b>, contre
  {{ t.attendu }} attendu du hasard : {{ t.ecart_types }} écarts-types,
  p = {{ t.p }} — et {{ t.p_ajustee }} après correction pour tests multiples.
  <b>Le test n’est pas retenu</b>, et il s’en faut de peu.</p>
  <p>Ce qu’il faut en dire, ni plus ni moins : <b>quelque chose se reproduit
  d’une saison à l’autre, mais on ne peut pas le distinguer du hasard sur
  {{ c.stabilite.effectif }} aventuriers</b>. Un joueur bon une fois l’est
  peut-être encore ; ces données ne permettent pas de l’affirmer.</p>
</div>

<p class="note"><strong>Deux réserves, en sens contraires.</strong> Ces
{{ c.stabilite.effectif }} aventuriers ne sont pas un échantillon : ce sont ceux
que la production a <em>rappelés</em>, donc les meilleurs de leur saison.
Comparer des gens déjà triés sur le talent écrase mécaniquement la corrélation —
le vrai lien est donc plus fort que {{ t.observe }}. En sens inverse, une
édition de revenants n’est pas une saison ordinaire : on y affronte des
adversaires bien plus forts, ce que le classement ne sait pas corriger, et cela
brouille la comparaison dans l’autre sens.</p>

<p class="note">Ce test est le seul déclaré ici, et il entre au
<a href="{{ '/methode/' | relative_url }}">registre corrigé</a> avec les
autres : un test qu’on tiendrait à l’écart de la liste serait un test gratuit.
Dans la première version de cette page, il valait 0,039 pour p = 0,73 — c’est le
même artefact du soir du départ qui l’écrasait.</p>

## Le score n’a jamais vu le palmarès — et il le retrouve

Le contrôle qui manquerait à n’importe quel autre top. Aucune des quatre
facettes ne sait qui a gagné. Où tombent les vainqueurs ?

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
<tr><td class="nombre">{{ l.rang }}</td><td>{% include lien-aventurier.html id=l.id nom=l.nom %}</td>
    <td class="nombre">{{ l.score }}</td>
    <td class="nombre">{{ l.part_top }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

## Les quatre classements par facette

Le top synthétique cache ce qu’il moyenne — et puisque les facettes ne se
parlent pas, ce sont ces quatre listes qui portent l’information. Chacune sur sa
mesure, avec le compte brut qui la fonde.

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
<tr><td class="nombre">{{ l.rang }}</td><td>{% include lien-aventurier.html id=l.id nom=l.nom %}</td>
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
participation, sur ses seules quatre facettes, sans rien cumuler.

<div class="tableau-large">
<table data-triable>
<thead><tr><th class="nombre">#</th><th>Aventurier</th><th>Saison</th><th class="nombre">Année</th><th>Fin de parcours</th><th class="nombre">Score</th></tr></thead>
<tbody>
{% for l in c.top_saisons %}
<tr><td class="nombre">{{ l.rang }}</td><td>{% include lien-aventurier.html id=l.id nom=l.aventurier %}</td>
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
<tr><td class="nombre">{{ l.rang }}</td><td>{% include lien-aventurier.html id=l.id nom=l.nom %}</td>
    <td class="nombre">{{ l.score }}</td>
    <td class="nombre">{{ l.rang_general }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

## Le classement complet, nom par nom

Les {{ c.joueurs_classes }} aventuriers, cherchables et triables. Les quatre
colonnes de droite donnent le rang **sur chaque facette** : c’est là que se voit
le mieux qu’un bon rang général peut cacher une facette au fond du tableau, et
l’inverse.

<div class="filtres" data-filtre="tableau-classement">
  <div class="champ">
    <label for="qc">Chercher un aventurier</label>
    <input type="search" id="qc" data-role="texte" placeholder="Claude Dartois, Jade Handi, Moundir…" autocomplete="off">
  </div>
  <button type="button" class="bascule" data-role="vider">Tout effacer</button>
  <p class="compte" data-role="compte" aria-live="polite"></p>
</div>

<div class="tableau-large tableau-haut">
<table id="tableau-classement" data-triable>
<thead><tr>
  <th class="nombre">Rang</th><th>Aventurier</th>
  <th class="nombre">Saisons</th><th class="nombre">Titres</th>
  <th class="nombre">Score</th>
  <th class="nombre">Dans le top {{ c.taille }}</th>
  <th class="nombre">Rang, 5<sup>e</sup>–95<sup>e</sup></th>
  {% for f in c.facettes %}<th class="nombre">{{ f.libelle | remove: "Le " | remove: "La " | remove: "Les " }}</th>{% endfor %}
</tr></thead>
<tbody>
{% for l in c.tous %}
<tr>
  <td class="nombre">{{ l.rang }}</td>
  <td>{% include lien-aventurier.html id=l.id nom=l.nom %}</td>
  <td class="nombre">{{ l.saisons }}</td>
  <td class="nombre">{{ l.titres }}</td>
  <td class="nombre">{{ l.score }}</td>
  <td class="nombre">{{ l.part_top }} %</td>
  <td class="nombre" data-val="{{ l.rang_p95 | minus: l.rang_p05 }}">{{ l.rang_p05 }} – {{ l.rang_p95 }}</td>
  {% for f in c.facettes %}<td class="nombre">{{ l.rangs[f.cle] }}</td>{% endfor %}
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Un rang n’est pas une note. La colonne « dans le top » dit sous
quelle part des {{ rb.tirages }} pondérations l’aventurier y figure, et
l’avant-dernière l’étendue de ses rangs : quand elle est large, le rang de
gauche ne veut pas dire grand-chose. Et pour les
{{ c.joueurs_classes | minus: c.carrieres.size }} aventuriers d’une ou deux
saisons, la preuve reste mince — le rétrécissement les tient près de la
moyenne, ce qui est la seule chose honnête à faire quand on ne sait pas.</p>

## Le biais que ce classement ne sait pas réparer

{% assign be = c.biais_epoque %}

Deux facettes sur quatre — la discrétion, la lecture — se lisent sur les
bulletins, et **le dépouillement des conseils s’effondre à l’époque récente**.
Les joueurs des dernières saisons sont donc, sur ces deux facettes, ramenés à la
moyenne faute d’observations. Ce n’est pas une opinion sur leur niveau, c’est
un trou dans la source.

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
classement. <strong>Les facettes ne se parlent pas</strong> : la moyenne des
quatre est une convention, pas une grandeur.
<strong>Les poids sont arbitraires</strong> : {{ rb.socle }} joueur seulement
tient dans plus de 99 % des pondérations, quand {{ rb.candidats }} peuvent
entrer dans le top.
<strong>La stabilité n’est pas établie</strong> — p = {{ t.p }}, à la limite.
<strong>Deux facettes sur quatre dépendent d’un dépouillement inégal</strong>, et
la troisième — les épreuves — ignore {{ ce.victoires_invisibles }} victoires
faute de dénominateur.
<strong>La discrétion reste ambivalente</strong> : n’être jamais écrit peut
aussi vouloir dire qu’on ne menaçait personne — c’est ce que
<a href="{{ '/statistiques/jeu-social/' | relative_url }}">le jeu social</a>
montre en ne la classant que deuxième.
<strong>Et deux dimensions entières manquent</strong> : les colliers d’immunité,
relevés sur {{ site.data.stats.colliers.saisons_couvertes }} saisons seulement,
et les objets qui les ont remplacés — armes secrètes, totem maudit, talisman —
dont <a href="{{ '/sources/' | relative_url }}">les sources</a> ne donnent pas
le détail.</p>

Pour aller voir les mesures une par une :
[le jeu social]({{ '/statistiques/jeu-social/' | relative_url }}),
[les épreuves]({{ '/statistiques/epreuves/' | relative_url }}),
[les colliers]({{ '/statistiques/colliers/' | relative_url }}),
[la force réelle]({{ '/statistiques/force/' | relative_url }}) et
[les revenants]({{ '/statistiques/revenants/' | relative_url }}).

Et pour la donnée brute, participation par participation —
âge, métier, tribu, jour de sortie —
[les aventuriers]({{ '/aventuriers/' | relative_url }}).
