---
layout: page
title: La méthode
permalink: /methode/
chapeau: >-
  Quels modèles, sur quelles données, avec quelles limites — et la liste
  complète des tests, publiée pour qu’on ne puisse pas n’en garder que les bons.
---

{% assign m = site.data.stats.modeles %}

Onze pages de ce site reposent sur des modèles plutôt que sur des comptages :
[La recette du casting]({{ '/statistiques/casting/' | relative_url }}),
[Le pronostic]({{ '/statistiques/pronostic/' | relative_url }}),
[La force réelle]({{ '/statistiques/force/' | relative_url }}),
[Le jeu tenu serré]({{ '/statistiques/equilibre/' | relative_url }}),
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}) et
[La grille]({{ '/statistiques/grille/' | relative_url }}),
[Qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}) et
[Le vote du jury]({{ '/statistiques/jury/' | relative_url }}) et
[D’où ils viennent]({{ '/statistiques/geographie/' | relative_url }}),
[L’audience]({{ '/statistiques/audience/' | relative_url }}) et
[Avant et après la fusion]({{ '/statistiques/fusion/' | relative_url }}). Cette
page dit comment ils sont construits et ce qu’ils ne peuvent pas établir.

## Trois règles, tenues partout

**Jamais de p-value sans taille d’effet.** Un écart « significatif » de un quart
d’année reste un écart d’un quart d’année. Chaque test publie donc ce qu’on
observe, ce que le hasard donnerait, et l’écart entre les deux.

**Jamais de taille d’effet sans intervalle.** Un coefficient seul laisse croire à
une précision qui n’existe pas. Les intervalles à 95 % sont partout, et
plusieurs résultats de ce site consistent précisément en un intervalle qui
traverse la valeur neutre.

**Tous les tests sont déclarés.** La liste ci-dessous est complète : elle
contient les résultats nets comme les échecs. C’est ce qui rend la correction
pour tests multiples honnête — corriger sur une liste choisie après coup ne
corrige rien.

## Pourquoi corriger, et comment

{{ m.nb_tests }} tests sont menés. Au seuil habituel de 5 %, on attend un peu
plus d’un « résultat » né du seul hasard. La procédure de **Benjamini-Hochberg**
ajuste les p-values pour borner la part de fausses découvertes parmi celles
qu’on retient. Les deux valeurs sont publiées : brute et ajustée.

**{{ m.nb_retenus }} tests sur {{ m.nb_tests }}** franchissent le seuil après
correction.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Test</th><th>Question</th><th class="nombre">Observé</th>
  <th class="nombre">Attendu</th><th class="nombre">Écarts-types</th>
  <th class="nombre">p</th><th class="nombre">p ajustée</th><th>Retenu</th>
</tr></thead>
<tbody>
{% for t in m.registre %}
<tr>
  <td><b>{{ t.libelle }}</b></td>
  <td>{{ t.question }}</td>
  <td class="nombre">{{ t.observe }} {{ t.unite }}</td>
  <td class="nombre">{{ t.attendu }}</td>
  <td class="nombre" data-val="{{ t.ecart_types }}">{{ t.ecart_types }}</td>
  <td class="nombre">{{ t.p }}</td>
  <td class="nombre">{{ t.p_ajustee }}</td>
  <td>{% if t.retenu %}oui{% else %}non{% endif %}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Les modèles, un par un

### Le test de permutation

Utilisé pour toutes les questions de composition du casting. On rebat les
aventuriers au hasard entre les saisons, en gardant la taille de chaque casting,
et on recommence **{{ m.permutations }} fois**. La comparaison ne se fait donc
pas à la population française, mais **au même vivier, redistribué**. Un écart
qui subsiste est un écart que le hasard ne produit pas.

Variante de contrôle : rebattre uniquement à l’intérieur d’une même décennie.
Le casting a dérivé en vingt-cinq ans, et sans cette précaution on confondrait
une règle de composition avec un simple effet d’époque.

### L’analyse des correspondances multiples

Trois variables qualitatives — âge en tranches, sexe, famille de métier — ne se
projettent pas dans un plan par une moyenne. L’ACM passe par le tableau
disjonctif et le décompose, ce qui donne des **axes latents** : les directions
selon lesquelles les profils se séparent réellement, qu’aucune colonne ne porte.
Une classification automatique tourne ensuite sur ces axes ; le nombre de
groupes est celui qui maximise l’indice de silhouette, à condition qu’aucun
groupe ne pèse moins de 2 % du casting.

