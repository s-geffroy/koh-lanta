---
layout: page
title: Les prénoms
permalink: /statistiques/prenoms/
chapeau: >-
  Alexandra revient sept fois à Koh-Lanta. Est-ce beaucoup ? La question n’a
  de réponse qu’en la comparant à la France qui est née les mêmes années.
---

{% assign p = site.data.prenoms %}
{% assign c = site.data.stats.casting %}

Sept Alexandra, huit Maxime, six Nicolas. Cela paraît beaucoup — mais un prénom
courant produit mécaniquement des porteurs, et les aventuriers ne sont pas nés
n’importe quand. La seule question qui tienne est donc : **combien en
attendrait-on ?**

## D’abord, savoir quand ils sont nés

{% include graphiques/casting-generations.svg %}

<p class="legende-figure">Année de naissance déduite de l’âge annoncé au
tournage et de l’année de la saison. Calculable pour
{{ p.aventuriers_datables }} participations sur
{{ site.data.stats.general.participations }}.</p>

Les aventuriers sont nés entre **{{ p.periode.debut }}** et
**{{ p.periode.fin }}**, avec un sommet très net dans les années 1980. C’est
cette population-là — et pas la France d’aujourd’hui — qui sert de point de
comparaison.

## La méthode, en trois lignes

L’[INSEE publie le nombre de naissances par prénom, par sexe et par année
depuis 1900](https://www.insee.fr/fr/statistiques/8595130). Pour chaque prénom,
on calcule donc :

<p class="note"><strong>Attendu</strong> = somme, sur les
{{ p.aventuriers_datables }} aventuriers datables, de la probabilité qu’une
personne née cette année-là, de ce sexe, porte ce prénom.<br>
C’est le nombre d’aventuriers qui s’appelleraient ainsi si le casting était un
échantillon ordinaire des naissances françaises. L’indice est
<strong>observé ÷ attendu</strong> : 1 signifie « exactement la France ».</p>

## Le résultat

{% include graphiques/prenoms-ecart.svg %}

<p class="legende-figure">Les huit prénoms les plus sur-représentés, puis les
huit plus sous-représentés. Seuls les prénoms dont l’attendu atteint 1 sont
classés : en dessous, un seul porteur suffirait à afficher un facteur quarante,
et l’indice ne mesurerait plus que la rareté du prénom.</p>

Les écarts sont réels mais **modestes** : le plus sur-représenté ne dépasse pas
un facteur trois et demi. Autrement dit, **le casting de Koh-Lanta ressemble
beaucoup à la France de sa génération**. C’est en soi un résultat : on aurait pu
imaginer un tri involontaire, il n’y en a pas de marqué.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Prénom</th><th class="nombre">Observé</th>
  <th class="nombre">Attendu</th><th class="nombre">Indice</th>
</tr></thead>
<tbody>
{% for x in p.prenoms %}{% unless x.absent_du_fichier %}{% if x.attendu >= 1 %}
<tr>
  <td>{{ x.prenom }}</td>
  <td class="nombre">{{ x.observe }}</td>
  <td class="nombre">{{ x.attendu }}</td>
  <td class="nombre">×{{ x.indice }}</td>
</tr>
{% endif %}{% endunless %}{% endfor %}
</tbody>
</table>
</div>

## Ceux que le fichier national ne connaît pas

{% assign absents = 0 %}{% assign porteurs = 0 %}
{% for x in p.prenoms %}{% if x.absent_du_fichier %}
  {% assign absents = absents | plus: 1 %}
  {% assign porteurs = porteurs | plus: x.observe %}
{% endif %}{% endfor %}

**{{ absents }} prénoms** portés par **{{ porteurs }} aventuriers** n’apparaissent
pas au fichier national sur la période : Teheiura, Coumba, Moundir, Filomène,
Namadia, Guénaëlle, Wafa… L’INSEE verse en effet les prénoms trop rares dans un
seul sac, et n’enregistre que les naissances survenues en France.

C’est presque **un aventurier sur cinq**, et c’est sans doute le vrai résultat
de cette page : le casting va chercher bien au-delà des prénoms les plus donnés.

<p class="note">Trois réserves, qui portent toutes dans le même sens. L’âge est
celui annoncé au tournage et non une date de naissance : l’année déduite peut
être fausse d’un an. L’INSEE arrondit ses effectifs au multiple de cinq le plus
proche. Enfin, le prénom retenu ici est celui utilisé à l’écran — un diminutif
comme « Babeth » ne se retrouvera jamais à l’état civil, et gonfle donc la liste
des introuvables.</p>
