---
layout: page
espace: articles
title: Les articles
permalink: /articles/
description: "Les articles de Koh-Lanta en chiffres : ce que 34 saisons de votes permettent d'écrire sur les alliances, la menace et l'appartenance."
chapeau: "Le côté **Données** du site présente les chiffres. Ici, on s'en sert : chaque article s'appuie sur eux, et renvoie vers les pages où ils sont établis."
---

{%- comment -%}
  La liste vient de _data/navigation.yml, section `espace: articles` : un
  article ajoute au rail apparait ici sans autre ligne a ecrire.
{%- endcomment -%}
<ul class="cartes cartes-articles">
{%- for groupe in site.data.navigation -%}
{%- if groupe.espace == "articles" -%}
{%- for e in groupe.entrees -%}
{%- unless e.hub -%}
  <li class="carte">
    <a href="{{ e.url | relative_url }}">
      {%- assign quand = site.data.stats.articles.dates[e.url] -%}
      <span class="carte-rang">
        {%- if quand %}{{ quand.texte }}{% endif -%}
        {%- if quand and e.version %} · {% endif -%}
        {%- if e.version %}{{ e.version }}{% endif -%}
      </span>
      <span class="carte-titre">{{ e.titre }}</span>
      <span class="carte-resume">{{ e.resume }}</span>
    </a>
  </li>
{%- endunless -%}
{%- endfor -%}
{%- endif -%}
{%- endfor -%}
</ul>