**Le bandeau en est exclu**, et cette exclusion est un correctif : tant qu’il y
figurait, le test du « mélange d’archétypes » sortait à 7,95 écarts-types. Les
couleurs en jeu changeant d’une saison à l’autre, une saison ne pouvait
mécaniquement pas contenir tous les profils — le test mesurait la grille des
tribus, pas le casting. Sans le bandeau, il tombe à 1,06 et n’est pas retenu.

### Le modèle de Plackett-Luce

Un gagnant parmi K. Chaque aventurier reçoit une force ; la probabilité qu’il
gagne vaut sa force divisée par la somme des forces présentes. Ajusté par
l’algorithme MM, avec une loi a priori Gamma — sans elle, un joueur invaincu
partirait à l’infini et un joueur sans victoire n’aurait pas d’estimation finie.

Le plateau de chaque épreuve est **reconstruit** : `epreuves.yml` ne contient que
les vainqueurs. La reconstruction se contrôle elle-même — le vainqueur doit
figurer dans son propre plateau — et son taux d’échec,
**{{ m.force.taux_echec_reconstruction }} %**, est publié.

### Le modèle de durée de Cox

Pour savoir qui sort plus vite à saison identique. Stratifié par saison : on ne
compare que des aventuriers du même plateau, ce qui neutralise la durée de la
saison, la taille du casting et l’époque. Les abandons sont **censurés**, pas
comptés comme des éliminations : quitter le jeu de soi-même n’est pas en être
sorti.

### La segmentation binaire

Pour dater une rupture de format. On cherche la coupure de la série des saisons
qui sépare le mieux deux régimes, sur plusieurs indicateurs standardisés à la
fois. **La date sort des données**, elle n’est pas choisie — et comme une
coupure existe toujours, sa qualité est comparée à celle de la meilleure coupure
obtenue sur des saisons remises dans un ordre au hasard.

### Le logit conditionnel

Quand le choix est contraint — un juré choisit parmi les finalistes de sa
saison, pas parmi tout le casting — c’est le modèle juste. Chaque choix forme
son propre groupe de comparaison, ce qui absorbe d’un coup tout ce qui est
constant à l’intérieur du groupe : la saison, l’année, le caractère du juré. Il
ne reste que ce qui distingue les options **entre elles**.

### Le modèle nul du réseau des votes

Pour la persistance des alliances, le modèle nul ne consiste pas à supposer que
personne ne vote pareil. On **rebat les bulletins à l’intérieur de chaque
conseil**, en gardant intacte la répartition des voix — quatre contre l’un, deux
contre l’autre. Ce qui disparaît est le seul lien d’un conseil au suivant. Tout
ce qui survit à ce brassage est donc de la coordination qui traverse le temps.

Ce brassage porte une contrainte qui n’a rien d’un détail : **un votant ne peut
pas recevoir son propre nom**. Sans elle, 12,5 % des bulletins tirés étaient des
couples impossibles — et comme un tel couple partage forcément le sexe, le
métier et le bandeau de son auteur, l’attendu s’en trouvait gonflé et trois
résultats spectaculaires sortaient de nulle part. Ils se sont évanouis une fois
la contrainte posée. L’épisode est raconté sur
[Qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}), parce qu’il
dit mieux que tout ce qu’un test de permutation vaut : **exactement ce que vaut
son modèle nul**.

### La régression logistique, pour un oui ou un non

Quand la chose à expliquer est binaire — être rappelé ou non, partir ou non — et
que les observations ne se regroupent pas naturellement, c’est le modèle
ordinaire. Il rend des **rapports de cotes** : au-dessus de 1, l’événement est
plus probable, toutes les autres variables tenues fixes. Il sert sur
[Les revenants]({{ '/statistiques/revenants/' | relative_url }}) pour séparer ce
que la production choisit de ce que la longévité explique déjà.

Ses coefficients ne figurent **pas** dans le registre des tests corrigés :
celui-ci ne contient que les tests de permutation, dont le modèle nul est
explicite et vérifiable. Un coefficient de régression y est publié avec son
intervalle, et il se lit comme tel — une estimation, pas une découverte.

### Le modèle nul qui n’est pas un tirage au hasard

