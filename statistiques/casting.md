---
layout: page
title: La recette du casting
permalink: /statistiques/casting/
chapeau: >-
  Un casting de vingt personnes n’est pas un tirage au sort. Reste à savoir
  ce que la production impose vraiment — et ce qu’elle laisse au hasard.
---

{% assign m = site.data.stats.modeles %}
{% assign c = m.casting %}
{% assign reg = m.registre %}

On lit souvent que la production « équilibre » ses castings. C’est une phrase
facile à écrire et difficile à vérifier : par rapport à quoi serait-il
équilibré ? Cette page répond en construisant le point de comparaison qui
manque — **le même vivier, rebattu au hasard**.

<p class="note"><strong>La méthode, en une phrase.</strong> On prend les
{{ c.effectif }} aventuriers des {{ c.saisons }} saisons classiques, on les
redistribue au hasard entre les saisons en gardant la taille de chaque casting,
et on recommence {{ m.permutations }} fois. Ce que la production a réellement
fait se compare alors à ces {{ m.permutations }} castings imaginaires. Ce n’est
pas une comparaison à la France : c’est une comparaison au hasard, à vivier
identique.</p>

## Ce que la production impose : la parité, au candidat près

{% assign t = reg | where: "cle", "parite" | first %}

{% include graphiques/casting-parite.svg %}

<p class="legende-figure">Écart moyen à la parité, en nombre de personnes. La
silhouette est la distribution des {{ t.tirages }} tirages à pile ou face ; le
trait vertical est ce qu’on observe réellement.</p>

<div class="constat">
  <p>Un casting de Koh-Lanta s’écarte de la parité de
  <b>{{ t.observe }} personne</b> en moyenne. Un tirage à pile ou face
  s’en écarterait de <b>{{ t.attendu }}</b>.</p>
  <p>C’est <b>{{ t.ecart_types }} écarts-types</b> en dessous du hasard
  — p ajustée {{ t.p_ajustee }}. Autrement dit : la plupart des saisons partent
  <b>exactement</b> à égalité, et les autres à une personne près. Le hasard, lui,
  produit régulièrement des castings à douze contre huit.</p>
  <p>Ce n’est pas « viser l’équilibre ». C’est un quota, tenu depuis
  vingt-cinq ans.</p>
</div>

C’est le résultat le plus net de tout ce site, et il ne se voit nulle part à
l’écran. La page [Âge et longévité]({{ '/statistiques/longevite/' | relative_url }})
notait déjà 50,1 % de femmes au total ; ce qu’on mesure ici est différent et
bien plus fort : ce n’est pas le **total** qui est équilibré, c’est **chaque
saison prise séparément**.

## Ce qu’elle impose beaucoup moins : l’écart d’âge

{% assign t = reg | where: "cle", "etendue_ages" | first %}

{% include graphiques/casting-etendue-ages.svg %}

<p class="legende-figure">Écart-type des âges à l’intérieur d’un même casting,
en années.</p>

L’écart observé est de **{{ t.observe }} ans** contre **{{ t.attendu }}**
attendus : le test le détecte ({{ t.ecart_types }} écarts-types, p ajustée
{{ t.p_ajustee }}), et il tient quand on ne rebat les castings qu’à l’intérieur
de leur propre décennie. Mais **l’écart vaut un quart d’année**. Il est réel et
il est négligeable : la production mélange les âges à peine plus qu’un tirage au
sort ne le ferait.

C’est exactement le genre de résultat qu’un test seul ferait mal lire. « Un
effet significatif » aurait suffi à titrer ; la taille de l’effet dit qu’il n’y
a rien à en tirer.

## Ce qu’elle n’impose pas du tout : la variété des métiers

{% assign t = reg | where: "cle", "familles_metiers" | first %}

{% include graphiques/casting-metiers.svg %}

<p class="legende-figure">Nombre total de cases « saison × famille de métier »
occupées, sur les {{ c.saisons }} saisons classiques.</p>

On imagine volontiers une liste de courses — il faut un pompier, il faut un
coach sportif, il faut un agriculteur. Les chiffres ne la montrent pas :
**{{ t.observe }} cases remplies contre {{ t.attendu }} attendues**, p =
{{ t.p }}. La couverture des métiers est celle qu’un tirage au hasard produit
tout seul.

## Les deux tribus : un contraste d’âge, mais pas une règle

