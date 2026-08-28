---
layout: page
title: Le vote du jury
permalink: /statistiques/jury/
chapeau: >-
  Le seul scrutin où écrire un nom veut dire « qu’il gagne » — et le seul rendu
  par des gens qu’on a fait sortir. Pardonnent-ils ?
---

{% assign m = site.data.stats.modeles %}
{% assign j = m.jury_final %}

Deux réponses circulent depuis vingt-cinq ans, et elles se contredisent : on
respecte celui qui a osé vous éliminer, ou on ne lui pardonne jamais. Aucune des
deux n’avait jamais été mesurée — les bulletins de jury n’étaient pas
exploitables avant la [réparation d’extraction]({{ '/sources/' | relative_url }})
qui a fait passer les éliminations rattachées de 203 à 578.

Ils le sont maintenant : **{{ j.bulletins }} bulletins de jury** sur
{{ j.saisons }} saisons.

## Le chiffre brut, et pourquoi il ment

<div class="constat">
  <p><b>{{ j.part_vers_bourreau }} %</b> des bulletins de jury vont à un
  finaliste qui avait écrit le nom du juré au conseil. Quand un tel finaliste
  figure parmi les candidats, c’est même
  <b>{{ j.part_quand_disponible }} %</b> — sur
  {{ j.bulletins_avec_bourreau_disponible }} bulletins.</p>
  <p>Trois jurés sur quatre couronnent donc celui qui les a sortis. On tient
  la démonstration : le jury récompense l’audace.</p>
</div>

Sauf que non. Un finaliste a traversé toute la saison, il a voté à chaque
conseil, il a donc écrit beaucoup de noms — dont probablement le vôtre. La
question n’est pas « le juré vote-t-il pour son bourreau », elle est **« le juré
vote-t-il pour son bourreau plus souvent que pour l’autre finaliste »**.

## Le modèle

<p class="note">Un juré choisit parmi les finalistes de sa saison : c’est un
choix contraint, qui se modélise par un <strong>logit conditionnel</strong>.
Chaque juré forme son propre groupe de comparaison, ce qui absorbe d’un coup la
saison, l’année, son propre caractère et tout ce qui lui est particulier. Il ne
reste que ce qui distingue les finalistes <em>entre eux, aux yeux de ce
juré-là</em>.</p>

{% include graphiques/jury-coefficients.svg %}

<p class="legende-figure">Rapports de cotes. Au-dessus de 1, le juré vote plus
souvent pour ce finaliste ; un intervalle qui traverse 1 signifie qu’on ne peut
pas conclure.</p>

{% assign c0 = j.coefficients[0] %}{% assign c1 = j.coefficients[1] %}

<div class="constat">
  <p><b>Avoir éliminé le juré ne change rien.</b> Cote
  ×{{ c0.rapport }}, intervalle {{ c0.bas }} à {{ c0.haut }}, p =
  {{ c0.p }}. Ni rancune, ni respect : les {{ j.part_quand_disponible }} % du
  chiffre brut s’expliquent entièrement par le fait qu’un finaliste écrit
  beaucoup de noms.</p>
  <p><b>Avoir voté avec le juré, en revanche, compte.</b> Chaque conseil passé
  du même côté multiplie la cote par <b>{{ c1.rapport }}</b>
  ({{ c1.bas }} à {{ c1.haut }}, p = {{ c1.p }}). Sur cinq conseils partagés,
  cela double les chances.</p>
</div>

Le jury final ne juge donc ni le parcours ni l’affront : **il prolonge
l’alliance**. Ce que le juré récompense, c’est celui avec qui il écrivait les
mêmes noms — la même variable qui, en cours de jeu, fait tenir plus longtemps
que tout le reste.
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}).

<p class="note">Les limites, et elles sont réelles. {{ j.bulletins }} bulletins,
c’est peu : l’intervalle sur l’effet « m’a éliminé » va de {{ c0.bas }} à
{{ c0.haut }}, et une rancune modérée y tiendrait sans être détectée. On ne peut
donc pas conclure qu’il n’y a <em>aucun</em> effet, seulement qu’il n’y en a pas
de grand. Par ailleurs le modèle ne connaît du parcours d’un finaliste que ses
bulletins : ni ses épreuves gagnées, ni son plaidoyer final, ni ce que le jury a
vu de lui à l’écran. Ce sont peut-être ces choses-là qui décident, et elles ne
sont nulle part dans ces données.</p>
