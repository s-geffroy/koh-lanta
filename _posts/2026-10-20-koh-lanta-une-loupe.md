---
layout: article
espace: articles
title: "Une loupe, pas un miroir"
titre: "Koh-Lanta n’est pas la vraie vie : c’est une loupe"
chapeau: "Ce que les votes de toutes les saisons disent vraiment des alliances, de la menace et de l’appartenance."
description: "Koh-Lanta n’est pas la vraie vie, c’est une loupe : ce que les votes de toutes les saisons disent des alliances, de la menace et de l’appartenance."
date: 2026-10-20
last_modified_at: 2026-10-23
author: Sylvain Geffroy
permalink: /articles/koh-lanta-une-loupe/
autre_version: /articles/amplificateur-institutionnel/
autre_version_titre: "Lire la version longue →"
---
{%- comment -%}
  Les chiffres viennent de stats.articles (tools/articles.py) : ils suivent
  les donnees. Les phrases, elles, ne suivent pas -- chaque conclusion ecrite
  ici est inscrite dans AFFIRMATIONS, et verifie_site.py refuse l'article le
  jour ou les donnees ne la disent plus.
{%- endcomment -%}
{%- assign a = site.data.stats.articles -%}

« Au travail, c'est Koh-Lanta. »

La formule est pratique : alliances, coups de bluff, rivalités, éliminations symboliques. Mais prise au sérieux, elle est trompeuse.

**Koh-Lanta n'est pas un miroir de la vraie vie. C'est une loupe.**

Le jeu prend des mécanismes que l'on retrouve partout — dépendance, coopération, réputation, appartenance — et les place sous des règles très particulières : petit groupe, ressources rares, vote éliminatoire, sortie impossible autrement qu'en abandonnant, règles qui changent en cours de route. Il ne révèle pas « comment les humains sont vraiment ». Il montre **comment les mêmes humains se comportent quand on change les règles**.

Cela se lit dans les votes : **{{ a.saisons }} saisons diffusées, {{ a.conseils }} conseils de saisons terminées et {{ a.bulletins }} bulletins**, chacun recopié nom par nom et [sourcé]({{ '/sources/' | relative_url }}). Et les votes ne racontent pas tout à fait l'histoire que l'on croit.

## Une société artificielle, mais très réglée

Koh-Lanta passe pour un retour à la vie primitive. C'est l'inverse : tout y est institution — équipes, immunités, conseils, votes, avantages, réunification, finale.

Et plusieurs institutions ordinaires y manquent. Un aventurier ne peut pas changer d'entreprise, signer un contrat avec son alliance, s'assurer contre l'élimination autrement qu'en trouvant un collier, ou modifier les règles. Ce qui manque compte autant que ce qui est là.

## Quand on ne peut pas partir, les autres deviennent tout

Le sociologue Richard Emerson l'a formulé simplement : le pouvoir naît de la dépendance. Si j'ai besoin de vous et ne peux pas vous remplacer, vous avez du pouvoir sur moi. Albert Hirschman parlait d'*exit* : quand on ne peut pas partir, il reste à se faire entendre ou à rester loyal.

À Koh-Lanta, on ne part qu'en abandonnant. Les liens locaux deviennent donc la principale assurance. Et cela se voit : **se retrouver sans un seul des aventuriers avec qui l'on a déjà voté va de pair avec {{ a.tests.vote_isole.valeur }} points (de pourcentage) de risque en plus de sortir**, quand le hasard en donnerait {{ a.tests.vote_isole.attendu_rond }} ([la pire place]({{ '/statistiques/pire-place/' | relative_url }})).

> **Pas de sortie possible → plus de dépendance → perdre son dernier allié devient la pire place du jeu.**

## Les alliances tiennent plus qu'on ne le croit

Le jeu a la réputation d'être celui des trahisons. Les votes disent autre chose. Deux aventuriers qui ont voté ensemble revotent ensemble **bien plus souvent** que deux qui se sont séparés — {{ a.tests.persistance_alliances.valeur_ronde }} points d'écart. Et l'on écrit moins souvent le nom d'un ancien partenaire que si les alliances ne comptaient pas ([les alliances]({{ '/statistiques/alliances/' | relative_url }})).

