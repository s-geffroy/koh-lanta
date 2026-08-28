---
layout: page
title: Les aventuriers
permalink: /aventuriers/
chapeau: >-
  Toutes les participations relevées, saison par saison. Le tableau se
  cherche, se filtre et se trie.
---

{% assign g = site.data.stats.general %}

Les **{{ g.participations }} participations** relevées, toutes saisons
confondues. {{ g.personnes }} personnes différentes : la différence tient aux
{{ site.data.stats.records.nb_multi_participants }} aventuriers revenus jouer
une ou plusieurs fois.

<div class="filtres" data-filtre="tableau-aventuriers">
  <div class="champ">
    <label for="q">Chercher un nom, un métier, une tribu</label>
    <input type="search" id="q" data-role="texte" placeholder="Teheiura, plombier, Ratanak…" autocomplete="off">
  </div>

  <div class="champ">
    <label for="f-saison">Saison</label>
    <select id="f-saison" data-champ="saison">
      <option value="">Toutes</option>
      {%- for x in site.data.saisons -%}
      {%- unless x.annulee -%}
      <option value="{{ x.id }}">{{ x.titre }} ({{ x.annee }})</option>
      {%- endunless -%}
      {%- endfor -%}
    </select>
  </div>

  <div class="champ">
    <label for="f-sort">Manière de sortir</label>
    <select id="f-sort" data-champ="sort">
      <option value="">Toutes</option>
      <option value="vainqueur">Vainqueur</option>
      <option value="finaliste">Finaliste</option>
      <option value="elimine_conseil">Éliminé au conseil</option>
      <option value="elimine_poteaux">Éliminé aux poteaux</option>
      <option value="elimine_orientation">Éliminé à l’orientation</option>
      <option value="elimine_ambassadeurs">Éliminé par les ambassadeurs</option>
      <option value="elimine_duel">Éliminé en duel</option>
      <option value="abandon_medical">Abandon médical</option>
      <option value="abandon_volontaire">Abandon volontaire</option>
    </select>
  </div>

  <button type="button" class="bascule" data-role="vider">Tout effacer</button>
  <p class="compte" data-role="compte" aria-live="polite"></p>
</div>

<p class="note">Cliquez sur un en-tête pour trier le tableau sur cette colonne.
Sans JavaScript, la recherche et les filtres disparaissent, mais le tableau
reste entier et lisible, dans l’ordre chronologique des saisons puis de
sortie.</p>

<div class="tableau-large tableau-haut">
<table id="tableau-aventuriers" data-triable>
<thead><tr>
  <th>Aventurier</th><th>Saison</th><th class="nombre">Année</th>
  <th class="nombre">Âge</th><th>Sexe</th><th>Métier</th>
  <th>Tribu</th><th class="nombre">Jour de sortie</th><th>Sortie</th>
</tr></thead>
<tbody>
{% assign saisons = site.data.saisons %}
{% for p in site.data.participations %}
  {% assign sa = "" %}
  {% for x in saisons %}{% if x.id == p.saison %}{% assign sa = x %}{% endif %}{% endfor %}
<tr data-saison="{{ p.saison }}" data-sort="{{ p.sort }}">
  <td>{{ p.nom_complet | default: p.nom }}</td>
  <td>{{ sa.titre }}</td>
  <td class="nombre">{{ sa.annee }}</td>
  <td class="nombre">{{ p.age }}</td>
  <td>{% if p.genre == "f" %}F{% elsif p.genre == "h" %}H{% endif %}</td>
  <td>{{ p.profession }}</td>
  <td>{% if p.couleur %}<span class="pastille" style="background: var(--tribu-{{ p.couleur }})"></span>{% endif %}{{ p.tribu }}</td>
  <td class="nombre">{{ p.jour_sortie }}</td>
  <td>{{ p.motif }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
