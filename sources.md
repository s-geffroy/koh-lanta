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

## La troisième source : une page par aventurier

Les tables de saison, quelle que soit leur origine, ne portent ni la résidence
sur les éditions anciennes, ni le détail des tribus avec leurs jours, ni le
palmarès d’épreuves. Le wiki Fandom a autre chose : **une page par aventurier**,
avec une fiche — l’*Infobox Aventuriers* — qui donne tout cela, saison par
saison, pour quelqu’un qui en a joué quatre comme pour quelqu’un qui en a joué
une.

{{ site.data.stats.completude.comblees }} valeurs manquantes ont été comblées
par ces fiches. Elles n’ont **jamais** remplacé une valeur déjà établie par une
table : une fiche est saisie à la main par un lecteur, une table est relue par
beaucoup. Les désaccords sont comptés et laissés au rapport d’extraction, pas
tranchés en silence.

Ces pages ont aussi réglé un problème que les tables ne pouvaient pas voir.

- **Sept aventuriers n’avaient qu’un prénom.** Les éditions de retour présentent
  parfois les revenants par leur seul prénom, et quand plusieurs personnes du
  jeu de données portent ce prénom, le rattachement automatique s’abstient. Le
  wiki classe ses pages par saison : une seule « Victor » est classée dans
  *La Guerre des chefs*, et c’est Victor Rollinger. Sept noms de famille ont été
  rendus de cette façon ; un seul résiste, la Sabira de *Panama*, qui n’a pas de
  page.
- **Trois participations comptaient pour deux personnes.** « Phil Bizet » et
  « Philippe Bizet », « Clémentine Julien » et « Clémentine Jullien » sont deux
  orthographes d’une même personne — et sur le wiki, deux titres qui **renvoient
  à la même page**. Deux identifiants dont la page a la même empreinte sont donc
  la même personne, et c’est la page qui dit lequel des deux noms est le bon.
  Le nombre de personnes distinctes passe de 535 à
  {{ site.data.stats.general.personnes }}.

Limite, et elle est réelle :
{{ site.data.stats.completude.sans_fiche }} participations sur
{{ site.data.stats.completude.participations }} n’ont aucune fiche individuelle
exploitable — les castings les plus anciens, et l’édition de célébrités de 2012,
dont les invités n’ont pas de page. Ce qui manque encore manque surtout là.

## Deux sources de référence, pour comparer

