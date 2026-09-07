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

## La fin de saison, lue dans deux colonnes et dans le récit

{% assign fc = site.data.stats.finale.couverture %}

Deuxième information à ne pas venir d’un tableau de résultats : **qui a gagné
l’épreuve des poteaux**. `epreuves.yml` ne porte aucun nom d’épreuve, et le
catalogue des épreuves nommées ne raccorde « Poteaux » à aucune saison. Pire :
la dernière épreuve d’immunité individuelle relevée **n’est pas** les poteaux —
pour huit saisons, son vainqueur est justement la personne portée
`elimine_poteaux`. La déduire aurait donné un résultat faux et silencieux.

Deux gisements ont été croisés : la colonne « Épreuve des poteaux » du tableau
de déroulement des deux wikis, et les notes de bas de page, dont la tournure est
stable — « <em>Cynthia, vainqueur de l’épreuve des poteaux, décide d’affronter
Clarisse</em> ».

<div class="constat">
  <p><b>{{ fc.vainqueur_des_poteaux_connu }} saisons sur
  {{ fc.saisons_au_format }}</b> livrent le vainqueur des poteaux —
  {{ fc.part_poteaux }} %. Le choix du finaliste n’est explicitement énoncé que
  pour {{ fc.choix_atteste }} d’entre elles ; ailleurs, l’autre finaliste est
  déduit par soustraction et le champ le dit.</p>
</div>

L’ordre d’arrivée à l’orientation pose une question de nature différente : les
sources listent les qualifiés, mais **rien n’annonce que cette liste soit
ordonnée**. Deux vérifications indépendantes ont donc été montées, et elles
tournent à chaque régénération. Le récit nomme parfois un rang — « <em>Loïc
trouve le premier poignard</em> » : sur {{ fc.saisons_ordre_teste }} saisons,
**{{ fc.rangs_confirmes }} rangs** sont ainsi confrontables à la place que la
cellule leur donne, et {{ fc.rangs_dementis }} la contredit. Et les deux wikis,
rédigés séparément, écrivent le même ordre sur {{ fc.ordre_concordant }} des
{{ fc.ordre_croisable }} saisons où les deux le détaillent.

`verifie.py` échoue si un seul rang vient à être démenti : le jour où l’ordre
cessera d’être l’ordre d’arrivée,
[la page qui en vit]({{ '/statistiques/finale/' | relative_url }}) cessera
d’être publiable, et on le saura sans avoir à y penser.

## Le scrutin final, retrouvé en deux fois

{% assign jj = site.data.stats.jury %}

Le vote du jury tient **une colonne par finaliste** dans les matrices sources :
celle du gagnant et celle du battu. Seule la première était reconnue. Les autres
étaient rangées du côté des éliminations, où leurs bulletins comptaient à
l’envers — un juré qui écrit « Cynthia » pour la couronner était compté comme
votant contre elle.

La première réparation s’est appuyée sur le **titre** de la colonne :
« Finaliste », « Gagnant ». Elle a rendu quarante-neuf bulletins. Mais dix-sept
saisons ne titrent pas leur colonne finale : elles lui donnent simplement le
**numéro de l’épisode**, comme à un conseil ordinaire, et elles échappaient donc
au titre.

La seconde réparation ne regarde plus le titre mais la **place**. Le scrutin
final occupe les dernières colonnes de la matrice, une par personne arrivée au
bout — et celui qu’on y donne pour « éliminé » est un **finaliste déclaré**, ce
qui est impossible pour une vraie élimination : un finaliste, par définition, va
jusqu’au vote. Les deux conditions réunies, sans jamais l’une sans l’autre,
identifient la colonne sans ambiguïté.

<div class="constat">
  <p><b>67 scrutins de jury</b> sur {{ jj.saisons }} saisons, contre 32 avant
  les réparations, et <b>300 bulletins</b> contre 196 —
  {{ jj.effectif }} colonnes de lauréat, le reste étant celles des finalistes
  battus. <b>Il n’en manque plus aucun</b> : chaque voix annoncée par les
  sources est lue et attribuée.</p>
  <p>Le décompte annoncé et les bulletins relevés coïncident désormais
  <b>partout</b>.</p>
