---
layout: page
title: "Le format des saisons depuis 2001"
titre: La grille
description: "Deux décisions que Koh-Lanta ne commente jamais : le jour où la production réunit les tribus, et la dérive de son format, qui n’a pas de date."
permalink: /statistiques/grille/
chapeau: >-
  Deux décisions que la production ne commente jamais : le jour où elle réunit
  les tribus, et la dérive de son format — qui n’a pas de date.
---

{% assign m = site.data.stats.modeles %}
{% assign f = m.fusion %}
{% assign r = m.ruptures %}

## La réunification tombe à une date, pas à un nombre de joueurs

C’est le geste le plus lourd d’une saison. Deux logiques peuvent le commander :
réunir quand il reste assez peu de monde pour que le jeu individuel commence —
une règle **de jeu** — ou réunir à un épisode fixe pour que la seconde moitié
tienne dans la grille — une règle **de programme**.

Les deux se distinguent, parce que la taille des castings a changé : de
{{ f.casting_min }} aux premières saisons à {{ f.casting_max }} aux récentes.

<p class="note"><strong>Comment on repère la réunification sans la deviner.</strong>
Après elle, les immunités sont individuelles. Le dernier épisode portant une
immunité <em>collective</em> est donc le dernier épisode d’avant la
réunification. {{ f.saisons }} saisons classiques s’y prêtent.</p>

{% include graphiques/fusion-grille.svg %}

<p class="legende-figure">Chaque saison figure deux fois : par l’épisode où la
réunification tombe, et par le nombre de joueurs qu’elle laisse en jeu.</p>


<div class="constat">
  <p>Quand le casting gagne un membre, l’épisode de la réunification recule en
  moyenne de <b>{{ f.pente_episode.pente }}</b> — intervalle
  {{ f.pente_episode.bas }} à {{ f.pente_episode.haut }}, p = {{ f.pente_episode.p }}. <b>L’intervalle contient zéro</b> : ce recul ne se
  distingue pas du hasard. Même pris tel quel, il ne ferait que
  {{ f.croissance_episode_texte }} sur toute la croissance observée, de
  {{ f.casting_min }} à {{ f.casting_max }} personnes.
  La médiane reste l’épisode {{ f.episode_median }}, de {{ f.annee_min }} à {{ f.annee_max }}.</p>
  <p>Le nombre de joueurs restants, lui, bouge de
  <b>{{ f.pente_restants.pente }}</b> ({{ f.pente_restants.bas }} à
  {{ f.pente_restants.haut }}) — soit
  <b>{{ f.croissance_restants }} joueurs</b> de
  plus sur la même croissance. Le casting grossit, le plateau réuni grossit
  avec lui, et la date ne bouge pas de façon mesurable.</p>
  <p>La réunification suit donc la <b>grille de diffusion</b> bien plus que
  l’état du jeu. Les castings ont grossi de {{ f.croissance }} personnes, et le
  plateau réuni est passé de {{ f.restants_casting_min }} joueurs, en médiane
  avec les plus petits castings, à {{ f.restants_casting_max }} avec les plus
  grands. Tout se passe comme si le programme décidait, et le jeu s’adaptait —
ce que les données montrent, c’est la régularité de la date, pas l’intention.</p>
</div>

<p class="note"><strong>Cette conclusion a basculé deux fois, et il faut le
dire.</strong> La page a d’abord écrit « il ne bouge pas » : la pente valait
0,008, avec un intervalle de −0,135 à 0,152. Deux saisons ont ensuite changé,
pour la même raison — <a href="{{ '/sources/' | relative_url }}">une réparation du relevé des
épreuves</a>. <i>Cambodge</i> était <em>écartée</em> du calcul, son dernier
collectif tombant à un épisode qui ne laissait que quatre joueurs ; c’était un
défaut de numérotation, et la saison rentre aujourd’hui dans le rang.
<i>La Revanche des 4 Terres</i> plaçait sa réunification à l’épisode 4 sur 17 — un
chiffre lu dans un tableau de classement des quatre tribus pris pour un tableau
de résultats ; elle la place désormais à l’épisode
{% assign r4t = f.lignes | where: "saison", "s27" | first %}{{ r4t.episode }}. La pente est alors passée à 0,111,
intervalle 0,016 à 0,205, et la page a écrit que la réunification reculait.
Le 20 octobre 2026, la relecture des numéros d’épisode des épreuves a fait
repasser la borne basse sous zéro, sans que rien ne le signale : la page a
continué d’affirmer un recul pendant deux jours. C’est ce que vaut un
résultat tenu par {{ f.saisons }} saisons et posé sur le seuil : il se lit
avec son intervalle, pas avec sa conclusion.</p>

