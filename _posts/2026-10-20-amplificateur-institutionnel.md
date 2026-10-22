---
layout: article
espace: articles
title: "Un amplificateur institutionnel"
titre: "Koh-Lanta comme amplificateur institutionnel : cadre mécaniste et confrontation aux votes"
version: "Version longue"
chapeau: "Le cadre théorique, les tests et leurs limites : ce qui tient, ce qui cède, et pourquoi l'ordinaire se prédit mieux que l'exceptionnel."
description: "Version longue : un cadre mécaniste confronté à tous les votes du jeu. Les alliances et l'appartenance tiennent ; la compétence comme menace, non."
date: 2026-10-20
author: Sylvain Geffroy
permalink: /articles/amplificateur-institutionnel/
math: true
autre_version: /articles/koh-lanta-une-loupe/
autre_version_titre: "Lire la version courte →"
---
{%- comment -%}
  Les chiffres viennent de stats.articles (tools/articles.py) : ils suivent
  les donnees. Les conclusions ecrites ici sont inscrites dans AFFIRMATIONS,
  et verifie_site.py refuse la page le jour ou les donnees ne les disent plus.
  Les seuls nombres ecrits en dur sont ceux de la version precedente : ils
  appartiennent a son histoire, pas aux donnees.
{%- endcomment -%}
{%- assign a = site.data.stats.articles -%}