Les nuls décrits jusqu’ici tirent uniformément : l’éliminé au hasard parmi les
présents, les bulletins rebattus, les comptes redistribués. Un quatrième type
existe et il répond à une autre question — **ce que le hasard produit** n’est
plus la bonne référence quand on veut savoir si un effet dépasse **ce qu’un
modèle déjà ajusté explique**.

Pour l’enchaînement des victoires d’épreuve, le nul tire donc les vainqueurs
**selon les forces estimées** par le modèle de Plackett-Luce. Un enchaînement
qui n’excède pas ce nul-là ne dit rien de plus que « les forts sont forts ».
[La force réelle]({{ '/statistiques/force/' | relative_url }}) publie les deux
références côte à côte, parce que c’est leur écart qui est le résultat.

Ce nul est **conservateur** : les forces sont ajustées sur les mêmes épreuves,
enchaînements compris, si bien qu’un élan réel y serait partiellement absorbé.
Il permet de conclure « rien au-delà du niveau » ; il ne permettrait pas de
conclure l’inverse.

### Le repère mobile : une chance sur n

Une probabilité de sortir ne se lit jamais seule. À un conseil à six, on part
une fois sur six ; à douze, une fois sur douze. Le repère de toutes les
probabilités conditionnelles de ce site est donc **la moyenne de 1/n sur les
présences considérées**, et il change d’une catégorie à l’autre : le doyen d’un
camp l’est plus souvent quand le camp est petit, donc son hasard à lui est plus
haut que la moyenne générale.

Le modèle nul correspondant est le plus simple qui soit et c’est lui qui fait
tout le travail : à chaque conseil, **on tire l’éliminé au hasard parmi les
présents**. La taille du conseil, la saison, l’époque, la composition du camp
restent exactement ce qu’elles étaient ; seule disparaît la question posée. Un
écart qui survit à ce brassage ne peut plus être un effet de taille. Sans lui,
[le doyen du camp]({{ '/statistiques/autour-du-feu/' | relative_url }}) aurait
été publié comme un résultat.

### Le modèle nul des comptes de voix

Le brassage ci-dessus a une limite qu’il faut nommer, parce qu’elle a failli
produire un test vide : **il change qui a écrit, jamais combien de voix chacun
reçoit.** Le nombre de voix d’une personne y est rigoureusement le même avant et
après la permutation. Toute question portant sur ce nombre — « celui qui a été
visé la dernière fois est-il visé encore ? » — resterait donc invariante, et le
test rendrait mécaniquement zéro.

Le nul qu’il faut alors redistribue les **comptes** entre les présents d’un même
conseil, l’éliminé gardant le sien : chaque soirée conserve sa forme de
dépouillement — cinq voix, deux voix, une — et son résultat, et seule l’identité
de ceux qui les reçoivent est tirée au sort. Il sert sur
[Sachant le conseil d’avant]({{ '/statistiques/conditionnelles/' | relative_url }}).

### La corrélation de rang, et la tendance qu’il faut d’abord retirer

Deux grandeurs qui dérivent chacune avec les années se corrèlent toujours, et le
lien ne dit alors rien de plus que « le temps passe ». Chaque fois que deux
séries temporelles sont mises face à face, on ajuste donc une droite sur l’année
et on ne corrèle que les **résidus** — l’écart d’une saison à ce que son époque
laissait attendre. La corrélation brute est publiée à côté, pour qu’on voie ce
que la précaution enlève : sur
[L’audience]({{ '/statistiques/audience/' | relative_url }}), elle fait passer un
lien de −0,64 à −0,30, et le résultat de spectaculaire à nul.

### Le rétrécissement vers la moyenne, plutôt qu’un seuil qui exclut

Un taux sur trois essais ne veut rien dire — mais écarter d’un classement tous
ceux qui n’ont que trois essais fabrique un classement de survivants, et les
seuils employés ailleurs sur ce site
([les épreuves]({{ '/statistiques/epreuves/' | relative_url }}),
[le jeu social]({{ '/statistiques/jeu-social/' | relative_url }})) coupent la
population en deux plutôt que de la mesurer.

Le [top des joueurs]({{ '/statistiques/top/' | relative_url }}) prend l’autre
route : chaque taux est tiré vers la moyenne de la population, d’autant plus
fort que les essais sont rares. Faute de preuve, un aventurier vaut la
moyenne — il ne vaut ni zéro, ni l’exclusion, et il reste dans le classement
avec son incertitude.

