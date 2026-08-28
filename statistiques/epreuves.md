---
layout: page
title: Les épreuves
permalink: /statistiques/epreuves/
chapeau: >-
  Les meilleurs ratios, les totaux de carrière, et le profil qui domine vraiment — âge, métier, sexe.
---

{% assign e = site.data.stats.epreuves %}

C’est la question qui revient le plus souvent, et celle sur laquelle circulent
le plus de chiffres invérifiables : **qui domine les épreuves ?**

**{{ e.epreuves }} épreuves** ont été relevées sur **{{ e.saisons_couvertes }}
saisons** — {{ e.immunites }} d’immunité, {{ e.conforts }} de confort ;
{{ e.collectives }} remportées par une tribu, {{ e.individuelles }} par une
personne.

<ul class="chiffres">
  <li class="chiffre"><b>{{ e.epreuves }}</b><span>épreuves relevées</span></li>
  <li class="chiffre"><b>{{ e.individuelles }}</b><span>individuelles</span></li>
  <li class="chiffre"><b>{{ e.collectives }}</b><span>collectives</span></li>
  <li class="chiffre"><b>{{ e.saisons_couvertes }}</b><span>saisons couvertes sur 34</span></li>
</ul>

## Le classement des ratios

<p class="note">Le dénominateur n’est pas le nombre d’épreuves de la saison,
mais celui des épreuves individuelles <strong>disputées avant sa sortie</strong> :
un aventurier éliminé au jour 9 n’a pas rendez-vous avec les épreuves du jour
30. Un seuil de {{ e.seuil_classement }} épreuves disputées écarte les
parcours trop courts, où une seule victoire suffirait à afficher un ratio
spectaculaire. {{ e.classement_effectif }} aventuriers passent ce seuil.</p>

{% include graphiques/epreuves-ratios.svg %}

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th class="nombre">#</th><th>Aventurier</th><th>Saison</th>
  <th class="nombre">Gagnées</th><th class="nombre">Disputées</th><th class="nombre">Ratio</th>
</tr></thead>
<tbody>
{% for x in e.classement_ratio %}
<tr>
  <td class="nombre">{{ forloop.index }}</td>
  <td><strong>{{ x.personne }}</strong></td>
  <td>{{ x.titre }} ({{ x.annee }}){% if x.speciale %} <em>— édition spéciale</em>{% endif %}</td>
  <td class="nombre">{{ x.gagnees }}</td>
  <td class="nombre">{{ x.disputees }}</td>
  <td class="nombre">{{ x.ratio }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Les totaux d’une carrière

Le ratio récompense l’efficacité sur une saison. Le cumul, lui, récompense la
longévité : revenir jouer quatre ou cinq fois donne quatre ou cinq fois plus
d’occasions.

{% include graphiques/epreuves-cumuls.svg %}

**{{ e.meilleurs_cumuls[0].personne }}** est en tête avec
**{{ e.meilleurs_cumuls[0].victoires }} victoires individuelles**, devant
{{ e.meilleurs_cumuls[1].personne }} ({{ e.meilleurs_cumuls[1].victoires }}).
Les deux comptent parmi les aventuriers les plus rappelés du programme : leur
total dit autant leur nombre de participations que leur niveau.

## Quel profil gagne les épreuves

C’est ici que les données deviennent intéressantes, parce qu’elles contredisent
ce que la page sur les [métiers]({{ '/statistiques/professions/' | relative_url }})
laissait entendre.

{% include graphiques/epreuves-metier.svg %}

<p class="legende-figure">Nombre moyen d’épreuves individuelles remportées par
aventurier de chaque famille — rapporté à l’effectif, donc comparable.</p>

**{{ e.par_metier[0].libelle }}** arrive en tête avec
{{ e.par_metier[0].victoires_par_aventurier }} victoire par personne. Rien de
surprenant. Mais le fait notable est ailleurs : cette domination athlétique
**ne se convertit pas en victoires finales**. Le sport gagne les épreuves et
perd le jury.

{% include graphiques/epreuves-age.svg %}

L’âge trace une courbe nette : les **25-34 ans** remportent environ une épreuve
par personne, les **45 ans et plus** trois fois moins. C’est le seul domaine où
l’âge pèse aussi franchement — et il éclaire la page
[longévité]({{ '/statistiques/longevite/' | relative_url }}) : si les plus âgés
sortent plus tôt, c’est d’abord qu’ils gagnent moins d’immunités.

{% include graphiques/epreuves-genre.svg %}

L’écart entre femmes et hommes est le plus marqué de tout ce site :
**{{ e.par_genre[1].victoires_par_aventurier }}** épreuve par aventurier contre
**{{ e.par_genre[0].victoires_par_aventurier }}** par aventurière, sur des
effectifs pourtant identiques. Rapproché du fait que les deux gagnent la finale
aussi souvent, cela dit une chose simple : **la domination sportive n’est pas
ce qui fait gagner Koh-Lanta.**

## Gagner la première mène-t-il plus loin ?

{% assign pe = site.data.stats.premiere_epreuve %}
La première épreuve individuelle d’une saison marque le début du jeu personnel.
Celui qui la remporte tient en moyenne **{{ pe.survie_gagnants }} %** de la
saison, contre **{{ pe.survie_ensemble }} %** pour l’ensemble des aventuriers.

L’écart est réel, et il est modeste : neuf points. Surtout, il repose sur
**{{ pe.effectif }} cas seulement** — une saison ne fournit qu’une première
épreuve individuelle, et {{ pe.saisons_couvertes }} saisons en ont une de
relevée. À cette taille, l’écart resterait compatible avec le hasard : il est
donné pour ce qu’il est, une indication, pas une loi.

## Ce que cette page ne dit pas

**Cinq saisons manquent** — {{ e.saisons_sans_donnee | join: ", " }} — faute de
source donnant leurs épreuves épisode par épisode. Les totaux et les ratios
portent donc sur {{ e.saisons_couvertes }} saisons, pas sur les 34.

**Les épreuves de finale sont exclues.** Dans les dernières émissions, les
tableaux sources changent de colonnes et y listent les qualifiés plutôt que le
vainqueur : les lire comme des victoires en fabriquerait de fausses. Orientation
et poteaux ne sont donc pas comptés.

**La nature des épreuves n’est pas connue** — endurance, équilibre, précision,
aquatique. Les sources ne la donnent pas de façon exploitable. Tant qu’elle
manquera, aucune analyse par type d’épreuve ne figurera ici.