{% assign t = reg | where: "cle", "tribus_ages" | first %}
{% assign tm = reg | where: "cle", "tribus_ages_mediane" | first %}
{% assign tf = reg | where: "cle", "tribus_femmes" | first %}

Sur les {{ c.duos_de_tribus }} saisons classiques parties sur exactement deux
tribus, on peut rebattre les bandeaux **à l’intérieur de chaque saison** et voir
si les tribus réelles se ressemblent plus, ou moins, que des tribus tirées au
sort.

{% include graphiques/casting-tribus-ages.svg %}

<p class="legende-figure">Écart d’âge moyen entre les deux tribus de départ.</p>

À la moyenne, l’écart est de **{{ t.observe }} ans** contre {{ t.attendu }}
attendus ({{ t.ecart_types }} écarts-types, p ajustée {{ t.p_ajustee }}) : les
tribus diffèrent **plus** qu’un tirage au sort, et non moins. Mais la médiane
raconte autre chose.

{% include graphiques/casting-tribus-ages-mediane.svg %}

<p class="legende-figure">Le même écart, mesuré à la médiane — insensible aux
valeurs extrêmes.</p>

<div class="constat">
  <p>À la médiane, l’écart tombe à {{ tm.observe }} ans contre
  {{ tm.attendu }} attendus, p = {{ tm.p }} : <b>plus rien</b>.</p>
  <p>La moyenne était portée par trois saisons — {% for x in c.tribus_les_plus_contrastees %}<b>{{ x.titre }}</b> ({{ x.annee }}, {{ x.ecart }} ans d’écart){% unless forloop.last %}, {% endunless %}{% endfor %} —
  où les deux camps opposent franchement deux générations. Ailleurs, les tribus
  sont composées comme le hasard les composerait.</p>
  <p>Il n’y a donc pas de règle de composition par l’âge. Il y a
  <b>trois éditions</b> qui ont fait ce choix, et dix-sept qui ne l’ont pas
  fait.</p>
</div>

Sur la part de femmes, les deux tribus sont plus semblables que le hasard ne les
ferait — {{ tf.observe }} points d’écart contre {{ tf.attendu }} attendus — mais
p ajustée {{ tf.p_ajustee }} : c’est une piste, pas un résultat. Il faudrait
plus de vingt saisons pour trancher.

## Y a-t-il des archétypes ?

{% include graphiques/casting-plan.svg %}

<p class="legende-figure">Les {{ c.effectif }} aventuriers projetés sur les deux
dimensions qui séparent le plus les profils (âge, sexe, métier, bandeau). Les
points nommés sont les modalités.</p>

La classification automatique ne trouve que **{{ c.nb_archetypes }} groupes**, et
elle les sépare mal : l’indice de silhouette plafonne à {{ c.silhouette }}, très
loin de ce qui signalerait des familles nettes.

<div class="tableau-large">
<table>
<thead><tr><th>Profil</th><th class="nombre">Effectif</th><th class="nombre">Part</th><th class="nombre">Âge médian</th><th class="nombre">Femmes</th></tr></thead>
<tbody>
{% for a in c.archetypes %}
<tr>
  <td>{{ a.libelle }}</td>
  <td class="nombre">{{ a.effectif }}</td>
  <td class="nombre">{{ a.part }} %</td>
  <td class="nombre">{{ a.age_median }}</td>
  <td class="nombre">{{ a.part_femmes }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Un petit groupe d’étudiants de moins de 25 ans se détache ; tout le reste forme
un seul bloc. **Il n’y a pas de galerie de personnages** dans les données du
casting — pas au niveau de l’âge, du sexe, du métier et du bandeau, les seules
choses que ce jeu de données connaisse.

<p class="note">Ce que cette page ne peut pas dire. Elle ne voit que quatre
variables : la production, elle, recrute aussi sur un entretien, une histoire
personnelle, une aisance devant la caméra — rien de tout cela n’est ici. Un
casting parfaitement banal sur l’âge et le métier peut être très travaillé sur
des critères que ces données ignorent. Et un écart mesuré ne dit jamais son
origine : la parité peut venir d’une consigne comme d’un vivier de candidatures
déjà équilibré. Ces données ne tranchent pas — <a href="{{ '/methode/' | relative_url }}">la méthode</a>
détaille pourquoi.</p>
