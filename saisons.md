---
layout: page
title: Les saisons
permalink: /saisons/
chapeau: >-
  Trente-quatre éditions diffusées, deux interrompues, et quatre indicateurs
  qui disent ce qu’a été chacune d’elles.
---

{% assign s = site.data.stats %}

{{ s.general.saisons_diffusees }} saisons diffusées entre
{{ s.general.premiere_annee }} et {{ s.general.derniere_annee }} :
{{ s.general.saisons_classiques }} éditions classiques et
{{ s.general.saisons_speciales }} éditions spéciales. Deux saisons de plus ont
été tournées mais **jamais diffusées**, interrompues en cours de tournage.

## Les éditions classiques

<ul class="saison-grille">
{%- for x in site.data.saisons -%}
{%- unless x.speciale or x.annulee -%}
  <li class="saison">
    <p class="saison-numero">SAISON {{ x.numero }} · {{ x.annee }} · {{ x.duree_jours }} JOURS</p>
    <p class="saison-titre">{{ x.titre }}</p>
    <p class="saison-lieu">{{ x.lieu }}, {{ x.pays }}</p>
    <p class="saison-tribus">
      {%- for t in x.tribus -%}
      <span class="pastille" style="background: var(--tribu-{{ t.couleur }})"
            title="{{ t.nom }}"></span>
      {%- endfor -%}
      <span class="saison-tribus-noms">{{ x.tribus | map: "nom" | join: " · " }}</span>
    </p>
    <p class="saison-vainqueur">
      {%- if x.vainqueurs -%}Vainqueur : <b>{{ x.vainqueurs | join: " et " }}</b>
      {%- else -%}<i>saison en cours</i>{%- endif -%}
    </p>
  </li>
{%- endunless -%}
{%- endfor -%}
</ul>

## Les éditions spéciales

Elles font revenir d’anciens aventuriers. Leurs chiffres sont tenus à part
partout sur ce site : des revenants de quarante ans qui rejouent tirent les
moyennes d’âge vers le haut sans rien dire du casting ordinaire.

<ul class="saison-grille">
{%- for x in site.data.saisons -%}
{%- if x.speciale and x.annulee != true -%}
  <li class="saison">
    <p class="saison-numero">SPÉCIALE · {{ x.annee }} · {{ x.duree_jours }} JOURS</p>
    <p class="saison-titre">{{ x.titre }}</p>
    <p class="saison-lieu">{{ x.lieu }}, {{ x.pays }}</p>
    <p class="saison-vainqueur">
      {%- if x.vainqueurs -%}Vainqueur : <b>{{ x.vainqueurs | join: " et " }}</b>
      {%- else -%}<i>saison en cours</i>{%- endif -%}
    </p>
  </li>
{%- endif -%}
{%- endfor -%}
</ul>

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

## Les saisons comparées

Au-delà du casting, quatre indicateurs disent ce qu’a été chaque saison.

### Un aventurier a-t-il écrasé les épreuves ?

{% include graphiques/saisons-domination.svg %}

<p class="legende-figure">Indice de concentration des victoires individuelles.
Proche de zéro, les victoires ont circulé ; proche de un, une seule personne a
tout raflé.</p>

Le **Viêtnam (2010)** détient le record des saisons classiques : Claude Dartois
y remporte sept épreuves individuelles à lui seul. À l’opposé, **Fidji (2017)**
est la saison la plus partagée du programme.

### Le camp vote-t-il d’un bloc ?

{% include graphiques/saisons-dispersion.svg %}

<p class="legende-figure">Dispersion moyenne des bulletins au conseil. Zéro :
tout le monde écrit le même nom. Un : chacun vote dans son coin, plus personne
ne contrôle rien.</p>

### Des conseils serrés ou écrasants ?

{% include graphiques/saisons-tension.svg %}

<p class="legende-figure">Part des conseils où l’élimination s’est jouée à une
voix près.</p>

### L’abandon recule

{% include graphiques/saisons-abandon.svg %}

<p class="legende-figure">Part des aventuriers ayant quitté le jeu d’eux-mêmes
ou sur décision médicale.</p>

Deux saisons n’ont connu **aucun abandon** : *L’Île au trésor* (2016) et *Les
Reliques du destin* (2026). À l’autre bout, *Palau* (2009) en a perdu plus d’un
sur cinq.

### Le tableau complet

<p class="note">Cliquez sur un en-tête pour trier le tableau sur cette colonne.
Sans JavaScript, il reste entièrement lisible, dans l’ordre chronologique.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th class="nombre">N°</th><th>Saison</th><th class="nombre">Casting</th>
  <th class="nombre">Âge moyen</th><th class="nombre">Femmes</th>
  <th class="nombre">Survie moyenne</th>
  <th class="nombre">Abandons</th><th class="nombre">Conseils</th>
  <th class="nombre">Conseils serrés</th><th class="nombre">Dispersion</th>
  <th class="nombre">Domination</th><th class="nombre">Colliers</th>
</tr></thead>
<tbody>
{% for x in s.indicateurs.saisons %}{% unless x.speciale or x.en_cours %}
  {%- assign meta = "" -%}
  {%- for y in s.saisons -%}{%- if y.numero == x.numero and y.speciale != true -%}{%- assign meta = y -%}{%- endif -%}{%- endfor -%}
<tr>
  <td class="nombre">{{ x.numero }}</td>
  <td>{{ x.titre }} <small>({{ x.annee }})</small></td>
  <td class="nombre">{{ meta.effectif }}</td>
  <td class="nombre">{{ meta.age_moyen }}</td>
  <td class="nombre">{{ meta.part_femmes }} %</td>
  <td class="nombre" data-val="{{ x.survie_moyenne }}">{{ x.survie_moyenne }} %
    <span class="cellule-barre" style="width: {{ x.survie_moyenne }}%"></span></td>
  <td class="nombre">{{ x.taux_abandon }} %</td>
  <td class="nombre">{{ x.conseils }}</td>
  <td class="nombre">{% if x.tension_conseils %}{{ x.tension_conseils }} %{% else %}—{% endif %}</td>
  <td class="nombre">{% if x.dispersion_votes %}{{ x.dispersion_votes }}{% else %}—{% endif %}</td>
  <td class="nombre">{% if x.domination_epreuves %}{{ x.domination_epreuves }}{% else %}—{% endif %}</td>
  <td class="nombre">{{ x.colliers }}</td>
</tr>
{% endunless %}{% endfor %}
</tbody>
</table>
</div>

<p class="note">Un tiret signale une saison dont les sources ne permettent pas
de calculer l’indicateur : pas de bilan d’épreuves, ou trop peu de conseils au
dépouillement complet.</p>

## Composition du casting

{% include graphiques/saisons-femmes.svg %}

<p class="legende-figure">Part de femmes au départ de chaque saison classique.
La production vise l’équilibre : l’écart à 50 % tient au plus à un ou deux
aventuriers.</p>
