---
layout: page
title: Le pronostic
permalink: /statistiques/pronostic/
chapeau: >-
  Si la production choisit ses vainqueurs au casting, cela doit se voir : une
  fiche d’inscription suffirait à les désigner. On a essayé — puis on a posé la
  même question au conseil, où la réponse n’est pas la même.
---

{% assign m = site.data.stats.modeles %}
{% assign p = m.pronostic %}
{% assign t = m.registre | where: "cle", "pronostic_vainqueur" | first %}

La page précédente montre que la production **compose** ses castings au cordeau.
La question suivante vient toute seule : cette composition dit-elle quelque
chose du résultat ?

## La règle du jeu, pour le modèle

On n’autorise que ce qui est connu **le jour du casting** : l’âge, le sexe, la
famille de métier, la couleur du bandeau, la taille du plateau et l’année.
Aucune information de jeu — pas une épreuve gagnée, pas un bulletin reçu, pas un
jour de survie. La question n’est pas « peut-on deviner à mi-parcours », elle est
« le recrutement contient-il déjà la réponse ».

<p class="note"><strong>Une saison exclue à chaque tour.</strong> Le modèle
apprend sur {{ p.saisons }} saisons moins une, et pronostique celle qu’il n’a
jamais vue. Un découpage au hasard serait tricher : deux aventuriers du même
casting ne sont pas indépendants, et la moitié d’une saison suffirait à deviner
l’autre. On mesure ensuite <strong>à quelle place le modèle a rangé celui qui a
réellement gagné</strong>, dans son propre casting. Le hasard donne
{{ p.rang_hasard }} sur une vingtaine.</p>

## Le résultat

{% include graphiques/pronostic-rang.svg %}

<p class="legende-figure">Rang moyen attribué au vrai vainqueur. La silhouette
est ce que donnent {{ t.tirages }} classements rebattus au hasard à l’intérieur
de chaque saison.</p>

<div class="constat">
  <p>Le modèle place le futur vainqueur au rang <b>{{ p.rang_moyen }}</b>
  en moyenne — intervalle {{ p.rang_intervalle[0] }} à
  {{ p.rang_intervalle[1] }}. Le hasard le placerait au rang
  <b>{{ p.rang_hasard }}</b>.</p>
  <p>p = {{ t.p }}. Il n’y a <b>rien</b> : la fiche d’inscription ne contient
  aucune information sur l’issue de la saison.</p>
</div>

Et ce n’est pas une affaire de modèle trop simple. Sur la part de saison tenue
— une cible bien plus riche que la seule victoire, avec {{ p.effectif }}
observations au lieu de {{ p.vainqueurs }} — la variance expliquée hors
échantillon est de **{{ p.r2_survie_lineaire }}** pour le modèle linéaire et de
**{{ p.r2_survie_arbre }}** pour un gradient boosting, autorisé à trouver
n’importe quelle interaction non linéaire. Les deux font **moins bien que
prédire la moyenne pour tout le monde**.

## Ce qui porte le peu de signal qu’il y a

{% include graphiques/pronostic-importances.svg %}

<p class="legende-figure">De combien le rang du vainqueur se dégrade quand on
brouille une seule variable. Une valeur positive signifie que la variable
servait un peu.</p>

Les contributions sont de l’ordre d’une demi-place sur vingt. Aucune ne survit à
son propre intervalle. Il n’y a pas de variable cachée à trouver ici : il n’y a
pas de signal du tout.

## Et en cours de jeu ? La même question, posée au conseil

{% assign pv = site.data.stats.prevision %}
{% assign tp = m.registre | where: "cle", "prevision_conseil" | first %}
{% assign jeu = pv.jeux | last %}
{% assign fic = pv.jeux | first %}

La fiche d’inscription ne dit rien. Mais la fiche d’inscription n’est pas le
jeu. **La même discipline se pose à une question bien plus dure et bien plus
intéressante : le soir d’un conseil, sachant tout ce qui a précédé, peut-on
désigner celui qui va partir ?**

Le protocole est identique — une saison exclue à chaque tour, le modèle
pronostique une soirée qu’il n’a jamais vue — et le modèle est un **logit
conditionnel** : chaque conseil forme son propre groupe de comparaison. Le
modèle ne compare jamais deux soirées entre elles, seulement les présents d’une
même soirée. La taille du conseil, la saison, l’époque et la composition du camp
disparaissent donc du calcul sans qu’on ait à les mesurer.

<p class="note"><strong>Celui qui porte l’immunité sort du choix, il ne devient
pas une variable.</strong> Qu’il ne puisse pas être éliminé est une règle du
jeu, pas une chose à deviner : lui donner un coefficient gonflerait l’adresse du
modèle avec ce que tout le monde sait déjà. Le modèle choisit donc parmi ceux
qui peuvent réellement partir.</p>

{% include graphiques/prevision-premiers.svg %}

<p class="legende-figure">Part des {{ jeu.conseils }} conseils où le modèle
place en tête celui qui part réellement. Le repère est le hasard : une chance
sur le nombre de présents.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Ce que le modèle sait</th><th class="nombre">Variables</th>
  <th class="nombre">Conseils</th>
  <th class="nombre">Rang du vrai éliminé</th>
  <th class="nombre">Désigné en premier</th>