La force du rétrécissement n’est **pas choisie à la main**. Elle est estimée sur
les données par la méthode des moments : on retranche à la dispersion observée
des taux la part qui s’explique par le seul hasard d’échantillonnage — binomiale
pour une proportion, de Poisson pour un comptage, et pour une note continue la
variance d’un même joueur d’une saison à l’autre. Ce qui reste est la dispersion
**entre** joueurs, et c’est elle qui décide.

Deux conséquences se lisent directement, et elles sont publiées. Quand cette
dispersion est franche, le rétrécissement est faible et le classement est net.
Quand elle **n’est pas décelable** — c’est le cas de la longueur de parcours —
le rétrécissement part au plafond, et la facette cesse de distinguer les joueurs
un à un. C’est un résultat, pas un réglage.

### Le dernier événement d’une trajectoire n’est pas un événement comme les autres

Le piège est général et il ne se voit dans aucun contrôle de cohérence : les
données sont exactes, c’est la question qui est mal posée.

Dès qu’on mesure un **taux le long d’une trajectoire qui se termine**, le
dernier événement est structurellement différent — et il est présent exactement
une fois pour chacun. « S’en sort-il quand il est visé au conseil ? » compte
alors l’élimination elle-même, un échec que personne ne peut éviter. « Écrit-il
le nom de celui qui part ? » compte le bulletin qu’il a émis le soir de son
propre départ, faux par construction puisqu’on ne vote pas pour soi.

Sur un joueur bien documenté, cet événement se dilue. Sur un joueur qu’on
n’observe qu’une fois, il est **toute** la mesure. Le biais n’est donc pas du
bruit : il est systématiquement dirigé contre les moins documentés.

Le [top des joueurs]({{ '/statistiques/top/' | relative_url }}) en porte les
trois conséquences, toutes publiées : une facette **retirée** parce que son
seul signal était cet échec obligatoire, deux facettes **corrigées** en
écartant le soir du départ, et un résultat publié qui **s’est renversé** —
l’accord entre facettes qu’on croyait mesurer n’était que cet artefact, compté
trois fois.

Le contrôle qui l’attrape est simple, et il vaut pour toute couche datée :
**retirer le dernier événement de chaque trajectoire, et regarder ce qu’il
reste de la mesure**. S’il ne reste rien — un taux de 100 % pour tout le
monde — la mesure ne mesurait que lui.

### Tirer les pondérations plutôt que d’en défendre une

Dès qu’un chiffre agrège plusieurs mesures, quelqu’un a décidé de leur poids
relatif, et cette décision ne se démontre pas. Plutôt que de la défendre, on
l’échantillonne : dix mille pondérations tirées uniformément sur le simplexe —
une loi de Dirichlet de paramètres tous égaux à 1, c’est-à-dire *aucune opinion*
sur l’importance relative des composantes — et le classement refait à chaque
fois.

Ce qu’on publie alors n’est plus un rang mais une **distribution de rangs** :
la part des pondérations qui gardent un joueur dans le top, et l’intervalle
central de ses rangs. Ce qui survit à toutes les pondérations est un fait ; le
reste est un choix d’auteur, et il est affiché comme tel. La même précaution
vaudrait pour n’importe quel indice composite, et elle manque à la plupart.

### La validation « une saison exclue à chaque tour »

Pour le pronostic. Le modèle apprend sur toutes les saisons sauf une et
pronostique celle qu’il n’a jamais vue. Un découpage au hasard serait tricher :
deux aventuriers d’un même casting ne sont pas indépendants.

## Reproductibilité

Ces modèles reposent sur des dizaines de milliers de tirages. Sans précaution,
`_data/stats.yml` changerait à chaque construction et le site publierait des
chiffres différents **sans qu’aucune donnée ait bougé**.

- Une graine unique, **{{ m.graine }}**, dont dérive chaque générateur — un par
  usage, pour qu’ajouter une analyse ne déplace pas les chiffres d’une autre.
- Un seul fil de calcul dans l’atelier : le nombre de fils change l’ordre des
  additions, donc les derniers chiffres d’une moyenne.
- Un contrôle automatique qui **refuse** tout tirage non graîné et tout
  estimateur construit sans graine, en lisant l’arbre syntaxique des scripts.
- La construction est jouée deux fois, sous deux empreintes de hachage
  différentes, et le fichier produit doit être identique au bit près.

Le défaut a déjà été payé une fois sur ce site, sur le classement des familles de
métiers : trois familles à effectif égal changeaient d’ordre d’une publication à
l’autre.

