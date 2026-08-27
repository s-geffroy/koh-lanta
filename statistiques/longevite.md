---
layout: page
title: Âge et longévité
permalink: /statistiques/longevite/
---

{% assign s = site.data.stats %}

Combien de temps tient-on ? La mesure retenue ici est la **part de la saison
passée dans le jeu** : sortir au jour 20 d'une saison de 40 jours vaut 50 %.
Elle permet de comparer des éditions de durées différentes.

## L'âge

{% include graphiques/age-survie.svg %}

La courbe n'est pas celle qu'on attendrait. Ce ne sont ni les plus jeunes ni les
plus âgés qui durent : **la tranche 30-34 ans tient le plus longtemps**
({{ s.age[2].survie_moyenne }} % de la saison), tandis que les 18-24 ans
({{ s.age[0].survie_moyenne }} %) et les 45 ans et plus
({{ s.age[5].survie_moyenne }} %) sortent nettement plus tôt.

{% include graphiques/age-finale.svg %}

L'accès à la finale confirme le creux du milieu de trentaine et l'avantage des
30-34 ans. Une seule victoire est venue de la tranche des 45 ans et plus, sur
{{ s.age[5].effectif }} aventuriers.

<div class="tableau-large">
<table>
<thead><tr>
  <th>Tranche</th><th class="nombre">Aventuriers</th><th class="nombre">Part du casting</th>
  <th class="nombre">Survie moyenne</th><th class="nombre">Finales</th>
  <th class="nombre">Taux de finale</th><th class="nombre">Victoires</th>
</tr></thead>
<tbody>
{% for a in s.age %}
<tr>
  <td>{{ a.tranche }}</td>
  <td class="nombre">{{ a.effectif }}</td>
  <td class="nombre">{{ a.part_du_casting }} %</td>
  <td class="nombre">{{ a.survie_moyenne }} %</td>
  <td class="nombre">{{ a.finales }}</td>
  <td class="nombre">{{ a.taux_finale }} %</td>
  <td class="nombre">{{ a.victoires }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Femmes et hommes

Le casting est **rigoureusement paritaire** :
{{ s.genre.resume[0].effectif }} femmes pour
{{ s.genre.resume[1].effectif }} hommes, soit
{{ s.genre.resume[0].part_du_casting }} % contre
{{ s.genre.resume[1].part_du_casting }} %. La production compose ses saisons à
l'équilibre, et le fait depuis le début.

{% include graphiques/genre-survie.svg %}

<p class="legende-figure">Part moyenne de la saison passée dans le jeu, par
décennie.</p>

L'écart de longévité, lui, est constant : les hommes durent en moyenne
**{{ s.genre.resume[1].survie_moyenne }} %** de la saison contre
**{{ s.genre.resume[0].survie_moyenne }} %** pour les femmes. Il se resserre
dans les années 2020 sans disparaître.

{% include graphiques/genre-finale.svg %}

Et pourtant, au bout du compte, **les taux d'accès à la finale sont
identiques** — {{ s.genre.resume[0].taux_finale }} % contre
{{ s.genre.resume[1].taux_finale }} % — et les victoires se partagent
{{ s.vainqueurs.par_genre[0].effectif }} à {{ s.vainqueurs.par_genre[1].effectif }}.

C'est le résultat le plus intéressant de cette page : les femmes sortent plus
tôt **en moyenne**, mais celles qui passent la réunification vont au bout aussi
souvent que les hommes. L'écart se joue dans la première moitié du jeu, pas dans
la seconde.

<div class="tableau-large">
<table>
<thead><tr>
  <th>&nbsp;</th><th class="nombre">Aventuriers</th><th class="nombre">Part du casting</th>
  <th class="nombre">Âge moyen</th><th class="nombre">Survie moyenne</th>
  <th class="nombre">Taux de finale</th><th class="nombre">Victoires</th>
</tr></thead>
<tbody>
{% for x in s.genre.resume %}
<tr>
  <td>{{ x.libelle }}</td>
  <td class="nombre">{{ x.effectif }}</td>
  <td class="nombre">{{ x.part_du_casting }} %</td>
  <td class="nombre">{{ x.age_moyen }} ans</td>
  <td class="nombre">{{ x.survie_moyenne }} %</td>
  <td class="nombre">{{ x.taux_finale }} %</td>
  <td class="nombre">{{ x.victoires }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Les revenants

{{ s.records.nb_multi_participants }} aventuriers ont joué plus d'une fois.

<div class="tableau-large">
<table>
<thead><tr><th>Aventurier</th><th class="nombre">Participations</th></tr></thead>
<tbody>
{% for m in s.records.multi_participants %}
<tr><td>{{ m.nom }}</td><td class="nombre">{{ m.participations }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>
