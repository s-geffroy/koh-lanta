---
layout: page
title: "Le vote du jury final"
titre: Le vote du jury
description: "Le vote du jury final de Koh-Lanta, rendu par ceux qu’on a fait sortir : il ne punit pas de façon établie, il récompense celui avec qui l’on votait."
permalink: /statistiques/jury/
chapeau: >-
  Le seul scrutin où écrire un nom veut dire « qu’il gagne » — et le seul rendu
  par des gens qu’on a fait sortir. Punissent-ils ? On ne peut pas l’affirmer.
  Ils récompensent, en revanche, celui avec qui ils votaient.
---

{% assign m = site.data.stats.modeles %}
{% assign j = m.jury_final %}

Deux réponses circulent depuis vingt-cinq ans, et elles se contredisent : on
respecte celui qui a osé vous éliminer, ou on ne lui pardonne jamais. Aucune des
deux n’avait jamais été mesurée — les bulletins de jury n’étaient pas
exploitables avant la [réparation d’extraction]({{ '/sources/' | relative_url }})
qui a fait passer les éliminations rattachées de 203 à 578.

Une seconde réparation a suivi, et elle touche cette page plus que toute autre.
Le scrutin final tient **une ligne par finaliste** dans les tableaux sources :
celle du gagnant, et celle du battu. L’extraction ne reconnaissait que la
première — la seconde était rangée du côté des éliminations, où ses bulletins
comptaient à l’envers. L’échantillon ne contenait donc, à un bulletin près, que
des jurés ayant voté **pour le futur vainqueur**. Les voix de l’autre côté du
choix sont revenues ; les chiffres de cette page ont bougé, et l’une de ses
conclusions avec.

Ils le sont maintenant : **{{ j.bulletins }} bulletins de jury** sur
{{ j.saisons }} saisons.

## Le chiffre brut, et pourquoi il ment

<div class="constat">
  <p><b>{{ j.part_vers_bourreau }} %</b> des bulletins de jury vont à un
  finaliste qui avait écrit le nom du juré au conseil. Quand un tel finaliste
  figure parmi les candidats, c’est même
  <b>{{ j.part_quand_disponible }} %</b> — sur
  {{ j.bulletins_avec_bourreau_disponible }} bulletins.</p>
  <p>Ces jurés-là couronnent donc, le plus souvent, celui qui les a sortis. On
  tient la démonstration : le jury récompense l’audace.</p>
</div>

Sauf que non. Un finaliste a traversé toute la
saison, il a voté à chaque conseil, il a donc écrit beaucoup de noms — dont
probablement le vôtre. La question n’est pas « le juré vote-t-il pour son
bourreau », elle est **« le juré vote-t-il pour son bourreau plus souvent que
pour l’autre finaliste »**. Posée ainsi, elle ne donne plus la démonstration.

## Le modèle

<p class="note">Un juré choisit parmi les finalistes de sa saison : c’est un
choix contraint, qui se modélise par un <strong>logit conditionnel</strong>.
Chaque juré forme son propre groupe de comparaison, ce qui absorbe d’un coup la
saison, l’année, son propre caractère et tout ce qui lui est particulier. Il ne
reste que ce qui distingue les finalistes <em>entre eux, aux yeux de ce
juré-là</em>. Les jurés d’une même saison jugent les mêmes finalistes : leurs
bulletins ne sont pas indépendants, et l’incertitude vient donc d’un tirage des
saisons, non des bulletins.</p>

{% include graphiques/jury-coefficients.svg %}

<p class="legende-figure">Rapports de cotes. Au-dessus de 1, le juré vote plus
souvent pour ce finaliste ; un intervalle qui traverse 1 signifie qu’on ne peut
pas conclure.</p>

{% assign c0 = j.coefficients[0] %}{% assign c1 = j.coefficients[1] %}

<div class="constat">
  <p><b>Avoir écrit le nom du juré : rien d’établi.</b> Cote ×{{ c0.rapport }},
  intervalle {{ c0.bas }} à {{ c0.haut }}, p ajustée {{ c0.p_ajustee }} —
  l’intervalle <b>contient 1</b>. L’estimation va dans le sens d’une rancune,
  mais on ne peut pas l’affirmer.</p>
  <p><b>Avoir voté avec le juré rapporte.</b> Chaque conseil passé du même côté
  multiplie la cote par <b>{{ c1.rapport }}</b> ({{ c1.bas }} à {{ c1.haut }},
  p ajustée {{ c1.p_ajustee }}). Sur cinq conseils partagés, la cote est
  multipliée par {{ c1.cinq_conseils }}.</p>
</div>