## Où s’arrête ce site

Une question mérite d’être posée franchement : reste-t-il quelque chose à
chercher ? La réponse tient à la **puissance** — la taille du plus petit effet
qu’un jeu de données de cette taille peut encore distinguer du hasard.

<div class="tableau-large">
<table>
<thead><tr><th>Niveau d’analyse</th><th class="nombre">Observations</th><th class="nombre">Plus petit effet décelable</th></tr></thead>
<tbody>
<tr><td>Une grandeur de saison</td><td class="nombre">26</td><td class="nombre">0,55 écart-type</td></tr>
<tr><td>Une grandeur de saison, audience comprise</td><td class="nombre">33</td><td class="nombre">0,49 écart-type</td></tr>
<tr><td>Une grandeur de participation</td><td class="nombre">509</td><td class="nombre">0,12 écart-type</td></tr>
<tr><td>Une part au niveau du bulletin</td><td class="nombre">1 840</td><td class="nombre">3,2 points</td></tr>
<tr><td>Une part sur les conseils mixtes</td><td class="nombre">1 103</td><td class="nombre">4,2 points</td></tr>
<tr><td>Une part sur le vote du jury</td><td class="nombre">177</td><td class="nombre">10,5 points</td></tr>
</tbody>
</table>
</div>

<p class="note">Lecture : à 80 % de puissance et au seuil habituel de 5 %. Un
effet plus petit que la valeur indiquée existe peut-être — ces données ne
sauraient pas le voir.</p>

Trois conséquences, et elles ne vont pas dans le même sens.

**Le niveau de la saison est épuisé.** Vingt-six saisons classiques ne
permettent de détecter qu’un effet d’un demi-écart-type. Tout ce qui pouvait s’y
voir — la rupture de régime, la fusion calée sur la grille, l’absence d’effet
des mécaniques — a été cherché. Ce qui resterait serait si gros qu’il sauterait
déjà aux yeux. C’est aussi le niveau le plus fragile : vingt-trois valeurs
d’âge ajoutées au jeu de données ont suffi à déplacer de sept ans la date de
rupture, sans rien changer à son existence.
[La grille]({{ '/statistiques/grille/' | relative_url }}) le raconte.

**Le niveau du bulletin reste le bon endroit**, et c’est là que les résultats les
plus solides de ce site ont été trouvés : la persistance des alliances,
l’appartenance à la majorité, la protection du bandeau de départ, la trahison
qui n’en est pas une. Mais les questions qui restent à ce niveau — qui propose un
nom, qui suit, dans quel ordre les bulletins sont écrits — demandent une
information que **les sources ne contiennent pas**.

**Le nombre de tests, lui, n’est pas la limite.** On pourrait le croire :
{{ site.data.stats.modeles.registre | size }} tests déclarés, cela commence à
compter. Vérification faite, en ajoutant vingt tests sans résultat au registre,
**aucun des {{ site.data.stats.modeles.nb_retenus }} résultats retenus ne
tombe** — ils sont trop nets pour cela. Ce n’est donc pas une raison de
s’arrêter, et ce serait malhonnête de le prétendre.

**Le vrai risque n’est pas le nombre de tests, c’est le modèle nul.** Deux fois
sur ce site, un résultat spectaculaire s’est révélé fabriqué par la manière de
tirer au sort : le vote homophile, où le modèle nul laissait un aventurier
recevoir son propre nom ; le mélange d’archétypes, où le bandeau — assigné par
la production, et différent d’une saison à l’autre — rendait le résultat vrai
par construction. Les deux sont racontés là où ils sont tombés, et non effacés.
Aucune correction pour tests multiples n’aurait attrapé ni l’un ni l’autre.

**Le dernier champ inexploité l’a été.** L’origine géographique était la seule
piste de taille qui restait ; elle a donné
[D’où ils viennent]({{ '/statistiques/geographie/' | relative_url }}), et elle a
donné le contraire de ce qu’on attendait — le casting épouse l’état civil de sa
génération, il n’épouse pas sa géographie. Il ne reste, après elle, aucun champ
du jeu de données dont on n’ait rien tiré.

**Mais un jeu de données ne s’épuise pas comme une piste.** Cette page a d’abord
conclu que le travail s’arrêtait là. Deux fois de suite, elle s’est trompée.

