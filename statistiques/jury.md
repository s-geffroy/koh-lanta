---
layout: page
title: Le vote du jury
description: "Le vote du jury final de Koh-Lanta : le seul scrutin rendu par ceux qu’on a fait sortir. Pardonnent-ils à celui qui les a éliminés ? Non."
permalink: /statistiques/jury/
chapeau: >-
  Le seul scrutin où écrire un nom veut dire « qu’il gagne » — et le seul rendu
  par des gens qu’on a fait sortir. Pardonnent-ils ? Non.
---

{% assign m = site.data.stats.modeles %}
{% assign j = m.jury_final %}

Deux réponses circulent depuis vingt-cinq ans, et elles se contredisent : on
respecte celui qui a osé vous éliminer, ou on ne lui pardonne jamais. Aucune des
deux n’avait jamais été mesurée — les bulletins de jury n’étaient pas
exploitables avant la [réparation d’extraction]({{ '/sources/' | relative_url }})
qui a fait passer les éliminations rattachées de 203 à 578.

Une seconde réparation a suivi, et elle touche cette page plus que toute autre.
Le scrutin final tient **une ligne par finaliste** dans les tableaux sources :
celle du gagnant, et celle du battu. L’extraction ne reconnaissait que la
première — la seconde était rangée du côté des éliminations, où ses bulletins
comptaient à l’envers. L’échantillon ne contenait donc, à un bulletin près, que
des jurés ayant voté **pour le futur vainqueur**. Les voix de l’autre côté du
choix sont revenues ; les chiffres de cette page ont bougé, et l’une de ses
conclusions avec.

Ils le sont maintenant : **{{ j.bulletins }} bulletins de jury** sur
{{ j.saisons }} saisons.

## Le chiffre brut, et pourquoi il ment

<div class="constat">
  <p><b>{{ j.part_vers_bourreau }} %</b> des bulletins de jury vont à un
  finaliste qui avait écrit le nom du juré au conseil. Quand un tel finaliste
  figure parmi les candidats, c’est même
  <b>{{ j.part_quand_disponible }} %</b> — sur
  {{ j.bulletins_avec_bourreau_disponible }} bulletins.</p>
  <p>Près de deux jurés sur trois couronnent donc celui qui les a sortis. On
  tient la démonstration : le jury récompense l’audace.</p>
</div>

Sauf que non — et le retournement est complet. Un finaliste a traversé toute la
saison, il a voté à chaque conseil, il a donc écrit beaucoup de noms — dont
probablement le vôtre. La question n’est pas « le juré vote-t-il pour son
bourreau », elle est **« le juré vote-t-il pour son bourreau plus souvent que
pour l’autre finaliste »**. Posée ainsi, elle donne l’inverse.

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
  <p><b>Avoir éliminé le juré coûte.</b> Cote ×{{ c0.rapport }}, intervalle
  {{ c0.bas }} à {{ c0.haut }}, p = {{ c0.p }} — l’intervalle <b>ne contient pas
  1</b>. À conseils partagés égaux, le finaliste qui a écrit le nom d’un juré
  voit sa cote d’obtenir sa voix <b>presque divisée par deux</b>. Le jury
  n’oublie pas.</p>
  <p><b>Avoir voté avec le juré rapporte davantage encore.</b> Chaque conseil
  passé du même côté multiplie la cote par <b>{{ c1.rapport }}</b>
  ({{ c1.bas }} à {{ c1.haut }}, p = {{ c1.p }}). Sur cinq conseils partagés,
  cela fait plus que doubler les chances.</p>
</div>

Le jury final ne juge donc ni le parcours ni le mérite : **il solde les
comptes**. Il couronne celui avec qui le juré écrivait les mêmes noms — la même
variable qui, en cours de jeu, fait tenir plus longtemps que tout le reste — et
il fait payer celui qui a écrit le sien.

<p class="note"><strong>Cette page disait le contraire, et il faut dire
pourquoi.</strong> Elle concluait « ni rancune, ni respect » sur 196 bulletins
dont <b>195 allaient au lauréat</b> : le scrutin final tient une colonne par
finaliste, et celle du battu n’était pas extraite. Un échantillon composé
presque uniquement de jurés ayant voté pour le vainqueur ne pouvait, sur cette
variable-là, que ne rien trouver — le bourreau y est presque toujours celui qui
gagne. Les colonnes manquantes ont été récupérées, puis le dernier bulletin
absent avec elles : <b>le scrutin final est aujourd’hui complet</b>, chaque voix
annoncée par les sources étant lue et attribuée. {{ j.bulletins }} bulletins sur
{{ j.saisons }} saisons, et l’effet apparaît. Il n’a pas changé de valeur, il
est devenu <em>observable</em>.
<a href="{{ '/sources/' | relative_url }}">Les sources</a> racontent la
réparation.</p>
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}).

### La mise à l’épreuve : et si ce n’était que le bandeau ?

{% assign ab = j.avec_bandeau %}

Le camp d’origine gouverne le bulletin **en cours de jeu** mieux que tout le
reste — c’est le résultat le plus net de
[Qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}). Or deux
personnes du même bandeau votent souvent ensemble. L’effet du co-vote pourrait
donc n’être que le reflet du bandeau. Le même modèle, avec cette variable de
plus :

<div class="tableau-large">
<table>
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
  <p><b>Le bandeau, ici, ne fait rigoureusement rien</b> : cote ×{{ ab.coefficients[2].rapport }},
  intervalle {{ ab.coefficients[2].bas }} à {{ ab.coefficients[2].haut }},
  p = {{ ab.coefficients[2].p }}. Ce qui gouverne le conseil ne gouverne pas le
  jury — et c’est en soi un résultat, vu la force de l’effet en cours de jeu.</p>
  <p><b>Et l’effet du co-vote survit au contrôle.</b> L’estimation ne bouge
  pas ({{ c1.rapport }} devient {{ ab.coefficients[1].rapport }}), l’intervalle
  s’élargit sans atteindre 1 : {{ ab.coefficients[1].bas }} à
  {{ ab.coefficients[1].haut }}, p = {{ ab.coefficients[1].p }}. Ce n’est donc
  pas le bandeau déguisé : c’est bien avec qui l’on a voté, conseil après
  conseil, que le juré récompense.</p>
</div>

<p class="note">Le contraste vaut d’être noté : le bandeau tombe à
{{ ab.coefficients[2].rapport }}, c’est-à-dire exactement rien, tandis que les
deux autres variables tiennent sans bouger. Ce qui décide au conseil — d’où l’on
vient — cesse d’exister au jury ; ce qui décide au jury, c’est ce qu’on s’est
fait l’un à l’autre.</p>

<p class="note">Les limites, et elles sont réelles. {{ j.bulletins }} bulletins
restent peu : l’intervalle sur l’effet « m’a éliminé » va de {{ c0.bas }} à
{{ c0.haut }} — la rancune est établie, son ampleur ne l’est
qu’approximativement. Aucun de ces deux tests n’est déclaré au
registre corrigé de <a href="{{ '/methode/' | relative_url }}">la méthode</a> :
ce sont les coefficients d’un modèle, publiés avec leur intervalle, et il faut
les lire comme tels. Enfin le modèle ne connaît du parcours d’un finaliste que
ses bulletins : ni ses épreuves gagnées, ni son plaidoyer final, ni ce que le
jury a vu de lui à l’écran. Ce sont peut-être ces choses-là qui décident, et
elles ne sont nulle part dans ces données.</p>