</div>

Restaient cinq colonnes dont le total annoncé contredisait les bulletins, et
elles ne disaient pas la même chose. Sur <i>Les Armes secrètes</i>, la source de
référence intervertit simplement les deux totaux — l’autre wiki les donne dans
le bon ordre, et les bulletins tranchent : Maxine l’emporte par neuf voix contre
quatre. Sur <i>Le Totem maudit</i>, la matrice étale le jury sur trois colonnes
et y range chaque juré selon **sa propre ligne**, pas selon le nom qu’il écrit :
trois bulletins étaient dans la colonne voisine, et l’égalité **4-4** d’où sont
sortis les deux vainqueurs de cette saison-là restait invisible.

Un bulletin de jury appartient à la colonne de celui qu’il nomme — c’est la
définition du scrutin, pas une préférence. Le relevé les y remet, et le décompte
d’une colonne devient le nombre de ses bulletins. Cette substitution ne se fait
qu’à une condition : que le scrutin soit **complet**, la somme des bulletins
atteignant le nombre de voix annoncé. Sur un relevé partiel, un total lu vaut
mieux qu’un total recalculé.

Le tout dernier bulletin a demandé un troisième geste. Sur
<i>Les Chasseurs d’immunité</i>, la matrice annonçait onze voix et n’en faisait
lire que dix : le lecteur de matrice écarte les cellules qui répètent le nom de
leur propre ligne, parce qu’on ne vote pas pour soi. **Sauf que deux Léa jouent
cette saison-là** — l’une siège au jury, l’autre est en finale — et « Léa vote
Léa » n’était pas la diagonale du tableau, c’était un vrai bulletin. Le
garde-fou connaît désormais les prénoms portés en double : sur tout le corpus,
il n’écartait que **trois cellules, et les trois étaient des homonymes**. Aucune
n’était l’artefact contre lequel il avait été écrit.

Ce qui a été retrouvé n’était pas neutre. L’échantillon d’avant contenait
195 bulletins sur 196 **allant au lauréat** : sur la question « le juré
punit-il celui qui l’a éliminé », il ne pouvait rien montrer, puisque le
bourreau y était presque toujours le gagnant. Avec les deux côtés du choix,
[la page du jury]({{ '/statistiques/jury/' | relative_url }}) conclut désormais
l’inverse de ce qu’elle concluait.

## Deux personnes, un seul prénom

Les tables ne désignent les gens que par leur prénom, et une saison en compte
parfois deux qui le partagent : deux Léa aux *Chasseurs d’immunité*, deux Cécile
à *La Tribu maudite*, deux Jérôme à *La Revanche des 4 Terres*, deux Philippe à
*La Nouvelle Édition*. Aucun de ces noms n’est deviné. Trois choses, et trois
seulement, peuvent trancher — et toutes viennent de la source ou de la structure
du jeu :

- **le nom de la note.** La source écrit une note exprès pour les séparer, et
  elle la **nomme** : `<ref name="jerome-orange">`. Ce nom voyage avec la note
  même quand elle est simplement rappelée, sans son texte. C’est le signal le
  plus sûr, et c’est celui qui a réglé le dernier cas.
- **le texte de la note**, quand il est là : « Léa<sup>De la tribu jaune</sup> ».
- **le surlignage**, à défaut : la table des colliers peint chaque nom à la
  couleur de sa tribu. Avec une précaution qui a été payée — le surlignage suit
  la tribu du **moment**, qui après la réunification n’est plus celle d’origine.
  On ne lit donc que les couleurs de départ de la saison.
- **la présence.** On ne ramasse pas un collier après être sorti du jeu : celui
  du 38<sup>e</sup> jour ne peut pas appartenir à la Léa partie au 23<sup>e</sup>.
