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
n’avoir jamais servi. Il est renseigné pour **{{ g.participations }}
participations** de saisons classiques — et c’est déjà une limite, sur laquelle
on revient à la fin.

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
au-dessus de 1, on trouve la Corse, la Nouvelle-Aquitaine, Provence-Alpes-Côte
d’Azur, Auvergne-Rhône-Alpes, l’Occitanie — la montagne et les deux littoraux du
Sud. En dessous, les Hauts-de-France, les Pays de la Loire, le Centre-Val de
Loire, la Bretagne.

Deux lignes sortent vraiment de l’intervalle.

<div class="constat">
  <p><b>La Corse fournit quatre fois sa part</b> : six aventuriers pour un
  et demi attendus, intervalle 1,46 à 8,54. C’est la seule région dont
  l’intervalle ne contient pas 1 par le haut.</p>
  <p><b>La Réunion n’en fournit aucun</b>, pour quatre attendus — intervalle
  0 à 0,92, entièrement sous 1. En ajoutant la Guadeloupe et la Guyane, les
  départements d’outre-mer pèsent <b>deux aventuriers pour près de neuf
  attendus</b>, et les deux viennent de Martinique.</p>
</div>

## Les départements, pour mémoire

Quatre-vingts départements pour trois cents personnes, cela fait trois
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

<p class="note"><strong>La couverture est partielle et elle n’est pas
aléatoire.</strong> Le département n’est renseigné que pour
{{ g.participations }} participations, et il manque à des saisons
<em>entières</em> — les plus anciennes surtout. Ce résultat décrit donc le
recrutement des années {{ g.annees[0] }}-{{ g.annees[1] }} tel que les quinze
saisons documentées le montrent, pas les vingt-cinq ans du programme.</p>

<p class="note"><strong>Trois réserves de mesure.</strong> Le lieu relevé est
celui annoncé à l’antenne : c’est une résidence au moment du tournage, pas un
lieu de naissance. {{ g.nb_hors_fichier }} participations sont écartées faute de
figurer au fichier national ({{ g.hors_fichier | join: ", " }}). Et le fichier
INSEE s’arrête à {{ g.derniere_annee_insee }} : pour la saison de
{{ g.annees[1] }}, la population de {{ g.derniere_annee_insee }} est reconduite.</p>
