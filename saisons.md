---
layout: page
title: Les saisons
permalink: /saisons/
---

{% assign s = site.data.stats %}

{{ s.general.saisons_diffusees }} saisons diffusées entre
{{ s.general.premiere_annee }} et {{ s.general.derniere_annee }} :
{{ s.general.saisons_classiques }} éditions classiques et
{{ s.general.saisons_speciales }} éditions spéciales. Deux saisons de plus ont
été tournées mais **jamais diffusées**, interrompues en cours de tournage.

## Les éditions classiques

<div class="tableau-large">
<table>
<thead><tr>
  <th class="nombre">N°</th><th>Titre</th><th class="nombre">Année</th>
  <th>Lieu</th><th class="nombre">Jours</th><th class="nombre">Casting</th>
  <th class="nombre">Âge moyen</th><th class="nombre">Femmes</th><th>Vainqueur</th>
</tr></thead>
<tbody>
{% for x in s.saisons %}{% unless x.speciale %}
<tr>
  <td class="nombre">{{ x.numero }}</td>
  <td><strong>{{ x.titre }}</strong></td>
  <td class="nombre">{{ x.annee }}</td>
  <td>{{ x.lieu }}, {{ x.pays }}</td>
  <td class="nombre">{{ x.duree_jours }}</td>
  <td class="nombre">{{ x.effectif }}</td>
  <td class="nombre">{{ x.age_moyen }}</td>
  <td class="nombre">{{ x.part_femmes }} %</td>
  <td>{{ x.vainqueurs | join: " et " }}</td>
</tr>
{% endunless %}{% endfor %}
</tbody>
</table>
</div>

## Les éditions spéciales

Elles font revenir d'anciens aventuriers. Leurs chiffres sont tenus à part
partout sur ce site : des revenants de quarante ans qui rejouent tirent les
moyennes d'âge vers le haut sans rien dire du casting ordinaire.

<div class="tableau-large">
<table>
<thead><tr>
  <th>Titre</th><th class="nombre">Année</th><th>Lieu</th>
  <th class="nombre">Jours</th><th class="nombre">Casting</th>
  <th class="nombre">Âge moyen</th><th>Vainqueur</th>
</tr></thead>
<tbody>
{% for x in s.saisons %}{% if x.speciale %}
<tr>
  <td><strong>{{ x.titre }}</strong></td>
  <td class="nombre">{{ x.annee }}</td>
  <td>{{ x.lieu }}, {{ x.pays }}</td>
  <td class="nombre">{{ x.duree_jours }}</td>
  <td class="nombre">{{ x.effectif }}</td>
  <td class="nombre">{{ x.age_moyen }}</td>
  <td>{% if x.en_cours %}<em>saison en cours</em>{% else %}{{ x.vainqueurs | join: " et " }}{% endif %}</td>
</tr>
{% endif %}{% endfor %}
</tbody>
</table>
</div>

## Les saisons interrompues

<div class="tableau-large">
<table>
<thead><tr><th class="nombre">N°</th><th class="nombre">Année</th><th>Lieu prévu</th><th>Motif</th></tr></thead>
<tbody>
{% for x in site.data.saisons %}{% if x.annulee %}
<tr>
  <td class="nombre">{{ x.numero }}</td>
  <td class="nombre">{{ x.annee }}</td>
  <td>{{ x.lieu }}, {{ x.pays }}</td>
  <td>{{ x.motif_annulation }}</td>
</tr>
{% endif %}{% endfor %}
</tbody>
</table>
</div>

## Composition du casting

{% include graphiques/saisons-femmes.svg %}

<p class="legende-figure">Part de femmes au départ de chaque saison classique.
La production vise l'équilibre : l'écart à 50 % tient au plus à un ou deux
aventuriers.</p>