Cela se voit indirectement ailleurs sur ce site. Les
[petits multiples]({{ '/saisons/' | relative_url }}) montrent des courbes de
survie « remarquablement stables » : le calendrier n’a presque pas bougé, et
c’est ce « presque » que la pente ci-dessus mesure.

{% if f.ecartees.size > 0 %}
<p class="note">{{ f.ecartees | size }} saison{% if f.ecartees.size > 1 %}s sont écartées{% else %} est écartée{% endif %} du calcul :
{% for x in f.ecartees %}<b>{{ x.titre }}</b> porte une immunité collective à
l’épisode {{ x.episode }}, qui ne laisserait que {{ x.restants }} joueurs — ce
n’est pas une réunification mais une épreuve par équipes d’après-réunification. Le
repère y échoue, et on le dit plutôt que de le corriger à la main.{% endfor %}</p>
{% else %}
<p class="note">Aucune saison n’est écartée du calcul : le repère — dernier
épisode à immunité collective — trouve une réunification plausible sur les
{{ f.saisons }} saisons classiques qui s’y prêtent. Ce n’était pas le cas
auparavant, et c’est la même réparation qui l’a permis.</p>
{% endif %}

## Le jeu a changé — mais la date ne se laisse pas fixer

Une émission ne publie pas ses changements de format. Mais si le jeu a basculé,
plusieurs indicateurs doivent basculer **ensemble**, et à la même date.

<p class="note"><strong>La méthode.</strong> On cherche la coupure qui sépare le
mieux les {{ r.saisons }} saisons classiques en deux régimes, sur
{{ site.data.stats.mots.indicateurs_rupture }} indicateurs à la fois — taille du casting, durée, âge moyen, taux d’abandon,
nombre de conseils, objets d’immunité. <strong>La date sort des données</strong>,
elle n’est pas choisie. Reste à savoir si cette coupure vaut mieux qu’une
coupure au hasard : on remet donc les saisons dans un ordre aléatoire, et on
recommence.</p>

{% include graphiques/ruptures-nulle.svg %}

<p class="legende-figure">Qualité de la meilleure coupure, face à la meilleure
coupure obtenue sur des saisons remises dans un ordre au hasard.</p>

<div class="constat">
  <p><b>Le jeu a changé</b> : {{ r.test.ecart_types }} {{ r.test.ecart_types_mot }} au-dessus
  de ce qu’une coupure au hasard obtiendrait, p ajustée {{ r.test.p_ajustee }}. Remettez les {{ r.saisons }} saisons dans le désordre
  et aucune coupure n’approche celle-ci.</p>
  <p><b>Mais rien ne dit qu’il ait basculé plutôt que glissé.</b> Contre des
  séries qui suivent la même tendance régulière, la meilleure coupure ne se
  distingue pas : {{ r.test_glissement.ecart_types }}
  {{ r.test_glissement.ecart_types_mot }}, p ajustée {{ r.test_glissement.p_ajustee }}. Une dérive continue suffit à la produire.</p>
  <p><b>Mais sa date n’est pas identifiée.</b> La meilleure coupure tombe en
  {{ r.annee_rupture }} et ne devance la deuxième — {{ r.second.annee }} — que
  de <b>{{ r.avance }} %</b>. Et <b>{{ r.nb_proches }} dates</b> tiennent à
  10 % près, réparties sur <b>{{ r.fenetre.etendue }} ans</b>, de
  {{ r.fenetre.debut }} à {{ r.fenetre.fin }}.</p>
</div>

{% include graphiques/ruptures-profil.svg %}

<p class="legende-figure">Ce que chaque date de coupure envisageable sépare. Un
pic isolé désignerait une année ; ce profil-là est un plateau étalé sur
{{ r.fenetre.etendue }} ans.</p>