- **la place dans le scrutin.** Sur un vote de jury, la cible est forcément un
  finaliste et le votant forcément quelqu’un qui n’en est pas un.

**Il ne reste aucun nom non rattaché** : 80 citations de colliers sur 80,
865 vainqueurs d’épreuve sur 865.

<p class="note"><strong>Une piste a été suivie puis abandonnée, et elle mérite
d’être racontée.</strong> Les tribus de <i>La Revanche des 4 Terres</i>
s’appellent Timog, Hilaga, Kanluran, Silangan dans les tableaux — et « la tribu
du Sud » dans les notes. Le récit fait lui-même la traduction (« Timog du
sud »), et il était tentant de s’en servir pour rattacher un nom. La mise à
l’épreuve l’a écartée : sur un autre collier, la note dit « valable que pour un
membre de la tribu du Sud » — c’est <em>le collier</em> qui est restreint, pas
sa détentrice, et le rapprochement lui aurait attribué une tribu qui n’est pas
la sienne. Une phrase où un nom et une tribu se croisent ne dit pas que l’un
appartient à l’autre. Le pont n’a pas été gardé.</p>

<p class="note">Deux corrections nommées accompagnent ce chantier, chacune
appuyée sur la source elle-même. <i>La Nouvelle Édition</i> affiche
« [[Philippe Duron|Phiippe]] » : le libellé perd un « l » que la cible du lien
porte, et que le reste de la page écrit correctement — sans quoi « Phiippe »
entrait dans la comparaison des prénoms avec le fichier de l’INSEE. Et la fiche
française de <i>La Revanche des Héros</i> nomme une tribu « Mawar » à la teinte
de Nekmao — « Mawar » étant la tribu rouge de <i>Malaisie</i>, une autre saison.
La fiche anglaise et le wiki Fandom ne connaissent que Klahan et Nekmao : deux
sources contre une, et la couleur pour arbitre.</p>

## Éliminé, puis revenu

Cinq conseils donnent pour éliminé quelqu’un qui a fini la saison. Ce n’est pas
une faute de lecture : **quatre sont de vrais retours en jeu**, et les sources
les racontent. Panama consacre à l’un d’eux le titre de son neuvième épisode —
« <i>Le retour de Linda</i> ». Au <i>Feu sacré</i>, Tania est votée deux fois et
revient deux fois, une fois par un duel, une fois pour remplacer un abandon. À
<i>La Nouvelle Édition</i>, Martin sort dernier d’une épreuve d’immunité et
revient par un duel à l’épisode suivant.

Le jeu de données ne sait pas dire « éliminé puis revenu » : `sort` ne retient
que le point d’arrivée. Tant qu’on ne le savait pas, **la première élimination
d’un revenant passait pour sa sortie** — Francis, finaliste du <i>Pacifique</i>,
comptait trois conseils traversés et zéro épreuve disputée, au lieu de quatorze
et onze. C’est corrigé : une élimination au conseil ne date la sortie que de
ceux qui en sont réellement sortis.

<p class="note"><strong>Le cinquième cas n’est pas un retour, c’est une source
qui se contredit.</strong> Au <i>Pacifique</i>, la matrice des votes donne
Francis éliminé au deuxième épisode par sept voix sur huit, et le tableau des
candidats de la même page en fait le finaliste, sorti au quarantième jour. Aucun
récit ne mentionne de repêchage cette saison-là, et Wikipédia ne publie pas de
matrice pour cette édition : il n’y a rien à croiser. Les deux affirmations sont
gardées telles quelles — l’élimination dans les conseils, la finale dans les
participations — et le désaccord est dit ici plutôt que tranché au hasard.</p>

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

## Cinq saisons sans épreuves, et pourquoi elles le resteront

*Bocas del Toro*, *Palau*, *Malaisie*, *Johor* et *Le Choc des héros* n’ont
aucune épreuve relevée — ni confort, ni immunité, pas une ligne. Ce n’est pas un
défaut de lecture, et la question a été reprise à zéro.

