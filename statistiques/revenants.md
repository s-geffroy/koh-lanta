---
layout: page
title: Les revenants
permalink: /statistiques/revenants/
chapeau: >-
  Rejouer Koh-Lanta, est-ce un avantage ? Le chiffre qui saute aux yeux dit
  oui. Il dit surtout autre chose.
---

{% assign r = site.data.stats.revenants %}
{% assign g = site.data.stats.general %}

{{ g.participations }} participations pour {{ g.personnes }} personnes : la
différence tient à ceux qui sont revenus. Ils ont déjà vu l’île, ils savent
faire un feu, ils connaissent le rythme des conseils. On s’attend donc à ce
qu’ils fassent mieux — et à première vue, c’est le cas.

## Le paradoxe

{% include graphiques/revenants-paradoxe.svg %}

<p class="legende-figure">Part moyenne de la saison passée en jeu. Les
revenants sont comptés deux fois : une fois pour leur première aventure, une
fois pour chacun de leurs retours.</p>

Comparés en bloc, les revenants tiennent plus longtemps que les autres. La
conclusion facile serait : **l’expérience paie**. Mais séparons leur première
aventure de leurs retours.

<div class="constat">
  <p>Les revenants tenaient déjà <b>{{ r.paradoxe[1].survie_moyenne }} %</b> de
  la saison lors de leur <b>première</b> participation, contre
  {{ r.paradoxe[0].survie_moyenne }} % pour ceux qui n’ont jamais été rappelés.
  Ils étaient donc <b>déjà exceptionnels avant de revenir</b>.</p>
  <p>Et lorsqu’ils reviennent, ils tombent à
  <b>{{ r.paradoxe[2].survie_moyenne }} %</b> : <b>moins bien qu’à leur premier
  passage</b>.</p>
  <p>Ce n’est donc pas l’expérience qui explique l’écart, c’est le casting. La
  production rappelle ceux qui sont allés loin ; l’écart était acquis avant que
  le retour ne commence.</p>
</div>

C’est un **biais de sélection**, et c’est la raison pour laquelle une moyenne
comparée à une autre moyenne ne suffit presque jamais. Le groupe des revenants
n’est pas un échantillon des aventuriers : c’est le haut du panier, choisi
exprès.

<p class="note">Ce que ces chiffres ne disent pas : pourquoi le retour se passe
moins bien. Deux explications tiennent également debout et ces données ne
permettent pas de trancher entre elles. Les revenants sont des cibles connues,
et l’on vote contre ceux qu’on redoute ; mais les éditions spéciales
rassemblent aussi des joueurs tous très forts, où la moitié doit forcément
sortir tôt.</p>

## Qui la production redemande

{% assign rp = site.data.stats.modeles.rappel %}

Avant de se demander si revenir paie, il faut se demander **qui est
rappelé** — et là, ce n’est plus le jeu qui décide, c’est la production. Sur
les **{{ rp.effectif }} premières participations** assez anciennes pour qu’un
retour ait eu le temps de se produire (avant {{ rp.annee_limite }}),
**{{ rp.rappeles }} ont été suivies d’une autre édition** :
{{ rp.part }} %.

{% include graphiques/rappel-sort.svg %}

