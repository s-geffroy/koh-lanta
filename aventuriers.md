---
layout: page
title: Les aventuriers de Koh-Lanta
description: "Les 645 participations à Koh-Lanta, saison par saison : durée, épreuves, votes, manière de sortir. Un tableau qui se cherche, se filtre et se trie."
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

<p class="note">Ce tableau décrit <strong>une aventure à la fois</strong> :
qui, où, quand, jusqu’à quel jour. Il ne dit pas comment on a joué. Pour cela,
<a href="{{ '/statistiques/top/' | relative_url }}">le classement des
joueurs</a> range les
{{ site.data.stats.classement.joueurs_classes }} aventuriers sur quatre
facettes — aller loin, gagner les épreuves, n’être pas visé au conseil, écrire
le nom de celui qui part — et il se cherche de la même façon.</p>

<div class="filtres" data-filtre="tableau-aventuriers">
  <div class="champ">
    <label for="q">Chercher un nom, un métier, une tribu, un département</label>
    <input type="search" id="q" data-role="texte" placeholder="Ugo Lartiche, plombier, Ratanak, Gironde…" autocomplete="off">
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

<p class="note"><strong>Chaque nom est une fiche</strong>, et chaque titre de
saison aussi. La fiche d’un aventurier rassemble ses saisons, sa place sur les
quatre facettes du classement et ce qu’on sait de ses conseils ; celle d’une
saison donne son casting entier, ses conseils et son audience.</p>

<p class="note">Cliquez sur un en-tête pour trier le tableau sur cette colonne.
Sans JavaScript, la recherche et les filtres disparaissent, mais le tableau
reste entier et lisible, dans l’ordre chronologique des saisons puis de
sortie.</p>

<p class="note"><strong>Rang et épreuves gagnées</strong> viennent des fiches
individuelles du wiki Fandom, qui sont les seules à les porter : ils manquent
donc là où la fiche manque. Le palmarès y compte tout ce que le wiki appelle une
victoire — duels de l’île des bannis et épreuves de finale compris — là où
<a href="{{ '/statistiques/epreuves/' | relative_url }}">la page des épreuves</a>
ne compte que ce qui figure au bilan épisode par épisode. Les deux comptes sont
identiques dans sept cas sur dix ; <a href="{{ '/sources/' | relative_url }}">Les
sources</a> disent pourquoi pas dans les trois autres.</p>

<div class="tableau-large tableau-haut">
<table id="tableau-aventuriers" data-triable>
<thead><tr>
  <th>Aventurier</th><th>Saison</th><th class="nombre">Année</th>
  <th class="nombre">Âge</th><th>Sexe</th><th>Métier</th>
  <th>Origine</th><th>Tribu</th><th class="nombre">Jour de sortie</th>
  <th class="nombre">Rang</th><th class="nombre">Épreuves gagnées</th><th>Sortie</th>
</tr></thead>
<tbody>
{% assign saisons = site.data.saisons %}
{% for p in site.data.participations %}
  {% assign sa = "" %}
  {% for x in saisons %}{% if x.id == p.saison %}{% assign sa = x %}{% endif %}{% endfor %}
<tr data-saison="{{ p.saison }}" data-sort="{{ p.sort }}">
  <td><a href="{{ '/aventuriers/' | append: p.id | append: '/' | relative_url }}">{{ p.nom_complet | default: p.nom }}</a></td>
  <td><a href="{{ '/saisons/' | append: p.saison | append: '/' | relative_url }}">{{ sa.titre }}</a></td>
  <td class="nombre">{{ sa.annee }}</td>
  <td class="nombre">{{ p.age }}</td>
  <td>{% if p.genre == "f" %}F{% elsif p.genre == "h" %}H{% endif %}</td>
  <td>{{ p.profession }}</td>
  <td>{{ p.localisation }}</td>
  <td>{% if p.couleur %}<span class="pastille" style="background: var(--tribu-{{ p.couleur }})"></span>{% endif %}{{ p.tribu }}</td>
  <td class="nombre">{{ p.jour_sortie }}</td>
  <td class="nombre">{{ p.classement }}</td>
  <td class="nombre"{% if p.victoires_individuelles %} data-val="{{ p.victoires_individuelles }}"{% endif %}>{% if p.victoires_individuelles %}{{ p.victoires_individuelles }} ind.{% if p.victoires_collectives %} · {{ p.victoires_collectives }} coll.{% endif %}{% endif %}</td>
  <td>{{ p.motif }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Une même personne revient ici autant de fois qu’elle a joué :
c’est un tableau de <strong>participations</strong>, pas de personnes. Le
<a href="{{ '/statistiques/top/' | relative_url }}">classement des joueurs</a>
fait l’inverse — une ligne par aventurier, ses saisons cumulées, et son rang
sur chacune des quatre facettes.</p>
