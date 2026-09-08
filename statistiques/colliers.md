---
layout: page
title: Les colliers d’immunité
description: "Les colliers d’immunité de Koh-Lanta suivis un par un : où ils étaient cachés, qui les a trouvés, et ce qu’ils ont réellement changé au conseil."
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

## Qui les trouve, qui les joue, qui en tire quelque chose

Trois comptes, et c’est le troisième qui vaut : **trouver un collier n’est pas
le jouer, et le jouer n’est pas annuler des voix.**

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Aventurier</th><th class="nombre">Trouvés</th><th class="nombre">Joués</th><th class="nombre">Annulations efficaces</th></tr></thead>
<tbody>
{% for x in c.palmares %}
<tr><td><strong>{% include lien-aventurier.html id=x.id nom=x.nom %}</strong></td>
    <td class="nombre">{{ x.trouves }}</td>
    <td class="nombre">{{ x.joues }}</td>
    <td class="nombre">{{ x.efficaces }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p><b>{{ c.porteurs }} aventuriers</b> se partagent les
  {{ c.colliers_attribues }} colliers attribués : personne ou presque n’en
  trouve plusieurs, et <b>{{ c.palmares[0].nom }}</b> est le seul à faire
  {{ c.palmares[0].trouves }} sur {{ c.palmares[0].trouves }} — trouvés, joués,
  et efficaces à chaque fois.</p>
</div>

### Éliminé avec le collier dans la poche

{% assign perdus = c.elimines_avec_collier %}
La catégorie la plus cruelle du tableau : l’avoir trouvé, ne pas l’avoir joué,
et partir quand même. Elle compte **{{ perdus | size }} cas**.

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Aventurier</th><th>Saison</th><th class="nombre">Année</th></tr></thead>
<tbody>
{% for x in perdus %}
<tr><td>{% include lien-aventurier.html id=x.id nom=x.nom %}</td><td>{{ x.titre }}</td><td class="nombre">{{ x.annee }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note"><strong>Ce palmarès n’est pas un palmarès de carrière.</strong>
Les colliers ne sont relevés que sur <b>{{ c.saisons_couvertes }} saisons</b>.
Un aventurier absent de ce tableau n’en a pas forcément jamais trouvé : il a
peut-être joué là où la source ne dit rien. Claude Dartois, premier du
<a href="{{ '/statistiques/top/' | relative_url }}">classement des joueurs</a>,
en est un exemple — une seule de ses quatre saisons est couverte ici, et il n’y
apparaît pas. C’est pour cette raison exactement que les colliers ne sont pas
une facette de ce classement.</p>

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

## Ce que les bulletins savent que ce tableau ignore

{% assign co = site.data.stats.conseils %}

Le tableau ci-dessus suit la **vie d’un objet** : où il était caché, qui l’a
trouvé, ce qu’il en a fait. Cette information n’existe que sur
{{ c.saisons_couvertes }} saisons. Mais il reste une trace ailleurs : dans la
matrice des votes, une voix annulée par un objet est **barrée**. Et cette
trace-là existe sur {{ co.saisons_avec_objet_joue }} saisons.

<div class="constat">
  <p><b>{{ co.conseils_avec_objet_joue }} conseils</b> portent la marque d’un
  objet d’immunité joué, sur {{ co.saisons_avec_objet_joue }} saisons —
  {{ co.voix_annulees_par_objet }} voix effacées.</p>
  <p>Quand un seul aventurier est protégé — les
  {{ co.objet_un_seul_protege }} cas où l’on sache qui l’objet couvrait — il
  reste en jeu <b>{{ co.objet_a_sauve }} fois sur
  {{ co.objet_un_seul_protege }}</b>. Un objet joué au bon conseil ne rate
  jamais.</p>
  <p>Le vrai problème n’est donc pas l’efficacité de l’objet, c’est la
  décision : {{ c.jamais_trouves }} colliers n’ont jamais été trouvés, et
  beaucoup de ceux qui l’ont été sont partis avec leur détenteur, dans la
  poche.</p>
</div>

<p class="note">Attention à ne pas confondre deux marques identiques.
Lorsque <em>tous</em> les bulletins d’un conseil sont barrés, ce n’est pas un
objet : c’est le tour entier qui est nul, une égalité suivie d’un second vote.
Ce cas-là pèse {{ co.voix_annulees_tour_nul }} voix sur
{{ co.conseils_tour_nul }} conseils, et il était compté avec les colliers
jusqu’à cette version du site. <a href="{{ '/statistiques/conseils/' | relative_url }}">Les
conseils</a> détaillent la distinction.</p>