**[Le fichier des prénoms de l’INSEE](https://www.insee.fr/fr/statistiques/8595130)**
— nombre de naissances par prénom, par sexe et par année depuis 1900, sous
[licence ouverte v2](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
Il ne sert qu’à une chose : donner un point de comparaison aux
[prénoms des aventuriers]({{ '/statistiques/prenoms/' | relative_url }}).

**[Les estimations de population de l’INSEE](https://www.insee.fr/fr/statistiques/8560704)**
— population au 1<sup>er</sup> janvier par département, sexe et groupe d’âges,
séries depuis 1990, même licence. Elles servent au seul calcul de
[l’origine géographique]({{ '/statistiques/geographie/' | relative_url }}) : sans
elles, « vingt-quatre Parisiens » ne veut rien dire.

Dans les deux cas, le sous-ensemble effectivement lu — nos prénoms et nos années
de naissance ; les départements et les années de nos saisons — est versionné
dans le dépôt, comme le wikitexte brut : c’est la preuve de provenance, et elle
permet de refaire le calcul sans redemander les fichiers complets à l’INSEE.

## Les audiences

{% assign au = site.data.audiences %}

**[L’article général de Wikipédia](https://fr.wikipedia.org/wiki/Koh-Lanta)**
porte un tableau d’audiences que ce site a longtemps ignoré : pour chaque
saison, l’audience du lancement, celle de la finale, la moyenne, la part de
marché et — sur douze saisons — les recettes publicitaires, chaque ligne
appuyée sur une source de presse. Les articles de saison y ajoutent le détail
**épisode par épisode** quand ils l’ont.

- {{ au.saisons_couvertes }} saisons sur {{ au.saisons_diffusees }} ont une
  audience de saison. La seule qui manque est celle en cours.
- {{ au.episodes | size }} mesures épisode par épisode, sur
  {{ au.saisons_par_episode | size }} saisons.

Le contrôle est direct et il est publié : sur les quatorze saisons où l’on a à
la fois le détail et la moyenne annoncée, **douze concordent à 0,5 % près**. Les
deux autres — *La Revanche des héros* et *L’Île des héros* — s’écartent de 5 %,
et l’écart vient de la source, dont le tableau ne s’accorde pas avec sa propre
ligne de synthèse. Rien n’est corrigé à la main.

Limite de nature : c’est l’audience **veille**, en direct. Le rattrapage n’y est
pas, et il pèse aujourd’hui près d’un quart de l’audience du programme.

## Un nom lu dans la prose, et ce que ça coûte

{% assign ng = site.data.ambassadeurs %}

Une seule information de ce site ne vient pas d’un tableau : **le nom des
ambassadeurs**. Il n’apparaît que dans une note de bas de page — « <em>Les deux
ambassadeurs (Léa et Pauline) se mettent d’accord pour éliminer Ricky.</em> »
Lire de la prose est faillible, et la seule réponse honnête est de mesurer.

<div class="constat">
  <p><b>{{ ng.nommees }} ambassades sur {{ ng.ambassades }}</b> livrent leurs
  noms — {{ ng.part_nommees }} %. Là où les deux sources les nomment, elles
  s’accordent {{ ng.sources_accord }} fois sur
  {{ ng.sources_accord | plus: ng.sources_desaccord }}.</p>
</div>

Trois contrôles écartent une lecture douteuse : le nom doit désigner un
participant de la saison **sans homonyme**, l’ambassadeur doit être **encore en
jeu** à cet épisode, et le nombre de noms lus doit correspondre à celui que la
note annonce. Ce dernier contrôle écarte une saison où la note dit « deux
ambassadeurs » avant d’ajouter une « ambassadrice secrète ».

Et une divergence a été trouvée : sur <i>Les Reliques du destin</i>, Wikipédia
compte Jade parmi les quatre ambassadeurs, Fandom compte Cynthia. Aucun des deux
n’est retenu. Elle n’est apparue qu’après correction d’un motif de lecture trop
strict qui ne lisait qu’une des deux sources : **une comparaison ne vaut que si
les deux côtés ont vraiment été lus**, et le premier chiffrage annonçait à tort
zéro divergence.

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
  ailleurs ;
- `fandom (page individuelle)` — un champ vide comblé par la fiche de
  l’aventurier ;
- `categorie Fandom de la saison` — un nom de famille rendu à un prénom nu ;
- `page Fandom commune (redirection)` — deux orthographes réunies en une
  personne.

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

**Les lieux.** Les fiches individuelles donnent tantôt le département, tantôt la
ville, tantôt une province d’Ancien Régime, avec une orthographe libre. Une
table fermée les ramène à la graphie du fichier INSEE — sans quoi « Toulouse »
et « Haute-Garonne » sont deux endroits, et la comparaison avec la population
perd les deux. Les cas ambigus n’y figurent pas : « Brassac » est dans le Tarn
*et* dans le Puy-de-Dôme, « Mauléon » dans les Deux-Sèvres *et* les
Pyrénées-Atlantiques. Ces deux-là restent tels quels, et hors du calcul.

## Ce qui manque

Le jeu de données n’est pas complet, et le dire fait partie du travail. Voici la
mesure exacte, champ par champ. Elle se recalcule à chaque construction : aucune
phrase de cette page n’a besoin d’être reprise quand une valeur est trouvée.

{% assign co = site.data.stats.completude %}

<div class="constat">
  <p><b>{{ co.part_remplie }} %</b> des
  {{ co.valeurs_suivies }} valeurs suivies sont renseignées —
  {{ co.champs_suivis }} champs sur {{ co.participations }} participations.
  {{ co.champs_complets }} champs n’ont plus aucun trou.</p>
</div>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Champ</th><th class="nombre">Renseigné</th><th class="nombre">Manquant</th>
  <th class="nombre">Part</th><th class="nombre">Dont fiche individuelle</th>
</tr></thead>
<tbody>
{% for c in co.champs %}
<tr>
  <td>{{ c.libelle }}</td>
  <td class="nombre">{{ c.remplis }}</td>
  <td class="nombre">{{ c.manquants }}</td>
  <td class="nombre" data-val="{{ c.part }}">{{ c.part }} %</td>
  <td class="nombre">{{ c.depuis_page_individuelle }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Les trois derniers champs — rang final, victoires collectives et
individuelles — <strong>n’existent que par les fiches individuelles</strong> :
aucune table de saison ne les porte. Ils sont donc renseignés là où une fiche
existe, et nulle part ailleurs. Le rang final se contrôle contre le jour de
sortie : sur 27 saisons sur 34, les deux classent les aventuriers dans
exactement le même ordre.</p>

<p class="note">La même mesure, <strong>édition par édition</strong> et type de
donnée par type de donnée, tient sur une seule grille :
<a href="{{ '/completude/' | relative_url }}">Ce qu’on sait de chaque
édition</a>.</p>

Ce qui reste, et pourquoi :

- **Le dépouillement des conseils est partiel.** Sur
  {{ site.data.stats.conseils.conseils }} conseils relevés,
  {{ site.data.stats.conseils.conseils_complets }} ont un dépouillement dont on
  peut garantir qu’il est complet. Les analyses bulletin par bulletin ne portent
  que sur ceux-là ; les agrégats — qui part, avec combien de voix — utilisent
  tous les conseils. Deux causes, mesurées : **245 conseils n’annoncent aucun
  décompte** — la source ne dit pas combien de voix ont été exprimées, donc la
  complétude n’y est pas vérifiable ; et **163 annoncent un décompte que le
  tableau ne remplit pas entièrement**, dont 69 à un seul bulletin près. Ceux-là
  ont été inspectés cellule par cellule : les cases sont **vides dans la source**.
  Ce n’est pas une lecture qui échoue, c’est un wiki qui n’a pas tout noté.
- **Les épreuves ne couvrent pas toutes les saisons.**
  {{ site.data.stats.epreuves.saisons_couvertes }} saisons sur 34 ont un bilan
  épisode par épisode exploitable ; les cinq autres
  ({{ site.data.stats.epreuves.saisons_sans_donnee | join: ", " }}) n’en ont
  pas. Les épreuves de finale sont exclues : les tableaux sources y changent de
  colonnes et listent les qualifiés plutôt que le vainqueur. Quant à la
  **nature** des épreuves, le wiki la donne — {{ site.data.epreuves_nommees.nb_epreuves }}
  pages d’épreuves récurrentes, typées — mais sans le numéro d’épisode, si bien
  que seules {{ site.data.epreuves_nommees.raccord.part_raccordee }} % des
  épreuves relevées peuvent la recevoir, et pas au hasard.
  [Les épreuves]({{ '/statistiques/epreuves/' | relative_url }}) le mesure.
- **Les colliers d’immunité ne sont détaillés que sur
  {{ site.data.stats.colliers.saisons_couvertes }} saisons.** Les autres les
  mentionnent sans donner leur destin. Et seuls les *colliers* sont suivis :
  armes secrètes, totem maudit et talisman du feu sacré sont des mécaniques
  distinctes, absentes de ces comptes. En revanche le **fait qu’un objet ait
  été joué** se lit dans les bulletins barrés, sur
  {{ site.data.stats.conseils.saisons_avec_objet_joue }} saisons : c’est une
  information plus pauvre — on ne sait pas de quel objet il s’agit — mais
  beaucoup plus large.
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

## Deux autres pannes silencieuses, et ce qu’elles cachaient

La réparation du `75px` racontée plus haut n’était pas la dernière. Deux autres
défauts d’extraction ne produisaient **aucune erreur** : simplement, des données
manquaient.

**Les bulletins enveloppés dans une pastille de tribu.** Depuis 2020, les
tableaux de Fandom n’écrivent plus le nom visé en clair : ils l’enveloppent dans
un modèle, `{% raw %}{{Tribebox-bw|Ilog|Lili}}{% endraw %}`, dont le premier
paramètre est la tribu et le second le nom. Le nettoyage général du wikitexte
retire les modèles — et donc effaçait le nom. Résultat :
*Les 4 Terres* et *Le Totem maudit* n’avaient **aucun bulletin**, et six autres
saisons récentes en avaient la moitié. Le second paramètre est désormais sorti
du modèle avant nettoyage : **{{ site.data.stats.conseils.bulletins }} bulletins
au lieu de 3 206**, et {{ site.data.stats.conseils.conseils_complets }} conseils
au dépouillement garanti complet au lieu de 264.

Deux autres bugs de lecture tombaient au même endroit : un intitulé de ligne
écrit `|►Votes` — avec le tuyau du tableau resté collé — faisait chercher les
votants tout en bas de la table, où il n’y en a pas ; et le nom du votant était
lu dans la première colonne d’étiquette alors qu’il est dans la dernière, quand
la ligne y loge d’abord ses pastilles de tribu.

Un contrôle refuse désormais qu’une saison entière annonce des décomptes de
voix sans qu’un seul bulletin en soit lu. C’est exactement la forme qu’avait
cette panne, et elle ne pouvait pas se voir autrement.

**Un article qui n’était pas le bon.** Le récupérateur demandait à Wikipédia
« Koh-Lanta: Bocas del Toro », que le wiki **redirige vers l’article général du
programme** — dix-neuf kilo-octets, qui passaient donc tous les contrôles de
taille. Le fichier était dans le dépôt depuis le début, présenté comme la source
de la saison 3. Il n’apportait rien, mais il mentait sur sa provenance. Le
récupérateur vérifie maintenant que la page atteinte est bien celle demandée, et
refuse la redirection vers un autre article ; la saison 3 est désormais
déclarée sans source Wikipédia, ce qu’elle a toujours été.

## Une épreuve croisée sur les bulletins

{% assign cv = site.data.croisement_votes %}

Sur une partie des saisons, les deux sources publient **chacune** leur matrice
des votes. Jusqu’ici on gardait la plus riche et on jetait l’autre. C’est du
gâchis : la seconde permet de vérifier la première.

<div class="constat">
  <p>{{ cv.bulletins_communs }} bulletins figurent dans les deux sources.
  <b>{{ cv.identiques }} sont identiques — {{ cv.part_identiques }} %.</b>
  {{ cv.divergents }} divergent.</p>
  <p>C’est la première mesure directe de la fiabilité du relevé des votes, et
  elle est rassurante. Les {{ cv.divergents }} divergences sont toutes deux le
  même problème : deux Jérôme dans <i>La Revanche des 4 Terres</i>, que les
  deux wikis distinguent différemment.</p>
</div>

La seconde source apporte en outre
{{ cv.ajoutes_par_seconde_source }} bulletins que la première ignore. C’est
peu, et c’est délibérément peu : **l’appariement n’est fait que lorsqu’un
épisode ne contient qu’un seul conseil de chaque côté.** Un épisode à deux
conseils — une égalité suivie d’un second vote — ne se découpe pas de la même
façon d’une source à l’autre, et les apparier au nom de l’éliminé confondrait
le premier tour avec le second.

<p class="note">Cette prudence n’est pas théorique : une première version
appariait sur l’épisode <em>et</em> le nom de l’éliminé, sans vérifier
l’unicité. Elle annonçait 39 bulletins gagnés et 16 divergences — dont sept
fabriquées de toutes pièces par la confusion des deux tours d’un même épisode.
La règle stricte donne moins de bulletins et un taux d’accord plus élevé : les
deux chiffres sont vrais, les précédents ne l’étaient pas.</p>

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