Il faut le dire dans ce sens, et pas dans l’autre : **le jeu d’avant n’est pas
le jeu d’après, et c’est solide** ; **l’année du basculement, elle, n’est pas
mesurable ici**. La lecture qui reste debout est celle d’une dérive étalée sur
{{ r.fenetre.etendue }} ans, pas d’un changement de grille annoncé un vendredi soir.

<p class="note"><strong>Pourquoi deux modèles nuls.</strong> Remettre les
saisons dans le désordre détruit aussi toute tendance : n’importe quelle
évolution lente bat ce hasard-là, qui dit seulement que la série n’est pas
stable. Pour savoir si elle <em>casse</em>, il faut la comparer à une évolution
régulière, avec ses écarts remis au hasard. Ce second test a été ajouté le
22 octobre 2026 ; la page affirmait jusque-là « une rupture existe ».</p>

<p class="note"><strong>Comment on le sait.</strong> Une version antérieure de
cette page datait la rupture de 2012 et l’affirmait sans réserve. Les
compléments de données qui ont suivi — les âges manquants, puis trois cents
bulletins de conseil retrouvés — ont fait bouger le maximum d’une révision à
l’autre ; il tombe aujourd’hui en {{ r.annee_rupture }}. Un critère qu’une
révision de données déplace ne désigne pas une année : il désigne une
époque. <a href="{{ '/statistiques/audience/' | relative_url }}">L’audience</a>
resserre ses meilleures coupures bien davantage — {{ m.audience.nb_proches }}
dates sur {{ m.audience.fenetre.etendue }} an, au lieu de
{{ r.nb_proches }} sur {{ r.fenetre.etendue }} ans —, mais là non plus, la
coupure ne se distingue pas d’un déclin régulier.</p>

{% include graphiques/ruptures-serie.svg %}

<p class="legende-figure">Les deux séries qui basculent le plus franchement.</p>

<div class="tableau-large">
<table data-triable><caption class="hors-ecran">Le jeu a changé — mais la date ne se laisse pas fixer</caption>
<thead><tr>
  <th>Indicateur</th><th class="nombre">Avant {{ r.annee_rupture }}</th>
  <th class="nombre">Après</th><th class="nombre">Écart, en écarts-types</th>
</tr></thead>
<tbody>
{% for d in r.detail %}
<tr>
  <td>{{ d.libelle }}</td>
  <td class="nombre">{{ d.avant }}</td>
  <td class="nombre">{{ d.apres }}</td>
  <td class="nombre" data-val="{{ d.ecart_types }}">{{ d.ecart_types }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

{% assign objets = r.detail | where: "libelle", "Objets d’immunité en jeu" | first %}
{% assign casting = r.detail | where: "libelle", "Taille du casting" | first %}
{% assign abandon = r.detail | where: "libelle", "Taux d’abandon" | first %}
Le portrait est cohérent, et il ne se réduit à aucun de ses traits. **Les objets
d’immunité apparaissent** — ils étaient à zéro, ils sont à
{{ objets.apres }} par saison. **Le casting grossit**
({{ casting.avant }} → {{ casting.apres }}), **les conseils se multiplient**,
**le casting vieillit**, et **les abandons sont divisés par {{ r.abandon_rapport }}**
({{ abandon.avant }} % → {{ abandon.apres }} %).

Ce dernier point vaut d’être souligné : la page
[Comment on sort]({{ '/statistiques/sorties/' | relative_url }}) présente la
chute des abandons comme une évolution graduelle, décennie par décennie. Elle
l’est peut-être bien — la rupture, elle, ne sait pas dire l’année.

<p class="note">Ce que cette rupture ne dit pas. Elle ne dit pas <em>ce qui</em>
a changé en premier, ni pourquoi : {{ site.data.stats.mots.indicateurs_rupture }} indicateurs qui bougent ensemble ne se
hiérarchisent pas. Elle ne dit pas non plus qu’il n’y en a qu’une — la méthode
en cherche une seule, et avec {{ r.saisons }} saisons il serait imprudent d’en
chercher deux. Et elle ne dit surtout pas l’année : le tableau ci-dessus compare
deux moyennes de part et d’autre d’une coupure qui aurait pu tomber n’importe où
entre {{ r.fenetre.debut }} et {{ r.fenetre.fin }} sans presque rien perdre.</p>
