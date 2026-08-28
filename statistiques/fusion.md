---
layout: page
title: Avant et après la fusion
permalink: /statistiques/fusion/
chapeau: >-
  La réunification coupe la saison en deux jeux. On dit qu’avant on élimine le
  faible et qu’après on élimine le fort. C’est l’inverse.
---

{% assign m = site.data.stats.modeles %}
{% assign a = m.avant_apres %}
{% assign reg = m.registre %}
{% assign tf = reg | where: "cle", "fusion_force" | first %}
{% assign ts = reg | where: "cle", "fusion_serre" | first %}
{% assign tx = reg | where: "cle", "fusion_sexe" | first %}
{% assign ta = reg | where: "cle", "ambassadeurs_force" | first %}

Jusqu’à la réunification, on vote **par tribu** : le camp doit gagner les
épreuves collectives, et perdre un bon joueur coûte cher. Après, chacun joue
pour soi et un bon joueur devient une menace. Le raisonnement est si naturel
qu’il est répété partout : **avant on élimine le faible, après on élimine le
fort.**

Il est faux, et c’est mesurable.

<p class="note"><strong>Où tombe la coupure.</strong> Elle ne se devine pas :
après la réunification, les immunités sont individuelles. Le dernier épisode
portant une immunité <em>collective</em> est donc le dernier d’avant la fusion.
Le repère fonctionne sur {{ a.saisons }} saisons classiques, et
<a href="{{ '/statistiques/grille/' | relative_url }}">La grille</a> montre
qu’il tombe presque toujours au même épisode — le {{ a.episode_median }}<sup>e</sup>.</p>

## Deux jeux, cinq mesures

{% include graphiques/fusion-avant-apres.svg %}

<p class="legende-figure">{{ a.avant.conseils }} conseils avant la
réunification, {{ a.apres.conseils }} après, sur {{ a.saisons }} saisons. Le
rang de force va de 0 — le plus faible du camp ce soir-là — à 100, le plus
fort.</p>

<div class="tableau-large">
<table>
<thead><tr><th>Mesure</th><th class="nombre">Avant</th><th class="nombre">Après</th></tr></thead>
<tbody>
<tr><td>Conseils</td><td class="nombre">{{ a.avant.conseils }}</td><td class="nombre">{{ a.apres.conseils }}</td></tr>
<tr><td>Présents en moyenne</td><td class="nombre">{{ a.avant.presents_moyen }}</td><td class="nombre">{{ a.apres.presents_moyen }}</td></tr>
<tr><td>Conseils serrés</td><td class="nombre">{{ a.avant.part_serres }} %</td><td class="nombre">{{ a.apres.part_serres }} %</td></tr>
<tr><td>Femmes parmi les éliminés</td><td class="nombre">{{ a.avant.part_femmes }} %</td><td class="nombre">{{ a.apres.part_femmes }} %</td></tr>
<tr><td>Âge moyen des éliminés</td><td class="nombre">{{ a.avant.age_moyen }} ans</td><td class="nombre">{{ a.apres.age_moyen }} ans</td></tr>
<tr><td>Rang de force de l’éliminé</td><td class="nombre">{{ a.rang_force_avant }}</td><td class="nombre">{{ a.rang_force_apres }}</td></tr>
</tbody>
</table>
</div>

## On élimine le fort AVANT, pas après

{% include graphiques/fusion-force-nulle.svg %}

<p class="legende-figure">Écart entre le rang de force de l’éliminé après la
fusion et avant. La silhouette est celle de {{ tf.tirages }} tirages où
l’éliminé de chaque conseil est pris au hasard parmi les présents.</p>

<div class="constat">
  <p>Avant la réunification, l’éliminé se situe en moyenne au rang
  <b>{{ a.rang_force_avant }} sur 100</b> de son camp : <b>au-dessus de la
  médiane</b>. Après, il tombe à <b>{{ a.rang_force_apres }}</b> — la médiane,
  à peu de chose près.</p>
  <p>L’écart vaut {{ tf.observe }} points de rang,
  <b>{{ tf.ecart_types }} écarts-types</b> sous le hasard, p ajustée
  {{ tf.p_ajustee }}.</p>
  <p><b>C’est l’inverse de ce qu’on raconte.</b> La tribu qui perd sacrifie le
  joueur qu’elle a vu gagner ; le camp réuni, lui, choisit à peu près au milieu
  du classement.</p>
</div>

<p class="note"><strong>Le modèle nul fait tout le travail ici.</strong> À
chaque conseil, on tire l’éliminé <em>au hasard parmi les présents de ce
soir-là</em>. Tout ce qui tient à la composition du camp — son âge, son sexe,
son niveau — est donc déjà neutralisé. Ce qui reste ne peut être qu’un choix.</p>

### L’objection sérieuse, et ce qu’elle donne

La force est estimée sur les épreuves individuelles disputées. Un aventurier
éliminé avant la fusion en a disputé peu — deux, en médiane — quand ceux qui
restent seront jugés sur toute une saison. **On comparerait donc une estimation
vague à des estimations informées, et on prendrait le flou pour un résultat.**

Deux vérifications.

<div class="constat">
  <p><b>L’exposition n’explique pas la force.</b> La corrélation de rang entre
  le nombre d’épreuves disputées et la force estimée vaut
  <b>{{ a.robustesse.correlation_exposition_force }}</b> : à peine plus que
  zéro. Un joueur peu exposé n’est pas mécaniquement classé haut.</p>
  <p><b>À finesse d’estimation égale, l’écart tient.</b> En ne comparant
  l’éliminé qu’aux présents ayant disputé un nombre d’épreuves comparable — à
  trois près — le rang vaut <b>{{ a.robustesse.apparie.avant }}</b> avant
  ({{ a.robustesse.apparie.avant_effectif }} conseils) contre
  <b>{{ a.robustesse.apparie.apres }}</b> après
  ({{ a.robustesse.apparie.apres_effectif }}). L’écart se réduit, il ne
  disparaît pas.</p>
