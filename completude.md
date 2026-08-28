---
layout: page
title: La carte des trous
permalink: /completude/
chapeau: >-
  Une ligne par édition, une colonne par type de donnée, et à l’intersection ce
  qu’on sait vraiment. C’est la carte de ce qui manque.
---

{% assign c = site.data.stats.completude_saisons %}

Chaque page de ce site dit ce qui lui manque. Aucune ne le montrait d’un coup
d’œil. Voici la grille complète : **{{ c.saisons }} éditions** en ligne,
**{{ c.colonnes | size }} types de données** en colonne,
{{ c.cases }} croisements renseignés.

<div class="constat">
  <p>Toutes cases confondues, le jeu de données est rempli à
  <b>{{ c.moyenne }} %</b>.</p>
  {%- assign top = c.lignes | where: "saison", c.meilleure | first -%}
  {%- assign bas = c.lignes | where: "saison", c.pire | first -%}
  <p>L’édition la mieux documentée est <i>{{ top.titre }}</i> ({{ top.annee }}),
  à <b>{{ top.score }} %</b> ; la moins bien, <i>{{ bas.titre }}</i>
  ({{ bas.annee }}), à {{ bas.score }} % — la saison en cours au moment de la
  construction, dont tout n’est pas encore connu.</p>
</div>

<ul class="legende-completude">
  <li data-etat="complet"><i></i> complet</li>
  <li data-etat="eleve"><i></i> 80 % et plus</li>
  <li data-etat="partiel"><i></i> 50 à 80 %</li>
  <li data-etat="mince"><i></i> moins de 50 %</li>
  <li data-etat="manquant"><i></i> rien</li>
  <li data-etat="sans_objet"><i></i> sans objet</li>
</ul>

<p class="note"><strong>« Sans objet » n’est pas « manquant ».</strong> Une
saison d’avant 2011 n’a pas de collier d’immunité : la case est hachurée, pas
vide. De même pour les éditions spéciales, dont la réunification n’est pas
mesurée, et pour les saisons sans ambassade. Confondre les deux ferait passer
une règle du jeu pour une lacune.</p>

<div class="tableau-large tableau-haut">
<table class="grille-completude">
<thead><tr>
  <th class="saison">Édition</th>
  {% for col in c.colonnes %}<th class="case-tete" title="{{ col.libelle }}">{{ col.court }}</th>{% endfor %}
  <th class="nombre">Ensemble</th>
</tr></thead>
<tbody>
{% for l in c.lignes %}
<tr>
  <td class="saison">
    <b>{{ l.titre }}</b>
    <small>{% if l.numero %}saison {{ l.numero }}{% else %}édition spéciale{% endif %} · {{ l.annee }} · {{ l.pays }}</small>
  </td>
  {% for x in l.cellules %}
  <td class="case" data-etat="{{ x.etat }}" title="{{ l.titre }} — {{ x.texte }}"><span>{% if x.etat == "sans_objet" %}·{% elsif x.nature == "fait" %}{% if x.etat == "complet" %}✓{% else %}—{% endif %}{% else %}{{ x.valeur | round }}{% endif %}</span></td>
  {% endfor %}
  <td class="nombre">{{ l.score }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Survolez une case pour lire le détail : « 16/16 », « 8 relevées »,
« non nommés ». Les colonnes marquées d’une coche sont des faits — la donnée
existe ou n’existe pas ; les autres portent une part.</p>

## Ce que la grille montre en colonnes

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Type de donnée</th><th class="nombre">Moyenne</th>
  <th class="nombre">Éditions complètes</th><th class="nombre">Concernées</th>
</tr></thead>
<tbody>
{% for col in c.par_colonne %}
<tr>
  <td>{{ col.libelle }}</td>
  <td class="nombre" data-val="{{ col.moyenne }}">{{ col.moyenne }} %</td>
  <td class="nombre">{{ col.completes }}</td>
  <td class="nombre">{{ col.concernees }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Trois lectures se détachent.

**Ce qui est acquis.** Le casting, l’âge et le métier sont complets sur les
{{ c.saisons }} éditions. Le jour de sortie et les voix reçues n’ont plus qu’une
poignée de trous. Ce socle-là ne bougera plus.

**Ce qui dépend d’une seule source.** Le rang final et le palmarès d’épreuves
n’existent que par les fiches individuelles du wiki ; ils manquent partout où la
fiche manque, c’est-à-dire sur les castings les plus anciens et l’édition de
célébrités. [Les sources]({{ '/sources/' | relative_url }}) détaillent.

**Ce qui restera mince.** Le dépouillement complet des conseils plafonne : la
moitié des conseils n’annonce même pas combien de voix ont été exprimées, si
bien que leur complétude n’est pas vérifiable. C’est la colonne la plus basse de
la grille, et c’est aussi celle dont dépendent les résultats les plus forts du
site — [les alliances]({{ '/statistiques/alliances/' | relative_url }}),
[qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}).

## Comment lire une ligne

Une édition bien remplie ne garantit rien : la grille dit ce qu’on **a**, pas ce
qu’on peut en **conclure**. Une saison à 95 % dont les conseils ne sont pas
dépouillés ne sert à aucune analyse de vote. Inversement, une saison à 70 % dont
les bulletins sont complets vaut beaucoup pour
[les alliances]({{ '/statistiques/alliances/' | relative_url }}).

<p class="note"><strong>Deux éditions annulées</strong> — celles de 2013 et de
2018, interrompues en tournage — ne figurent pas dans la grille : elles n’ont ni
casting complet ni résultat, et les compter à zéro fausserait toutes les
moyennes.</p>
