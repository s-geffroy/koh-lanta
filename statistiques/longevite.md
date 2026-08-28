---
layout: page
title: Âge et longévité
permalink: /statistiques/longevite/
chapeau: >-
  À quel âge tient-on le plus longtemps ? Et pourquoi les femmes sortent-elles plus tôt tout en gagnant autant de finales ?
---

{% assign s = site.data.stats %}

Combien de temps tient-on ? La mesure retenue ici est la **part de la saison
passée dans le jeu** : sortir au jour 20 d’une saison de 40 jours vaut 50 %.
Elle permet de comparer des éditions de durées différentes.

## L’âge

{% include graphiques/age-survie.svg %}

La courbe n’est pas celle qu’on attendrait. Ce ne sont ni les plus jeunes ni les
plus âgés qui durent : **la tranche 30-34 ans tient le plus longtemps**
({{ s.age[2].survie_moyenne }} % de la saison), tandis que les 18-24 ans
({{ s.age[0].survie_moyenne }} %) et les 45 ans et plus
({{ s.age[5].survie_moyenne }} %) sortent nettement plus tôt.

{% include graphiques/age-finale.svg %}

L’accès à la finale confirme le creux du milieu de trentaine et l’avantage des
30-34 ans. Une seule victoire est venue de la tranche des 45 ans et plus, sur
{{ s.age[5].effectif }} aventuriers.

<div class="tableau-large">
<table data-triable>
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
l’équilibre, et le fait depuis le début.

{% include graphiques/genre-survie.svg %}

<p class="legende-figure">Part moyenne de la saison passée dans le jeu, par
décennie.</p>

L’écart de longévité, lui, est constant : les hommes durent en moyenne
**{{ s.genre.resume[1].survie_moyenne }} %** de la saison contre
**{{ s.genre.resume[0].survie_moyenne }} %** pour les femmes. Il se resserre
dans les années 2020 sans disparaître.

{% include graphiques/genre-finale.svg %}

Et pourtant, au bout du compte, **les taux d’accès à la finale sont
identiques** — {{ s.genre.resume[0].taux_finale }} % contre
{{ s.genre.resume[1].taux_finale }} % — et les victoires se partagent
{{ s.vainqueurs.par_genre[0].effectif }} à {{ s.vainqueurs.par_genre[1].effectif }}.

C’est le résultat le plus intéressant de cette page : les femmes sortent plus
tôt **en moyenne**, mais celles qui passent la réunification vont au bout aussi
souvent que les hommes. L’écart se joue dans la première moitié du jeu, pas dans
la seconde.

<div class="tableau-large">
<table data-triable>
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

## Le peigne des torches

La courbe de survie de l’accueil est une moyenne : elle dit combien il en reste,
pas qui. Voici la même chose sans moyenne du tout — **un trait par
participation**, rangé du séjour le plus court au plus long.

{% include graphiques/peigne-torches.svg %}

<p class="peigne-legende">Un trait, un aventurier ; sa longueur, ses jours de
jeu ; sa couleur, son bandeau de départ. La bordure droite de cette figure
<em>est</em> la courbe de survie du programme, dessinée avec ses individus au
lieu d’un tracé. Les traits les plus courts sont ceux des premiers conseils, le
bloc plein du bas celui des finalistes. Les éditions spéciales, plus courtes, y
figurent avec leur durée réelle — c’est pourquoi la médiane y tombe plus tôt que
sur la courbe des seules saisons classiques. Les participations sans jour de
sortie établi n’y sont pas.</p>

## Chaque aventurier, un point

Les moyennes par tranche d’âge lissent ce que cette figure montre en clair : à
tout âge, on peut sortir au troisième jour comme aller en finale.

{% include graphiques/longevite-nuage.svg %}

<p class="legende-figure">Une participation à une saison classique par point :
l’âge en abscisse, la part de la saison tenue en ordonnée. Les vainqueurs et
les finalistes sont dessinés par-dessus la masse, sans quoi elle les
recouvrirait.</p>

**La dispersion est le résultat.** Le nuage n’a pas de pente marquée : l’âge ne
prédit pas la longévité. Ce qu’on voit, c’est une bande dense de sorties
précoces à tous les âges, et des vainqueurs répartis de vingt à cinquante ans.

## Les revenants

{{ s.records.nb_multi_participants }} aventuriers ont joué plus d’une fois.

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Aventurier</th><th class="nombre">Participations</th></tr></thead>
<tbody>
{% for m in s.records.multi_participants %}
<tr><td>{{ m.nom }}</td><td class="nombre">{{ m.participations }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Ces écarts sont des moyennes brutes : ils mélangent l’âge, le
métier et l’époque, qui n’ont pas la même composition d’une saison à l’autre.
<a href="{{ '/statistiques/equilibre/' | relative_url }}">Le jeu tenu serré</a>
les sépare par un modèle de durée — et l’écart hommes-femmes y rétrécit
jusqu’au bord du détectable.</p>