Le relevé cherche un tableau sous cinq titres différents, dont « Bilan par
épisode », « Déroulement » et « Détail des éliminations ». **Aucune de ces cinq
saisons n’en porte un.** *Malaisie* a bien une section « Détail des
éliminations » — c’est la matrice des votes, qui ne dit rien des épreuves.
Wikipédia n’a par ailleurs **aucun article français** pour *Bocas del Toro*,
*Palau* ni *Johor* : les deux dernières ont été récupérées sur la version
anglaise, qui ne publie que l’ordre d’élimination et les votes.

Une seule piste existait : *Bocas del Toro* est la seule des cinq à publier un
résumé par épisode, et cette prose nomme des vainqueurs. Elle a été essayée,
puis écartée — elle ne rend que **six épisodes sur treize**, elle ne nomme que
des **tribus**, et elle s’arrête à la réunification, c’est-à-dire précisément là
où commencent les épreuves individuelles. Or ce sont elles qui manquent : sans
elles, pas de dénominateur, pas de ratio. Une extraction qui livrerait la moitié
d’une moitié, au prix d’une lecture de prose libre, coûterait plus en fausses
lignes qu’elle ne rapporterait.

<p class="note">Le palmarès, lui, n’est pas perdu. Les fiches individuelles
donnent le compte de victoires par personne et par saison — il est renseigné
pour 77 des 90 participations de ces cinq éditions. Ce qui manque n’est pas
« combien chacun a gagné », c’est « quelle épreuve, quel soir ».</p>

## Trois défauts dans la lecture des épreuves, trouvés en construisant un classement

Vouloir classer les joueurs oblige à diviser leurs victoires par leurs
occasions. C’est en cherchant ce dénominateur qu’on s’est aperçu que quatre
aventuriers de *Cambodge* affichaient **cinq victoires pour zéro épreuve
disputée**. Le tirage du fil a sorti trois défauts distincts, tous silencieux.

**Le premier : un tableau de classement lu comme un tableau de résultats.** La
section « Bilan par épisode » de *La Revanche des 4 Terres* contient deux
tableaux. Le premier est un encart déroulant qui donne l’**ordre d’arrivée des
quatre tribus** sur les épisodes 1 à 4 ; le vrai bilan de la saison vient juste
en dessous. Le lecteur s’arrêtait au premier tableau. Quatre colonnes sous
« Confort », quatre sous « Immunité », lues comme quatre vainqueurs :
**trente-deux victoires fabriquées**, et le vrai tableau jamais ouvert. Le
lecteur parcourt désormais tous les tableaux d’une section, et rejette ceux qui
donnent plusieurs vainqueurs *différents* pour un même rôle au même épisode —
ce qui distingue un classement d’un résultat, un `colspan` sur un en-tête
légitime produisant, lui, des cellules identiques.

**Le deuxième : une ligne par élimination prise pour un épisode.** Le tableau
« Challenges » de Wikipédia en anglais n’a pas de colonne d’épisode : il a une
**date de diffusion**, et une ligne par sortie. Le compteur implicite donnait
donc vingt-et-un « épisodes » au *Cambodge*, qui en compte quatorze — et toutes
ses épreuves individuelles se retrouvaient numérotées après la sortie de ceux
qui les avaient gagnées. La date, elle, est recopiée sur chaque ligne d’un même
soir : compter les dates **distinctes** rend le vrai numéro, sans rien deviner.

**Le troisième : deux sources, deux numérotations.** Wikipédia en anglais
compte dix-sept épisodes au *Totem maudit* là où le tableau des votes en compte
quatorze — il coupe en deux des soirées que la page française garde entières.
Les deux décrivent les mêmes épreuves, mais « l’épreuve a-t-elle eu lieu avant
sa sortie ? » n’a plus de réponse juste quand les deux fichiers ne parlent pas
la même langue. Le choix de la source ne se fait donc plus au volume mais à
l’**accord avec les conseils** : une page dont la numérotation dépasse de plus
de deux le dernier conseil numéroté est écartée, et le rapport le dit.