Cet article étudie *Koh-Lanta* non comme une miniature de « la vraie vie », mais comme un **dispositif institutionnel et médiatique qui repondère des mécanismes sociaux et stratégiques documentés ailleurs** : compétition relative, coalition, pouvoir-dépendance, réputation, identité de groupe, conformité. Nous écrivons symboliquement l'état du jeu $$S_{KL}=T_{KL}(G_{ref})$$, où $$T_{KL}$$ est la transformation institutionnelle d'un référentiel trans-domaines, et nous le séparons de sa représentation diffusée, $$O_{diffusé}=M_{prod}(S_{KL},A,C)$$ ([Corner, 2002](#ref-corner2002) ; [Couldry, 2004](#ref-couldry2004) ; [Andrejevic, 2004](#ref-andrejevic2004)).

La version précédente de ce texte reposait sur neuf conseils pilotes et un seul cas prospectif. Celle-ci confronte le cadre à une base exhaustive : **{{ a.saisons }} saisons, {{ a.aventuriers }} aventuriers, {{ a.conseils }} conseils d'élimination de saisons terminées, dont {{ a.conseils_complets }} au bulletin près, et {{ a.bulletins }} bulletins**, reconstruits depuis Wikipédia et le wiki Fandom et publiés avec leurs sources. Les hypothèses y sont lues dans un registre de **{{ a.nb_tests }} tests de permutation**, conçus indépendamment de cet article, dont {{ a.nb_retenus }} résistent à la correction de Benjamini-Hochberg.

Trois résultats réorganisent la thèse. (1) Les mécanismes **relationnels** — isolement, persistance des coalitions, ciblage répété, appartenance d'origine — sont nettement plus marqués que ne le produirait une élimination au hasard parmi les présents. (2) L'exemple le plus cité de la version précédente, **la compétence qui devient une menace après la réunification, n'est pas observé** : l'éliminé n'est pas plus fort aux épreuves après la réunification qu'avant (écart de {{ a.tests.fusion_force.observe }} points de rang, p ajustée {{ a.tests.fusion_force.p }}). (3) La version précédente donnait 42,9 % à l'issue ordinaire d'un conseil, l'élimination sans égalité ni objet joué ; c'est en réalité l'issue de **{{ a.issues.ordinaire }} %** des conseils. Une prédiction qui ignore cette fréquence peut tomber juste une fois et rester mal calibrée.

**Mots-clés :** Koh-Lanta ; institutions ; télé-réalité ; coalitions ; réputation ; identité sociale ; tests de permutation ; calibration.

## 1. Introduction

Comparer *Koh-Lanta* au monde professionnel, politique ou social est intuitif : on y voit alliances, réputation, compétition, coopération et retournements. Mais une analogie globale du type « la vie est un Koh-Lanta » est analytiquement faible. Elle ne distingue pas ce qui relève de mécanismes humains généraux de ce qui résulte de l'architecture particulière du jeu.

Notre point de départ est inverse : *Koh-Lanta* est intéressant **parce qu'il n'est pas la vie ordinaire**. Il organise un petit groupe, ferme la plupart des options de sortie, impose des votes éliminatoires, alterne des régimes collectifs et individuels, crée des ressources rares et maintient un horizon terminal. Il retire en même temps des institutions courantes : contrats opposables, assurance, marché de substitution, mobilité entre organisations, capacité à modifier les règles.

La question est donc :

> **Comment l'architecture institutionnelle et médiatique de Koh-Lanta rend-elle certains mécanismes sociaux plus saillants, moins saillants ou qualitativement différents — et lesquels de ces déplacements se lisent effectivement dans les votes ?**

La seconde moitié de la question est l'apport de cette version. La précédente concluait que « la prochaine étape décisive [était] de produire une base événementielle plus large ». Cette base existait : c'est celle de ce site, qui publie chaque conseil, chaque bulletin et chaque test avec son modèle nul. Nous l'utilisons ici telle qu'elle est publiée, sans construire de mesure ad hoc, à une exception près (section 6.4).

Trois interprétations restent exclues. L'émission n'est pas une expérience contrôlée. Les participants ne représentent pas la population générale. Ce qui est diffusé n'est pas l'expérience vécue.

## 2. Positionnement théorique

### 2.1. Compétition relative et tournoi

L'économie des tournois montre qu'une récompense fondée sur le rang relatif modifie les incitations ([Lazear et Rosen, 1981](#ref-lazearrosen1981tournaments)). La conséquence la plus souvent tirée pour *Koh-Lanta* est conditionnelle :

$$
Valeur_{productive}(compétence) \neq Valeur_{stratégique}(compétence)
$$

Une compétence utile au collectif tant que les tribus s'affrontent deviendrait une menace quand chacun anticipe la phase individuelle. C'est une hypothèse **directionnelle et testable** : après la réunification, l'éliminé devrait être plus haut dans le classement de force du camp qu'avant. La section 6.1 montre qu'elle ne se vérifie pas.

### 2.2. Coalition, vote et pouvoir de pivot

Les coalitions coordonnent des acteurs aux intérêts partiellement divergents ([Riker, 1962](#ref-riker1962) ; [Frohlich, 1975](#ref-frohlich1975)). Le pouvoir de pivot a une formulation robuste dans les jeux de vote : une voix vaut par le nombre de coalitions qu'elle fait basculer ([Shapley et Shubik, 1954](#ref-shapleyshubik1954)). Les petits effectifs et les décisions discrètes du jeu rendent cette logique visible. Une coalition qui compte doit **persister** d'un conseil à l'autre et **protéger** ses membres : deux propriétés mesurables.

### 2.3. Pouvoir, dépendance et options de sortie

Pour Emerson, la dépendance de B envers A croît avec le besoin de ce que A contrôle et décroît avec les alternatives de B ([Emerson, 1962](#ref-emerson1962) ; [Hillman et al., 2009](#ref-hillman2009)). Hirschman distingue *exit*, *voice* et *loyalty* ([Hirschman, 1970](#ref-hirschman1970)). *Koh-Lanta* réduit l'exit : on peut changer d'alliance, pas d'arène. L'hypothèse est que **la fermeture de l'arène augmente la valeur des liens locaux** — et donc, symétriquement, le coût de n'en avoir plus aucun.

### 2.4. Information, signalisation et réputation

L'asymétrie d'information et la signalisation structurent les échanges quand intentions et types sont privés ([Akerlof, 1970](#ref-akerlof1970lemons) ; [Spence, 1973](#ref-spence1973signaling)). La réputation ajoute une dimension temporelle : elle soutient la coopération par réciprocité indirecte ([Nowak et Sigmund, 1998](#ref-nowaksigmund1998)) mais, dans un tournoi éliminatoire, elle peut aussi désigner une cible :

$$
Réputation \rightarrow Menace\ perçue \rightarrow Ciblage
$$

Le premier maillon n'est pas observable dans nos données ; le dernier l'est. Nous testons la forme réduite : **avoir été visé expose-t-il à l'être encore, et à partir ?**

### 2.5. Apprentissage social, conformité et cascades

Une cascade informationnelle se produit quand les décisions observées conduisent un acteur à négliger son information privée ([Bikhchandani et al., 1998](#ref-bikhchandani1998cascades) ; [Bikhchandani et al., 2024](#ref-bikhchandani2024cascades)) ; suivre une majorité pour éviter un coût social relève d'autre chose. Les bulletins ne distinguent pas les deux. Ils permettent seulement de tester une conséquence commune : **le vote minoritaire est-il sanctionné ?**

### 2.6. Identité sociale

La catégorisation en groupes affecte évaluations et comportements, même quand les groupes sont arbitraires ([Tajfel et Turner, 1979](#ref-tajfelturner1979)). Les tribus de *Koh-Lanta* sont constituées par la production ; elles disparaissent à la réunification. Si l'identité de groupe persiste, la **tribu initiale** doit continuer de protéger après la réunification, et les sorties doivent s'y **enchaîner par camp**.

### 2.7. Coopération, sanction, réseaux, rationalité limitée

Biens publics et sanction coûteuse ([Fehr et Gächter, 2000](#ref-fehrgaechter2000) ; [Fehr et Schurtenberger, 2018](#ref-fehrschurtenberger2018)), liens faibles et brokerage ([Granovetter, 1973](#ref-granovetter1973) ; [Burt, 2004](#ref-burt2004)), rationalité limitée, stress et rareté ([Simon, 1955](#ref-simon1955behavioral) ; [McEwen, 1998](#ref-mcewen1998) ; [Hollon et al., 2015](#ref-hollon2015) ; [Shah et al., 2012](#ref-shah2012scarcity) ; [Shah et al., 2019](#ref-shah2019replication)) restent dans le référentiel. Nos données ne permettent de les tester que marginalement ; nous ne leur attribuons aucun résultat. Le *groupthink* reste hors du noyau explicatif ([Aldag et Fuller, 1993](#ref-aldagfuller1993)).

## 3. Le dispositif télévisuel fait partie du modèle

Nous séparons l'état du jeu de sa représentation :

$$
S_{KL}=T_{KL}(G_{ref}) \qquad O_{diffusé}=M_{prod}(S_{KL},A,C)
$$

où $$M_{prod}$$ représente sélection, montage et mise en récit, $$A$$ les actions des participants et $$C$$ le contexte de production. Les participants savent qu'ils sont filmés : la médiatisation est **condition d'action** autant que **condition d'observation** ([Corner, 2002](#ref-corner2002) ; [Couldry, 2004](#ref-couldry2004) ; [Andrejevic, 2004](#ref-andrejevic2004) ; [Jost, 2004](#ref-jost2004)).

Cette séparation a une conséquence pratique. Le vote est l'un des rares éléments de $$O_{diffusé}$$ que le montage ne peut pas réécrire : le décompte est montré, et les sources le recopient bulletin par bulletin. Les motifs déclarés, eux, passent par le confessionnal et le montage. Nous fondons donc les résultats sur **qui a écrit quel nom**, et jamais sur ce qui a été dit pour le justifier.

## 4. Un référentiel trans-domaines, pas un « graphe de la vraie vie »

$$G_{ref}=(V,E)$$ est un référentiel où $$V$$ contient des mécanismes documentés dans plusieurs littératures et $$E$$ des relations hypothétiques. La transformation $$T_{KL}$$ indique qualitativement que le dispositif renforce la sélection relative, réduit l'exit, rend les votes et les pivots plus conséquents, augmente l'importance locale des réputations, et retire contrats, assurance et innovation institutionnelle.

Les pondérations numériques des versions exploratoires ne servent pas de preuve. Cette version remplace leur rôle par une question plus simple : **pour chaque arête de $$T_{KL}$$ qui a une conséquence observable dans les votes, cette conséquence apparaît-elle ?**

## 5. Données et méthode

### 5.1. La base

Les données sont celles de ce site ; les chiffres de cette page suivent leurs mises à jour. Elles sont reconstruites à partir de trois sources croisées — les pages de saison de Wikipédia, celles du wiki Fandom francophone, et les pages individuelles de ce wiki — avec une provenance champ par champ ([les sources]({{ '/sources/' | relative_url }})).

<div class="tableau-large" markdown="1">

| Élément | Effectif |
|---|---:|
| Saisons diffusées | {{ a.saisons }} |
| Aventuriers distincts | {{ a.aventuriers }} |
| Participations | {{ a.participations }} |
| Conseils d'élimination, saisons terminées | {{ a.conseils }} |
| … dont décomptés au bulletin près | {{ a.conseils_complets }} |
| Bulletins | {{ a.bulletins }} |

</div>

Un contrôle automatique refuse toute incohérence connue : un immunisé éliminé, un votant déjà sorti, un total annoncé que ses bulletins contredisent. Les exceptions acceptées sont nommées une à une, avec leur raison. Avant toute analyse de cet article, une révision a corrigé 159 conseils qui portaient une panne silencieuse — coquilles de nom, votes noirs de l'éliminé lus comme des votes ordinaires, sorties sans vote comptées comme des conseils.

Les **sorties sans vote** (abandons, orientation, poteaux, duels, ambassadeurs, épreuves éliminatoires) ne sont pas des conseils et en sont exclues. Le **vote du jury final** est exclu : son sens est inversé.

### 5.2. Les tests

Chaque test oppose une statistique observée à sa distribution sous un **modèle nul de permutation** (10 000 tirages), construit pour respecter la structure du soir : l'éliminé est tiré au hasard **parmi les présents du conseil**, ce qui fixe la taille et la composition du camp ; ou les bulletins sont rebattus entre les votants d'un même conseil, sans qu'aucun ne puisse écrire son propre nom. Les {{ a.nb_tests }} tests du registre sont corrigés ensemble par Benjamini-Hochberg ; nous rapportons la p ajustée. Le registre complet est public ([la méthode]({{ '/methode/' | relative_url }})).

Deux règles de construction, chacune née d'un faux résultat corrigé sur le site, s'appliquent à toutes les mesures :

- **un épisode n'est pas un conseil** : un même soir peut en compter plusieurs (tour nul et second vote, deux tribus, finale) ; aucun rapprochement ne se fait sur le seul numéro d'épisode ;
- **le modèle nul doit faire varier la statistique mesurée** : un tirage qui laisse la statistique invariante rend un test vide, lu comme « non concluant ».

### 5.3. Statut de la confrontation

Les tests du registre ont été conçus et publiés **indépendamment** de cet article, sans référence à son cadre. Ce n'est pas un préenregistrement : la correspondance entre tests et mécanismes (tableau 2) a été établie après lecture des résultats. Pour limiter ce biais, nous rapportons **tous** les tests qui touchent un mécanisme du cadre, y compris ceux qui le contredisent ou ne concluent pas.

Ces tests sont **observationnels**. Un écart au modèle nul dit qu'un choix n'est pas aléatoire ; il ne dit pas quel motif l'a produit.

### 5.4. L'auto-description du dispositif

La production présente elle-même la réunification comme une recomposition — des stratégies, des relations ou de la nature de la compétition — et y associe la négociation des ambassadeurs. La version précédente en faisait un corpus. Nous le gardons pour ce qu'il est : la manière dont le dispositif se décrit, non ce que font les candidats. La section 6.3 confronte l'une à l'autre.

Le **pilote rétrospectif de neuf conseils** de la version précédente est retiré des résultats : codé sur des résumés postérieurs à l'issue, il était exposé à la fuite, et la base exhaustive le rend inutile.

## 6. Résultats

### 6.1. La compétence ne devient pas une menace — du moins pas aux épreuves

Le site estime une [force aux épreuves]({{ '/statistiques/force/' | relative_url }}) pour chaque aventurier, à partir de {{ a.force.epreuves }} épreuves de {{ a.force.saisons }} saisons, et classe chaque éliminé parmi les présents du soir (0 = le plus faible, 100 = le plus fort).

<div class="tableau-large" markdown="1">

| Test | Observé | Attendu sous le nul | p ajustée |
|---|---:|---:|---:|
| Rang de force de l'éliminé, après moins avant la réunification | {{ a.tests.fusion_force.observe }} points | {{ a.tests.fusion_force.attendu }} | {{ a.tests.fusion_force.p }} |
| Rang de force de l'éliminé choisi par les ambassadeurs | {{ a.tests.ambassadeurs_force.observe }} | {{ a.tests.ambassadeurs_force.attendu }} | {{ a.tests.ambassadeurs_force.p }} |

</div>

L'éliminé est au rang {{ a.force.rang_avant }} avant la réunification ({{ a.force.conseils_avant }} conseils mesurables) et {{ a.force.rang_apres }} après ({{ a.force.conseils_apres }} conseils). L'écart ne dépasse pas ce que le hasard produit. Les ambassadeurs, qui décident seuls, ne choisissent pas autrement qu'un tirage.

L'hypothèse 2.1 n'est donc pas confirmée **sous cette mesure**. Trois réserves bornent la conclusion. La force aux épreuves n'est qu'une compétence parmi d'autres : la compétence stratégique ou sociale n'est pas mesurée. Le test est peu puissant avant la réunification ({{ a.force.conseils_avant }} conseils). Enfin, une menace perçue peut être neutralisée par l'immunité, que le plus fort gagne plus souvent : un effet de ciblage pourrait exister et ne pas aboutir. Mais le résultat interdit d'écrire, comme le faisait la version précédente, que « la compétence devient une menace » sans qualification.

### 6.2. Les mécanismes relationnels dominent

Le tableau 2 rassemble les tests du registre qui touchent un mécanisme du cadre. « Points » désigne un écart de probabilité, en points de pourcentage. La dernière colonne renvoie à la page où le test est publié.

**Tableau 2 — Mécanismes du cadre et tests du registre**

<div class="tableau-large" markdown="1">

| Mécanisme (section) | Test | Observé | Attendu | p ajustée | Page |
|---|---|---:|---:|---:|---|
| Dépendance (2.3) | Partir quand plus aucun allié n'est présent, moins quand il en reste un | {{ a.tests.vote_isole.observe }} pts | {{ a.tests.vote_isole.attendu }} | {{ a.tests.vote_isole.p }} | [pire-place]({{ '/statistiques/pire-place/' | relative_url }}) |
| Coalition (2.2) | Voter ensemble après avoir voté ensemble, moins après s'être séparés | {{ a.tests.persistance_alliances.observe }} pts | {{ a.tests.persistance_alliances.attendu }} | {{ a.tests.persistance_alliances.p }} | [alliances]({{ '/statistiques/alliances/' | relative_url }}) |
| Coalition (2.2) | Part des bulletins visant un ancien co-votant | {{ a.tests.trahison.observe }} % | {{ a.tests.trahison.attendu }} % | {{ a.tests.trahison.p }} | [alliances]({{ '/statistiques/alliances/' | relative_url }}) |
| Réciprocité (2.2) | La cible de la fois d'avant écrit le nom de son auteur | {{ a.tests.retour_de_baton.observe }} % | {{ a.tests.retour_de_baton.attendu }} % | {{ a.tests.retour_de_baton.p }} | [conditionnelles]({{ '/statistiques/conditionnelles/' | relative_url }}) |
| Réputation (2.4) | Partir après avoir été visé, moins sans l'avoir été | {{ a.tests.menace_voix.observe }} pts | {{ a.tests.menace_voix.attendu }} | {{ a.tests.menace_voix.p }} | [conditionnelles]({{ '/statistiques/conditionnelles/' | relative_url }}) |
| Réputation (2.4) | Être visé après avoir été visé, moins sans l'avoir été | {{ a.tests.cible_persistante.observe }} pts | {{ a.tests.cible_persistante.attendu }} | {{ a.tests.cible_persistante.p }} | [conditionnelles]({{ '/statistiques/conditionnelles/' | relative_url }}) |
| Réputation (2.4) | Partir après 1 à 3 voix, moins après 4 ou plus | {{ a.tests.menace_sommet.observe }} pts | {{ a.tests.menace_sommet.attendu }} | {{ a.tests.menace_sommet.p }} | [conditionnelles]({{ '/statistiques/conditionnelles/' | relative_url }}) |
| Identité (2.6) | Après la réunification, part des bulletins visant sa tribu initiale | {{ a.tests.vote_bandeau_apres_fusion.observe }} % | {{ a.tests.vote_bandeau_apres_fusion.attendu }} % | {{ a.tests.vote_bandeau_apres_fusion.p }} | [qui-vise-qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}) |
| Identité (2.6) | Sorties consécutives du même camp après la réunification | {{ a.tests.decimation.observe }} | {{ a.tests.decimation.attendu }} | {{ a.tests.decimation.p }} | [alliances]({{ '/statistiques/alliances/' | relative_url }}) |
| Identité (2.6) | Partir quand sa tribu initiale est la moins représentée | {{ a.tests.bandeau_minoritaire.observe }} pts | {{ a.tests.bandeau_minoritaire.attendu }} | {{ a.tests.bandeau_minoritaire.p }} | [autour-du-feu]({{ '/statistiques/autour-du-feu/' | relative_url }}) |
| Catégorie (2.6) | Partir quand son sexe est le moins représenté | {{ a.tests.sexe_minoritaire.observe }} pts | {{ a.tests.sexe_minoritaire.attendu }} | {{ a.tests.sexe_minoritaire.p }} | [autour-du-feu]({{ '/statistiques/autour-du-feu/' | relative_url }}) |
| Conformité (2.5) | Partir après avoir voté avec la minorité | {{ a.tests.camp_perdant.observe }} pts | {{ a.tests.camp_perdant.attendu }} | {{ a.tests.camp_perdant.p }} | [conditionnelles]({{ '/statistiques/conditionnelles/' | relative_url }}) |
| Changement de régime (4) | Conseils où l'éliminé n'a pas la majorité, après moins avant la réunification | {{ a.tests.fusion_serre.observe }} pts | {{ a.tests.fusion_serre.attendu }} | {{ a.tests.fusion_serre.p }} | [réunification]({{ '/statistiques/reunification/' | relative_url }}) |
| Changement de régime (4) | Écart d'âge de l'éliminé à son camp, avant moins après | {{ a.tests.age_bascule_fusion.observe }} ans | {{ a.tests.age_bascule_fusion.attendu }} | {{ a.tests.age_bascule_fusion.p }} | [réunification]({{ '/statistiques/reunification/' | relative_url }}) |
| Changement de régime (4) | Part de femmes parmi les éliminés, après moins avant | {{ a.tests.fusion_sexe.observe }} pts | {{ a.tests.fusion_sexe.attendu }} | {{ a.tests.fusion_sexe.p }} | [réunification]({{ '/statistiques/reunification/' | relative_url }}) |
| Ambassadeurs (5.4) | Rang de survie ultérieure des ambassadeurs | {{ a.tests.ambassadeurs_survie.observe }} | {{ a.tests.ambassadeurs_survie.attendu }} | {{ a.tests.ambassadeurs_survie.p }} | [réunification]({{ '/statistiques/reunification/' | relative_url }}) |

</div>

Quatre lectures s'en dégagent.

**La dépendance a un coût mesurable.** Se retrouver sans aucun des aventuriers avec qui l'on a déjà voté augmente de {{ a.tests.vote_isole.valeur }} points la probabilité de sortir, quand le hasard en donnerait {{ a.tests.vote_isole.attendu }}. C'est la conséquence la plus directe de l'hypothèse 2.3 : dans une arène fermée, le lien local est une ressource, et son absence une exposition.

**Les coalitions persistent et protègent.** Deux aventuriers qui ont voté ensemble revotent ensemble bien plus souvent que deux qui se sont séparés ({{ a.tests.persistance_alliances.observe }} points), et l'on écrit moins souvent le nom d'un ancien co-votant que le hasard ne le voudrait ({{ a.tests.trahison.observe }} % contre {{ a.tests.trahison.attendu }} %). La « trahison » existe, mais moins qu'une indifférence aux alliances ne le produirait.

**Le ciblage s'entretient, sans sommet.** Avoir été visé expose à l'être encore et à partir. Mais survivre à un vote massif ne protège pas mieux que survivre à deux bulletins : la menace n'a pas de sommet. La forme réduite de la chaîne réputationnelle (2.4) est donc observée ; ses maillons intermédiaires ne le sont pas.

**L'identité de groupe survit à la disparition du groupe.** Après la réunification, on écrit le nom de quelqu'un de sa tribu initiale dans {{ a.tests.vote_bandeau_apres_fusion.observe }} % des bulletins, contre {{ a.tests.vote_bandeau_apres_fusion.attendu }} % attendus ; les sorties s'enchaînent par camp ; appartenir au camp minoritaire expose. Les tribus, artefacts de production, deviennent des identités effectives — exactement ce que prédit le paradigme des groupes minimaux ([Tajfel et Turner, 1979](#ref-tajfelturner1979)). En revanche, appartenir au **sexe** minoritaire du camp **protège** ({{ a.tests.sexe_minoritaire.observe }} points) : toutes les catégories ne fonctionnent pas comme des groupes. C'est un argument direct pour observer une conséquence avant de coder une identité.

La conformité (2.5) se lit, de justesse : avoir voté avec la minorité expose au conseil suivant (p ajustée {{ a.tests.camp_perdant.p }}). Une première rédaction de cette version concluait l'inverse ; la correction des sorties sans vote du 21 octobre 2026 a fait passer le seuil à ce résultat, qui reste fragile.

### 6.3. La réunification se lit dans les votes, pas seulement dans le discours

Le dispositif **se présente** comme changeant de régime à la réunification (5.4). Les votes le confirment : après la réunification, la part de conseils où l'éliminé ne réunit pas la majorité des voix augmente de {{ a.tests.fusion_serre.valeur }} points ; la part de femmes parmi les éliminés baisse de {{ a.tests.fusion_sexe.valeur }} points, alors que le modèle nul tient compte de la composition du camp.

L'âge, lui, ne permet pas de conclure. Avant la réunification, l'éliminé a en moyenne {{ a.age.avant }} de plus que la moyenne de son camp ce soir-là ; après, {{ a.age.apres }} de moins. La bascule, {{ a.age.bascule }} sur {{ a.age.conseils }} conseils, va dans le même sens, mais ne passe pas le seuil (p ajustée {{ a.tests.age_bascule_fusion.p }}). Une première rédaction de cette version la donnait retenue de justesse, en prévenant qu'une saison mal relevée suffirait à la faire repasser dessous. C'est ce qui est arrivé le 21 octobre 2026 : trente sorties par épreuve éliminatoire, jusque-là comptées comme des conseils sans bulletin, ont été rendues à leur nature.

L'auto-description et le comportement coïncident sur ce point. Les ambassadeurs, eux, ne partent pas plus tôt de façon établie : leur rang de survie ultérieure ({{ a.tests.ambassadeurs_survie.observe }} contre {{ a.tests.ambassadeurs_survie.attendu }} attendus) va dans ce sens, mais ne passe pas le seuil (p ajustée {{ a.tests.ambassadeurs_survie.p }}). Le résultat a franchi le seuil trois fois, dans un sens puis dans l'autre, au fil des corrections des 21 et 22 octobre 2026 : il ne s'affirme pas.

### 6.4. L'ordinaire d'abord : la fréquence des issues d'un conseil

La version précédente avait verrouillé, avant un conseil, une distribution de probabilité sur la nature de son issue. Le tableau 3 la confronte à la fréquence observée sur toutes les saisons terminées.

**Tableau 3 — Issues d'un conseil**

<div class="tableau-large" markdown="1">

| Issue | Version précédente | Saisons terminées ({{ a.issues.conseils }} conseils) |
|---|---:|---:|
| Élimination ordinaire | 42,9 % | {{ a.issues.ordinaire }} % |
| Égalité puis second vote | 28,6 % | {{ a.issues.egalite_revote }} % |
| Renversement par un objet d'immunité | 14,3 % | {{ a.issues.renversement }} % |
| Égalité tranchée sans second vote | 14,3 % | {{ a.issues.egalite_tranchee }} % |

</div>

Ces fréquences sont la seule mesure de cet article qui ne figure pas ailleurs sur le site. L'unité est le **conseil décisif** — celui dont sort un éliminé rattaché. Il est classé « égalité puis second vote » si le conseil qui le précède immédiatement, le même soir, est un tour nul, ou si la [boule noire]({{ '/statistiques/conseils/' | relative_url }}) l'a tranché — elle ne se tire qu'après un second vote resté à égalité ; « renversement » si un objet d'immunité a annulé des voix et que, sans lui, le protégé en aurait reçu plus que l'éliminé ; « égalité tranchée » si le conseil décisif lui-même finit à égalité en tête. Les {{ a.issues.sans_bulletin }} conseils décisifs dont la source ne donne aucun bulletin ne sont pas classés.

L'issue la plus probable de la distribution verrouillée était la bonne : le conseil visé par la prédiction s'est achevé par une élimination ordinaire. Mais la distribution sous-estimait nettement l'issue la plus fréquente, et surestimait d'autant les trois autres. Un verrou prospectif protège contre la réécriture après coup ; il ne protège pas contre une distribution mal ancrée. **Avant de prédire une issue, il faut connaître sa fréquence de base** : c'est le premier concurrent qu'une prédiction doit battre, et celle de la version précédente ne le battait pas.

### 6.5. La prévision individuelle

La version précédente s'abstenait de désigner l'éliminé. Le site publie un modèle qui le tente : entraîné sur toutes les saisons sauf une, il classe les présents de chaque conseil de la saison exclue du plus au moins menacé. L'éliminé réel tombe en moyenne à la position normalisée {{ a.tests.prevision_conseil.observe }}, quand le hasard donne {{ a.tests.prevision_conseil.attendu }} (p ajustée {{ a.tests.prevision_conseil.p }}) ([le pronostic]({{ '/statistiques/pronostic/' | relative_url }})). Le signal est réel et modeste : il ne désigne pas l'éliminé, il le place un peu plus haut que la moyenne. À l'inverse, l'âge, le sexe, le métier et la couleur ne placent pas le futur vainqueur mieux que le hasard (p ajustée {{ a.tests.pronostic_vainqueur.p }}).

## 7. Hypothèses mécanistes, après confrontation

<div class="tableau-large" markdown="1">

| Chaîne | Version précédente | Cette version |
|---|---|---|
| Faible exit → dépendance → valeur des coalitions | hypothèse | **conséquences observées** : coût de l'isolement, persistance et protection des coalitions (6.2) |
| Réputation → menace perçue → ciblage | hypothèse | **forme réduite observée** : ciblage persistant ; maillons intermédiaires non mesurés (6.2) |
| Compétence → menace en phase individuelle | présentée comme mécanisme central | **non observée** à la mesure de la force aux épreuves (6.1) |
| Catégorisation → identité de groupe | hypothèse | **observée pour la tribu initiale, inversée pour le sexe** (6.2) |
| Conformité / cascade | distinction conceptuelle | **observée, de justesse** (6.2) |
| Réunification → changement de régime | auto-description | **auto-description confirmée par les votes** (6.3) |
| Rareté → stress → simplification | hypothèse | **non testée** |

</div>

Une séquence de conseil, aussi parlante soit-elle, reste une illustration et non une preuve. Elle relève de $$O_{diffusé}$$ : le motif est rapporté, le vote est observé.

## 8. Ce que le dispositif retire

Exit et mobilité, contrats et tiers garant, assurance, création de valeur positive-sum, innovation institutionnelle ([Hirschman, 1970](#ref-hirschman1970) ; [Ostrom, 1990](#ref-ostrom1990)) restent absents. Les résultats de 6.2 leur donnent une portée concrète : en l'absence de contrat, la seule garantie d'une alliance est sa persistance, et celle-ci est mesurable ; en l'absence d'exit, la perte du dernier allié est l'une des situations les plus exposées du jeu.

## 9. Transportabilité

$$
Présence \neq Intensité \neq Effet \neq Recommandation
$$

Le pouvoir-dépendance est transportable comme structure. La « compétence comme menace », déjà conditionnelle à un tournoi, n'est pas même établie dans le tournoi qui en est l'exemple canonique. L'article ne produit aucune « stratégie de vie ».

## 10. Limites

1. Sélection non représentative des participants, et casting construit (le site montre une parité hommes-femmes plus stricte que ne le donnerait le hasard).
2. Réactivité au dispositif, et expérience antérieure des participants qui reviennent.
3. Montage : les votes sont robustes au montage, les motifs ne le sont pas.
4. Sources secondaires : la base repose sur deux wikis collaboratifs, recoupés entre eux ; {{ a.conseils_incomplets }} conseils de saisons terminées ne sont pas décomptés au bulletin près.
5. Correspondance tests-mécanismes établie après lecture des résultats (5.3).
6. Tests observationnels : un écart au hasard n'identifie pas son motif.
7. Force aux épreuves comme seule mesure de compétence.
8. Aucune série de prédictions verrouillées : la calibration n'est mesurée que contre les fréquences passées.
9. Accord inter-codeurs absent pour le codage des mécanismes ; les bulletins, eux, ne sont pas codés mais recopiés.
10. Hétérogénéité des traditions théoriques mobilisées.

## 11. Discussion

La version précédente avait resserré la thèse sous l'effet de la critique. Celle-ci la resserre sous l'effet des données, et dans une direction différente.

Les mécanismes qui se lisent le mieux dans les votes ne sont pas ceux qui structurent le récit habituel de l'émission. Le récit privilégie la compétence menaçante, le stratège démasqué, le retournement. Les votes privilégient l'appartenance d'origine, la persistance des alliances et le coût de l'isolement : des mécanismes lents, peu spectaculaires, qui relèvent de la dépendance et de l'identité plutôt que du calcul. C'est un résultat sur $$M_{prod}$$ autant que sur $$S_{KL}$$ : ce que le montage met en avant n'est pas ce qui pèse le plus dans les décisions.

Nous soutenons donc que :
1. plusieurs phénomènes visibles se décrivent par des mécanismes étudiés indépendamment ;
2. les règles du jeu changent leurs conditions de pertinence, et la réunification en est la démonstration la plus nette ;
3. les mécanismes relationnels l'emportent, dans les votes, sur la compétence ;
4. l'objet diffusé est médiatisé et performé, et sa mise en récit ne coïncide pas avec ce que révèlent les votes.

## 12. Conclusion

*Koh-Lanta* peut servir de **cas-limite institutionnel** pour étudier comment une architecture fermée repondère des mécanismes sociaux ordinaires. Confronté à tous ses votes, le cadre tient sur la dépendance, la coalition et l'identité de groupe ; il cède sur la compétence comme menace ; et toute prévision doit d'abord se mesurer à la fréquence de l'ordinaire.

La prochaine étape n'est plus de constituer une base — elle existe — mais de **verrouiller des prédictions en série**, ancrées sur les fréquences de base, et de mesurer la compétence autrement qu'aux épreuves.

> **Koh-Lanta n'est pas un modèle de la vraie vie ; il rend certaines dépendances institutionnelles exceptionnellement visibles.**

## Données

Données, sources et registre des tests : sur ce site, pages [les sources]({{ '/sources/' | relative_url }}) et [la méthode]({{ '/methode/' | relative_url }}). Fréquences des issues d'un conseil : construction décrite en 6.4.

## Références

- <span id="ref-akerlof1970lemons"></span>Akerlof, George A. (1970). The Market for « Lemons »: Quality Uncertainty and the Market Mechanism. *The Quarterly Journal of Economics*, 84(3), 488–500. <https://doi.org/10.2307/1879431>
- <span id="ref-aldagfuller1993"></span>Aldag, Ramon J. et Fuller, Sally R. (1993). Beyond fiasco: A reappraisal of the groupthink phenomenon and a new model of group decision processes. *Psychological Bulletin*, 113(3), 533–552. <https://doi.org/10.1037/0033-2909.113.3.533>
- <span id="ref-andrejevic2004"></span>Andrejevic, Mark (2004). *Reality TV: The Work of Being Watched*. Rowman & Littlefield.
- <span id="ref-bikhchandani1998cascades"></span>Bikhchandani, Sushil, Hirshleifer, David et Welch, Ivo (1998). Learning from the Behavior of Others: Conformity, Fads, and Informational Cascades. *Journal of Economic Perspectives*, 12(3), 151–170. <https://doi.org/10.1257/jep.12.3.151>
- <span id="ref-bikhchandani2024cascades"></span>Bikhchandani, Sushil, Hirshleifer, David, Tamuz, Omer et Welch, Ivo (2024). Information Cascades and Social Learning. *Journal of Economic Literature*, 62(3), 1040–1093. <https://doi.org/10.1257/jel.20241472>
- <span id="ref-burt2004"></span>Burt, Ronald S. (2004). Structural Holes and Good Ideas. *American Journal of Sociology*, 110(2), 349–399. <https://doi.org/10.1086/421787>
- <span id="ref-corner2002"></span>Corner, John (2002). Performing the Real: Documentary Diversions. *Television & New Media*, 3(3), 255–269. <https://doi.org/10.1177/152747640200300302>
- <span id="ref-couldry2004"></span>Couldry, Nick (2004). Teaching Us to Fake It: The Ritualized Norms of Television's « Reality » Games. Dans Murray, Susan et Ouellette, Laurie (dir.), *Reality TV: Remaking Television Culture*, p. 57–74. New York University Press.
- <span id="ref-emerson1962"></span>Emerson, Richard M. (1962). Power-Dependence Relations. *American Sociological Review*, 27(1), 31–41. <https://doi.org/10.2307/2089716>
- <span id="ref-fehrgaechter2000"></span>Fehr, Ernst et Gächter, Simon (2000). Cooperation and Punishment in Public Goods Experiments. *American Economic Review*, 90(4), 980–994. <https://doi.org/10.1257/aer.90.4.980>
- <span id="ref-fehrschurtenberger2018"></span>Fehr, Ernst et Schurtenberger, Ivo (2018). Normative foundations of human cooperation. *Nature Human Behaviour*, 2, 458–468. <https://doi.org/10.1038/s41562-018-0385-5>
- <span id="ref-frohlich1975"></span>Frohlich, Norman (1975). The Instability of Minimum Winning Coalitions. *American Political Science Review*, 69(3), 943–946. <https://doi.org/10.2307/1958408>
- <span id="ref-granovetter1973"></span>Granovetter, Mark S. (1973). The Strength of Weak Ties. *American Journal of Sociology*, 78(6), 1360–1380. <https://doi.org/10.1086/225469>
- <span id="ref-hillman2009"></span>Hillman, Amy J., Withers, Michael C. et Collins, Brian J. (2009). Resource Dependence Theory: A Review. *Journal of Management*, 35(6), 1404–1427. <https://doi.org/10.1177/0149206309343469>
- <span id="ref-hirschman1970"></span>Hirschman, Albert O. (1970). *Exit, Voice, and Loyalty: Responses to Decline in Firms, Organizations, and States*. Harvard University Press.
- <span id="ref-hollon2015"></span>Hollon, Nick G., Burgeno, Lauren M. et Phillips, Paul E. M. (2015). Stress effects on the neural substrates of motivated behavior. *Nature Neuroscience*, 18, 1405–1412. <https://doi.org/10.1038/nn.4114>
- <span id="ref-jost2004"></span>Jost, François (2004). *La télévision du quotidien : entre réalité et fiction*. De Boeck / INA.
- <span id="ref-lazearrosen1981tournaments"></span>Lazear, Edward P. et Rosen, Sherwin (1981). Rank-Order Tournaments as Optimum Labor Contracts. *Journal of Political Economy*, 89(5), 841–864. <https://doi.org/10.1086/261010>
- <span id="ref-mcewen1998"></span>McEwen, Bruce S. (1998). Stress, Adaptation, and Disease: Allostasis and Allostatic Load. *Annals of the New York Academy of Sciences*, 840, 33–44. <https://doi.org/10.1111/j.1749-6632.1998.tb09546.x>
- <span id="ref-nowaksigmund1998"></span>Nowak, Martin A. et Sigmund, Karl (1998). Evolution of indirect reciprocity by image scoring. *Nature*, 393, 573–577. <https://doi.org/10.1038/31225>
- <span id="ref-ostrom1990"></span>Ostrom, Elinor (1990). *Governing the Commons: The Evolution of Institutions for Collective Action*. Cambridge University Press.
- <span id="ref-riker1962"></span>Riker, William H. (1962). *The Theory of Political Coalitions*. Yale University Press.
- <span id="ref-shah2012scarcity"></span>Shah, Anuj K., Mullainathan, Sendhil et Shafir, Eldar (2012). Some consequences of having too little. *Science*, 338(6107), 682–685. <https://doi.org/10.1126/science.1222426>
- <span id="ref-shah2019replication"></span>Shah, Anuj K., Mullainathan, Sendhil et Shafir, Eldar (2019). An exercise in self-replication: Replicating Shah, Mullainathan, and Shafir (2012). *Journal of Economic Psychology*, 75, 102127. <https://doi.org/10.1016/j.joep.2018.12.001>
- <span id="ref-shapleyshubik1954"></span>Shapley, L. S. et Shubik, Martin (1954). A Method for Evaluating the Distribution of Power in a Committee System. *American Political Science Review*, 48(3), 787–792. <https://doi.org/10.2307/1951053>
- <span id="ref-simon1955behavioral"></span>Simon, Herbert A. (1955). A Behavioral Model of Rational Choice. *The Quarterly Journal of Economics*, 69(1), 99–118. <https://doi.org/10.2307/1884852>
- <span id="ref-spence1973signaling"></span>Spence, Michael (1973). Job Market Signaling. *The Quarterly Journal of Economics*, 87(3), 355–374. <https://doi.org/10.2307/1882010>
- <span id="ref-tajfelturner1979"></span>Tajfel, Henri et Turner, John C. (1979). An Integrative Theory of Intergroup Conflict. Dans Austin, William G. et Worchel, Stephen (dir.), *The Social Psychology of Intergroup Relations*, p. 33–47. Brooks/Cole.
{: .references}
