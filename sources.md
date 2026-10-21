---
layout: page
title: Les sources
description: "D’où viennent les données de Koh-Lanta : chaque champ, sa source, la façon dont les contradictions ont été tranchées, et ce qui manque encore."
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
d’un aventurier. Limite : toutes les saisons ne disposent pas d’une page
détaillée.

**[Le wiki Koh-Lanta sur Fandom](https://kohlanta.fandom.com/fr/)** — une page
par saison, pour les {{ g.saisons_diffusees }} éditions. C’est la source du nom
complet, de l’âge, du métier, du département d’origine, du jour de sortie exact
et du total des voix reçues, ainsi que du détail des conseils. Limite : son
tableau de candidats est incomplet sur plusieurs saisons, et il ne donne le sexe que
par l’accord du participe.

Aucune des deux ne suffit seule. Pour chaque saison, la source de référence est
**celle dont l’effectif correspond au nombre de candidats annoncé** ; l’autre
vient compléter, champ par champ.

## La troisième source : une page par aventurier

Les tables de saison, quelle que soit leur origine, ne portent ni la résidence
sur les éditions anciennes, ni le détail des tribus avec leurs jours, ni le
palmarès d’épreuves. Le wiki Fandom a autre chose : **une page par aventurier**,
avec une fiche — l’*Infobox Aventuriers* — qui donne tout cela, saison par
saison, pour quelqu’un qui en a joué quatre comme pour quelqu’un qui en a joué
une.

{{ site.data.stats.completude.comblees }} valeurs manquantes ont été comblées
par ces fiches. Elles n’ont **jamais** remplacé une valeur déjà établie par une
table : une fiche est saisie à la main par un lecteur, une table est relue par
beaucoup. Les désaccords sont comptés et laissés au rapport d’extraction, pas
tranchés en silence.

Ces pages ont aussi réglé un problème que les tables ne pouvaient pas voir.

- **Sept aventuriers n’avaient qu’un prénom.** Les éditions de retour présentent
  parfois les revenants par leur seul prénom, et quand plusieurs personnes du
  jeu de données portent ce prénom, le rattachement automatique s’abstient. Le
  wiki classe ses pages par saison : une seule « Victor » est classée dans
  *La Guerre des chefs*, et c’est Victor Rollinger. Sept noms de famille ont été
  rendus de cette façon ; un seul résiste, la Sabira de *Panama*, qui n’a pas de
  page.
- **Trois participations comptaient pour deux personnes.** « Phil Bizet » et
  « Philippe Bizet », « Clémentine Julien » et « Clémentine Jullien » sont deux
  orthographes d’une même personne — et sur le wiki, deux titres qui **renvoient
  à la même page**. Deux identifiants dont la page a la même empreinte sont donc
  la même personne, et c’est la page qui dit lequel des deux noms est le bon.
  Le nombre de personnes distinctes passe de 535 à
  {{ site.data.stats.general.personnes }}.

Limite, et elle est réelle :
{{ site.data.stats.completude.sans_fiche }} participations sur
{{ site.data.stats.completude.participations }} n’ont aucune fiche individuelle
exploitable — les castings les plus anciens, et l’édition de célébrités de 2012,
dont les invités n’ont pas de page. Ce qui manque encore manque surtout là.

## Les parcours de tribu, et ce qu’ils ne disent pas

Le parcours d’un aventurier, c’est la suite de ses tribus, chacune bornée en
jours. Wikipédia le donne pour les saisons récentes ; pour les autres, il vient
de la fiche Fandom, qui l’écrit à la main, et le 20 octobre 2026 il a fallu en
reprendre la lecture.

**Deux défauts de lecture**, sur cinquante parcours. La fiche écrit tantôt
« Kumo (Jour 1 - 12) », tantôt « Kumo (Jour 1 - Jour 12) » : le second « Jour »
n’était pas prévu, et toute la parenthèse restait collée au nom de la tribu.
Ailleurs, les jours étaient repérés sur la ligne brute, puis le nom coupé
*après* le retrait des liens — et la coupe tombait à côté : « Mogo (Jou ».
S’y ajoutaient des graphies de travers — « LankawaÏ », « Bokkor », « Tribu
réunifié », un tuyau d’infobox collé devant « Tengah » — qui empêchaient de
rattacher l’étape à sa tribu, donc à sa couleur. Tout cela est relu
correctement, et une étape qui commencerait avant la fin de la précédente
(« Tribu réunifiée (Jour 1-28) » après « Kanawa (Jour 1-19) ») est tenue pour
la coquille qu’elle est.

**Ensuite, ce que la source ne donne pas.** Pour les saisons anciennes, la
fiche écrit la suite des tribus *sans aucun jour* — « Kumo, Tribu réunifiée ».
Les jours n’ont été posés que lorsqu’ils sont sûrs : le jour 1, seulement si
la fiche le prouve (sortie au jour 39 après 39 jours de jeu) — un remplaçant
arrivé au jour 4, un revenant après un trou n’entrent pas dans ce calcul ; le
jour de la réunification ou d’un échange de tribus, seulement s’il se lit,
identique, chez tous les autres aventuriers datés de la saison ; le jour de
sortie pour la dernière étape. Chacun de ces faits se pose seul, sans attendre
les autres. Un échange que rien ne date reste sans date. Les parcours
vides, enfin, ont été complétés par le tableau des candidats du wiki
*Survivor*, sans jours quand il n’en donne pas.

Trois aventuriers résistaient à tout rapprochement, et chacun avait sa
raison. Le wiki *Survivor* nomme Sabira « SL », ses initiales : même tribu,
même échange, même sortie au jour 10. Il écrit le nom de Maryline juste, mais
son lien avec une coquille. Et Myriam est sortie avant la formation des tribus
— le tableau Fandom écrit « Aucune » dans un cadre de couleur nommé « Bannie »,
et c’est ce nom de cadre qui était devenu sa tribu, comme pour Joëlle et Amel.
Une tribu initiale n’est plus jamais un état : « Bannie », « Absente » cèdent
la place au premier vrai campement, ou à rien.

**Puis les légendes de Wikipédia, lues de travers elles aussi.** Wikipédia
colore chaque étape : un code pour une tribu (« #fee347 »), mais un *nom* pour
la tribu réunifiée (« white »), pour les bannis (« black »), et parfois rien.
Seuls les codes étaient lus : 313 étapes disparaissaient, dont toutes les
réunifications écrites en blanc — 221 parcours s’arrêtaient à la réunification. Elles
sont lues ; une étape encore en cours, « (jour 19 – ) », n’a plus de jour de
fin inventé ; et la tribu initiale reste la première tribu à vraie couleur, pas
la « Tribu des hommes » ni la « Tribu unique » des tout premiers jours.

**Enfin, les jours de sortie.** Confrontés au parcours, une trentaine ne
tenaient pas. Chaque cas a été soumis à tous les témoins disponibles —
Wikipédia en français et en anglais, le wiki *Survivor*, la fiche Fandom et
ses jours de jeu — et la majorité l’a emporté. Le tableau de saison Fandom,
d’où viennent ces jours, est décalé d’un jour sur toute la saison de *Nicoya*,
et en fin de saison aux *Armes secrètes*, à *La Tribu maudite*, au *Choc des
héros*, à *La Nouvelle Édition* et à *La Légende*. Trois durées de saison
suivent : 35 jours aux *Armes secrètes*, 41 à *La Tribu maudite*, 20 au *Choc
des héros*. Une confrontation de chaque jour de sortie à tous les témoins, sur
toutes les saisons, ne montre plus aucune saison décalée d’ensemble. Quatre étapes fausses à la source sont
corrigées, dont celle de Patricia, que sa légende plaçait dans la tribu
réunifiée alors qu’elle sort à la réunion des ambassadeurs. Les revenants,
eux, gardent comme jour de sortie celui de leur première élimination : leur
parcours continue après, et c’est normal.

Quand les témoins étaient à égalité, on en a cherché un de plus, dans les
récits datés. La page Fandom de Marie confirme l’élimination d’Estelle au
22<sup>e</sup> jour de *Vanuatu* ; celle de Lau place la sortie de Laurent au
15<sup>e</sup> de *L’Île au trésor* ; le résumé de Wikipédia, l’abandon de
Freddy au 2<sup>e</sup> de *La Légende*. Deux cas restent à égalité, et
n’ont pas été changés : Ludovic, éliminé à l’orientation de *Vanuatu* au jour
38 ou 39, et la durée de *Caramoan*, 39 ou 40 jours — trois témoins de chaque
côté. Une recherche sur le web n’a rien tranché : pour *Caramoan*, le wiki
*Télé-réalité* fait finir la saison au 39<sup>e</sup> jour, mais ses parcours
recopient le format de Wikipédia ; Christelle parle en interview de « 40 jours
sur cette île », une formule orale qui peut arrondir ; et les autres sites de
statistiques reprennent le tableau Fandom. Pour Ludovic, aucune page ne date
l’orientation.

<p class="note">Au moment de cette reprise, 50 étapes portaient un nom de
tribu mêlé de dates, et 32 parcours contredisaient leur jour de sortie : il
n’y en a plus. 49 parcours vides ont été complétés, souvent sans jours. Il
reste 172 étapes sans jours et 4 parcours vides, ceux d’<em>All Stars</em>,
saison en cours. Les étapes sans jours ne seront complétées que si une source
les date.</p>

## La quatrième source : le wiki anglophone de *Survivor*, en témoin

**[Le wiki *Survivor*](https://survivor.fandom.com/wiki/Koh-Lanta)** — wiki
anglophone consacré aux déclinaisons de l’émission dans le monde, sous licence
[CC BY-SA](https://www.fandom.com/licensing). Chaque saison de *Koh-Lanta* y a
une page et un **guide d’épisodes** : pour chaque soir, le confort, l’immunité
et l’éliminé ; les invités d’une récompense entre crochets ; une note pour
chaque cas particulier. Il est tenu par d’autres mains que Wikipédia et le wiki
Fandom francophone, ce qui en fait un troisième témoin.

Il sert à deux choses, depuis le 20 octobre 2026 :

- **trancher** quand les deux premières sources se contredisent sur le gagnant
  d’une épreuve. Ses pages par épisode, qui écrivent « Winners: » en toutes
  lettres, ont départagé plusieurs cas que rien d’autre ne réglait ;
- **combler** les {{ site.data.stats.mots.saisons_source_unique }} saisons dont
  aucune autre page ne donne les épreuves :
  {{ site.data.stats.epreuves.saisons_source_unique_texte }}. Pour elles, il est
  la seule source, et le site le dit partout où cela compte ;
- **compléter les parcours de tribu** restés vides : son tableau des candidats
  donne, pour chacun, la tribu de chaque phase du jeu.

Il range sous « Immunity » des choses que ce site ne compte pas comme des
épreuves : un duel gagné, un avantage, une immunité **donnée** après un
changement de tribu, une course du premier jour. Ses notes le disent, et ces
cases sont écartées à la lecture. Les pages de saison et les guides sont
versionnés dans le dépôt (`specs/sources/survivor/`), comme le wikitexte des
deux autres wikis.

## Deux sources de référence, pour comparer

**[Le fichier des prénoms de l’INSEE](https://www.insee.fr/fr/statistiques/8595130)**
— nombre de naissances par prénom, par sexe et par année depuis 1900, sous
[licence ouverte v2](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
Il ne sert qu’à une chose : donner un point de comparaison aux
[prénoms des aventuriers]({{ '/statistiques/prenoms/' | relative_url }}).

**[Les estimations de population de l’INSEE](https://www.insee.fr/fr/statistiques/8560704)**
— population au 1<sup>er</sup> janvier par département, sexe et groupe d’âges,
séries depuis 1990, même licence. Elles servent au seul calcul de
[l’origine géographique]({{ '/statistiques/geographie/' | relative_url }}) : sans
{% assign paris = site.data.geographie.departements | where: "departement", "Paris" | first %}
elles, « {{ paris.observe }} Parisiens » ne veut rien dire.

Dans les deux cas, le sous-ensemble effectivement lu — nos prénoms et nos années
de naissance ; les départements et les années de nos saisons — est versionné
dans le dépôt, comme le wikitexte brut : c’est la preuve de provenance, et elle
permet de refaire le calcul sans redemander les fichiers complets à l’INSEE.

## Les audiences

{% assign au = site.data.audiences %}
{% assign ac = site.data.stats.audience_controle %}

**[L’article général de Wikipédia](https://fr.wikipedia.org/wiki/Koh-Lanta)**
porte un tableau d’audiences que ce site a longtemps ignoré : pour chaque
saison, l’audience du lancement, celle de la finale, la moyenne, la part de
marché et — sur {{ ac.recettes }} saisons — les recettes publicitaires, chaque ligne
appuyée sur une source de presse. Les articles de saison y ajoutent le détail
**épisode par épisode** quand ils l’ont.

- {{ au.saisons_couvertes }} saisons sur {{ au.saisons_diffusees }} ont une
  audience de saison. La seule qui manque est celle en cours.
- {{ au.episodes | size }} mesures épisode par épisode, sur
  {{ au.saisons_par_episode | size }} saisons.

Le contrôle est direct et il est publié : sur les {{ ac.saisons }} saisons où l’on
a à la fois le détail et la moyenne annoncée, **{{ ac.concordantes }} concordent à
0,5 % près**. Les autres — {{ ac.discordantes_texte }} — s’en écartent davantage,
et l’écart vient de la source, dont le tableau ne s’accorde pas avec sa propre
ligne de synthèse. Rien n’est corrigé à la main.

Limite de nature : c’est l’audience **veille**, en direct. Le rattrapage n’y est
pas, et ces données ne permettent pas de dire combien il pèse.

## Un nom lu dans la prose, et ce que ça coûte

{% assign ng = site.data.ambassadeurs %}

Une seule information de ce site ne vient pas d’un tableau : **le nom des
ambassadeurs**. Il n’apparaît que dans une note de bas de page — « <em>Les deux
ambassadeurs (Léa et Pauline) se mettent d’accord pour éliminer Ricky.</em> »
Lire de la prose est faillible, et la seule réponse honnête est de mesurer.

<div class="constat">
  <p><b>{{ ng.nommees }} ambassades sur {{ ng.ambassades }}</b> livrent leurs
  noms — {{ ng.part_nommees }} %. Là où les deux sources les nomment, elles
  s’accordent {{ ng.sources_accord }} fois sur
  {{ site.data.stats.ambassades_sources_communes }}.</p>
</div>

Trois contrôles écartent une lecture douteuse : le nom doit désigner un
participant de la saison **sans homonyme**, l’ambassadeur doit être **encore en
jeu** à cet épisode, et le nombre de noms lus doit correspondre à celui que la
note annonce. Ce dernier contrôle écarte une saison où la note dit « deux
ambassadeurs » avant d’ajouter une « ambassadrice secrète ».

Et une divergence a été trouvée : sur <i>Les Reliques du destin</i>, Wikipédia
compte Jade parmi les quatre ambassadeurs, Fandom compte Cynthia. Aucun des deux
n’est retenu. Elle n’est apparue qu’après correction d’un motif de lecture trop
strict qui ne lisait qu’une des deux sources : **une comparaison ne vaut que si
les deux côtés ont vraiment été lus**, et le premier chiffrage annonçait à tort
zéro divergence.

## La fin de saison, lue dans deux colonnes et dans le récit

{% assign fc = site.data.stats.finale.couverture %}

Deuxième information à ne pas venir d’un tableau de résultats : **qui a gagné
l’épreuve des poteaux**. `epreuves.yml` ne porte aucun nom d’épreuve, et le
catalogue des épreuves nommées ne raccorde « Poteaux » à aucune saison. Pire :
la dernière épreuve d’immunité individuelle relevée **n’est pas** les poteaux —
pour plusieurs saisons, son vainqueur est justement la personne portée
`elimine_poteaux`. La déduire aurait donné un résultat faux et silencieux.

Deux gisements ont été croisés : la colonne « Épreuve des poteaux » du tableau
de déroulement des deux wikis, et les notes de bas de page, dont la tournure est
stable — « <em>Cynthia, vainqueur de l’épreuve des poteaux, décide d’affronter
Clarisse</em> ».

<div class="constat">
  <p><b>{{ fc.vainqueur_des_poteaux_connu }} saisons sur
  {{ fc.saisons_au_format }}</b> livrent le vainqueur des poteaux —
  {{ fc.part_poteaux }} %. Le choix du finaliste n’est explicitement énoncé que
  pour {{ fc.choix_atteste }} d’entre elles ; ailleurs, l’autre finaliste est
  déduit par soustraction et le champ le dit.</p>
</div>

L’ordre d’arrivée à l’orientation pose une question de nature différente : les
sources listent les qualifiés, mais **rien n’annonce que cette liste soit
ordonnée**. Deux vérifications indépendantes ont donc été montées, et elles
tournent à chaque régénération. Le récit nomme parfois un rang — « <em>Loïc
trouve le premier poignard</em> » : sur {{ fc.saisons_ordre_teste }} saisons,
**{{ fc.rangs_confirmes }} rangs** sont ainsi confrontables à la place que la
cellule leur donne, et {{ fc.rangs_dementis }} la contredit. Et les deux wikis,
rédigés séparément, écrivent le même ordre sur {{ fc.ordre_concordant }} des
{{ fc.ordre_croisable }} saisons où les deux le détaillent.

`verifie.py` échoue si un seul rang vient à être démenti : le jour où l’ordre
cessera d’être l’ordre d’arrivée,
[la page qui en vit]({{ '/statistiques/finale/' | relative_url }}) cessera
d’être publiable, et on le saura sans avoir à y penser.

## Le scrutin final, retrouvé en deux fois

{% assign jj = site.data.stats.jury %}

Le vote du jury tient **une colonne par finaliste** dans les matrices sources :
celle du gagnant et celle du battu. Seule la première était reconnue. Les autres
étaient rangées du côté des éliminations, où leurs bulletins comptaient à
l’envers — un juré qui écrit « Cynthia » pour la couronner était compté comme
votant contre elle.

La première réparation s’est appuyée sur le **titre** de la colonne :
« Finaliste », « Gagnant ». Elle a rendu quarante-neuf bulletins. Mais dix-sept
saisons ne titrent pas leur colonne finale : elles lui donnent simplement le
**numéro de l’épisode**, comme à un conseil ordinaire, et elles échappaient donc
au titre.

La seconde réparation ne regarde plus le titre mais la **place**. Le scrutin
final occupe les dernières colonnes de la matrice, une par personne arrivée au
bout — et celui qu’on y donne pour « éliminé » est un **finaliste déclaré**, ce
qui est impossible pour une vraie élimination : un finaliste, par définition, va
jusqu’au vote. Les deux conditions réunies, sans jamais l’une sans l’autre,
identifient la colonne sans ambiguïté.

<div class="constat">
  <p><b>{{ jj.lignes }} colonnes de jury</b> sur {{ jj.saisons }} saisons, contre
  32 avant les réparations, et <b>{{ jj.bulletins_lus }} bulletins</b> contre 196 —
  {{ jj.effectif }} colonnes de lauréat, le reste étant celles des finalistes
  battus. <b>Il n’en manque plus aucun</b> : chaque voix annoncée par les
  sources est lue et attribuée.</p>
  <p>Le décompte annoncé et les bulletins relevés coïncident désormais
  <b>partout où la source annonce un décompte</b> :
  {{ jj.decomptes_discordants }} scrutin discordant.</p>
</div>

Restaient cinq colonnes dont le total annoncé contredisait les bulletins, et
elles ne disaient pas la même chose. Sur <i>Les Armes secrètes</i>, la source de
référence intervertit simplement les deux totaux — l’autre wiki les donne dans
le bon ordre, et les bulletins tranchent : Maxine l’emporte par neuf voix contre
quatre. Sur <i>Le Totem maudit</i>, la matrice étale le jury sur trois colonnes
et y range chaque juré selon **sa propre ligne**, pas selon le nom qu’il écrit :
trois bulletins étaient dans la colonne voisine, et l’égalité **4-4** d’où sont
sortis les deux vainqueurs de cette saison-là restait invisible.

Un bulletin de jury appartient à la colonne de celui qu’il nomme — c’est la
définition du scrutin, pas une préférence. Le relevé les y remet, et le décompte
d’une colonne devient le nombre de ses bulletins. Cette substitution ne se fait
qu’à une condition : que le scrutin soit **complet**, la somme des bulletins
atteignant le nombre de voix annoncé. Sur un relevé partiel, un total lu vaut
mieux qu’un total recalculé.

Le tout dernier bulletin a demandé un troisième geste. Sur
<i>Les Chasseurs d’immunité</i>, la matrice annonçait onze voix et n’en faisait
lire que dix : le lecteur de matrice écarte les cellules qui répètent le nom de
leur propre ligne, parce qu’on ne vote pas pour soi. **Sauf que deux Léa jouent
cette saison-là** — l’une siège au jury, l’autre est en finale — et « Léa vote
Léa » n’était pas la diagonale du tableau, c’était un vrai bulletin. Le
garde-fou connaît désormais les prénoms portés en double : sur tout le corpus,
il n’écartait que **trois cellules, et les trois étaient des homonymes**. Aucune
n’était l’artefact contre lequel il avait été écrit.

Ce qui a été retrouvé n’était pas neutre. L’échantillon d’avant contenait
195 bulletins sur 196 **allant au lauréat** : sur la question « le juré
punit-il celui qui l’a éliminé », il ne pouvait rien montrer, puisque le
bourreau y était presque toujours le gagnant. Avec les deux côtés du choix,
[la page du jury]({{ '/statistiques/jury/' | relative_url }}) conclut désormais
l’inverse de ce qu’elle concluait.

## Deux personnes, un seul prénom

Les tables ne désignent les gens que par leur prénom, et une saison en compte
parfois deux qui le partagent : deux Léa aux *Chasseurs d’immunité*, deux Cécile
à *La Tribu maudite*, deux Jérôme à *La Revanche des 4 Terres*, deux Philippe à
*La Nouvelle Édition*. Aucun de ces noms n’est deviné. Cinq choses, et cinq
seulement, peuvent trancher — et toutes viennent de la source ou de la structure
du jeu :

- **le nom de la note.** La source écrit une note exprès pour les séparer, et
  elle la **nomme** : `<ref name="jerome-orange">`. Ce nom voyage avec la note
  même quand elle est simplement rappelée, sans son texte. C’est le signal le
  plus sûr, et c’est celui qui a réglé le dernier cas.
- **le texte de la note**, quand il est là : « Léa<sup>De la tribu jaune</sup> ».
- **le surlignage**, à défaut : la table des colliers peint chaque nom à la
  couleur de sa tribu. Avec une précaution qui a été payée — le surlignage suit
  la tribu du **moment**, qui après la réunification n’est plus celle d’origine.
  On ne lit donc que les couleurs des tribus initiales de la saison.
- **la présence.** On ne ramasse pas un collier après être sorti du jeu : celui
  du 38<sup>e</sup> jour ne peut pas appartenir à la Léa partie au 23<sup>e</sup>.
- **la place dans le scrutin.** Sur un vote de jury, la cible est forcément un
  finaliste et le votant forcément quelqu’un qui n’en est pas un.

{% assign rt = site.data.stats.rattachement %}
**Il ne reste aucun nom de personne non rattaché** : {{ rt.colliers_rattaches }}
citations de colliers sur {{ rt.colliers }}, {{ rt.vainqueurs_rattaches }}
vainqueurs d’épreuve sur {{ rt.vainqueurs }}. Les libellés qui restent sont des
noms d’équipe — {{ rt.vainqueurs_restants_texte }} — que le relevé ne sait pas
encore rattacher à une tribu.

<p class="note"><strong>Une piste a été suivie puis abandonnée, et elle mérite
d’être racontée.</strong> Les tribus de <i>La Revanche des 4 Terres</i>
s’appellent Timog, Hilaga, Kanluran, Silangan dans les tableaux — et « la tribu
du Sud » dans les notes. Le récit fait lui-même la traduction (« Timog du
sud »), et il était tentant de s’en servir pour rattacher un nom. La mise à
l’épreuve l’a écartée : sur un autre collier, la note dit « valable que pour un
membre de la tribu du Sud » — c’est <em>le collier</em> qui est restreint, pas
sa détentrice, et le rapprochement lui aurait attribué une tribu qui n’est pas
la sienne. Une phrase où un nom et une tribu se croisent ne dit pas que l’un
appartient à l’autre. Le pont n’a pas été gardé.</p>

<p class="note">Deux corrections nommées accompagnent ce chantier, chacune
appuyée sur la source elle-même. <i>La Nouvelle Édition</i> affiche
« [[Philippe Duron|Phiippe]] » : le libellé perd un « l » que la cible du lien
porte, et que le reste de la page écrit correctement — sans quoi « Phiippe »
entrait dans la comparaison des prénoms avec le fichier de l’INSEE. Et la fiche
française de <i>La Revanche des Héros</i> nomme une tribu « Mawar » à la teinte
de Nekmao — « Mawar » étant la tribu rouge de <i>Malaisie</i>, une autre saison.
La fiche anglaise et le wiki Fandom ne connaissent que Klahan et Nekmao : deux
sources contre une, et la couleur pour arbitre.</p>

## Éliminé, puis revenu

{{ site.data.stats.conseils.retours_en_jeu }} conseils donnent pour éliminé
quelqu’un qui a fini la saison. Ce n’est pas une faute de lecture : **ce sont de
vrais retours en jeu**, et les sources les racontent. Panama consacre à l’un
d’eux le titre de son neuvième épisode — « <i>Le retour de Linda</i> ». Au
<i>Feu sacré</i>, Tania est votée deux fois et revient deux fois, une fois par
un duel, une fois pour remplacer un abandon. À <i>La Nouvelle Édition</i>, Martin
sort dernier d’une épreuve d’immunité et revient par un duel à l’épisode
suivant. Deux d’entre eux sont allés jusqu’à la victoire : Christina, à
<i>Palau</i>, que la source anglaise dit « revenue en jeu », et André, à
<i>Fidji</i>, éliminé avec son binôme puis réintégré par un duel. Ces deux-là,
le site les a longtemps tenus pour une erreur de la source.

Le jeu de données ne sait pas dire « éliminé puis revenu » : `sort` ne retient
que le point d’arrivée. Tant qu’on ne le savait pas, **la première élimination
d’un revenant passait pour sa sortie** — Francis, finaliste du <i>Pacifique</i>,
comptait trois conseils traversés et zéro épreuve disputée, au lieu de quatorze
et onze. C’est corrigé : une élimination au conseil ne date la sortie que de
ceux qui en sont réellement sortis.

<p class="note"><strong>Le cinquième cas n’est pas un retour, c’est une source
qui se contredit.</strong> Au <i>Pacifique</i>, la matrice des votes donne
Francis éliminé au deuxième épisode par sept voix sur huit, et le tableau des
candidats de la même page en fait le finaliste, sorti au quarantième jour. Aucun
récit ne mentionne de repêchage cette saison-là, et Wikipédia ne publie pas de
matrice pour cette édition : il n’y a rien à croiser. Les deux affirmations sont
gardées telles quelles — l’élimination dans les conseils, la finale dans les
participations — et le désaccord est dit ici plutôt que tranché au hasard.</p>

## La traçabilité

Chaque enregistrement du jeu de données porte un bloc `sources` qui indique,
**pour chaque champ**, d’où vient la valeur retenue. On y lit `wikipedia-fr`,
`fandom`, mais aussi :

- `arbitrage manuel` — un prénom sans accord de participe, tranché à la main ;
- `déduit de sa participation de 2009` — l’âge d’un revenant, calculé depuis une
  année où il était connu ;
- `dernier jour de la saison (finale)` — un finaliste sort le dernier jour, par
  définition ;
- `recoupement sur le prénom` — un sexe établi grâce à la même personne vue
  ailleurs ;
- `fandom (page individuelle)` — un champ vide comblé par la fiche de
  l’aventurier ;
- `categorie Fandom de la saison` — un nom de famille rendu à un prénom nu ;
- `page Fandom commune (redirection)` — deux orthographes réunies en une
  personne.

Le wikitexte brut des pages consultées est conservé dans le dépôt, avec les
scripts qui l’ont récupéré : n’importe qui peut refaire le chemin.

## Les arbitrages

Quelques points ont demandé une décision explicite.

**Les durées de saison.** Sur {{ site.data.stats.general.saisons_diffusees }} saisons,
{{ site.data.stats.general.durees_concordantes }} voient le tableau récapitulatif et
les tables de candidats s’accorder exactement. Pour
{{ site.data.stats.mots.durees_divergentes }} d’entre elles, ils divergent d’un jour. C’est alors le **jour attesté par les tables de candidats**
qui est retenu — la sortie d’un finaliste est datée plus précisément qu’une
durée de résumé — et la valeur annoncée est conservée à côté. Deux fois, ce
jour attesté s’est révélé faux, et la règle a cédé : aux *Armes secrètes*, à
*La Tribu maudite* et au *Choc des héros*, le tableau de saison Fandom est
décalé d’un jour, contre la fiche des finalistes, les légendes de Wikipédia et
le wiki *Survivor*. Ces trois saisons durent 35, 41 et 20 jours.

**Les homonymes.** Deux Léa en saison 25, deux Cécile en 26, deux Jérôme en 27 :
ce sont bien des personnes différentes, et non des doublons. Elles sont
distinguées par leur âge et leur métier, jamais devinées.

**Les métiers.** Les {{ site.data.stats.general.metiers_distincts }} intitulés distincts sont regroupés en
familles par une table de mots-clés, lue dans l’ordre : le premier poste dont un
mot-clé apparaît l’emporte. L’ordre porte donc du sens — « éducateur sportif »
rencontre le sport avant l’enseignement, « maître-nageur » rencontre l’action et
le secours avant le sport. Cette table est un fichier du dépôt, faite pour être
relue et discutée.

**Les lieux.** Les fiches individuelles donnent tantôt le département, tantôt la
ville, tantôt une province d’Ancien Régime, avec une orthographe libre. Une
table fermée les ramène à la graphie du fichier INSEE — sans quoi « Toulouse »
et « Haute-Garonne » sont deux endroits, et la comparaison avec la population
perd les deux. Les cas ambigus n’y figurent pas : « Brassac » est dans le Tarn
*et* dans le Puy-de-Dôme, « Mauléon » dans les Deux-Sèvres *et* les
Pyrénées-Atlantiques. Ces deux-là restent tels quels, et hors du calcul.

## Cinq saisons sans épreuves, jusqu’au troisième témoin

Jusqu’au 20 octobre 2026, *Bocas del Toro*, *Palau*, *Malaisie*, *Johor* et
*Le Choc des héros* n’avaient aucune épreuve relevée — ni confort, ni immunité,
pas une ligne. Ce n’était pas un défaut de lecture, et la question avait été
reprise à zéro.

Le relevé cherche un tableau sous cinq titres différents, dont « Bilan par
épisode », « Déroulement » et « Détail des éliminations ». **Aucune de ces cinq
saisons n’en portait un**, ni sur Wikipédia ni sur le wiki Fandom. *Malaisie* a bien une section « Détail des
éliminations » — c’est la matrice des votes, qui ne dit rien des épreuves.
Wikipédia n’a par ailleurs **aucun article français** pour *Bocas del Toro*,
*Palau* ni *Johor* : les deux dernières ont été récupérées sur la version
anglaise, qui ne publie que l’ordre d’élimination et les votes.

Une seule piste existait : *Bocas del Toro* est la seule des cinq à publier un
résumé par épisode, et cette prose nomme des vainqueurs. Elle a été essayée,
puis écartée — elle ne rend que **six épisodes sur treize**, elle ne nomme que
des **tribus**, et elle s’arrête à la réunification, c’est-à-dire précisément là
où commencent les épreuves individuelles. Or ce sont elles qui manquent : sans
elles, pas de dénominateur, pas de ratio. Une extraction qui livrerait la moitié
d’une moitié, au prix d’une lecture de prose libre, coûterait plus en fausses
lignes qu’elle ne rapporterait. La section concluait donc qu’elles resteraient
vides.

C’était sans compter le wiki *Survivor*, présenté plus haut, dont le guide d’épisodes donne, pour chacune des cinq, le confort et l’immunité
de chaque soir. Elles sont relevées depuis, sur cette **seule source**, avec
trois précautions :

- leur numérotation a été confrontée aux conseils, éliminé par éliminé : elle
  concorde partout ;
- chaque case à plusieurs noms a été vérifiée sur la page de l’épisode, qui
  écrit « Winners: » en toutes lettres — un duo gagnant, deux tribus à égalité
  qui « split the reward », quatre gagnants nommés ;
- ce que le guide range sous « Immunity » sans que ce soit une épreuve — au
  *Choc des héros*, le duel qui précède la réunion des ambassadeurs et rend
  Christina intouchable au conseil suivant — est écarté, comme dans les autres saisons. Une immunité gagnée puis
  conservée, parce que le conseil qu’elle devait couvrir a été annulé, reste
  une immunité gagnée.

Le défaut qui reste est celui de toute source unique : une erreur du guide ne
serait recoupée par rien.

## Trois défauts dans la lecture des épreuves, trouvés en construisant un classement

Vouloir classer les joueurs oblige à diviser leurs victoires par leurs
occasions. C’est en cherchant ce dénominateur qu’on s’est aperçu que quatre
aventuriers de *Cambodge* affichaient **cinq victoires pour zéro épreuve
disputée**. Le tirage du fil a sorti trois défauts distincts, tous silencieux.

**Le premier : un tableau de classement lu comme un tableau de résultats.** La
section « Bilan par épisode » de *La Revanche des 4 Terres* contient deux
tableaux. Le premier est un encart déroulant qui donne l’**ordre d’arrivée des
quatre tribus** sur les épisodes 1 à 4 ; le vrai bilan de la saison vient juste
en dessous. Le lecteur s’arrêtait au premier tableau. Quatre colonnes sous
« Confort », quatre sous « Immunité », lues comme quatre vainqueurs :
**trente-deux victoires fabriquées**, et le vrai tableau jamais ouvert. Le
lecteur parcourt désormais tous les tableaux d’une section, et rejette ceux qui
donnent plusieurs vainqueurs *différents* pour un même rôle au même épisode —
ce qui distingue un classement d’un résultat, un `colspan` sur un en-tête
légitime produisant, lui, des cellules identiques.

**Le deuxième : une ligne par élimination prise pour un épisode.** Le tableau
« Challenges » de Wikipédia en anglais n’a pas de colonne d’épisode : il a une
**date de diffusion**, et une ligne par sortie. Le compteur implicite donnait
donc vingt-et-un « épisodes » au *Cambodge*, qui en compte quatorze — et toutes
ses épreuves individuelles se retrouvaient numérotées après la sortie de ceux
qui les avaient gagnées. La date, elle, est recopiée sur chaque ligne d’un même
soir : compter les dates **distinctes** rend le vrai numéro, sans rien deviner.

**Le troisième : deux sources, deux numérotations.** Wikipédia en anglais
compte dix-sept épisodes au *Totem maudit* là où le tableau des votes en compte
quatorze — il coupe en deux des soirées que la page française garde entières.
Les deux décrivent les mêmes épreuves, mais « l’épreuve a-t-elle eu lieu avant
sa sortie ? » n’a plus de réponse juste quand les deux fichiers ne parlent pas
la même langue. Le choix de la source ne se fait donc plus au volume mais à
l’**accord avec les conseils** : une page dont la numérotation dépasse de plus
de deux le dernier conseil numéroté est écartée, et le rapport le dit.

<p class="note"><strong>La réparation a elle-même révélé une contradiction, et
on l’a d’abord mal expliquée.</strong> Une fois le vrai tableau de <em>La
Revanche des 4 Terres</em> ouvert, le vérificateur a signalé que Maxime gagnait
l’immunité individuelle de l’épisode 13 <em>et</em> partait au conseil du même
soir. On l’a lu, à tort, comme une épreuve éliminatoire rangée sous
« Immunité », et on a retiré la seule attribution qui se contredisait. La vraie
cause était ailleurs : tout le tableau était rangé un épisode trop loin, et
l’immunité que Maxime avait gagnée à l’épisode 12 tombait sur le soir de son
élimination. La section suivante raconte comment on l’a trouvée.</p>

Ce que cela a déplacé, au moment de la correction : **766 épreuves relevées
devenaient 749**, dont **375 individuelles au lieu de 368** — on en perdait en
volume, on en gagnait en vérité. La couverture de la première épreuve passait de
28 à 29 saisons, le modèle de force était estimé sur 284 épreuves au lieu de 271
et sur 28 saisons au lieu de 26. Aucun des tests du
[registre corrigé]({{ '/methode/' | relative_url }}) n’a changé de conclusion :
21 retenus avant, 21 après. D’autres compléments ont suivi : le relevé compte
aujourd’hui {{ site.data.stats.epreuves.epreuves }} épreuves, dont
{{ site.data.stats.epreuves.individuelles }} individuelles, et le modèle de force
porte sur {{ site.data.stats.modeles.force.epreuves_retenues }} épreuves et
{{ site.data.stats.modeles.force.saisons_retenues }} saisons.

**Une conclusion publiée a néanmoins basculé, et il faut la nommer.**
[La grille]({{ '/statistiques/grille/' | relative_url }}) affirmait que
l’épisode de la réunification **ne bouge pas** avec la taille du casting —
{% assign pf = site.data.stats.modeles.fusion.pente_episode %}
pente 0,008, intervalle −0,135 à 0,152. Elle vaut désormais {{ pf.pente }},
intervalle {{ pf.bas }} à {{ pf.haut }}, p = {{ pf.p }} : la réunification recule bel et
bien, de **{{ site.data.stats.modeles.fusion.croissance_episode_texte }}** sur
toute la croissance des castings. Deux saisons expliquent le
renversement, et les deux étaient fausses. *Cambodge* était <em>écartée</em> du
calcul parce que son dernier collectif tombait à un épisode ne laissant que
quatre joueurs — c’était le décalage de numérotation. *La Revanche des 4 Terres*
plaçait sa réunification à l’épisode 4 sur 17, chiffre lu dans le tableau de classement
des quatre tribus ; elle la place maintenant à l’épisode 8. La page a été
réécrite, et elle raconte ce qu’elle disait avant.

## Une ligne reprise, six défauts trouvés derrière elle

Le 20 octobre 2026, on a repris une seule ligne : l’épisode 13 de *La Revanche
des 4 Terres*. Le relevé y donnait le confort à Maxime et Noémie, l’immunité à
Noémie. La source dit Jérôme et Jérôme — deux homonymes, l’un de la tribu
orange, l’autre de la bleue. En remontant le fil, on a trouvé six défauts de
lecture, tous silencieux, et on les a cherchés dans toutes les saisons.

**Le numéro d’épisode effacé.** Wikipédia écrit la colonne des épisodes avec un
modèle, {% raw %}`{{9e|épisode}}`{% endraw %}. Le nettoyage du texte efface les modèles, et le
numéro avec eux. Le lecteur comptait alors les lignes, et un épisode tenu sur
deux lignes — deux conseils le même soir — décalait d’un cran tout ce qui
suivait. Quatre saisons étaient rangées un épisode trop loin : *Les Armes
secrètes*, *La Revanche des 4 Terres*, *Les Reliques du destin* et *Le Combat
des héros*.

**Une case fusionnée comptée deux fois.** Les saisons récentes étalent un même
cycle sur deux soirs, et la case de l’épreuve couvre alors deux lignes. Elle
était lue à chacune : vingt-deux épreuves comptées deux fois, dans sept saisons.
Les notes de la source disent où tombe chaque épreuve — « Pour l’épreuve de
confort » sur le premier soir, « Pour l’épreuve d’immunité et le conseil » sur
le second — et c’est la règle désormais appliquée.

**Le nom surligné.** Un autre modèle écrit un nom à la couleur de sa tribu.
Effacé lui aussi, il ne laissait de « Maxime et Naïs » que le « et » : un
confort perdu.

**L’invité pris pour un vainqueur.** Les résumés de Wikipédia en anglais
écrivent « Alban [Romuald] » : Alban gagne et emmène Romuald. Le nom entre
crochets était compté comme un second vainqueur, soit neuf victoires de confort
de trop dans quatre saisons. Fandom, là où il couvre la même saison, ne cite que
le gagnant.

**La finale lue comme une épreuve ordinaire.** Les tableaux anglais nomment
leurs épreuves de finale à leur façon — « Treasure Hunt », « Poles Challenge ».
Le lecteur, qui s’arrêtait sur leurs noms français, les laissait passer : le
trio de l’orientation devenait un confort, le gagnant des poteaux une immunité.
Dix épreuves de finale ont été retirées, dans huit saisons.

**Des lignes qui ne sont pas des épisodes.** Le bilan de Fandom pour *La
Légende* numérote ses lignes, et il saute quatre épisodes. Les dates de
diffusion et les jours que donne Wikipédia ont permis de remettre chaque épreuve
à son soir. À *L’Île des héros*, deux numérotations coexistent — le confinement
a coupé des soirées en deux — et le relevé suit maintenant celle des conseils.

<p class="note"><strong>Des attributions démenties par une autre
source.</strong> Linda, à <em>Panama</em> : à l’épisode 9, la note de Wikipédia
précise que l’immunité lui a été <em>donnée</em> à son retour dans le jeu, et à
l’épisode 13, Fandom montre qu’il s’agissait des poteaux. Yassin, au <em>Combat
des héros</em> : le récit de l’épisode 4 le dit deuxième de l’épreuve, pas
vainqueur. Claire, au <em>Cambodge</em> : la page anglaise donnait l’immunité de
l’épisode 10 à Vincent ; Fandom la donne à Claire, et la page de Claire, qui lui
compte « quatre épreuves au total », ne tient qu’avec celle-là.</p>

Deux règles ont été arrêtées au passage. Avec trois ou quatre tribus, Fandom
remplit une colonne par tribu classée. À l’immunité, toutes les tribus classées
sont protégées — sur les douze soirs concernés, l’éliminé du conseil vient
toujours de la seule tribu qui ne l’est pas — et elles comptent comme les
gagnantes d’une même épreuve ; au confort, seule la première l’emporte. Et un confort gagné par trois personnes
Et un confort d’équipe ne donne de victoire individuelle à personne, que la
source écrive « Équipe de Vincent » ou nomme les cinq membres. On ne le déclare
que si une source l’écrit : compter les noms ne suffit pas, deux duos gagnants
ou trois récompenses individuelles ne font pas une équipe.

Au moment de la correction, **743 épreuves relevées devenaient 671**, dont
**328 individuelles au lieu de 362**. Le relevé en compte aujourd’hui
{{ site.data.stats.epreuves.epreuves }}, dont
{{ site.data.stats.epreuves.individuelles }} individuelles. Le contrôle final
tient sur toutes les saisons : chaque immunité individuelle a un conseil le même
soir, et son gagnant n’en est jamais l’éliminé.

À *Vanuatu*, épisode 9, Wikipédia en anglais donnait l’immunité à Ludovic, et
Fandom écrivait « Personne ». Un troisième témoin a tranché : le wiki
anglophone de *Survivor*, dont le tableau des votes porte « Individual
Immunity » face à Ludovic le soir où Alain part. La même page lui compte trois
victoires individuelles, et ce total ne tombe juste qu’avec cette immunité,
ajoutée à ses deux conforts. C’est Ludovic.

Deux conforts restaient indécis, avec quatre et cinq gagnants nommés sans
qu’aucun tableau dise « équipe ». Les récits ont tranché, et ce sont bien des
épreuves d’équipe. À *Caramoan*, épisode 1, le même wiki décrit « four groups
of four » en lice pour le riz. À *L’Île au trésor*, épisode 9, la page Fandom
d’Alexandra raconte que « l’épreuve de confort va se jouer en équipe de 5 » ;
l’équipe de Bruno, dont elle fait partie, l’emporte.

## Le troisième témoin, saison par saison

Le même 20 octobre, chaque saison du relevé a été confrontée au guide
d’épisodes du wiki *Survivor*, puis, à chaque écart, à la page de l’épisode et
aux récits de Wikipédia. La plupart des écarts n’en étaient pas : le guide
range sous « Immunity » des duels et des immunités données, compte toutes les
tribus d’un classement, et nomme certains homonymes par leur initiale
(« Jérôme M. ») là où le relevé a rattaché le bon nom. Ce qui restait a été
corrigé :

- **Une immunité manquait aux *Armes secrètes*, épisode 5** : une épreuve
  combinée, confort et immunité, gagnée par Toa, avant le conseil où Magali,
  une Oro, est éliminée. Wikipédia et Fandom n’écrivaient que la seconde
  immunité du soir.
- **Les tribus protégées des phases à quatre tribus** — *La Revanche des 4
  Terres*, épisodes 1 à 4, et *Le Totem maudit*, épisode 2 — n’étaient pas
  toutes comptées : la page française ne nommait que la première arrivée.
- **Trois gagnants oubliés** : Anne-Sophie au *Totem maudit*, épisode 3 ;
  Claude, dans l’équipe de trois qui gagne le confort de *La Légende*,
  épisode 13 ; les deuxièmes des premières immunités de *La Légende*, que le
  récit dit immunisés aussi.
- **Un confort qui n’a pas eu lieu** : *La Tribu maudite*, épisode 1 —
  « Exceptionnellement, il n’y a pas d’épreuve de confort durant ce premier
  épisode », écrit Wikipédia ; le tableau Fandom en donnait un.

<p class="note"><strong>Une correction publiée était fausse.</strong> Pour le
confort du <em>Totem maudit</em>, épisode 10, la page anglaise écrit « François
[Fouzi, Louana, Ambre, Bastien] », et on n’avait retenu que François. Trois
témoins disent cinq gagnants : le tableau Fandom, le wiki <em>Survivor</em>, et
les fiches Fandom de Fouzi, Louana, Ambre et Bastien, dont le compte de
victoires individuelles ne tombe juste qu’avec celle-là. Les cinq ont été
rétablis.</p>

Au moment de cette vérification, **671 épreuves relevées devenaient 789**, dont
**388 individuelles au lieu de 328** — l’essentiel venant des cinq saisons
ajoutées. Le modèle de force est passé de 28 à
{{ site.data.stats.modeles.force.saisons_retenues }} saisons.

**Une conclusion publiée a basculé, et il faut la nommer.**
[La réunification]({{ '/statistiques/reunification/' | relative_url }}) concluait que l’âge de
l’éliminé bascule à la réunification « mais on ne peut pas l’affirmer » :
p ajustée 0,22. Avec le relevé corrigé, la date de la réunification a bougé
pour plusieurs saisons, et le test passe le seuil, de justesse. La page le dit,
avec l’ancienne conclusion en regard. Aucun autre test du registre n’a changé
de conclusion.

À *Pacifique*, épisode 3, Fandom donne le confort à Kanawa, le wiki *Survivor*
à Kumo, et aucun récit ne raconte l’épreuve — la dégustation. Deux indices
penchent pour Kanawa, et le relevé la garde. La page Fandom de l’épreuve écrit
« Pacifique : Kanawa (kit de pêche) ». Et les fiches des aventuriers restés
dans une même tribu jusqu’à la réunification comptent leurs victoires en
équipe : huit sur dix ne tombent juste qu’avec un confort aux Kanawa ce
soir-là, deux seulement avec un confort aux Kumo. C’est un faisceau, pas une
preuve : si un récit venait à dire l’inverse, il l’emporterait.

## Trois vainqueurs pour une saison qui n’est pas finie

*All Stars* a commencé le 25 août 2026 ; au moment de cette correction, quatre
conseils avaient été joués et deux personnes étaient sorties. Le fichier, lui,
portait **trois vainqueurs et quatre finalistes** — alors que la source
écrivait, pour seize des dix-huit candidats, « Encore en jeu ».

La cause est une colonne. Le tableau des candidats de Wikipédia porte
« Saisons précédentes » — « Vainqueur de la saison 9 », « Finaliste de la
saison 26 », « Éliminée le 12<sup>e</sup> jour du *Choc des héros* » — et, juste
après, « Départ ». Sur une saison en cours, la colonne de départ est **vide** :
personne n’est encore sorti. Le lecteur, qui retient « la dernière cellule qui
ressemble à un sort », tombait alors sur le palmarès et le prenait pour un
départ.

Le code connaissait pourtant le piège : il écartait déjà ces cellules pour ne
pas les ranger comme des **métiers**. Il le faisait simplement trop tard. Le
retrait a été remonté avant la recherche du départ.

Cela ne suffisait pas : un palmarès qui nomme une édition par son titre plutôt
que par son numéro échappe au motif. Plutôt que d’allonger sans fin une
expression régulière, on s’appuie désormais sur ce qu’une source **affirme** :
quand elle écrit « Encore en jeu », l’aventurier n’a pas de sort, et aucune
déduction faite ailleurs ne peut lui en inventer un.

<p class="note"><strong>Le point aveugle du vérificateur, et sa réparation.</strong>
Le contrôle « autant de vainqueurs dans les données que la saison en déclare »
sautait explicitement les saisons en cours — c’est pourquoi rien n’a
sonné. Deux règles le remplacent : une saison non terminée ne peut porter
<em>aucun</em> sort de fin d’aventure, et un sort ne peut pas contredire une
source qui écrit « encore en jeu ». Les deux ont été éprouvées en
réintroduisant la faute exacte.</p>

Effet sur les chiffres du site : **aucun**. Une saison en cours est écartée de
tous les calculs, et le balayage des 170 intervalles alors publiés n’a montré
aucun changement de conclusion. Ce qui a changé est la
[complétude]({{ '/completude/' | relative_url }}) : seize trous de plus,
assumés, là où il y avait seize réponses inventées.

## Le soir du départ, qui faussait trois mesures à la fois

Une question posée à la page du classement — *« et Freddy ? il est bien
classé ? »* — a déclenché une revue complète. Il était **530<sup>e</sup> sur
531**. Ce n’était pas un jugement sévère : c’était un défaut de construction.

{% assign ar = site.data.stats.classement.artefacts %}
Trois des cinq facettes du classement se lisaient sur les bulletins d’un
conseil. Toutes trois comptaient **le soir où l’aventurier quitte le jeu**, et
ce soir-là n’est pas un soir comme les autres.

**La résistance — retirée.** Elle demandait : « s’en sort-il quand son nom est
écrit ? ». Sur les {{ ar.resistance.occasions }} occasions où quelqu’un est visé
à un conseil dépouillé, **{{ ar.resistance.dont_le_soir_du_depart }} sont le
conseil qui l’élimine** — un échec que personne ne peut éviter,
compté comme un échec. Retirez-les et il ne reste que des survies : le taux
monte à **100 % pour tout le monde**. La facette n’avait pas d’autre signal que
cet échec obligatoire. Pire pour ceux qu’on observe peu : sur les
{{ ar.resistance.une_seule_occasion }} participations à une seule occasion
mesurée, **{{ ar.resistance.une_seule_et_fatale }} n’ont pour toute observation
que leur propre élimination**. La facette n’a pas été corrigée, elle
a été **supprimée** — on ne répare pas une mesure qui ne mesure rien.

**La lecture — corrigée.** On ne vote pas pour soi-même : le bulletin qu’un
aventurier émet le soir de son départ est faux par construction.
**{{ ar.lecture.justes_du_partant }} juste sur {{ ar.lecture.bulletins_du_partant }}.**
Les autres soirs, la justesse est de **{{ ar.lecture.taux_des_autres_soirs }} %**,
contre {{ ar.lecture.taux_tout_compris }} % si l’on garde tout. Ce bulletin-là est désormais écarté.

**La discrétion — corrigée.** Les voix qui vous éliminent pèsent
**{{ ar.discretion.part }} %** de toutes les voix relevées, et elles séparent les
*manières de sortir* bien plus que les joueurs : un éliminé au conseil en
reçoit, par définition, bien plus qu’un vainqueur. Les compter revenait à redemander « a-t-il été éliminé au conseil ? »,
ce que le parcours dit déjà. Le soir du départ en est écarté aussi.

<div class="constat">
  <p><b>Ce que la correction a renversé.</b> La page affirmait que les quatre
  facettes non physiques « se tiennent », avec des corrélations de 0,349 à
  0,507, et en concluait qu’il existait un jeu social cohérent. Cet accord
  <b>était fabriqué par le soir du départ</b>, présent dans les trois à la fois.
  Une fois retiré, la corrélation la plus forte entre deux facettes tombe à
  <b>{{ site.data.stats.classement.correlations[0].rho }}</b> — il n’y a plus
  d’accord du tout.</p>
  {% assign ts = site.data.stats.modeles.registre | where: "cle", "talent_stable" | first %}
  <p>Dans l’autre sens : le test de stabilité — un bon joueur l’est-il encore la
  fois suivante ? — passait alors de 0,039 pour p = 0,73 à 0,227 pour p = 0,06.
  Le même artefact l’écrasait. Il vaut aujourd’hui <b>{{ ts.observe }}</b>,
  p ajustée {{ ts.p_ajustee }} : un signal qui reste trop mince pour être
  retenu.</p>
</div>

<p class="note"><strong>La leçon, et elle dépasse ce classement.</strong> Chaque
fois qu’on mesure un taux sur une trajectoire qui se termine, le dernier
événement est structurellement différent des autres — et il est présent une fois
pour chacun. Sur un joueur bien documenté il se dilue ; sur un joueur qu’on
n’observe qu’une fois, il est <em>toute</em> la mesure. Ce n’est pas du bruit,
c’est un biais systématique contre les moins documentés, et il ne se voit pas
dans un contrôle de cohérence : les données étaient exactes, c’est la question
qui était mal posée.</p>

## Une saison qui se joue encore, et trois sources qui mentaient

Le wikitexte brut est versionné dans le dépôt : c’est la **preuve de
provenance**, et c’est elle qui permet de refaire tout le chemin sans
redemander les pages. Les scripts de récupération refusent donc de retélécharger
ce qu’ils ont déjà.

Cette règle est juste pour une saison terminée. Elle est **fausse pour une
saison en cours** : *All Stars* était figée à l’état du 27 août 2026, deux
épisodes, alors que trois avaient été diffusés. Les deux récupérateurs prennent
désormais une option explicite — `--rafraichir sp8` — et le rafraîchissement a
livré les éliminations de Moussa et de **Naoil Tita**, l’un des trois
anciens vainqueurs engagés.

### Trois fichiers de provenance fausse

Le contrôle qui les a trouvés est neuf, et il tient en deux règles : deux
fichiers de source ne peuvent pas être **identiques octet pour octet**, et un
fichier étiqueté `.en.wiki` ne peut pas porter les marqueurs d’une page
française. Il a sonné trois fois.

- **`sp8.en.wiki`** était la copie octet pour octet de la page **française**.
  Les lecteurs d’épreuves et de colliers lisent ce suffixe comme une troisième
  source : ils croyaient donc lire l’anglais. Et comme un fichier en cache ne se
  rafraîchit jamais, la copie avait survécu à la mise à jour de l’original —
  elle était **périmée en plus d’être mal étiquetée**.
- **`sp2.wiki`** et **`sp4.wiki`** — *Le Choc des héros* et *La Nouvelle
  Édition* — sont des pages **Fandom** déposées sous le nom de Wikipédia. Pour
  ces deux saisons, le dépôt croyait croiser deux sources indépendantes alors
  qu’il comparait une source à elle-même.

<div class="constat">
  <p>Conséquence directe sur le chiffre publié plus haut : l’épreuve croisée
  des bulletins portait sur <b>568 bulletins communs</b>. Elle en porte
  aujourd’hui <b>{{ site.data.croisement_votes.bulletins_communs }}</b>.
  <b>Une partie des bulletins croisés était une source comparée à elle-même</b>, et
  son accord parfait était acquis d’avance.</p>
  <p>Le taux, lui, ne bouge pas : {{ site.data.croisement_votes.part_identiques }} %
  d’accord, {{ site.data.croisement_votes.divergents }} divergences. Ce qui
  était faux n’était pas le résultat, c’était la <em>quantité de preuve</em>
  qu’on lui prêtait.</p>
</div>

### Un modèle coupé en deux, encore

Le rafraîchissement a aussi réveillé un vieux piège, sous une forme neuve. Les
tableaux Fandom récents écrivent l’éliminé ainsi :

    |{{Tribebox-bw||}}<span style="color:black">Égalité</span>

Le `||` est ici un **argument vide du modèle**, pas une fin de cellule. Le
découpage des cellules coupait dessus, et le relevé des conseils d’*All Stars*
s’est retrouvé avec un éliminé nommé « `{{Tribebox-bw` » et un autre nommé
« `}} Égalité` ». Le compteur de profondeur existait dans le code — il ne
servait qu’entre les lignes, jamais à l’intérieur d’une ligne. Il y sert
désormais, et aucune autre saison n’en est affectée : le contrôle a comparé les
699 conseils avant et après.

## Ce qui manque

Le jeu de données n’est pas complet, et le dire fait partie du travail. Voici la
mesure exacte, champ par champ. Elle se recalcule à chaque construction : aucune
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
individuelles — <strong>n’existent que par les fiches individuelles</strong> :
aucune table de saison ne les porte. Ils sont donc renseignés là où une fiche
existe, et nulle part ailleurs. Le rang final se contrôle contre le jour de
sortie : sur {{ site.data.stats.general.rang_concordant }} saisons sur
{{ site.data.stats.general.rang_compare }} comparables, les deux classent les
aventuriers dans exactement le même ordre.</p>

<p class="note">La même mesure, <strong>édition par édition</strong> et type de
donnée par type de donnée, tient sur une seule grille :
<a href="{{ '/completude/' | relative_url }}">La complétude, édition par
édition</a>.</p>

Ce qui reste, et pourquoi :

- **Le dépouillement des conseils est partiel.** Sur
  {{ site.data.stats.conseils.conseils }} conseils relevés,
  {{ site.data.stats.conseils.conseils_complets }} ont un dépouillement dont on
  peut garantir qu’il est complet. Les analyses bulletin par bulletin ne portent
  que sur ceux-là ; les agrégats — qui part, avec combien de voix — utilisent
  tous les conseils. Deux causes, mesurées : **{{ site.data.stats.conseils.conseils_sans_decompte }}
  conseils n’annoncent aucun décompte** — la source ne dit pas combien de voix
  ont été exprimées, donc la complétude n’y est pas vérifiable ; et
  **{{ site.data.stats.conseils.conseils_decompte_incomplet }} annoncent un
  décompte que le tableau ne restitue pas exactement**, dont
  {{ site.data.stats.conseils.conseils_un_bulletin_manquant }} auxquels manque
  un seul bulletin. Ceux-là
  ont été inspectés cellule par cellule : les cases sont **vides dans la source**.
  Ce n’est pas une lecture qui échoue, c’est un wiki qui n’a pas tout noté.
- **Les épreuves couvrent toutes les saisons, mais pas à égalité.**
  {{ site.data.stats.epreuves.saisons_couvertes }} saisons sur
  {{ site.data.stats.general.saisons_diffusees }} ont un bilan épisode par
  épisode ; pour {{ site.data.stats.mots.saisons_source_unique }} d’entre elles
  ({{ site.data.stats.epreuves.saisons_source_unique_texte }}), il ne vient que
  d’une source, le guide d’épisodes du wiki *Survivor*. Les épreuves de finale sont exclues : les tableaux sources y changent de
  colonnes et listent les qualifiés plutôt que le vainqueur. Quant à la
  **nature** des épreuves, le wiki la donne — {{ site.data.epreuves_nommees.nb_epreuves }}
  pages d’épreuves récurrentes, typées — mais sans le numéro d’épisode, si bien
  que seules {{ site.data.epreuves_nommees.raccord.part_raccordee }} % des
  épreuves relevées peuvent la recevoir, et pas au hasard.
  [Les épreuves]({{ '/statistiques/epreuves/' | relative_url }}) le mesure.
- **Les colliers d’immunité ne sont détaillés que sur
  {{ site.data.stats.colliers.saisons_couvertes }} saisons.** Les autres les
  mentionnent sans donner leur destin. Et seuls les *colliers* sont suivis :
  armes secrètes, totem maudit et talisman du feu sacré sont des mécaniques
  distinctes, absentes de ces comptes. En revanche le **fait qu’un objet ait
  été joué** se lit dans les bulletins barrés, sur
  {{ site.data.stats.conseils.saisons_avec_objet_joue }} saisons : c’est une
  information plus pauvre — on ne sait pas de quel objet il s’agit — mais
  beaucoup plus large.
- **La justesse de vote ne porte que sur une partie des conseils.** Elle exige
  un conseil au dépouillement complet <em>et</em> un éliminé rattaché :
  {{ site.data.stats.conseils.conseils_justesse }} conseils, pas les
  {{ site.data.stats.conseils.conseils }}. L’indicateur est
  publié avec sa base, et penche vers les saisons les mieux documentées.
- **Le vote du jury final n’est pas un conseil.** {{ site.data.stats.jury.saisons }}
  saisons en publient le détail, et les tableaux sources le présentent comme un scrutin
  ordinaire —
  avec le vainqueur en « sortant ». Or on n’y élimine personne : écrire un nom
  y signifie « qu’il gagne ». Ces {{ site.data.stats.jury.effectif }} scrutins
  sont marqués `type: jury` dans les données et tenus à l’écart de tout calcul
  d’élimination.
- **La saison en cours** au moment de la constitution des données n’a pas de
  vainqueur ni de jours de sortie complets : elle est exclue de tous les calculs.

## Une correction d’extraction, et ce qu’elle a déplacé

Les tableaux de Fandom affichent une vignette à côté du nom de l’éliminé :
`[[Fichier:Sara.png|75px|link=Sara Tallon]]`. Le nettoyage du wikitexte traitait
ce lien de fichier comme un lien ordinaire et en gardait la **taille
d’affichage**. Résultat : 478 conseils sur 681 portaient « 75px » en guise
d’aventurier, et n’étaient rattachables à personne.

La correction se fait à la racine, dans le nettoyage du wikitexte : un lien de
fichier ne rend plus que sa cible `link=`, ou rien. Les éliminés rattachés
passaient alors de 203 à **578**, et l’index « épisode de sortie » — celui qui
donne l’exposition aux épreuves — de 248 à environ 600 participations sur 645. Un
contrôle refuse désormais tout nom contenant de la syntaxe MediaWiki.

**La même vignette avait une seconde moitié, trouvée bien plus tard.** Quand la
cellule porte à la fois la vignette et le prénom —
`[[Fichier:Ugo.png|75px|link=Ugo Lartiche]]<br />Ugo` — le nettoyage rend les
deux à la suite : « Ugo Lartiche Ugo », qui n’est le nom de personne. Trois
saisons entières y perdaient leurs éliminés. La résolution essaie désormais, à
défaut du libellé entier, son plus long préfixe qui soit **exactement** un nom
complet de la saison : aucune valeur n’est devinée, et un préfixe ne peut jamais
valoir un prénom nu. Les éliminés rattachés passaient de 578 à 622 sur 649 ;
ils sont aujourd’hui **{{ site.data.stats.conseils.elimines_rattaches }}** sur
{{ site.data.stats.conseils.conseils_hors_jury }}.

Cette réparation-là a coûté un résultat. L’effet du **sexe minoritaire** portait
la plus haute des p ajustées retenues du site, et
[la page le disait]({{ '/statistiques/autour-du-feu/' | relative_url }}) — « une
saison de plus pourrait la faire basculer ». Quarante-quatre éliminations de
plus ont suffi : l’écart n’a presque pas bougé, la correction pour tests
multiples ne le gardait plus. C’est exactement ce à quoi sert une liste de tests
arrêtée avant de regarder — et elle a joué dans les deux sens : des bulletins
retrouvés plus tard l’y ont fait revenir (voir plus bas, « Les bulletins que
personne n’écrit »).

Trois chiffres publiés ont bougé, tous dans le sens d’une base plus large :

- les **votes du jury final** détectés passent de 8 à
  {{ site.data.stats.jury.effectif }}. Les scrutins manquants étaient comptés
  comme des éliminations ordinaires, ce qui inversait le sens de leurs
  bulletins ;
- le nombre d’aventuriers classables aux **ratios d’épreuves** passe de 89 à
  {{ site.data.stats.epreuves.classement_effectif }} ;
- les **fantômes** passent de 38 à
  {{ site.data.stats.indicateurs.nb_fantomes }}, l’ancien décompte reposant sur
  211 participations mesurables au lieu de
  {{ site.data.stats.indicateurs.mesurables }}. Leur taux de victoire, mesuré
  cette fois contre un groupe de comparaison correct, en est nettement réduit.

{{ site.data.stats.conseils.elimines_non_rattaches }} conseils restent volontairement
non rattachés : leur éliminé n’y est désigné que par un prénom que deux
aventuriers de la saison portent — Jérôme, dans *La Revanche des 4 Terres*.
Plutôt que de trancher, on laisse la valeur vide.

## Deux autres pannes silencieuses, et ce qu’elles cachaient

La réparation du `75px` racontée plus haut n’était pas la dernière. Deux autres
défauts d’extraction ne produisaient **aucune erreur** : simplement, des données
manquaient.

**Les bulletins enveloppés dans une pastille de tribu.** Dans les saisons
récentes, les tableaux de Fandom n’écrivent plus le nom visé en clair : ils l’enveloppent dans
un modèle, `{% raw %}{{Tribebox-bw|Ilog|Lili}}{% endraw %}`, dont le premier
paramètre est la tribu et le second le nom. Le nettoyage général du wikitexte
retire les modèles — et donc effaçait le nom. Résultat :
*Les 4 Terres* et *Le Totem maudit* n’avaient **aucun bulletin**, et six autres
saisons récentes en avaient la moitié. Le second paramètre est désormais sorti
du modèle avant nettoyage : **{{ site.data.stats.conseils.bulletins }} bulletins
au lieu de 3 206**, et {{ site.data.stats.conseils.conseils_complets }} conseils
au dépouillement garanti complet au lieu de 264.

Deux autres bugs de lecture tombaient au même endroit : un intitulé de ligne
écrit `|►Votes` — avec le tuyau du tableau resté collé — faisait chercher les
votants tout en bas de la table, où il n’y en a pas ; et le nom du votant était
lu dans la première colonne d’étiquette alors qu’il est dans la dernière, quand
la ligne y loge d’abord ses pastilles de tribu.

Un contrôle refuse désormais qu’une saison entière annonce des décomptes de
voix sans qu’un seul bulletin en soit lu. C’est exactement la forme qu’avait
cette panne, et elle ne pouvait pas se voir autrement.

**Un article qui n’était pas le bon.** Le récupérateur demandait à Wikipédia
« Koh-Lanta: Bocas del Toro », que le wiki **redirige vers l’article général du
programme** — dix-neuf kilo-octets, qui passaient donc tous les contrôles de
taille. Le fichier était dans le dépôt depuis le début, présenté comme la source
de la saison 3. Il n’apportait rien, mais il mentait sur sa provenance. Le
récupérateur vérifie maintenant que la page atteinte est bien celle demandée, et
refuse la redirection vers un autre article ; la saison 3 est désormais
déclarée sans source Wikipédia, ce qu’elle a toujours été.

## Une épreuve croisée sur les bulletins

{% assign cv = site.data.croisement_votes %}

Sur une partie des saisons, les deux sources publient **chacune** leur matrice
des votes. Jusqu’ici on gardait la plus riche et on jetait l’autre. C’est du
gâchis : la seconde permet de vérifier la première.

<div class="constat">
  <p>{{ cv.bulletins_communs }} bulletins figurent dans les deux sources.
  <b>{{ cv.identiques }} sont identiques — {{ cv.part_identiques }} %.</b>
  {{ cv.divergents }} divergent.</p>
  <p>C’est la première mesure directe de la fiabilité du relevé des votes, et
  elle est rassurante. Les {{ cv.divergents }} divergences sont toutes deux le
  même problème : deux Jérôme dans <i>La Revanche des 4 Terres</i>, que les
  deux wikis distinguent différemment.</p>
</div>

La seconde source apporte en outre
{{ cv.ajoutes_par_seconde_source }} bulletins que la première ignore. C’est
peu, et c’est délibérément peu : **l’appariement n’est fait que lorsqu’un
épisode ne contient qu’un seul conseil de chaque côté.** Un épisode à deux
conseils — une égalité suivie d’un second vote — ne se découpe pas de la même
façon d’une source à l’autre, et les apparier au nom de l’éliminé confondrait
le premier tour avec le second.

<p class="note">Cette prudence n’est pas théorique : une première version
appariait sur l’épisode <em>et</em> le nom de l’éliminé, sans vérifier
l’unicité. Elle annonçait 39 bulletins gagnés et 16 divergences — dont sept
fabriquées de toutes pièces par la confusion des deux tours d’un même épisode.
La règle stricte donne moins de bulletins et un taux d’accord plus élevé : les
deux chiffres sont vrais, les précédents ne l’étaient pas.</p>

## Le soir à plusieurs conseils, piège récurrent

{% assign af = site.data.stats.modeles.autour_du_feu %}
{% assign imm = af.immunite | first %}

Le paragraphe ci-dessus décrit un piège rencontré sur l’appariement des
bulletins. Il s’est représenté ailleurs, sous une autre forme, et il mérite
d’être nommé une bonne fois : **un épisode n’est pas un conseil.**

Un même soir peut en compter deux, trois, parfois quatre — une égalité suivie
d’un second vote, deux tribus qui votent chacune de leur côté, un épisode final
qui enchaîne les éliminations. Tout rapprochement fait sur le seul numéro
d’épisode y devient faux.

<div class="constat">
  <p>Contrôle : <b>l’aventurier qui gagne l’immunité individuelle ne peut pas
  être éliminé le soir même.</b> C’est une règle du jeu ; si les données la
  violent, c’est qu’un rattachement est bancal.</p>
  <p>Rapproché sur le seul épisode, le contrôle sortait <b>19 violations</b>.
  Toutes les dix-neuf tombaient sur un soir à plusieurs conseils : dans un
  épisode qui en compte trois, l’immunité gagnée avant le premier ne protège
  pas au troisième.</p>
  <p>Rapproché correctement — soirs à conseil unique, camp lu dans les
  bulletins — il en sortait encore trois. Le rattachement était juste ; c’est la
  question qui était mal posée. Les trois qui restaient étaient un autre défaut,
  de lecture cette fois : les finales de <i>Vanuatu</i>, <i>Palawan</i> et
  <i>Caramoan</i>, où l’épreuve éliminatoire était lue comme une immunité.
  L’extraction écarte désormais ces trios de finale — cinq saisons en
  portaient un — et il en sort <b>{{ imm.cas }} sur {{ imm.effectif }}
  présences</b>.</p>
</div>

Conséquence pour tout ce site : une épreuve du soir n’est jamais rattachée à un
conseil quand l’épisode en compte plusieurs.
[Sachant qui est autour du feu]({{ '/statistiques/autour-du-feu/' | relative_url }})
s’appuie sur cette règle.

## Les bulletins que personne n’écrit

{% assign cs = site.data.stats.conseils %}

Le site mesurait **20 %** de conseils dépouillés sur la période 2020-2024, contre
67 % au début des années 2000, et cette chute était donnée pour ce qu’elle
semblait être : une source qui en dirait moins. Vérification faite, c’est faux.
Le parseur lit **{{ cs.part_bulletins_lus }} %** des bulletins que les matrices
annoncent. Ce qui
manquait n’était pas la donnée, c’était une **règle de tout ou rien**.

Un conseil n’est déclaré dépouillé que si le nombre de bulletins lus égale
exactement le nombre de voix que la source annonce. Or, depuis
{{ cs.sans_votant.annee_min }}, le jeu produit des voix **que personne
n’écrit** : le *vote noir* qu’un éliminé offre à
un survivant, la *pénalité*, la *malédiction* qui donne une voix d’office à
celui qui la porte. La matrice leur consacre une ligne à part, sous les
candidats. Elles comptent dans le total annoncé — et aucun calcul de ce site ne
les comptait.

Il en manquait donc systématiquement une ou deux par conseil, et le conseil
entier tombait. Pas une erreur, pas un avertissement : simplement une case
« complet » à `false`, et vingt-cinq conseils de la saison 23 absents de toutes
les analyses au bulletin — sur une saison dont **82 % des bulletins étaient
pourtant lus**.

<div class="constat">
  {% assign dep = site.data.stats.classement.biais_epoque.depouillement %}
  <p>La réparation a d’abord rendu <b>120 bulletins sans votant</b>, sur treize
  saisons de 2017 à 2025. Les relevés suivants en ont retrouvé d’autres : on en
  compte aujourd’hui <b>{{ cs.sans_votant.bulletins }}</b>, sur
  {{ cs.sans_votant.saisons }} saisons de {{ cs.sans_votant.annee_min }} à
  {{ cs.sans_votant.annee_max }} — {{ cs.sans_votant.detail_texte }}.</p>
  <p>Conseils dépouillés : <b>279 → {{ cs.conseils_complets }}</b>. Sur
  2020-2024, la part passait alors de 20 % à 39 %, et sur 2015-2019 de 44 % à
  56 % ; elles sont aujourd’hui de <b>{{ dep[4].part }} %</b> et
  {{ dep[3].part }} %. Au moment de la réparation, <b>aucune saison antérieure
  à 2015 n’avait bougé d’un bulletin</b> — c’était le contrôle : elle ne devait
  toucher que les saisons où ces mécaniques existent.</p>
</div>

Un bulletin de mécanique **n’a pas de votant**, et le fichier le dit : il porte
`votant: null` et le motif qui l’a produit. Toutes les mesures du côté de
l’émetteur — la lecture, les alliances, la réciprocité, qui-vise-qui — le
laissent donc de côté sans qu’aucune ne l’ait demandé, parce qu’elles filtrent
déjà sur `votant_rattache`. Il ne compte que **là où il a un sens** : au-dessus
de la personne visée.

<p class="note"><strong>Un second défaut, trouvé en réparant le premier.</strong>
Une cellule bien formée sépare ses attributs de son contenu par un tuyau :
<code>| rowspan="3" | Lili</code>. Les tables récentes écrivent parfois
<code>| rowspan="3" &#123;&#123;Tribebox-bw|Ilog|Lili&#125;&#125;</code> — sans le second
tuyau, le suivant appartenant au modèle. Deux choses cassaient alors ensemble et
sans bruit : le <code>rowspan</code> n’était jamais appliqué, donc toutes les
lignes suivantes glissaient d’une colonne ; et le nom visé devenait
<code>rowspan="3" Lili</code>, que le contrôle « est-ce un vote ? » rejetait à
cause du signe égal — un contrôle posé, justement, pour attraper les attributs
qui débordent.</p>

<p class="note"><strong>Ce que la réparation a déplacé, et il faut le dire en
entier.</strong> Trois résultats ont alors changé de statut après correction de
Benjamini-Hochberg. Deux entraient :
<a href="{{ '/statistiques/qui-vise-qui/' | relative_url }}">on épargne le
voisin de département</a> et
<a href="{{ '/statistiques/autour-du-feu/' | relative_url }}">être du sexe
minoritaire protège</a>. Un sortait :
<a href="{{ '/statistiques/conditionnelles/' | relative_url }}">le sommet de la
menace</a>, dont l’écart a maigri de moitié — 15,4 points à 9,5 — dès que les
conseils qui lui manquaient sont arrivés. <strong>Un résultat qui tombe quand
l’échantillon grandit est un résultat qui n’aurait pas dû être affirmé</strong> ;
celui-là a été affirmé, et il l’est resté plusieurs semaines.</p>

{% assign tv = site.data.stats.modeles.registre | where: "cle", "vote_meme_departement" | first %}
{% assign tm = site.data.stats.modeles.registre | where: "cle", "menace_sommet" | first %}
<p class="note"><strong>Et depuis.</strong> Le voisin de département est ressorti
des résultats retenus, de justesse : p ajustée {{ tv.p_ajustee }}. Du sommet de la menace,
il ne reste rien — {{ tm.observe_arrondi }} points observés pour
{{ tm.attendu_arrondi }} attendus. Le sexe minoritaire, lui, tient toujours.</p>

## Comment c’est fabriqué

Les données sont extraites, croisées et vérifiées par des scripts Python, puis
commitées dans le dépôt. Un contrôle d’intégrité refuse tout jeu incohérent :
autant de vainqueurs que la saison en déclare, un jour de sortie qui ne dépasse pas la durée de
la saison, une couleur de tribu qui existe bien dans la saison, toute clé
étrangère résolue.

Les statistiques et les graphiques sont calculés en amont, une fois, et non à
l’affichage : le site ne fait que présenter un résultat déjà vérifié.

Une bonne partie des pages reposent en outre sur des **modèles** plutôt que sur
des comptages :
régression, analyse factorielle, modèle de durée, tests de permutation. Leurs
tirages aléatoires partent tous d’une graine fixe, et la construction est jouée
deux fois pour vérifier qu’elle rend le même fichier au bit près.
[La méthode]({{ '/methode/' | relative_url }}) en donne le détail et la liste
complète des tests.

## Les portraits et les comptes : une source, et deux preuves exigées

{% assign po = site.data.portraits.portraits %}
{% assign re = site.data.reseaux.comptes %}

Le site n’héberge **aucune photo de presse**. Les {{ po.size }} portraits
publiés viennent tous de Wikimedia Commons, et uniquement sous une licence qui
autorise la republication : domaine public, CC0, CC BY, CC BY-SA. Toute image
portant une restriction, une clause non commerciale ou une clause sans
modification est écartée par le script, pas par un choix au cas par cas. **Le
nom de l’auteur et la licence sont affichés sous chaque photo**, sur la fiche
elle-même : c’est la condition de ces licences, et il n’y a pas de page annexe
où les reléguer.

Les {{ re.size }} fiches qui portent des comptes publics les tiennent de
Wikidata, où un compte est rattaché à une personne identifiée. Chercher
« Instagram + prénom » aurait donné des liens vers la mauvaise personne.

**Le nom ne suffit pas à apparier, et c’est le point délicat.** Deux routes
{% assign wd = site.data.wikidata %}
mènent d’un nom à un élément Wikidata : le titre d’un article francophone
({{ wd.correspondances_titre }} correspondances) et le libellé de l’élément
lui-même ({{ wd.correspondances_libelle }}). Mais ces
correspondances mêlent Claude Dartois et Teheiura Teahui à une danseuse
ukrainienne et à un avocat, et rien dans le nom ne les sépare. Un élément n’est
donc retenu que s’il réunit **deux conditions** : être un être humain, et que le
jeu soit écrit quelque part — dans ses déclarations, dans sa description, ou
dans le texte de son article. **{{ wd.apparies }}** passent,
{{ wd.candidats_ecartes }} candidats sont écartés faute de preuve.

Sur ces {{ wd.apparies }}, {{ wd.images_trouvees }} portent une photo, dont
{{ wd.portraits_publies }} sous une licence libre : ce sont les seules publiées.

Ce que cela coûte, et qui est assumé : un aventurier dont l’article porte un
titre désambiguïsé n’est pas trouvé, et reste sans photo. Une fiche nue vaut
mieux qu’une fiche qui montre quelqu’un d’autre. **Le plafond n’est pas dans le
script, il est dans la source** : Wikimedia Commons n’héberge pas de photo
libre de la plupart des participants, et il n’existe pas d’autre gisement
d’images réutilisables pour ce programme.

Deux précisions sur le filtre. Une image portant la mention *personality
rights* est acceptée : ce n’est pas une restriction de droit d’auteur mais
l’avertissement posé sur toute photo où une personne est reconnaissable, et
publier le portrait de quelqu’un sur la page qui lui est consacrée est
précisément l’usage éditorial pour lequel ces images sont versées. Et une image
du domaine public peut n’avoir aucun auteur nommé : la licence s’affiche alors
seule, l’attribution n’étant pas exigée.
