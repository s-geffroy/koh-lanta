---
layout: page
title: Jaune contre rouge
permalink: /statistiques/tribus/
chapeau: >-
  Vaut-il mieux commencer chez les Jaunes ou chez les Rouges ? La question revient à chaque saison. La réponse tient en une ligne.
---

{% assign s = site.data.stats %}

C’est une question qui revient à chaque saison : vaut-il mieux commencer chez
les Jaunes ou chez les Rouges ? Sur {{ s.general.saisons_classiques }} saisons
classiques, la réponse tient en une ligne.

## Les victoires

{% include graphiques/tribus-victoires.svg %}

**{{ s.couleurs[0].victoires }} victoires pour le jaune, {{ s.couleurs[1].victoires }}
pour le rouge.** Égalité stricte. Les couleurs minoritaires — bleu, vert,
violet, orange — n’apparaissent que sur les saisons à trois ou quatre tribus, et
leurs effectifs sont trop faibles pour qu’on en tire quoi que ce soit.

## La survie

{% include graphiques/tribus-survie.svg %}

<p class="legende-figure">Part de la durée totale de la saison passée dans le
jeu, en moyenne, selon la couleur de la tribu de départ.</p>

L’écart entre jaune et rouge se compte en points, sur des effectifs de plus de
deux cents aventuriers chacun : il n’y a pas de signal.

## Ce que la couleur décide quand même

{% assign af = site.data.stats.modeles.autour_du_feu %}
{% assign tba = site.data.stats.modeles.registre | where: "cle", "bandeau_minoritaire" | first %}

Le bandeau ne décide rien du palmarès. Il décide en revanche **qui part**, dès
qu’on se retrouve du mauvais côté du compte.

<div class="constat">
  <p>Sachant que son bandeau d’origine est le <b>moins représenté</b> du camp
  assis au conseil, on est éliminé dans
  <b>{{ af.bandeau[0].probabilite }} %</b> des cas
  ({{ af.bandeau[0].cas }} sur {{ af.bandeau[0].effectif }}) ; quand il est le
  plus représenté, dans <b>{{ af.bandeau[1].probabilite }} %</b>.</p>
  <p>{{ tba.observe | round: 1 }} points d’écart, {{ tba.ecart_types }}
  écarts-types au-dessus d’un tirage au sort parmi les présents de chaque
  conseil, p ajustée {{ tba.p_ajustee }}.</p>
</div>

Les deux résultats de cette page ne se contredisent pas : **la couleur n’est pas
un avantage, c’est une appartenance.** Elle ne fait gagner personne, et elle
condamne celui qui se retrouve seul de sa sorte.
[Sachant qui est autour du feu]({{ '/statistiques/autour-du-feu/' | relative_url }})
détaille, avant et après la réunification.

## Le détail

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Couleur</th><th class="nombre">Aventuriers</th>
  <th class="nombre">Survie moyenne</th><th class="nombre">Finales</th>
  <th class="nombre">Taux de finale</th><th class="nombre">Victoires</th>
</tr></thead>
<tbody>
{% for c in s.couleurs %}
<tr>
  <td><span class="pastille" style="background: var(--tribu-{{ c.couleur }})"></span>{{ c.couleur | capitalize }}</td>
  <td class="nombre">{{ c.effectif }}</td>
  <td class="nombre">{{ c.survie_moyenne }} %</td>
  <td class="nombre">{{ c.finales }}</td>
  <td class="nombre">{{ c.taux_finale }} %</td>
  <td class="nombre">{{ c.victoires }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">La couleur noire correspond à la tribu maudite de 2024 et à
l’île des héros de 2020 : deux aventuriers seulement, aucune conclusion
possible.</p>

<p class="note">Deux autres pages recoupent ce résultat. Un modèle de durée
ne trouve aucun effet du bandeau sur le risque d’élimination
(<a href="{{ '/statistiques/equilibre/' | relative_url }}">Le jeu tenu serré</a>).
Et les deux tribus de départ ne sont pas composées à l’équilibre par une règle
générale : trois saisons seulement opposent nettement deux générations
(<a href="{{ '/statistiques/casting/' | relative_url }}">La recette du casting</a>).</p>
