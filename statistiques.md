---
layout: page
title: Les statistiques
permalink: /statistiques/
---

{% assign s = site.data.stats %}
{% assign g = s.general %}
{% assign v = s.vainqueurs %}

Tout ce qui suit est calculé sur les **{{ g.participations }} participations**
relevées entre {{ g.premiere_annee }} et {{ g.derniere_annee }}. Sauf mention
contraire, les chiffres portent sur les **{{ g.saisons_classiques }} saisons
classiques** : les {{ g.saisons_speciales }} éditions spéciales font revenir les
mêmes personnes et fausseraient les moyennes d'âge comme de longévité.

<ul class="chiffres">
  <li class="chiffre"><b>{{ v.age_moyen }} ans</b><span>âge moyen des vainqueurs</span></li>
  <li class="chiffre"><b>{{ v.part_40_et_plus }} %</b><span>de vainqueurs de 40 ans ou plus</span></li>
  <li class="chiffre"><b>{{ s.conseils.conseils }}</b><span>conseils dépouillés</span></li>
  <li class="chiffre"><b>{{ s.conseils.bulletins }}</b><span>bulletins relevés</span></li>
  <li class="chiffre"><b>{{ s.records.nb_multi_participants }}</b><span>aventuriers revenus jouer</span></li>
</ul>

## Les cinq entrées

<ul class="sommaire">
  <li><a href="{{ '/statistiques/vainqueurs/' | relative_url }}">Le profil du vainqueur</a>
      <p>Âge, sexe, métier, couleur de tribu : ce que les {{ v.effectif }} vainqueurs
         ont en commun, et ce qu'ils n'ont pas en commun.</p></li>
  <li><a href="{{ '/statistiques/tribus/' | relative_url }}">Jaune contre rouge</a>
      <p>La couleur de départ change-t-elle quelque chose ? Réponse courte : non.</p></li>
  <li><a href="{{ '/statistiques/professions/' | relative_url }}">Le métier</a>
      <p>Qui compose le casting, et quels métiers mènent le plus loin.</p></li>
  <li><a href="{{ '/statistiques/longevite/' | relative_url }}">Âge et longévité</a>
      <p>À quel âge on tient le plus longtemps, et l'écart persistant entre
         femmes et hommes.</p></li>
  <li><a href="{{ '/statistiques/sorties/' | relative_url }}">Comment on sort</a>
      <p>Conseil, poteaux, orientation, abandon : la mécanique des départs, et
         son évolution.</p></li>
  <li><a href="{{ '/statistiques/conseils/' | relative_url }}">Les conseils</a>
      <p>{{ s.conseils.bulletins }} bulletins dépouillés : les votes serrés, les
         colliers, qui vote contre qui.</p></li>
</ul>

## Le tableau d'ensemble

{% include graphiques/saisons-effectif.svg %}

<p class="legende-figure">Le casting s'étoffe avec le temps : les premières
saisons partaient à seize, les récentes à vingt-quatre.</p>

{% include graphiques/saisons-age.svg %}

<p class="legende-figure">L'âge moyen du casting, lui, reste remarquablement
stable autour de la trentaine sur vingt-cinq ans.</p>
