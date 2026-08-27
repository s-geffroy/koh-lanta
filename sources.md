---
layout: page
title: Les sources
permalink: /sources/
---

{% assign g = site.data.stats.general %}

Toutes les données de ce site viennent de sources publiques, croisées et
vérifiées. Cette page dit lesquelles, ce que chacune apporte, et où elle
s'arrête.

## Les deux sources principales

**[Wikipédia en français](https://fr.wikipedia.org/wiki/Koh-Lanta)** —
l'article général et les pages de chaque saison. C'est la référence pour la
liste des saisons, leurs dates de diffusion, leur lieu, leur durée, leurs tribus
et leurs vainqueurs. Ses tableaux de candidats donnent le sexe en clair et
bornent en jours l'appartenance à chaque tribu, donc la trajectoire complète
d'un aventurier. Limite : seule une quinzaine de saisons dispose d'une page
détaillée.

**[Le wiki Koh-Lanta sur Fandom](https://kohlanta.fandom.com/fr/)** — une page
par saison, pour les {{ g.saisons_diffusees }} éditions. C'est la source du nom
complet, de l'âge, du métier, du département d'origine, du jour de sortie exact
et du total des voix reçues, ainsi que du détail des conseils. Limite : son
tableau de candidats est incomplet sur six saisons, et il ne donne le sexe que
par l'accord du participe.

Aucune des deux ne suffit seule. Pour chaque saison, la source de référence est
**celle dont l'effectif correspond au nombre de candidats annoncé** ; l'autre
vient compléter, champ par champ.

## La traçabilité

Chaque enregistrement du jeu de données porte un bloc `sources` qui indique,
**pour chaque champ**, d'où vient la valeur retenue. On y lit `wikipedia-fr`,
`fandom`, mais aussi :

- `arbitrage manuel` — un prénom sans accord de participe, tranché à la main ;
- `déduit de sa participation de 2009` — l'âge d'un revenant, calculé depuis une
  année où il était connu ;
- `dernier jour de la saison (finale)` — un finaliste sort le dernier jour, par
  définition ;
- `recoupement sur le prénom` — un sexe établi grâce à la même personne vue
  ailleurs.

Le wikitexte brut des pages consultées est conservé dans le dépôt, avec les
scripts qui l'ont récupéré : n'importe qui peut refaire le chemin.

## Les arbitrages

Quelques points ont demandé une décision explicite.

**Les durées de saison.** Sur 34 saisons, 29 voient le tableau récapitulatif et
les tables de candidats s'accorder exactement. Pour cinq d'entre elles, ils
divergent d'un jour. C'est alors le **jour attesté par les tables de candidats**
qui est retenu — la sortie d'un finaliste est datée plus précisément qu'une
durée de résumé — et la valeur annoncée est conservée à côté.

**Les homonymes.** Deux Léa en saison 25, deux Cécile en 26, deux Jérôme en 27 :
ce sont bien des personnes différentes, et non des doublons. Elles sont
distinguées par leur âge et leur métier, jamais devinées.

**Les métiers.** Les quelque cinq cents intitulés distincts sont regroupés en
familles par une table de mots-clés, lue dans l'ordre : le premier poste dont un
mot-clé apparaît l'emporte. L'ordre porte donc du sens — « éducateur sportif »
rencontre le sport avant l'enseignement, « maître-nageur » rencontre l'action et
le secours avant le sport. Cette table est un fichier du dépôt, faite pour être
relue et discutée.

## Ce qui manque

Le jeu de données n'est pas complet, et le dire fait partie du travail.

- **Treize valeurs sont inconnues** sur près de dix mille : six âges, trois
  métiers, deux jours de sortie, un motif de sortie, une tribu. Elles sont
  laissées vides plutôt que devinées.
- **Le dépouillement des conseils est partiel.** Sur
  {{ site.data.stats.conseils.conseils }} conseils relevés,
  {{ site.data.stats.conseils.conseils_complets }} ont un dépouillement dont on
  peut garantir qu'il est complet. Les analyses bulletin par bulletin ne portent
  que sur ceux-là ; les agrégats — qui part, avec combien de voix — utilisent
  tous les conseils.
- **Les épreuves ne sont pas dans ce jeu de données.** Ni les victoires
  individuelles, ni les temps, ni les familles d'épreuves. Tant qu'elles n'y
  seront pas, aucun classement de type « meilleur ratio d'épreuves » ne figurera
  sur ce site.
- **La saison en cours** au moment de la constitution des données n'a pas de
  vainqueur ni de jours de sortie complets : elle est exclue de tous les calculs.

## Comment c'est fabriqué

Les données sont extraites, croisées et vérifiées par des scripts Python, puis
commitées dans le dépôt. Un contrôle d'intégrité refuse tout jeu incohérent :
une seule victoire par saison, un jour de sortie qui ne dépasse pas la durée de
la saison, une couleur de tribu qui existe bien dans la saison, toute clé
étrangère résolue.

Les statistiques et les graphiques sont calculés en amont, une fois, et non à
l'affichage : le site ne fait que présenter un résultat déjà vérifié.
