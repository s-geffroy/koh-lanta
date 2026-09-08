---
layout: page
title: Les statistiques de Koh-Lanta
description: "Toutes les analyses des données de Koh-Lanta : ce qui se compte, et ce que le hasard suffirait à expliquer. Le sommaire des entrées du site."
permalink: /statistiques/
chapeau: >-
  Vingt-sept entrées dans le même jeu de données. Onze comptent ce qui
  s’est passé ; seize le mettent à l’épreuve du hasard.
---

{% assign s = site.data.stats %}
{% assign g = s.general %}
{% assign v = s.vainqueurs %}

Tout ce qui suit est calculé sur les **{{ g.participations }} participations**
relevées entre {{ g.premiere_annee }} et {{ g.derniere_annee }}. Sauf mention
contraire, les chiffres portent sur les **{{ g.saisons_classiques }} saisons
classiques** : les {{ g.saisons_speciales }} éditions spéciales font revenir les
mêmes personnes et fausseraient les moyennes d’âge comme de longévité.

<ul class="chiffres">
  <li class="chiffre"><b>{{ v.age_moyen }} ans</b><span>âge moyen des vainqueurs</span></li>
  <li class="chiffre"><b>{{ v.part_40_et_plus }} %</b><span>de vainqueurs de 40 ans ou plus</span></li>
  <li class="chiffre"><b>{{ s.conseils.conseils }}</b><span>conseils dépouillés</span></li>
  <li class="chiffre"><b>{{ s.conseils.bulletins }}</b><span>bulletins relevés</span></li>
  <li class="chiffre"><b>{{ s.epreuves.epreuves }}</b><span>épreuves relevées</span></li>
  <li class="chiffre"><b>{{ s.colliers.colliers }}</b><span>colliers suivis</span></li>
  <li class="chiffre"><b>{{ s.records.nb_multi_participants }}</b><span>aventuriers revenus jouer</span></li>
</ul>

Onze entrées **décrivent** : elles comptent, elles font des parts et des
moyennes. Seize **testent** — elles comparent ce qu’on observe à ce que le
hasard produirait, et publient un intervalle plutôt qu’un point. Elles ne
remplacent pas les premières : on ne teste bien qu’un écart qu’on a d’abord
regardé. Les unes et les autres sont mêlées ci-dessous, parce qu’elles sont
rangées par **sujet** et non par méthode : « Les alliances » et « Qui vise
qui » parlent du même moment du jeu, quoi qu’elles emploient pour le dire. La
[méthode]({{ '/methode/' | relative_url }}) les détaille, et donne la liste
complète des tests menés — y compris ceux qui n’ont rien donné.

## Les vingt-sept entrées

{%- for groupe in site.data.navigation -%}
{%- if groupe.fil -%}
{%- assign total = 0 -%}
{%- for t in groupe.themes -%}
{%- for e in t.entrees -%}{%- unless e.hub -%}{%- assign total = total | plus: 1 -%}{%- endunless -%}{%- endfor -%}
{%- endfor -%}
{%- assign rang = 0 -%}
{%- for t in groupe.themes -%}
### {{ t.titre }}

<p class="chapeau-theme">{{ t.resume }}</p>

<ul class="cartes">
{%- for e in t.entrees -%}
{%- unless e.hub -%}
{%- assign rang = rang | plus: 1 -%}
  <li class="carte">
    <a href="{{ e.url | relative_url }}">
      <span class="carte-rang">{{ rang }}<i>/{{ total }}</i></span>
      <span class="carte-titre">{{ e.titre }}</span>
      <span class="carte-resume">{{ e.resume }}</span>
    </a>
  </li>
{%- endunless -%}
{%- endfor -%}
</ul>
{%- endfor -%}
{%- endif -%}
{%- endfor -%}

## Le tableau d’ensemble

Avant d’entrer dans le détail, deux mesures qui cadrent tout le reste : combien
d’aventuriers partent, et à quel âge.

{% include graphiques/saisons-effectif.svg %}

<p class="legende-figure">Le casting s’étoffe avec le temps : les premières
saisons partaient à seize, les récentes à vingt-quatre.</p>

{% include graphiques/saisons-age.svg %}

<p class="legende-figure">L’âge moyen du casting, lui, reste remarquablement
stable autour de la trentaine sur vingt-cinq ans.</p>
