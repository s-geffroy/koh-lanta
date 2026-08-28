---
layout: page
title: Le pronostic
permalink: /statistiques/pronostic/
chapeau: >-
  Si la production choisit ses vainqueurs au casting, cela doit se voir : une
  fiche d’inscription suffirait à les désigner. On a essayé.
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