La trahison existe : {{ a.tests.trahison.valeur_ronde }} % des bulletins visent quelqu'un avec qui l'on a déjà voté. Mais c'est moins que les {{ a.tests.trahison.attendu_rond }} % que produirait un jeu sans alliances. Sans contrat pour garantir une alliance, il reste sa durée — et elle se voit.

## Être très bon n'est pas (forcément) un problème

C'est l'idée la plus répétée sur le jeu : utile tant que les tribus s'affrontent, le meilleur deviendrait une menace à l'approche de la phase individuelle. « Je ne veux pas l'affronter à la fin. »

**Les votes ne la confirment pas.** Classons chaque éliminé parmi les votants du soir selon sa [force aux épreuves]({{ '/statistiques/force/' | relative_url }}), de 0 pour le plus faible du camp à 100 pour le plus fort. Avant la réunification, il se situe en moyenne au rang {{ a.force.rang_avant }} ; après, au rang {{ a.force.rang_apres }}. L'écart n'est pas plus grand que ce que le hasard produit. Les ambassadeurs, qui décident seuls, ne choisissent pas les forts plus que ne le ferait un tirage au sort ([la réunification]({{ '/statistiques/reunification/' | relative_url }})).

Prudence : la force aux épreuves n'est pas toute la compétence, et un fort ciblé peut se sauver en gagnant l'immunité. Mais l'idée que la réunification retourne le jeu contre les meilleurs ne se voit pas dans les chiffres. La règle de management qu'on en tire — « dans l'entreprise, le meilleur devient une cible » — repose sur un mécanisme que même le jeu ne montre pas.

## Être visé appelle à l'être encore

La réputation peut fabriquer une partie de la réalité : celui qu'on dit « dangereux » reçoit moins d'informations, plus de méfiance, plus de bulletins.

Ce que l'on voit dans les votes est compatible avec ce mécanisme, sans le prouver. **Avoir reçu une voix va de pair avec {{ a.tests.cible_persistante.valeur_ronde }} points de risque en plus d'en recevoir encore, et {{ a.tests.menace_voix.valeur_ronde }} points de plus de sortir au conseil suivant.** Et celui dont on a écrit le nom écrit le nôtre en retour bien plus souvent que le hasard ne le voudrait ([d'un conseil à l'autre]({{ '/statistiques/conditionnelles/' | relative_url }})).

On ne voit pas non plus qu'avoir survécu à un vote massif protège mieux qu'avoir survécu à deux bulletins — sans pouvoir exclure qu'il protège un peu.

## Une couleur d'équipe devient une identité

Les tribus sont créées par la production, à partir d'inconnus. À la réunification, elles disparaissent. Pourtant elles continuent de compter.

Après la réunification, **on écrit le nom de quelqu'un de sa tribu initiale dans {{ a.tests.vote_bandeau_apres_fusion.valeur_ronde }} % des bulletins, contre {{ a.tests.vote_bandeau_apres_fusion.attendu_rond }} % si l'on votait au hasard** ([qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }})). Et appartenir à la tribu initiale la moins nombreuse expose ([autour du feu]({{ '/statistiques/autour-du-feu/' | relative_url }})). Que les sorties s'enchaînent par tribu, comme si un camp était démonté un par un, n'est pas établi en revanche.

La psychologie sociale l'a montré il y a cinquante ans : des groupes arbitraires suffisent à créer de la préférence. Les tribus ne sont pas arbitraires — on y vit ensemble des semaines —, et l'on ne peut pas séparer ici l'identité de groupe des liens noués ; mais leur trace dans les votes va dans ce sens.

Mais toutes les catégories ne fonctionnent pas ainsi. Être du **sexe** le moins représenté du camp ne fait pas partir plus tôt : cela protège plutôt. Porter une étiquette ne suffit pas à faire un groupe ; il faut observer ce qu'elle produit.

## Voter avec la minorité : un coût, de justesse

On peut suivre une majorité par peur d'être isolé, ou parce qu'on pense qu'elle sait quelque chose. Les bulletins ne disent pas lequel des deux. Ils permettent seulement de vérifier si voter avec la minorité se paie au conseil suivant : c'est le cas, mais de justesse, et le résultat reste fragile.

## La réunification change vraiment le jeu

