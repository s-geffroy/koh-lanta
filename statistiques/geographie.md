---
layout: page
title: D’où ils viennent
permalink: /statistiques/geographie/
chapeau: >-
  Vingt-quatre Parisiens, est-ce beaucoup ? La question n’a de réponse qu’en la
  comparant à la France qui vivait là ces années-là.
---

{% assign g = site.data.geographie %}
{% assign reg = site.data.stats.modeles.registre %}
{% assign td = reg | where: "cle", "geographie_departements" | first %}
{% assign tr = reg | where: "cle", "geographie_regions" | first %}

Le département d’origine est le dernier champ important de ce jeu de données à
n’avoir jamais servi. Il est aujourd’hui renseigné pour
**{{ g.saisons_completes }} des {{ g.saisons_classiques }} saisons classiques
en entier**, et pour {{ g.participations }} participations comparables à la
population française — la limite qui reste est décrite à la fin.

<p class="note"><strong>La méthode, la même que pour les prénoms.</strong>
L’INSEE publie la population par département, par sexe et par groupe d’âges,
année par année depuis 1990. On prend la tranche <strong>20-59 ans</strong>,
celle qui recouvre le mieux les aventuriers, et <strong>l’année de chaque
saison</strong> : la France de 2003 n’est pas celle de 2026. L’attendu d’un
département est le nombre d’aventuriers qui en viendraient si le casting était
un tirage ordinaire. L’indice est <strong>observé ÷ attendu</strong> : 1
signifie « exactement la France ».</p>

## Le résultat : non, ce n’est pas la France

{% include graphiques/geographie-nulle.svg %}

<p class="legende-figure">Dispersion entre les effectifs observés par région et
ceux qu’un tirage dans la population produirait. La silhouette est celle de
{{ tr.tirages }} tirages simulés.</p>

<div class="constat">
  <p>À l’échelle des régions, la dispersion observée vaut
  <b>{{ tr.observe }}</b> contre <b>{{ tr.attendu }}</b> attendus —
  {{ tr.ecart_types }} écarts-types, p ajustée {{ tr.p_ajustee }}.</p>
  <p>Le recrutement <b>n’épouse pas la démographie française</b>. Au niveau des
  départements, même verdict : {{ td.observe }} contre {{ td.attendu }},
  p ajustée {{ td.p_ajustee }}.</p>
</div>

C’est l’inverse de ce que la page des
[prénoms]({{ '/statistiques/prenoms/' | relative_url }}) avait trouvé sur l’état
civil, où le casting collait de très près à sa génération. Sur la géographie, il
s’en écarte.

## Où, exactement

{% include graphiques/geographie-regions.svg %}

<p class="legende-figure">Indice observé ÷ attendu par région. À 1, la région
fournit exactement sa part de population. L’intervalle est celui de l’effectif
observé — la plupart traversent 1, et c’est le <em>tableau d’ensemble</em> qui
fait le résultat, pas une ligne isolée.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Région</th><th class="nombre">Observé</th><th class="nombre">Attendu</th>
  <th class="nombre">Indice</th><th class="nombre">Intervalle</th>
