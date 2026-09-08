---
layout: page
title: Les épreuves nommées
description: "Les épreuves de Koh-Lanta une par une : combien de fois chacune a été courue, dans quelles éditions, et qui détient le record de victoires."
permalink: /epreuves/
chapeau: >-
  Chaque épreuve qui porte un nom, les éditions où elle a été courue, et le
  détenteur du record.
---

{% assign f = site.data.epreuves_fiches.epreuves %}
{% assign en = site.data.epreuves_nommees %}

Le wiki nomme **{{ en.nb_epreuves }} épreuves**, pour {{ en.nb_apparitions }}
apparitions relevées. Toutes n’ont pas de page ici, et la raison est dans les
données : le nom cité par le wiki et l’épreuve relevée dans le déroulé de la
saison ne se raccordent que dans
**{{ en.raccord.part_raccordee }} %** des cas
({{ en.raccord.epreuves_raccordees }} sur {{ en.raccord.epreuves_relevees }}).
Quatre noms n’ont aucune apparition datée — « Poteaux » en fait partie, alors
que c’est la plus connue de toutes — et dix-sept n’ont aucun vainqueur nommé.

Les épreuves ci-dessous sont celles dont on sait à la fois **quand** elles ont
été courues et **par qui** elles ont été gagnées. Les autres restent comptées
dans le tableau de
[ce que les épreuves disent du jeu]({{ '/statistiques/epreuves/' | relative_url }}) :
une ligne dans un tableau n’a pas les mêmes exigences qu’une page entière.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Épreuve</th><th>Type</th>
  <th class="nombre">Apparitions</th><th class="nombre">Éditions</th>
  <th>Record</th><th class="nombre">Victoires</th>
</tr></thead>
<tbody>
{%- for cle in f -%}
{%- assign e = cle[1] %}
<tr>
  <td><a href="{{ '/epreuves/' | append: e.id | append: '/' | relative_url }}">{{ e.nom }}</a></td>
  <td>{{ e.type }}</td>
  <td class="nombre" data-val="{{ e.apparitions }}">{{ e.apparitions }}</td>
  <td class="nombre" data-val="{{ e.editions.size }}">{{ e.editions.size }}</td>
  <td>{% if e.record %}{% include lien-aventurier.html id=e.record.id nom=e.record.nom %}{% endif %}</td>
  <td class="nombre" data-val="{% if e.record %}{{ e.record.victoires }}{% else %}0{% endif %}">{% if e.record %}{{ e.record.victoires }}{% endif %}</td>
</tr>
{%- endfor %}
</tbody>
</table>
</div>

<p class="note">Une épreuve peut être courue plusieurs fois dans la même
édition : la colonne <em>apparitions</em> les compte toutes, la colonne
<em>éditions</em> ne compte que les saisons distinctes.</p>

<p><a href="{{ '/statistiques/epreuves/' | relative_url }}">Ce que les épreuves disent du jeu</a> ·
<a href="{{ '/saisons/' | relative_url }}">Toutes les saisons</a> ·
<a href="{{ '/sources/' | relative_url }}">Les sources</a></p>