La production présente la réunification comme le moment où « tout se recompose ». Ce n'est pas qu'un argument de bande-annonce : après la réunification, **les votes se divisent nettement plus** — la part de conseils où l'éliminé n'obtient pas la majorité augmente de {{ a.tests.fusion_serre.valeur_ronde }} points — et l'on élimine moins de femmes, à composition du camp égale ([la réunification]({{ '/statistiques/reunification/' | relative_url }})).

Sur ce point, ce que la production dit de son dispositif et ce que montrent les votes vont dans le même sens — même si les règles elles-mêmes, colliers individuels et camp plus nombreux, y sont sans doute pour quelque chose.

## L'ordinaire d'abord

Égalités, seconds votes, colliers qui renversent tout : ce sont les conseils dont on se souvient. Ce ne sont pas ceux qui arrivent le plus souvent. **{{ a.issues.ordinaire_rond }} % des conseils se terminent par une élimination ordinaire**, sans égalité ni renversement par un objet ; le renversement par un objet d'immunité n'en concerne que {{ a.issues.renversement }} %, l'égalité suivie d'un second vote {{ a.issues.egalite_revote }} %.

C'est la leçon la plus utile pour qui veut prévoir. Une prédiction qui surestime le spectaculaire peut tomber juste une fois et se tromper en moyenne. **Avant de prédire l'exceptionnel, il faut savoir à quelle fréquence arrive l'ordinaire.**

## Le montage fait partie de l'objet

La production choisit les règles, organise les situations, sélectionne les images et construit un récit. Les aventuriers le savent ; ceux qui reviennent connaissent le genre et arrivent avec une réputation.

Il faut donc distinguer le **jeu vécu** du **jeu montré**. Le motif d'un vote, c'est le montage qui nous le rapporte ; le vote lui-même est un fait, que le montage ne peut pas réécrire — même si les conseils qu'il n'a pas montrés en entier manquent au décompte. C'est pour cela que tout ce qui précède repose sur les bulletins, et jamais sur ce que les aventuriers disent de leurs raisons.

D'où une hypothèse — le montage n'a pas été mesuré ici, ce n'est donc pas un résultat. Le récit de l'émission semble mettre en avant le champion menaçant, le stratège démasqué, le retournement. Les votes, eux, mettent en avant la tribu initiale, l'alliance qui dure, l'isolement qui expose. **Ce que l'on montre ne serait pas ce qui pèse le plus.**

## Ce que le jeu retire

Contrats, assurance, possibilité de partir, de créer de la valeur, de changer les règles : ces amortisseurs de la vie réelle manquent. Elinor Ostrom a montré que des groupes savent inventer leurs propres règles pour gérer un problème collectif. Les aventuriers de Koh-Lanta, eux, jouent **dans** une institution qu'ils ne contrôlent pas — et c'est cette absence qui rend la dépendance et l'appartenance si lourdes.

## Une loupe, pas un miroir

> **Koh-Lanta ne nous dit pas comment les humains se comportent « naturellement » ; il montre comment certaines règles rendent certains mécanismes beaucoup plus importants que d'autres.**

Ce sont des hypothèses, que les votes rendent plausibles sans les démontrer :

Supprimez la sortie : le dernier allié devient vital.

Supprimez les contrats : seule la durée garantit une alliance.

Créez des groupes : ils survivent à leur dissolution.

Mettez tout cela sous caméra : le récit retiendrait la menace et le coup d'éclat, quand les votes retiennent l'appartenance.

La bonne question n'est donc pas : « Est-ce que la vraie vie ressemble à Koh-Lanta ? »

Mais :

> **Quelles règles, dans nos propres organisations, fabriquent les comportements que nous attribuons ensuite trop facilement aux individus ?**

*Mis à jour le 23 octobre 2026 : le modèle nul tire désormais l'éliminé parmi les votants du soir, et deux résultats cités dans la première version — l'enchaînement des sorties par camp et la sortie précoce des ambassadeurs — ne passent plus la correction.*

*Les tests, leurs modèles nuls et leurs limites sont détaillés dans la [version longue]({{ '/articles/amplificateur-institutionnel/' | relative_url }}) et sur la page [méthode]({{ '/methode/' | relative_url }}).*
