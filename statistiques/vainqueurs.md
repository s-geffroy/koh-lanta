---
layout: page
title: Le profil du vainqueur
permalink: /statistiques/vainqueurs/
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

## L'âge

{% include graphiques/vainqueurs-age.svg %}

La moyenne dit **{{ v.age_moyen }} ans**, la médiane **{{ v.age_median }}** : la
distribution est donc à peu près symétrique, sans poignée de vétérans tirant le
chiffre vers le haut. Mais elle est aussi **large**. Les extrêmes le montrent
mieux qu'une moyenne :

- le plus jeune vainqueur, **{{ s.records.plus_jeune_vainqueur.nom }}**, avait
  **{{ s.records.plus_jeune_vainqueur.age }} ans** ({{ s.records.plus_jeune_vainqueur.titre }},
  {{ s.records.plus_jeune_vainqueur.annee }}) ;
- la plus âgée, **{{ s.records.plus_age_vainqueur.nom }}**, en avait
  **{{ s.records.plus_age_vainqueur.age }}** ({{ s.records.plus_age_vainqueur.titre }},
  {{ s.records.plus_age_vainqueur.annee }}).

Trente et un ans d'écart entre les deux. **{{ v.part_40_et_plus }} %** des
vainqueurs ont quarante ans ou plus : l'idée d'un jeu réservé aux jeunes corps
ne tient pas devant les chiffres.

## Le sexe

<div class="tableau-large">
<table>
<thead><tr><th>&nbsp;</th><th class="nombre">Vainqueurs</th><th class="nombre">Part</th></tr></thead>
<tbody>
{% for x in v.par_genre %}
<tr><td>{{ x.libelle }}</td><td class="nombre">{{ x.effectif }}</td><td class="nombre">{{ x.part }} %</td></tr>
{% endfor %}
</tbody>
</table>
</div>

La parité est presque parfaite — et elle est plus remarquable qu'il n'y paraît :
comme on le verra sur la page consacrée à la [longévité]({{ '/statistiques/longevite/' | relative_url }}),
les femmes quittent le jeu **plus tôt** que les hommes en moyenne. Elles gagnent
donc autant en tenant moins longtemps.

## Le métier

{% include graphiques/vainqueurs-metier.svg %}

Aucune famille de métiers n'écrase les autres. Les trois premières —
encadrement, commerce, sport — pèsent {{ v.par_metier[0].part }} % chacune, et
ce sont aussi les mieux représentées dans le casting : leur avantage tient
largement à leur nombre au départ, pas à une supériorité.

## La couleur de tribu

<div class="tableau-large">
<table>
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
