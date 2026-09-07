---
layout: page
title: Le profil du vainqueur
permalink: /statistiques/vainqueurs/
chapeau: >-
  Ce que les vainqueurs ont en commun : un âge bien plus large qu’on ne le croit, une parité presque parfaite, aucune couleur de tribu gagnante — et un nom que, souvent, personne n’a jamais écrit.
---

{% assign s = site.data.stats %}
{% assign v = s.vainqueurs %}

Il y a **{{ v.effectif }} vainqueurs** sur les saisons classiques achevées —
plus que de saisons, parce que trois éditions se sont terminées sur une égalité
des voix du jury et ont sacré deux personnes.

<ul class="chiffres">
  <li class="chiffre"><b>{{ v.age_moyen }} ans</b><span>âge moyen</span></li>
  <li class="chiffre"><b>{{ v.age_median }} ans</b><span>âge médian</span></li>
  <li class="chiffre"><b>{{ v.age_min }} – {{ v.age_max }}</b><span>du plus jeune au plus âgé</span></li>
  <li class="chiffre"><b>{{ v.part_40_et_plus }} %</b><span>ont 40 ans ou plus</span></li>
</ul>

## L’âge

{% include graphiques/vainqueurs-age.svg %}

La moyenne dit **{{ v.age_moyen }} ans**, la médiane **{{ v.age_median }}** : la
distribution est donc à peu près symétrique, sans poignée de vétérans tirant le
chiffre vers le haut. Mais elle est aussi **large**. Les extrêmes le montrent
mieux qu’une moyenne :

- le plus jeune vainqueur, **{{ s.records.plus_jeune_vainqueur.nom }}**, avait
  **{{ s.records.plus_jeune_vainqueur.age }} ans** ({{ s.records.plus_jeune_vainqueur.titre }},
  {{ s.records.plus_jeune_vainqueur.annee }}) ;
- la plus âgée, **{{ s.records.plus_age_vainqueur.nom }}**, en avait
  **{{ s.records.plus_age_vainqueur.age }}** ({{ s.records.plus_age_vainqueur.titre }},
  {{ s.records.plus_age_vainqueur.annee }}).

Trente et un ans d’écart entre les deux. **{{ v.part_40_et_plus }} %** des
vainqueurs ont quarante ans ou plus : l’idée d’un jeu réservé aux jeunes corps
ne tient pas devant les chiffres.

## Le sexe

<div class="tableau-large">
<table data-triable>
<thead><tr><th>&nbsp;</th><th class="nombre">Vainqueurs</th><th class="nombre">Part</th></tr></thead>
<tbody>
{% for x in v.par_genre %}
<tr><td>{{ x.libelle }}</td><td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.part }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

La parité est presque parfaite — et elle est plus remarquable qu’il n’y paraît :
comme on le verra sur la page consacrée à la [longévité]({{ '/statistiques/longevite/' | relative_url }}),
les femmes quittent le jeu **plus tôt** que les hommes en moyenne. Elles gagnent
donc autant en tenant moins longtemps.

## Le métier

{% include graphiques/vainqueurs-metier.svg %}

Aucune famille de métiers n’écrase les autres. Les trois premières —
encadrement, commerce, sport — pèsent {{ v.par_metier[0].part }} % chacune, et
ce sont aussi les mieux représentées dans le casting : leur avantage tient
largement à leur nombre au départ, pas à une supériorité.

