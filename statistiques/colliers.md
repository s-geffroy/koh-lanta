---
layout: page
title: Les colliers d’immunité
permalink: /statistiques/colliers/
chapeau: >-
  Chaque collier d’immunité suivi un par un : où il était caché, qui l’a trouvé, et ce qu’il a réellement changé au conseil.
---

{% assign c = site.data.stats.colliers %}

Le collier d’immunité est apparu en 2011 et n’a plus quitté le jeu. C’est aussi
la mécanique sur laquelle circulent le plus d’affirmations invérifiables. Le
destin de **{{ c.colliers }} colliers** a été relevé sur
{{ c.saisons_couvertes }} saisons : où ils étaient cachés, qui les a trouvés,
s’ils ont servi, et combien de voix ils ont annulées.

<ul class="chiffres">
  <li class="chiffre"><b>{{ c.colliers }}</b><span>colliers suivis</span></li>
  <li class="chiffre"><b>{{ c.jamais_trouves }}</b><span>jamais trouvés</span></li>
  <li class="chiffre"><b>{{ c.voix_annulees }}</b><span>voix annulées</span></li>
  <li class="chiffre"><b>{{ c.voix_par_collier_joue }}</b><span>voix par collier joué</span></li>
</ul>

## Ce que devient un collier

{% include graphiques/colliers-issues.svg %}

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Issue</th><th class="nombre">Colliers</th>
  <th class="nombre">Part du total</th><th class="nombre">Part de ceux trouvés</th>
</tr></thead>
<tbody>
{% for i in c.issues %}
<tr>
  <td>{{ i.libelle }}</td>
  <td class="nombre">{{ i.effectif }}</td>
  <td class="nombre">{{ i.part_totale }} %</td>
  <td class="nombre">{% if i.part_des_trouves %}{{ i.part_des_trouves }} %{% else %}—{% endif %}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

**Le dénominateur change tout.** Rapporté à l’ensemble des colliers cachés, le
« joué et efficace » ne pèse que {{ c.issues[0].part_totale }} %. Mais un
collier que personne n’a découvert n’est l’échec de personne : rapporté aux
seuls colliers **trouvés**, il monte à {{ c.issues[0].part_des_trouves }} %.
Les deux chiffres sont vrais, ils ne répondent pas à la même question.

## Trois enseignements

**Un collier sur trois est joué pour rien.**
{{ c.issues[1].part_des_trouves }} % des colliers trouvés sont sortis du sac
sans annuler la moindre voix — leur détenteur n’était pas visé. C’est la peur
qui a parlé, pas la lecture du jeu.

**Un sur sept part avec son propriétaire.** Éliminé au conseil, collier dans le
sac : {{ c.issues[3].part_des_trouves }} % des colliers trouvés connaissent ce
sort. C’est le scénario que tout aventurier redoute, et il est plus rare qu’on
ne le raconte.

**Quand il sert, il sert beaucoup.** Un collier joué efficacement annule en
moyenne **{{ c.voix_par_collier_joue }} voix**. Il ne renverse pas une voix : il
efface un paquet de bulletins d’un coup.

## Saison par saison

{% include graphiques/colliers-saison.svg %}

<p class="legende-figure">La production a nettement augmenté le nombre d’objets
en jeu sur les saisons récentes.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Saison</th><th class="nombre">Année</th><th class="nombre">Colliers</th>
  <th class="nombre">Joués</th><th class="nombre">Voix annulées</th>
</tr></thead>
<tbody>
{% for x in c.par_saison %}
<tr>
  <td>{{ x.titre }}</td><td class="nombre">{{ x.annee }}</td>
  <td class="nombre">{{ x.colliers }}</td><td class="nombre">{{ x.joues }}</td>
  <td class="nombre">{{ x.voix_annulees }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Cette page ne couvre que les <strong>colliers d’immunité</strong>.
Les autres objets — armes secrètes (2021), totem maudit (2022), talisman du feu
sacré (2023) — sont des mécaniques distinctes, avec leurs propres règles, et
n’entrent pas dans ces comptes. Les {{ c.saisons_couvertes }} saisons couvertes
sont celles dont les sources donnent le destin de chaque collier ; les autres
mentionnent des colliers sans les détailler.</p>