</tr></thead>
<tbody>
{% for j in pv.jeux %}
<tr>
  <td><b>{{ j.libelle }}</b><br><small>{{ j.description }}</small></td>
  <td class="nombre">{{ j.variables }}</td>
  <td class="nombre">{{ j.conseils }}</td>
  <td class="nombre" data-val="{{ j.rang_moyen }}">{{ j.rang_moyen }}
    <small>(hasard {{ j.rang_hasard }})</small></td>
  <td class="nombre" data-val="{{ j.premiers }}">{{ j.premiers }} %
    <small>(hasard {{ j.premiers_hasard }} %)</small></td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Le <strong>rang du vrai éliminé</strong> se lit ainsi : on
classe les présents du plus au moins menacé selon le modèle, et l’on regarde à
quelle place s’y trouve celui qui est réellement parti — <b>0</b> pour la
première, <b>1</b> pour la dernière. Le hasard donne 0,5. Plus petit vaut
mieux.</p>

<div class="constat">
  <p>Avec la seule fiche d’inscription : <b>{{ fic.rang_moyen }}</b> contre
  {{ fic.rang_hasard }} au hasard. <b>Rien</b>, exactement comme au casting.</p>
  <p>Avec ce que la soirée a produit : <b>{{ jeu.rang_moyen }}</b>,
  {{ tp.ecart_types }} écarts-types, p ajustée <b>{{ tp.p_ajustee }}</b>. Le
  modèle désigne l’éliminé <b>en premier dans {{ jeu.premiers }} %</b> des
  conseils, contre {{ jeu.premiers_hasard }} % par le hasard.</p>
</div>

**Ce chiffre se lit dans les deux sens, et les deux comptent.** Passer de
{{ jeu.premiers_hasard }} % à {{ jeu.premiers }} % de bonnes désignations, c’est
un signal réel, établi hors échantillon, sur {{ jeu.conseils }} conseils de
{{ jeu.plis }} saisons. C’est aussi **trois conseils sur quatre où le modèle se
trompe de personne**. Le jeu n’est pas imprévisible ; il est très loin d’être
prévisible.

<p class="note"><strong>Pourquoi cette page compte plus que les autres.</strong>
Le reste du site publie des associations : chacune dit « ceci compte », aucune
ne dit « voilà ce qu’on saurait deviner ». Une association peut être solide et
sans aucun pouvoir de désignation — c’est même le cas ordinaire quand les effets
sont petits. Le pronostic hors échantillon est la seule mesure qui tranche, et
c’est la seule qu’aucune correction pour tests multiples ne peut sauver : un
modèle qui apprend du bruit le paie sur la saison qu’il n’a pas vue.</p>

<p class="note"><strong>Ce qui reste hors d’atteinte, et il faut le dire.</strong>
Ce modèle ne voit ni les alliances, ni ce qui s’est dit sur le camp, ni les
colliers non joués. Il ne voit que ce qui laisse une trace chiffrée. Les
{{ jeu.conseils }} conseils utilisables sont ceux dont le dépouillement est
connu — <a href="{{ '/completude/' | relative_url }}">la grille de
complétude</a> dit combien manquent, et
<a href="{{ '/sources/' | relative_url }}">Les sources</a> pourquoi. Un modèle
qui verrait le réseau des bulletins ferait sans doute mieux ; celui-ci mesure ce
qu’on peut deviner sans lui.</p>

## Ce que ce résultat veut dire

<div class="constat">
  <p>La production tient son casting d’une main ferme — la parité au candidat
  près — et <b>ce casting ne prédit rien</b>.</p>
  <p>Les deux faits vont ensemble. Un plateau composé au cordeau sur des
  critères qui n’ont aucun pouvoir prédictif, c’est la définition d’un
  <b>équilibre de départ</b> : on garantit la variété affichée, on ne
  pré-écrit pas le résultat.</p>
</div>

C’est aussi une mise en garde contre les pages descriptives de ce site,
celle-ci comprise. [Le métier]({{ '/statistiques/professions/' | relative_url }})
montre que l’encadrement accède moins souvent à la finale ;
[Âge et longévité]({{ '/statistiques/longevite/' | relative_url }}) montre que
les 30-34 ans tiennent le plus longtemps. Ces écarts sont réels — et ils sont
si petits devant la variabilité individuelle qu’ils **ne permettent de
pronostiquer personne**. Un écart moyen visible sur cinq cents personnes n’est
pas une information sur une personne.

<p class="note">Ce que ce résultat ne dit pas. Il ne dit pas que la production
ne choisit rien : il dit que ce qu’elle choisit n’est <em>pas dans ces quatre
variables</em>. Un profil de personnalité, une aisance à l’oral, une capacité à
tenir un récit — rien de cela n’est mesurable ici, et rien n’exclut que ce soit
déterminant. Il ne dit pas non plus qu’un meilleur modèle échouerait : il dit
qu’avec {{ p.vainqueurs }} vainqueurs, aucun modèle ne pourrait établir un effet
faible. <a href="{{ '/methode/' | relative_url }}">La méthode</a> détaille cette
limite.</p>