## La couleur de tribu

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Tribu de départ</th><th class="nombre">Victoires</th><th class="nombre">Part</th></tr></thead>
<tbody>
{% for c in v.par_couleur %}
<tr>
  <td><span class="pastille" style="background: var(--tribu-{{ c.couleur }})"></span>{{ c.couleur | capitalize }}</td>
  <td class="nombre">{{ c.effectif }}</td>
  <td class="nombre">{{ c.part }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Jaune et rouge sont **à égalité parfaite**. Le sujet a sa propre page :
[jaune contre rouge]({{ '/statistiques/tribus/' | relative_url }}).

## Les voix reçues

{% assign vv = s.indicateurs.voix_des_vainqueurs %}
{% assign cr = vv.couples_resume %}

Le vainqueur est-il celui que personne n’a vu venir ? La question se pose au
bulletin : sur toute sa saison, combien de fois son nom a-t-il été écrit ?

<ul class="chiffres">
  <li class="chiffre"><b>{{ vv.total }}</b><span>voix reçues, à eux {{ vv.effectif }}</span></li>
  <li class="chiffre"><b>{{ vv.moyenne }}</b><span>voix par vainqueur en moyenne</span></li>
  <li class="chiffre"><b>{{ vv.sans_aucune_voix }}</b><span>n’ont jamais été écrits</span></li>
  <li class="chiffre"><b>{{ vv.maximum }}</b><span>le maximum, sur une saison</span></li>
</ul>

{% include graphiques/vainqueurs-voix.svg %}

<p class="legende-figure">Nombre de vainqueurs par nombre total de voix reçues
sur l’ensemble de leur saison. Le repère est la moyenne des finalistes, seul
groupe à avoir traversé les mêmes conseils.</p>

<div class="constat">
  <p><b>{{ vv.part_sans_voix }} % des vainqueurs n’ont jamais reçu une seule
  voix</b> — {{ vv.sans_aucune_voix }} sur {{ vv.effectif }} :
  {% for x in vv.jamais_ecrits %}{{ x.nom }} ({{ x.annee }}){% unless forloop.last %}, {% endunless %}{% endfor %}.</p>
  <p>Mais l’inverse existe aussi, et il est récent. Le record est de
  <b>{{ vv.maximum }} voix</b> :
  {% for x in vv.records %}{{ x.nom }} ({{ x.titre }}, {{ x.annee }}){% unless forloop.last %}, {% endunless %}{% endfor %}.
  On peut donc gagner en ayant été la cible désignée d’un camp entier.</p>
</div>

## Un chiffre qui se compare mal

{% include graphiques/vainqueurs-menace.svg %}

<p class="legende-figure">Voix reçues rapportées au nombre de conseils
traversés — l’indicateur <em>menace</em> de la page
<a href="{{ '/statistiques/jeu-social/' | relative_url }}">Le jeu social</a>.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>&nbsp;</th><th class="nombre">Effectif</th><th class="nombre">Voix en moyenne</th>
  <th class="nombre">Parcours mesurables</th><th class="nombre">Voix par conseil</th>
</tr></thead>
<tbody>
{% for g in vv.par_sort %}
<tr><td>{{ g.libelle }}</td>
    <td class="nombre">{{ g.effectif }}</td>
    <td class="nombre">{{ g.voix_moyennes }}</td>
    <td class="nombre">{{ g.mesures }}</td>
    <td class="nombre">{{ g.menace_moyenne }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

La dernière colonne ne se calcule qu’au-delà de quatre conseils traversés :
c’est pourquoi son effectif est plus court que le premier, et c’est lui qu’il
faut lire.

{{ vv.par_sort[0].menace_moyenne }} voix par conseil contre
{{ vv.par_sort[2].menace_moyenne }} pour l’ensemble du casting : plus de quatre
fois moins. **L’écart est spectaculaire, et il ne prouve à peu près rien.** On
ne gagne pas si l’on est sorti, et l’on sort quand on est écrit : être peu visé
et aller au bout sont deux faces du même fait. Comparer un vainqueur à
quelqu’un parti au troisième conseil, c’est comparer un survivant à ceux qui
n’ont pas survécu.

## La seule comparaison qui tienne : le finaliste

Le finaliste a traversé **exactement les mêmes conseils** que le vainqueur, et
il a perdu. Si être discret fait gagner, l’écart doit se voir là.

Une ligne par couple vainqueur-finaliste : les saisons qui ont sacré deux
personnes en donnent donc deux, et celles dont le finaliste manque n’en donnent
aucune.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Saison</th><th class="nombre">Année</th>
  <th>Vainqueur</th><th class="nombre">Voix</th>
  <th>Finaliste</th><th class="nombre">Voix</th>
</tr></thead>
<tbody>
{% for x in vv.couples %}
<tr>
  <td>{{ x.titre }}</td><td class="nombre">{{ x.annee }}</td>
  <td>{{ x.vainqueur }}</td><td class="nombre" data-val="{{ x.voix_vainqueur }}"><b>{{ x.voix_vainqueur }}</b></td>
  <td>{{ x.finaliste }}</td><td class="nombre">{{ x.voix_finaliste }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p>En moyenne, <b>{{ cr.moyenne_vainqueur }} voix pour le vainqueur contre
  {{ cr.moyenne_finaliste }} pour le finaliste</b>. L’écart va dans le sens
  attendu, et il est du simple au double.</p>
  <p>Mais compté couple par couple, il fond : le vainqueur est le moins visé
  dans <b>{{ cr.vainqueur_moins_vise }} cas sur {{ cr.effectif }}</b>,
  contre {{ cr.vainqueur_plus_vise }} fois l’inverse et {{ cr.egalite }}
  égalités. <b>Ce n’est pas une démonstration</b> — c’est ce qu’on attendrait
  d’une pièce un peu biseautée, et sur si peu de saisons on ne saurait pas la
  distinguer d’une pièce honnête.</p>
</div>

<p class="note"><b>Aucun test n’est déclaré ici.</b> Les tests publiés par ce
site sont annoncés d’avance et corrigés ensemble par Benjamini-Hochberg
(<a href="{{ '/methode/' | relative_url }}">la méthode</a>) : en ajouter un
déplacerait les p ajustées de tous les autres, pour une comparaison que cette
page présente elle-même comme non concluante. Le tableau est là pour qu’on
puisse la refaire.</p>

<p class="note">Le total des voix vient du tableau des candidats, qui le donne
pour la saison entière — et non de la somme des conseils dépouillés, qui n’en
couvrent qu’une partie ; <a href="{{ '/completude/' | relative_url }}">la
complétude</a> dit laquelle. Une voix annulée par un collier compte ici comme
une voix reçue : elle dit que le nom a été écrit, ce qui est la question posée.</p>
