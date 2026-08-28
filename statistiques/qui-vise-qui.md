---
layout: page
title: Qui vise qui
permalink: /statistiques/qui-vise-qui/
chapeau: >-
  Écrit-on le nom de celui qui ne nous ressemble pas ? La réponse est non —
  sauf sur un point, et ce point survit à la disparition des tribus.
---

{% assign m = site.data.stats.modeles %}
{% assign h = m.homophilie %}
{% assign reg = m.registre %}

Le sexe, l’âge, le métier, le bandeau de départ : quatre façons de se ressembler
ou non. La page [Les conseils]({{ '/statistiques/conseils/' | relative_url }})
donne les parts brutes — {% assign vg = site.data.stats.conseils.vote_par_genre | first %}{{ vg.part }} %
des bulletins d’hommes visent une femme. Ces
parts ne veulent rien dire seules : si le camp entier a un nom en tête ce
soir-là, chacun l’écrit, quel que soit son propre profil.

<p class="note"><strong>Le point de comparaison.</strong> On redistribue les
bulletins d’un conseil entre ses votants, en gardant <em>exactement</em> le même
jeu de cibles. La popularité d’une cible est donc parfaitement neutralisée :
quatre voix contre l’un et deux contre l’autre restent quatre et deux. Ne
subsiste que la question posée — qui, parmi ceux qui ont écrit ces noms, a écrit
celui-là. Base : {{ h.bulletins }} bulletins sur {{ h.conseils }} conseils au
dépouillement complet.</p>

## D’abord, une erreur que j’ai faite — et ce qu’elle a produit

La première version de ce modèle nul rebattait les bulletins sans contrainte.
Elle laissait donc un votant recevoir **son propre nom** : un couple qui
n’existe dans aucun conseil réel — on ne vote pas contre soi — et qui partage
forcément le sexe, le métier et le bandeau de son auteur.

**12,5 % des bulletins tirés étaient de ce type**, contre 0 sur
{{ h.bulletins }} dans les données. L’attendu en était gonflé, et tout écart
paraissait spectaculaire :

{% assign ts = reg | where: "cle", "vote_meme_sexe" | first %}
{% assign ta = reg | where: "cle", "vote_ecart_age" | first %}
{% assign tm = reg | where: "cle", "vote_meme_metier" | first %}
{% assign tb = reg | where: "cle", "vote_meme_bandeau" | first %}

<div class="tableau-large">
<table>
<thead><tr><th>Effet mesuré</th><th class="nombre">Modèle nul fautif</th><th class="nombre">Modèle nul corrigé</th></tr></thead>
<tbody>
<tr><td>Viser quelqu’un du même sexe</td><td class="nombre">−8,8 écarts-types</td><td class="nombre">{{ ts.ecart_types }} écarts-types</td></tr>
<tr><td>L’écart d’âge avec sa cible</td><td class="nombre">+12,5</td><td class="nombre">{{ ta.ecart_types }}</td></tr>
<tr><td>Viser la même famille de métier</td><td class="nombre">−16,6</td><td class="nombre">{{ tm.ecart_types }}</td></tr>
<tr><td>Viser son propre bandeau</td><td class="nombre">−15,6</td><td class="nombre">{{ tb.ecart_types }}</td></tr>
</tbody>
</table>
</div>

Trois résultats sur quatre étaient entièrement fabriqués par le défaut du modèle
nul. Le quatrième a survécu, réduit. C’est dit ici parce que c’est la leçon
principale de cette page : **un test de permutation ne vaut que ce que vaut son
modèle nul**, et un nul mal contraint produit des écarts énormes et faux.

## Le sexe : rien

{% assign t = reg | where: "cle", "vote_meme_sexe" | first %}

{% include graphiques/vise-sexe.svg %}

<p class="legende-figure">Part des bulletins visant quelqu’un du même sexe.</p>

{{ t.observe }} % contre {{ t.attendu }} % attendus — p = {{ t.p }}. **Le sexe ne
gouverne pas le bulletin.** L’écart de huit points que montre la page des
conseils vient de la composition des conseils, pas d’un choix.

## Le métier : rien non plus

{% assign t = reg | where: "cle", "vote_meme_metier" | first %}

{% include graphiques/vise-metier.svg %}

<p class="legende-figure">Part des bulletins visant la même famille de métier.</p>

{{ t.observe }} % contre {{ t.attendu }} % — p = {{ t.p }}. Le pompier n’épargne
pas le militaire, le coach ne vise pas le cadre. Ce qui reste vrai, c’est qu’on
vise **rarement** son propre métier : mais on le vise rarement parce que peu de
gens partagent votre famille de métier dans un camp de vingt.

## L’âge : à peine

{% assign t = reg | where: "cle", "vote_ecart_age" | first %}

{% include graphiques/vise-age.svg %}

<p class="legende-figure">Écart d’âge moyen entre le votant et sa cible.</p>

{{ t.observe }} ans contre {{ t.attendu }} attendus. L’écart existe —
{{ t.ecart_types }} écarts-types — mais il ne franchit pas la correction pour
tests multiples (p ajustée {{ t.p_ajustee }}), et **il vaut deux mois**. Il n’y a
rien à en tirer.

## Le bandeau de départ : le seul qui compte, et il compte beaucoup

{% assign t = reg | where: "cle", "vote_bandeau_apres_fusion" | first %}

Avant la réunification, un conseil ne réunit qu’une tribu : tous les bulletins y
sont forcément « même bandeau », et la question ne s’y pose pas. On mesure donc
sur les **{{ h.conseils_mixtes }} conseils réunissant plusieurs bandeaux**,
soit {{ h.bulletins_mixtes }} bulletins.

{% include graphiques/vise-bandeau.svg %}

<p class="legende-figure">Part des bulletins visant quelqu’un de son propre
bandeau de départ, sur les seuls conseils mixtes.</p>

<div class="constat">
  <p>Une fois les tribus mélangées, <b>{{ t.observe }} %</b> des bulletins visent
  quelqu’un du camp d’origine de leur auteur. Le simple partage des cibles en
  prévoit <b>{{ t.attendu }} %</b>.</p>
  <p>{{ t.ecart_types }} écarts-types, p ajustée {{ t.p_ajustee }}. On écrit le
  nom d’un ancien coéquipier <b>un quart de fois moins souvent</b> qu’on ne le
  devrait.</p>
  <p>Le bandeau de départ n’existe plus. Il protège encore.</p>
</div>

C’est la même chose que la persistance des alliances, vue d’un autre angle et
mesurée sur d’autres bulletins : ce qui se joue au conseil n’a pas grand-chose à
voir avec ce que les gens sont, et tout à voir avec **qui ils ont côtoyé**.
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}).

<p class="note">Ce que cette page ne dit pas. Elle ne mesure aucune intention :
un bulletin ne dit pas pourquoi il a été écrit. Épargner son ancienne tribu peut
tenir à la loyauté comme au simple fait qu’on connaît mieux ses forces, ou qu’on
a besoin d’elle au vote suivant. Elle ne porte par ailleurs que sur les conseils
au dépouillement garanti complet — les saisons les mieux documentées y pèsent
plus lourd.</p>