<p class="note"><strong>La réparation a elle-même révélé une contradiction.</strong>
Une fois le vrai tableau de <em>La Revanche des 4 Terres</em> ouvert, le
vérificateur a signalé que Maxime gagnait l’immunité individuelle de l’épisode
13 <em>et</em> partait au conseil du même soir. Les deux ne peuvent pas tenir
ensemble. La cellule « Immunité » de ce soir-là porte trois noms : ce sont les
rescapés d’une <em>épreuve éliminatoire</em>, pas les vainqueurs d’une immunité.
Quand les deux faits se contredisent, c’est le conseil qui l’emporte — il est
attesté par ses bulletins, l’immunité ne l’est que par un nom dans une cellule.
La seule attribution qui se contredit est retirée, les deux autres restent, et
la ligne figure au rapport de construction.</p>

Ce que cela déplace : **766 épreuves relevées deviennent 749**, dont
**375 individuelles au lieu de 368** — on en perd en volume, on en gagne en
vérité. La couverture de la première épreuve passe de 28 à 29 saisons, le modèle
de force est estimé sur 284 épreuves au lieu de 271 et sur 28 saisons au lieu de
26. Aucun des tests du
[registre corrigé]({{ '/methode/' | relative_url }}) ne change de conclusion :
21 retenus avant, 21 après.

**Une conclusion publiée a néanmoins basculé, et il faut la nommer.**
[La grille]({{ '/statistiques/grille/' | relative_url }}) affirmait que
l’épisode de la réunification **ne bouge pas** avec la taille du casting —
pente 0,008, intervalle −0,135 à 0,152. Elle vaut désormais 0,111, intervalle
0,016 à 0,205, p = 0,022 : la fusion recule bel et bien, d’environ
**un épisode** sur toute la croissance des castings. Deux saisons expliquent le
renversement, et les deux étaient fausses. *Cambodge* était <em>écartée</em> du
calcul parce que son dernier collectif tombait à un épisode ne laissant que
quatre joueurs — c’était le décalage de numérotation. *La Revanche des 4 Terres*
plaçait sa fusion à l’épisode 4 sur 17, chiffre lu dans le tableau de classement
des quatre tribus ; elle la place maintenant à l’épisode 8. La page a été
réécrite, et elle raconte ce qu’elle disait avant.

## Trois vainqueurs pour une saison qui n’est pas finie

*All Stars* a commencé le 25 août 2026 ; au moment où ces données sont
constituées, quatre conseils ont été joués et deux personnes sont sorties. Le
fichier, lui, portait **trois vainqueurs et quatre finalistes** — alors que la
source écrit, pour seize des dix-huit candidats, « Encore en jeu ».

La cause est une colonne. Le tableau des candidats de Wikipédia porte
« Saisons précédentes » — « Vainqueur de la saison 9 », « Finaliste de la
saison 26 », « Éliminée le 12<sup>e</sup> jour du *Choc des héros* » — et, juste
après, « Départ ». Sur une saison en cours, la colonne de départ est **vide** :
personne n’est encore sorti. Le lecteur, qui retient « la dernière cellule qui
ressemble à un sort », tombait alors sur le palmarès et le prenait pour un
départ.

Le code connaissait pourtant le piège : il écartait déjà ces cellules pour ne
pas les ranger comme des **métiers**. Il le faisait simplement trop tard. Le
retrait a été remonté avant la recherche du départ.

Cela ne suffisait pas : un palmarès qui nomme une édition par son titre plutôt
que par son numéro échappe au motif. Plutôt que d’allonger sans fin une
expression régulière, on s’appuie désormais sur ce qu’une source **affirme** :
quand elle écrit « Encore en jeu », l’aventurier n’a pas de sort, et aucune
déduction faite ailleurs ne peut lui en inventer un.