<p class="legende-figure">Part des aventuriers rappelés dans une édition
ultérieure, selon la façon dont leur première aventure s’est terminée.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Fin de la première aventure</th><th class="nombre">Aventuriers</th><th class="nombre">Rappelés</th><th class="nombre">Probabilité</th><th class="nombre">Intervalle</th></tr></thead>
<tbody>
{% for x in rp.par_sort %}
<tr>
  <td>{{ x.modalite }}</td>
  <td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.cas }}</td>
  <td class="nombre" data-val="{{ x.probabilite }}"><b>{{ x.probabilite }} %</b></td>
  <td class="nombre">{{ x.bas }} – {{ x.haut }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

{% assign fin = rp.par_sort | first %}
{% assign dernier = rp.par_sort | last %}
La gradation est sans trou : **{{ fin.probabilite }} %** en haut du tableau,
**{{ dernier.probabilite }} %** en bas. Entre les deux, chaque façon de sortir a
sa probabilité d’être redemandé, et elles se rangent exactement dans l’ordre où
l’on s’attendrait à les trouver.

### La durée explique presque tout

{% include graphiques/rappel-survie.svg %}

<p class="legende-figure">Part des aventuriers rappelés selon le cinquième de
longévité auquel ils appartiennent.</p>

Le cinquième qui va le plus loin est rappelé
**{{ rp.par_survie[4].probabilite }} %** du temps, contre
**{{ rp.par_survie[0].probabilite }} %** pour celui qui sort le plus tôt : plus
de vingt fois moins. Le tableau des sorts, ci-dessus, ne dit peut-être rien de
plus que cela — un éliminé aux poteaux est allé loin par définition.

### Ce qui reste quand la durée est tenue fixe

{% include graphiques/rappel-modele.svg %}

<p class="legende-figure">Rapports de cotes d’une régression logistique sur les
{{ rp.effectif }} premières participations. Au-dessus de 1 : rappelé plus
souvent, toutes les autres variables tenues fixes.</p>

<div class="tableau-large">
<table>
<thead><tr><th>Variable</th><th class="nombre">Cote multipliée par</th><th class="nombre">Intervalle</th><th class="nombre">p</th></tr></thead>
<tbody>
{% for x in rp.coefficients %}
<tr><td>{{ x.libelle }}</td>
    <td class="nombre"><b>{{ x.rapport }}</b></td>
    <td class="nombre">{{ x.bas }} – {{ x.haut }}</td>
    <td class="nombre">{{ x.p }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p><b>La longévité domine</b> : dix points de saison tenus en plus multiplient
  la cote d’être rappelé par {{ rp.coefficients[0].rapport }}.</p>
  <p><b>L’âge compte, et il compte contre.</b> Dix ans de plus au casting
  divisent la cote par {{ 1.0 | divided_by: rp.coefficients[3].rapport | round: 2 }},
  à longévité, sexe et époque égaux — intervalle
  {{ rp.coefficients[3].bas }} à {{ rp.coefficients[3].haut }},
  p {{ rp.coefficients[3].p }}. La production rappelle plutôt les jeunes, et ce
  n’est pas parce qu’ils vont plus loin : c’est justement ce que le modèle tient
  fixe. [Âge et longévité]({{ '/statistiques/longevite/' | relative_url }}) montre
  d’ailleurs que ce sont les 30-34 ans qui durent le plus.</p>
  <p><b>Le sexe, non</b> : cote multipliée par {{ rp.coefficients[2].rapport }},
  intervalle {{ rp.coefficients[2].bas }} à {{ rp.coefficients[2].haut }}. Le
  rappel est aussi paritaire que le casting — et
  [la recette du casting]({{ '/statistiques/casting/' | relative_url }}) montre
  que cette parité-là est un quota.</p>
  <p><b>L’abandon coûte cher, sans qu’on puisse le chiffrer.</b> Cote multipliée
  par {{ rp.coefficients[1].rapport }} — divisée par cinq, donc — mais
  l’intervalle ({{ rp.coefficients[1].bas }} à {{ rp.coefficients[1].haut }})
  contient 1. Le tableau des sorts dit pourquoi : les deux dernières lignes
  réunissent quelques dizaines d’abandons et <b>un seul</b> retour. On voit la
  direction, pas l’ampleur.</p>
</div>

<p class="note"><strong>Ce que ce modèle ne peut pas voir.</strong> Il ne
connaît ni le temps d’antenne, ni le personnage que le montage a construit, ni
qui a refusé de revenir. Un aventurier peut n’avoir jamais été rappelé, ou avoir
dit non : ces données ne distinguent pas les deux, et l’écart mesuré mêle le
choix de la production et celui du candidat.</p>

## Le petit monde des revenants

{% include graphiques/revenants-graphe.svg %}

<p class="legende-figure">Chaque point est un aventurier revenu au moins deux
fois, rangé par ordre d’arrivée dans le programme ; sa taille dit combien
d’autres revenants il a croisés. Un arc relie deux personnes ayant partagé une
saison.</p>

Les {{ r.graphe.noeuds | size }} revenants forment un réseau serré :
{{ r.graphe.aretes | size }} liens entre eux, alors qu’un groupe de cette taille
pourrait en compter bien davantage sans jamais se recroiser. Les éditions
spéciales agissent comme des carrefours — elles rassemblent d’un coup une
vingtaine de personnes qui se connaissent déjà.

### Le plus connecté n’est pas le plus titré

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Aventurier</th><th class="nombre">Saisons</th>
  <th class="nombre">Aventuriers croisés</th>
</tr></thead>
<tbody>
{% for c in r.les_plus_connectes %}
<tr>
  <td>{{ c.nom }}</td>
  <td class="nombre">{{ c.saisons }}</td>
  <td class="nombre">{{ c.liens }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

**{{ r.les_plus_connectes[0].nom }}** a partagé une aventure avec
{{ r.les_plus_connectes[0].liens }} personnes différentes — plus que
{{ r.carrieres[0].nom }}, qui a pourtant joué plus longtemps. Le nombre de
saisons ne suffit pas : ce qui compte est la **taille** des castings qu’on a
traversés.

## Les plus longues carrières

{% include graphiques/revenants-carrieres.svg %}

<p class="legende-figure">Jours de jeu cumulés sur toutes les participations.
En vert, ceux qui n’ont jamais été éliminés une seule fois.</p>

{% assign sf = r.sans_faute %}
**{{ sf | size }} aventuriers n’ont jamais quitté le jeu avant la fin**, sur
l’ensemble de leurs participations :
{% for c in sf %}{{ c.nom }} ({{ c.saisons }} saisons, {{ c.jours }} jours){% unless forloop.last %}, {% endunless %}{% endfor %}.
Aucun conseil, aucun poteau, aucune orientation ne les a fait sortir.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Aventurier</th><th class="nombre">Saisons</th><th class="nombre">Jours joués</th>
  <th class="nombre">Jours possibles</th><th class="nombre">Part du temps</th>
</tr></thead>
<tbody>
{% for c in r.carrieres %}
<tr>
  <td>{{ c.nom }}</td>
  <td class="nombre">{{ c.saisons }}</td>
  <td class="nombre">{{ c.jours }}</td>
  <td class="nombre">{{ c.jours_possibles }}</td>
  <td class="nombre" data-val="{{ c.part_du_temps }}">{{ c.part_du_temps }} %
    <span class="cellule-barre" style="width: {{ c.part_du_temps }}%"></span></td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Les duos qui n’en finissent pas

{% include graphiques/revenants-duos.svg %}

<p class="legende-figure">Nombre de saisons partagées par les mêmes deux
personnes.</p>

**{{ r.nb_duos_recurrents }} duos** se sont retrouvés sur au moins deux saisons.
En tête, **{{ r.duos[0].a }} et {{ r.duos[0].b }}**, qui ont joué
{{ r.duos[0].saisons }} fois ensemble.

<p class="note">Le biais se retrouve tel quel dans un modèle multivarié : à
âge, sexe, métier et saison identiques, un aventurier déjà venu est éliminé
trois fois moins vite, et c’est le plus gros coefficient du modèle
(<a href="{{ '/statistiques/equilibre/' | relative_url }}">Le jeu tenu serré</a>).
Aucun contrôle statistique ne répare une sélection faite sur la variable même
qu’on étudie.</p>
