---
layout: page
title: Les sources
permalink: /sources/
chapeau: >-
  D’où vient chaque champ, comment les contradictions entre sources ont été tranchées, et ce qui manque encore.
---

{% assign g = site.data.stats.general %}

Toutes les données de ce site viennent de sources publiques, croisées et
vérifiées. Cette page dit lesquelles, ce que chacune apporte, et où elle
s’arrête.

## Les deux sources principales

**[Wikipédia en français](https://fr.wikipedia.org/wiki/Koh-Lanta)** —
l’article général et les pages de chaque saison. C’est la référence pour la
liste des saisons, leurs dates de diffusion, leur lieu, leur durée, leurs tribus
et leurs vainqueurs. Ses tableaux de candidats donnent le sexe en clair et
bornent en jours l’appartenance à chaque tribu, donc la trajectoire complète
d’un aventurier. Limite : seule une quinzaine de saisons dispose d’une page
détaillée.

**[Le wiki Koh-Lanta sur Fandom](https://kohlanta.fandom.com/fr/)** — une page
par saison, pour les {{ g.saisons_diffusees }} éditions. C’est la source du nom
complet, de l’âge, du métier, du département d’origine, du jour de sortie exact
et du total des voix reçues, ainsi que du détail des conseils. Limite : son
tableau de candidats est incomplet sur six saisons, et il ne donne le sexe que
par l’accord du participe.

Aucune des deux ne suffit seule. Pour chaque saison, la source de référence est
**celle dont l’effectif correspond au nombre de candidats annoncé** ; l’autre
vient compléter, champ par champ.

## Une troisième source, pour un seul usage

**[Le fichier des prénoms de l’INSEE](https://www.insee.fr/fr/statistiques/8595130)**
— nombre de naissances par prénom, par sexe et par année depuis 1900, sous
[licence ouverte v2](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
Il ne sert qu’à une chose : donner un point de comparaison aux
[prénoms des aventuriers]({{ '/statistiques/prenoms/' | relative_url }}). Aucune
donnée de Koh-Lanta n’en provient.

Le sous-ensemble effectivement lu — nos prénoms, nos années de naissance — est
versionné dans le dépôt, comme le wikitexte brut : c’est la preuve de
provenance, et elle permet de refaire le calcul sans redemander le fichier
complet à l’INSEE.

## La traçabilité

Chaque enregistrement du jeu de données porte un bloc `sources` qui indique,
**pour chaque champ**, d’où vient la valeur retenue. On y lit `wikipedia-fr`,
`fandom`, mais aussi :

- `arbitrage manuel` — un prénom sans accord de participe, tranché à la main ;
- `déduit de sa participation de 2009` — l’âge d’un revenant, calculé depuis une
  année où il était connu ;
- `dernier jour de la saison (finale)` — un finaliste sort le dernier jour, par
  définition ;
- `recoupement sur le prénom` — un sexe établi grâce à la même personne vue
  ailleurs.

Le wikitexte brut des pages consultées est conservé dans le dépôt, avec les
scripts qui l’ont récupéré : n’importe qui peut refaire le chemin.

## Les arbitrages

Quelques points ont demandé une décision explicite.

**Les durées de saison.** Sur 34 saisons, 29 voient le tableau récapitulatif et
les tables de candidats s’accorder exactement. Pour cinq d’entre elles, ils
divergent d’un jour. C’est alors le **jour attesté par les tables de candidats**
qui est retenu — la sortie d’un finaliste est datée plus précisément qu’une
durée de résumé — et la valeur annoncée est conservée à côté.

**Les homonymes.** Deux Léa en saison 25, deux Cécile en 26, deux Jérôme en 27 :
ce sont bien des personnes différentes, et non des doublons. Elles sont
distinguées par leur âge et leur métier, jamais devinées.

**Les métiers.** Les quelque cinq cents intitulés distincts sont regroupés en
familles par une table de mots-clés, lue dans l’ordre : le premier poste dont un
mot-clé apparaît l’emporte. L’ordre porte donc du sens — « éducateur sportif »
rencontre le sport avant l’enseignement, « maître-nageur » rencontre l’action et
le secours avant le sport. Cette table est un fichier du dépôt, faite pour être
relue et discutée.

## Ce qui manque

Le jeu de données n’est pas complet, et le dire fait partie du travail.

- **Treize valeurs sont inconnues** sur près de dix mille : six âges, trois
  métiers, deux jours de sortie, un motif de sortie, une tribu. Elles sont
  laissées vides plutôt que devinées.
- **Le dépouillement des conseils est partiel.** Sur
  {{ site.data.stats.conseils.conseils }} conseils relevés,
  {{ site.data.stats.conseils.conseils_complets }} ont un dépouillement dont on
  peut garantir qu’il est complet. Les analyses bulletin par bulletin ne portent
  que sur ceux-là ; les agrégats — qui part, avec combien de voix — utilisent
  tous les conseils.
- **Les épreuves ne couvrent pas toutes les saisons.**
  {{ site.data.stats.epreuves.saisons_couvertes }} saisons sur 34 ont un bilan
  épisode par épisode exploitable ; les cinq autres
  ({{ site.data.stats.epreuves.saisons_sans_donnee | join: ", " }}) n’en ont
  pas. Les épreuves de finale sont exclues : les tableaux sources y changent de
  colonnes et listent les qualifiés plutôt que le vainqueur. Enfin, la nature
  des épreuves — endurance, équilibre, précision — n’est nulle part donnée de
  façon exploitable.
- **Les colliers d’immunité ne sont détaillés que sur
  {{ site.data.stats.colliers.saisons_couvertes }} saisons.** Les autres les
  mentionnent sans donner leur destin. Et seuls les *colliers* sont suivis :
  armes secrètes, totem maudit et talisman du feu sacré sont des mécaniques
  distinctes, absentes de ces comptes.
- **La justesse de vote repose sur une base étroite.** Elle exige un conseil au
  dépouillement complet <em>et</em> un éliminé rattaché : quelques dizaines de
  conseils, pas les {{ site.data.stats.conseils.conseils }}. L’indicateur est
  publié avec sa base, et penche vers les saisons les mieux documentées.
- **Le vote du jury final n’est pas un conseil.** Vingt-neuf saisons en
  publient le détail, et les tableaux sources le présentent comme un scrutin
  ordinaire —
  avec le vainqueur en « sortant ». Or on n’y élimine personne : écrire un nom
  y signifie « qu’il gagne ». Ces {{ site.data.stats.jury.effectif }} scrutins
  sont marqués `type: jury` dans les données et tenus à l’écart de tout calcul
  d’élimination.
- **La saison en cours** au moment de la constitution des données n’a pas de
  vainqueur ni de jours de sortie complets : elle est exclue de tous les calculs.

## Une correction d’extraction, et ce qu’elle a déplacé

Les tableaux de Fandom affichent une vignette à côté du nom de l’éliminé :
`[[Fichier:Sara.png|75px|link=Sara Tallon]]`. Le nettoyage du wikitexte traitait
ce lien de fichier comme un lien ordinaire et en gardait la **taille
d’affichage**. Résultat : 478 conseils sur 681 portaient « 75px » en guise
d’aventurier, et n’étaient rattachables à personne.

La correction se fait à la racine, dans le nettoyage du wikitexte : un lien de
fichier ne rend plus que sa cible `link=`, ou rien. Les éliminés rattachés
passent de 203 à **578**, et l’index « épisode de sortie » — celui qui donne
l’exposition aux épreuves — de 248 à environ 600 participations sur 645. Un
contrôle refuse désormais tout nom contenant de la syntaxe MediaWiki.

Trois chiffres publiés ont bougé, tous dans le sens d’une base plus large :

- les **votes du jury final** détectés passent de 8 à
  {{ site.data.stats.jury.effectif }}. Vingt-quatre scrutins étaient comptés
  comme des éliminations ordinaires, ce qui inversait le sens de leurs
  bulletins ;
- le nombre d’aventuriers classables aux **ratios d’épreuves** passe de 89 à
  {{ site.data.stats.epreuves.classement_effectif }} ;
- les **fantômes** passent de 38 à
  {{ site.data.stats.indicateurs.nb_fantomes }}, l’ancien décompte reposant sur
  211 participations mesurables au lieu de
  {{ site.data.stats.indicateurs.mesurables }}. Leur taux de victoire, mesuré
  cette fois contre un groupe de comparaison correct, en est nettement réduit.

Deux conseils restent volontairement non rattachés : leur source donne le
vainqueur de la saison pour sortant en milieu de parcours, ce qui est
impossible. Plutôt que de trancher, on laisse la valeur vide.

## Comment c’est fabriqué

Les données sont extraites, croisées et vérifiées par des scripts Python, puis
commitées dans le dépôt. Un contrôle d’intégrité refuse tout jeu incohérent :
une seule victoire par saison, un jour de sortie qui ne dépasse pas la durée de
la saison, une couleur de tribu qui existe bien dans la saison, toute clé
étrangère résolue.

Les statistiques et les graphiques sont calculés en amont, une fois, et non à
l’affichage : le site ne fait que présenter un résultat déjà vérifié.

Quatre pages reposent en outre sur des **modèles** plutôt que sur des comptages :
régression, analyse factorielle, modèle de durée, tests de permutation. Leurs
tirages aléatoires partent tous d’une graine fixe, et la construction est jouée
deux fois pour vérifier qu’elle rend le même fichier au bit près.
[La méthode]({{ '/methode/' | relative_url }}) en donne le détail et la liste
complète des tests.