</tr></thead>
<tbody>
{% for r in g.regions %}
<tr>
  <td>{{ r.region }}</td>
  <td class="nombre">{{ r.observe }}</td>
  <td class="nombre">{{ r.attendu }}</td>
  <td class="nombre" data-val="{{ r.indice }}">×{{ r.indice }}</td>
  <td class="nombre">{{ r.indice_bas }} – {{ r.indice_haut }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Le gradient est net, et il est **géographique avant d’être démographique** :
au-dessus de 1, on trouve la Corse, Provence-Alpes-Côte d’Azur, la
Nouvelle-Aquitaine, l’Île-de-France, l’Occitanie, Auvergne-Rhône-Alpes — le
pourtour méditerranéen, la montagne, la façade atlantique et Paris. En dessous,
le Centre-Val de Loire, les Pays de la Loire, la Bourgogne-Franche-Comté, la
Bretagne, le Grand Est, les Hauts-de-France : une diagonale du Nord-Ouest et de
l’Est.

Six lignes sortent vraiment de leur intervalle — trois par le haut, trois par le
bas. Ce sont les seules qui se lisent isolément ; le reste du tableau ne vaut
qu’ensemble.

<div class="constat">
  <p><b>Au-dessus :</b>
  {%- for r in g.regions_hautes %} {{ r.region }} ×{{ r.indice }}
  [{{ r.indice_bas }} ; {{ r.indice_haut }}]{% unless forloop.last %} ·{% endunless %}
  {%- endfor %}.</p>
  <p><b>En dessous :</b>
  {%- for r in g.regions_basses %} {{ r.region }} ×{{ r.indice }}
  [{{ r.indice_bas }} ; {{ r.indice_haut }}]{% unless forloop.last %} ·{% endunless %}
  {%- endfor %}.</p>
  <p>Et le trou le plus net n’est pas une région de métropole :
  <b>l’outre-mer pèse {{ g.outremer.observe }} aventuriers pour
  {{ g.outremer.attendu }} attendus</b>. La Réunion, la plus peuplée des
  quatre, n’en a jamais fourni un seul ; les {{ g.outremer.observe }} viennent
  tous deux de Martinique.</p>
</div>

La Corse garde le plus fort indice, mais son intervalle est large — six
personnes, cela ne se mesure pas finement. Le résultat solide est ailleurs :
**Provence-Alpes-Côte d’Azur fournit une fois et trois quarts sa part**, sur
cinquante-cinq aventuriers, et son intervalle ne s’approche pas de 1.

## Les départements, pour mémoire

Cent départements pour {{ g.participations }} personnes, cela fait quatre
personnes par département : à ce grain, un indice est un bruit et non un
résultat. Le tableau est donné parce qu’il se lit, pas parce qu’il conclut.
{{ g.departements_classes }} départements atteignent un attendu de 1 et sont
classés.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Département</th><th class="nombre">Observé</th>
  <th class="nombre">Attendu</th><th class="nombre">Indice</th>
</tr></thead>
<tbody>
{% for d in g.departements %}{% if d.indice %}
<tr>
  <td>{{ d.departement }}</td>
  <td class="nombre">{{ d.observe }}</td>
  <td class="nombre">{{ d.attendu }}</td>
  <td class="nombre" data-val="{{ d.indice }}">×{{ d.indice }}</td>
</tr>
{% endif %}{% endfor %}
</tbody>
</table>
</div>

## Ce que ce résultat ne dit pas — et c’est beaucoup

<p class="note"><strong>Un écart n’est pas une intention.</strong> Trois
explications tiennent également debout et ces données ne permettent pas de
trancher entre elles : la production recrute là où elle va chercher ; les
candidatures viennent d’elles-mêmes davantage de certaines régions ; ou les deux
se renforcent. Un casting déséquilibré est le <em>résultat</em> d’une sélection,
pas la sélection elle-même.</p>

<p class="note"><strong>La couverture est bonne, mais elle n’est pas
uniforme.</strong> {{ g.saisons_completes }} des {{ g.saisons_classiques }}
saisons classiques ont leur casting <em>entièrement</em> localisé, et aucune
n’est muette. Cinq restent lacunaires — <em>Panama</em> (4 sur 16),
<em>Palawan</em> (5 sur 16), <em>Palau</em> (8 sur 18), <em>Pacifique</em>
(10 sur 17), et <em>L’Île au trésor</em> à une personne près. Quatre des cinq
sont antérieures à 2010 : le résultat pèse donc un peu plus lourd sur les
quinze dernières années que sur les cinq premières.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Saison</th><th class="nombre">Année</th>
<th class="nombre">Localisés</th><th class="nombre">Casting</th></tr></thead>
<tbody>
{% for c in g.couverture %}
<tr><td>{{ c.titre }}</td><td class="nombre">{{ c.annee }}</td>
<td class="nombre">{{ c.localisees }}</td><td class="nombre">{{ c.effectif }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note"><strong>Trois réserves de mesure.</strong> Le lieu relevé est
celui annoncé à l’antenne : c’est une résidence au moment du tournage, pas un
lieu de naissance. {{ g.nb_hors_fichier }} participations sont écartées faute de
figurer au fichier national ({{ g.hors_fichier | join: ", " }}). Et le fichier
INSEE s’arrête à {{ g.derniere_annee_insee }} : pour la saison de
{{ g.annees[1] }}, la population de {{ g.derniere_annee_insee }} est reconduite.</p>