D’abord une troisième source : les **pages individuelles du wiki Fandom**, qui
ont comblé {{ site.data.stats.completude.comblees }} valeurs vides, réuni des
personnes comptées deux fois, et rendu son nom de famille à sept aventuriers qui
n’en avaient pas.

Puis, pire : cette page affirmait qu’**aucune donnée d’audience n’existait en
source publique**. C’était faux, et il suffisait de regarder — l’article général
de Wikipédia porte un tableau complet, saison par saison, depuis 2001, avec ses
références de presse. La phrase avait été écrite sans vérification, et elle a
fermé pendant tout ce temps la piste la plus intéressante du jeu : la seule
grandeur que la production **ne décide pas**. Elle a donné
[L’audience]({{ '/statistiques/audience/' | relative_url }}), et deux des
résultats les plus nets du site.

La leçon n’est pas « il faut chercher davantage ». Elle est plus précise :
**une limite qu’on énonce sans la vérifier est une erreur qui se protège
elle-même.** Celle-là est restée en place parce qu’elle avait l’air prudente.

Ce qui manque réellement, après vérification cette fois : le **temps d’antenne**
par aventurier et l’**ordre des bulletins** à un conseil. Aucun des deux
n’apparaît dans une source publique consultable.

La **nature de chaque épreuve**, elle, a été retirée de cette liste — parce
qu’elle existe. Le wiki catalogue
{{ site.data.epreuves_nommees.nb_epreuves }} épreuves récurrentes avec leur
type. Elle reste inexploitable, mais pour une raison précise et mesurée : le
catalogue ne donne pas l’épisode, si bien que
{{ site.data.epreuves_nommees.raccord.part_raccordee }} % seulement des épreuves
relevées peuvent recevoir une nature — et ces 10 % sont exactement les épreuves
gagnées par les joueurs les moins dominants.
[Les épreuves]({{ '/statistiques/epreuves/' | relative_url }}) montre le
décompte. **C’est la troisième fois qu’une limite énoncée sans vérification se
révèle fausse au moins à moitié.**

<p class="note">Toutes ces limites se lisent aussi d’un coup d’œil, édition par
édition, sur <a href="{{ '/completude/' | relative_url }}">La complétude, édition par
édition</a>.</p>

## Ce que ces données ne peuvent pas établir

**Vingt-six saisons, c’est peu.** Les tests portant sur des grandeurs de saison
ont vingt-six observations. Seuls de gros effets y sont détectables ; un test non
concluant est publié comme non concluant, jamais retiré.

**Aucune donnée de montage.** Le temps d’antenne, la construction des
personnages, l’ordre dans lequel les bulletins sont dépouillés : rien de tout
cela n’existe dans ce jeu de données, et rien n’en sera dit. La nature des
épreuves existe, mais ne se raccorde pas ; les **chiffres de diffusion**
existent et se raccordent, mais s’arrêtent à l’audience « veille ». Les **chiffres de
diffusion**, eux, existent — cette page a longtemps prétendu le contraire — mais
ils s’arrêtent à l’audience « veille » et ignorent le rattrapage.

**Une corrélation n’est pas une intention.** C’est la limite qui traverse tout ce
travail. Une parité tenue au candidat près peut venir d’une consigne de casting
comme d’un vivier de candidatures déjà équilibré. Ces données mesurent le
**résultat** d’un processus de sélection ; elles n’observent pas le processus.
Partout où deux explications tiennent également debout, les deux sont nommées et
aucune n’est choisie.

**Un contrôle peut être trop sévère.** L’effet des alliances est mesuré à
nombre de conseils traversés constant — or traverser beaucoup de conseils, c’est
déjà avoir survécu. Le contrôle absorbe donc une part de ce qu’on cherche à
expliquer, et le coefficient publié est une borne basse. C’est dit sur la page,
et c’est le sens du chiffre : l’effet réel est au-dessus.

**Un repère reconstruit peut échouer.** La réunification est repérée par la
dernière immunité collective, et le plateau d’une épreuve par les survivants de
l’épisode. Ces deux reconstructions ont un taux d’échec, il est mesuré, et les
cas qui échouent sont écartés en le disant — jamais corrigés à la main.

**Les sources restent incomplètes.** Cinq saisons n’ont aucun bilan d’épreuves,
neuf seulement détaillent leurs colliers, et une part des conseils n’est pas
dépouillée intégralement. [Les sources]({{ '/sources/' | relative_url }})
recensent ces trous champ par champ.