Le jury final récompense donc d’abord **une alliance** : il couronne celui
avec qui le juré écrivait les mêmes noms — la même variable qui, en cours de
jeu, fait tenir plus longtemps que tout le reste. Qu’il fasse payer celui qui a
écrit le sien, les bulletins le suggèrent sans le prouver.

<p class="note"><strong>Cette page disait le contraire, et il faut dire
pourquoi.</strong> Elle concluait « ni rancune, ni respect » sur 196 bulletins
dont <b>195 allaient au lauréat</b> : le scrutin final tient une ligne par
finaliste, et celle du battu n’était pas extraite. Un échantillon composé
presque uniquement de jurés ayant voté pour le vainqueur ne pouvait, sur cette
variable-là, que ne rien trouver — le bourreau y est presque toujours celui qui
gagne. Les colonnes manquantes ont été récupérées, puis le dernier bulletin
absent avec elles : <b>le scrutin final est aujourd’hui complet</b>, chaque voix
annoncée par les sources étant lue et attribuée. {{ j.bulletins }} bulletins sur
{{ j.saisons }} saisons, et la rancune est apparue. Elle a de nouveau disparu
le 22 octobre 2026, quand l’incertitude a été calculée par saison plutôt que
par bulletin, et corrigée pour le nombre de coefficients publiés : la page
écrivait alors « le jury n’oublie pas ». Elle ne l’écrit plus.
<a href="{{ '/sources/' | relative_url }}">Les sources</a> racontent la
réparation.</p>

### La mise à l’épreuve : et si ce n’était que la tribu initiale ?

{% assign ab = j.avec_bandeau %}

La tribu initiale gouverne le bulletin **en cours de jeu** mieux que tout le
reste — c’est le résultat le plus net de
[Qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}). Or deux
personnes de la même tribu initiale votent souvent ensemble. L’effet du co-vote pourrait
donc n’être que le reflet de la tribu initiale. Le même modèle, avec cette variable de
plus :

<div class="tableau-large">
<table><caption class="hors-ecran">La mise à l’épreuve : et si ce n’était que la tribu initiale ?</caption>
<thead><tr><th>Variable</th><th class="nombre">Cote multipliée par</th><th class="nombre">Intervalle</th><th class="nombre">p</th></tr></thead>
<tbody>
{% for x in ab.coefficients %}
<tr><td>{{ x.libelle }}</td>
    <td class="nombre"><b>{{ x.rapport }}</b></td>
    <td class="nombre">{{ x.bas }} – {{ x.haut }}</td>
    <td class="nombre">{{ x.p }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p><b>La tribu initiale, ici, ne pèse rien de mesurable</b> : cote ×{{ ab.coefficients[2].rapport }},
  intervalle {{ ab.coefficients[2].bas }} à {{ ab.coefficients[2].haut }},
  p = {{ ab.coefficients[2].p }}. Ce qui gouverne le conseil ne gouverne pas le
  jury — et c’est en soi un résultat, vu la force de l’effet en cours de jeu.</p>
  <p><b>Et l’effet du co-vote survit au contrôle.</b> L’estimation ne bouge
  pas ({{ c1.rapport }} devient {{ ab.coefficients[1].rapport }}), l’intervalle
  s’élargit sans atteindre 1 : {{ ab.coefficients[1].bas }} à
  {{ ab.coefficients[1].haut }}, p = {{ ab.coefficients[1].p }}. Ce n’est donc
  pas la tribu initiale déguisée : c’est bien avec qui l’on a voté, conseil après
  conseil, que le juré récompense.</p>
</div>

<p class="note">Le contraste vaut d’être noté : la tribu initiale tombe à
{{ ab.coefficients[2].rapport }}, c’est-à-dire rien, tandis que le co-vote
tient sans bouger. Ce qui décide au conseil — d’où l’on
vient — cesse d’exister au jury ; ce qui décide au jury, c’est ce qu’on s’est
fait l’un à l’autre.</p>

<p class="note">Les limites, et elles sont réelles. {{ j.bulletins }} bulletins
restent peu : l’intervalle sur l’effet « m’a éliminé » va de {{ c0.bas }} à
{{ c0.haut }}{% if c0.retenu %} — l’effet passe la correction, mais son ampleur
ne se lit qu’approximativement{% else %} et contient 1 : la rancune n’est pas
établie{% endif %}. Ces coefficients sont corrigés avec tous les autres résultats
publiés (<a href="{{ '/methode/' | relative_url }}">la méthode</a>). Les
bulletins de <em>La Légende</em>, invalidés avec le vote du jury final, n’y
entrent pas. Enfin le modèle ne connaît du parcours d’un finaliste que
ses bulletins : ni ses épreuves gagnées, ni son plaidoyer final, ni ce que le
jury a vu de lui à l’écran. Ce sont peut-être ces choses-là qui décident, et
elles ne sont nulle part dans ces données.</p>
