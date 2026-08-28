---
layout: page
title: La méthode
permalink: /methode/
chapeau: >-
  Quels modèles, sur quelles données, avec quelles limites — et la liste
  complète des tests, publiée pour qu’on ne puisse pas n’en garder que les bons.
---

{% assign m = site.data.stats.modeles %}

Neuf pages de ce site reposent sur des modèles plutôt que sur des comptages :
[La recette du casting]({{ '/statistiques/casting/' | relative_url }}),
[Le pronostic]({{ '/statistiques/pronostic/' | relative_url }}),
[La force réelle]({{ '/statistiques/force/' | relative_url }}),
[Le jeu tenu serré]({{ '/statistiques/equilibre/' | relative_url }}),
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}) et
[La grille]({{ '/statistiques/grille/' | relative_url }}),
[Qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}) et
[Le vote du jury]({{ '/statistiques/jury/' | relative_url }}) et
[D’où ils viennent]({{ '/statistiques/geographie/' | relative_url }}). Cette page dit
comment ils sont construits et ce qu’ils ne peuvent pas établir.

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
<tr><td>Une grandeur de participation</td><td class="nombre">509</td><td class="nombre">0,12 écart-type</td></tr>
<tr><td>Une part au niveau du bulletin</td><td class="nombre">1 753</td><td class="nombre">3,3 points</td></tr>
<tr><td>Une part sur les conseils mixtes</td><td class="nombre">1 033</td><td class="nombre">4,4 points</td></tr>
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
conclu que le travail s’arrêtait là. Une troisième source est arrivée depuis —
les pages individuelles du wiki Fandom — et elle a comblé
{{ site.data.stats.completude.comblees }} valeurs vides, réuni des personnes
comptées deux fois, et rendu son nom de famille à sept aventuriers qui n’en
avaient pas. Elle n’a pas ouvert de question neuve ; elle a rendu deux réponses
plus fermes et une plus fragile. C’est le rappel utile : **avant de manquer de
méthode, on manque de données**, et il en reste toujours à aller chercher.

Ce qui manque vraiment, c’est ce qu’aucune source publique ne porte : aucune
audience, aucun temps d’antenne, aucune nature d’épreuve, aucun ordre de vote.
Ce sont précisément les choses qui permettraient de dire quelque chose du
**montage**.

## Ce que ces données ne peuvent pas établir

**Vingt-six saisons, c’est peu.** Les tests portant sur des grandeurs de saison
ont vingt-six observations. Seuls de gros effets y sont détectables ; un test non
concluant est publié comme non concluant, jamais retiré.

**Aucune donnée de montage ni d’audience.** Le temps d’antenne, la construction
des personnages, les chiffres de diffusion : rien de tout cela n’existe dans ce
jeu de données, et rien n’en sera dit.

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