<p class="note"><strong>Le point aveugle du vérificateur, et sa réparation.</strong>
Le contrôle « autant de vainqueurs dans les données que la saison en déclare »
sautait explicitement les saisons en cours — c’est pourquoi rien n’a
sonné. Deux règles le remplacent : une saison non terminée ne peut porter
<em>aucun</em> sort de fin d’aventure, et un sort ne peut pas contredire une
source qui écrit « encore en jeu ». Les deux ont été éprouvées en
réintroduisant la faute exacte.</p>

Effet sur les chiffres du site : **aucun**. Une saison en cours est écartée de
tous les calculs, et le balayage des 170 intervalles publiés ne montre aucun
changement de conclusion. Ce qui change est la
[complétude]({{ '/completude/' | relative_url }}) : seize trous de plus,
assumés, là où il y avait seize réponses inventées.

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
<a href="{{ '/completude/' | relative_url }}">La complétude, édition par
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

**La même vignette avait une seconde moitié, trouvée bien plus tard.** Quand la
cellule porte à la fois la vignette et le prénom —
`[[Fichier:Ugo.png|75px|link=Ugo Lartiche]]<br />Ugo` — le nettoyage rend les
deux à la suite : « Ugo Lartiche Ugo », qui n’est le nom de personne. Trois
saisons entières y perdaient leurs éliminés. La résolution essaie désormais, à
défaut du libellé entier, son plus long préfixe qui soit **exactement** un nom
complet de la saison : aucune valeur n’est devinée, et un préfixe ne peut jamais
valoir un prénom nu. Les éliminés rattachés passent de 578 à **622** sur 649.

Cette réparation-là a coûté un résultat. L’effet du **sexe minoritaire** portait
la plus haute des p ajustées retenues du site, et
[la page le disait]({{ '/statistiques/autour-du-feu/' | relative_url }}) — « une
saison de plus pourrait la faire basculer ». Quarante-quatre éliminations de
plus ont suffi : l’écart n’a presque pas bougé, la correction pour tests
multiples ne le garde plus. C’est exactement ce à quoi sert une liste de tests
arrêtée avant de regarder.

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

## Le soir à plusieurs conseils, piège récurrent

{% assign af = site.data.stats.modeles.autour_du_feu %}
{% assign imm = af.immunite | first %}

Le paragraphe ci-dessus décrit un piège rencontré sur l’appariement des
bulletins. Il s’est représenté ailleurs, sous une autre forme, et il mérite
d’être nommé une bonne fois : **un épisode n’est pas un conseil.**

Un même soir peut en compter deux, trois, parfois quatre — une égalité suivie
d’un second vote, deux tribus qui votent chacune de leur côté, un épisode final
qui enchaîne les éliminations. Tout rapprochement fait sur le seul numéro
d’épisode y devient faux.

<div class="constat">
  <p>Contrôle : <b>l’aventurier qui gagne l’immunité individuelle ne peut pas
  être éliminé le soir même.</b> C’est une règle du jeu ; si les données la
  violent, c’est qu’un rattachement est bancal.</p>
  <p>Rapproché sur le seul épisode, le contrôle sortait <b>19 violations</b>.
  Toutes les dix-neuf tombaient sur un soir à plusieurs conseils : dans un
  épisode qui en compte trois, l’immunité gagnée avant le premier ne protège
  pas au troisième.</p>
  <p>Rapproché correctement — soirs à conseil unique, camp lu dans les
  bulletins — il sort <b>{{ imm.cas }} violation sur {{ imm.effectif }}
  présences</b>. La donnée était juste ; c’est la question qui était mal
  posée.</p>
</div>

Conséquence pour tout ce site : une épreuve du soir n’est jamais rattachée à un
conseil quand l’épisode en compte plusieurs.
[Sachant qui est autour du feu]({{ '/statistiques/autour-du-feu/' | relative_url }})
s’appuie sur cette règle.

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
