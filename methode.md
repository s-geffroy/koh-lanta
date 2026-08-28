---
layout: page
title: La méthode
permalink: /methode/
chapeau: >-
  Quels modèles, sur quelles données, avec quelles limites — et la liste
  complète des tests, publiée pour qu’on ne puisse pas n’en garder que les bons.
---

{% assign m = site.data.stats.modeles %}

Huit pages de ce site reposent sur des modèles plutôt que sur des comptages :
[La recette du casting]({{ '/statistiques/casting/' | relative_url }}),
[Le pronostic]({{ '/statistiques/pronostic/' | relative_url }}),
[La force réelle]({{ '/statistiques/force/' | relative_url }}),
[Le jeu tenu serré]({{ '/statistiques/equilibre/' | relative_url }}),
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}) et
[La grille]({{ '/statistiques/grille/' | relative_url }}),
[Qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}) et
[Le vote du jury]({{ '/statistiques/jury/' | relative_url }}). Cette page dit
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
une règle de composition avec un simple effet d’époque. Cette variante a suffi à
faire tomber un résultat apparemment solide — le mélange d’archétypes.

### L’analyse des correspondances multiples

Quatre variables qualitatives ne se projettent pas dans un plan par une moyenne.
L’ACM passe par le tableau disjonctif et le décompose, ce qui donne des **axes
latents** : les directions selon lesquelles les profils se séparent réellement,
qu’aucune colonne ne porte. Une classification automatique tourne ensuite sur
ces axes.

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