</div>

Autrement dit : **parmi les joueurs qu’on connaît aussi mal les uns que les
autres, celui qui sort avant la fusion est celui qui avait gagné la plus grande
part de ses rares épreuves.**

## Le vote se divise après la fusion

{% include graphiques/fusion-serre-nulle.svg %}

<p class="legende-figure">Différence de part de conseils serrés, après moins
avant. Le hasard est ici une redistribution des étiquettes « avant » et
« après » entre les mêmes conseils.</p>

<div class="constat">
  <p>Un conseil est <b>serré</b> quand l’éliminé ne rassemble pas plus de la
  moitié des voix exprimées. Avant la fusion : {{ a.avant.part_serres }} %.
  Après : <b>{{ a.apres.part_serres }} %</b>.</p>
  <p>+{{ ts.observe }} points, {{ ts.ecart_types }} écarts-types, p ajustée
  {{ ts.p_ajustee }}. Le camp réuni ne se retourne pas d’un bloc : il se
  partage.</p>
</div>

C’est cohérent avec ce que montre
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}) : après la
fusion, plusieurs groupes coexistent et chacun écrit son nom. Avant, une tribu
qui vient de perdre une épreuve a souvent déjà tranché sur le chemin du retour.

## Et le sexe, lui, ne change pas

<div class="constat">
  <p>{{ a.avant.part_femmes }} % de femmes parmi les éliminés avant la fusion,
  {{ a.apres.part_femmes }} % après — {{ tx.observe }} points d’écart, soit
  {{ tx.ecart_types }} écarts-types, p ajustée {{ tx.p_ajustee }}.
  <b>Non concluant.</b></p>
  <p>À {{ a.avant.conseils }} et {{ a.apres.conseils }} conseils, un écart de
  sept points ne se distingue pas d’un tirage. On ne peut ni l’affirmer ni
  l’écarter.</p>
</div>

## Les ambassadeurs

{% assign amb = a.ambassadeurs %}

C’est la seule élimination sans conseil : deux aventuriers, un de chaque tribu,
se retrouvent seuls et doivent désigner un partant. S’ils ne s’accordent pas,
un tirage au sort tranche entre eux deux.

<ul class="chiffres">
  <li class="chiffre"><b>{{ amb.effectif }}</b><span>ambassades reconstituées</span></li>
  <li class="chiffre"><b>{{ amb.episode_median }}</b><span>épisode médian</span></li>
  <li class="chiffre"><b>{{ amb.age_moyen }}</b><span>âge moyen de l’éliminé</span></li>
  <li class="chiffre"><b>{{ amb.part_femmes }} %</b><span>de femmes parmi eux</span></li>
</ul>

L’ambassade tombe **juste avant la réunification** — épisode
{{ amb.episode_median }} en médiane, quand la fusion tombe au
{{ a.episode_median }}<sup>e</sup>. Ce n’est pas un hasard de calendrier : elle
sert précisément à équilibrer les tribus avant de les réunir.

{% include graphiques/ambassadeurs-nulle.svg %}

<p class="legende-figure">Rang de force de l’éliminé par les ambassadeurs, face
à un tirage au hasard parmi les présents.</p>

<div class="constat">
  <p>Sur les {{ amb.effectif_force }} ambassades où la force des présents est
  estimable, l’éliminé se situe au rang <b>{{ amb.rang_moyen }} sur 100</b> —
  {{ ta.ecart_types }} écart-type du hasard, p ajustée {{ ta.p_ajustee }}.</p>
  <p><b>Deux ambassadeurs qui décident seuls choisissent comme un tirage.</b>
  Du moins sur ce critère-là, et à cette taille-là : treize cas ne permettent
  de détecter qu’un effet énorme.</p>
</div>

C’est un résultat en creux, et il vaut d’être dit : le seul moment du jeu où
l’élimination échappe au vote collectif est aussi celui où l’on ne détecte
aucune logique — ni le fort, ni le faible, ni un sexe, ni un âge.

## Ce que cette page ne dit pas

<p class="note"><strong>La force est celle d’une carrière, pas d’un soir.</strong>
Le modèle de <a href="{{ '/statistiques/force/' | relative_url }}">force
réelle</a> estime un niveau constant sur toute la participation. Il ne sait pas
qu’un aventurier était blessé au douzième jour, ni qu’il a progressé. Le
classement d’un soir est donc approché — et l’approximation, mesurée
ci-dessus, ne suffit pas à expliquer l’écart.</p>

<p class="note"><strong>Cinq saisons n’ont pas de bilan par épisode</strong> et
ne peuvent donc pas être coupées en deux ; une sixième, <em>Cambodge</em>, a un
repère de réunification aberrant et est écartée. Les éditions spéciales le sont
aussi : leurs revenants faussent la comparaison des forces.</p>

<p class="note"><strong>On ne sait pas QUI part en ambassade</strong>, seulement
qui en revient éliminé. Le nom des deux ambassadeurs n’apparaît que dans le
récit des épisodes, jamais dans un tableau. La question la plus intéressante —
l’ambassadeur qui négocie s’en sort-il mieux ? — reste donc sans réponse.</p>
