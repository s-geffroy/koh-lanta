---
layout: page
title: Qui vise qui
description: "Qui vise qui à Koh-Lanta : écrit-on le nom de celui qui ne nous ressemble pas ? Un peu pour le sexe et le métier, nettement pour le camp de départ."
permalink: /statistiques/qui-vise-qui/
chapeau: >-
  Écrit-on le nom de celui qui ne nous ressemble pas ? Un peu, pour le sexe et
  le métier. Nettement, pour le camp de départ — et cela survit à la
  disparition des tribus.
---

{% assign m = site.data.stats.modeles %}
{% assign h = m.homophilie %}
{% assign reg = m.registre %}

Le sexe, l’âge, le métier, le bandeau de départ : quatre façons de se ressembler
ou non. La page [Les conseils]({{ '/statistiques/conseils/' | relative_url }})
donne les parts brutes — {% assign vg = site.data.stats.conseils.vote_par_genre | first %}{{ vg.part }} %
des bulletins sont écrits par {{ vg.libelle }}. Ces
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

Le défaut gonflait les quatre écarts. Corrigé, celui de l’âge disparaît ; ceux
du sexe et du métier survivent, très réduits ; seul le bandeau garde un écart
massif. C’est dit ici parce que c’est la leçon
principale de cette page : **un test de permutation ne vaut que ce que vaut son
modèle nul**, et un nul mal contraint produit des écarts énormes et faux.

## Le sexe : un peu

{% assign t = reg | where: "cle", "vote_meme_sexe" | first %}

{% include graphiques/vise-sexe.svg %}

<p class="legende-figure">Part des bulletins visant quelqu’un du même sexe.</p>

{{ t.observe }} % contre {{ t.attendu }} % attendus — {{ t.ecart_types }}
écarts-types, p ajustée {{ t.p_ajustee }}. **Retenu, et petit** : on vise un peu
moins souvent quelqu’un de son sexe que le partage des cibles ne le voudrait.
Les parts brutes de la page des conseils, elles, tiennent surtout à la
composition des conseils : une fois celle-ci neutralisée, il reste peu de
chose.

## Le métier : un peu aussi

{% assign t = reg | where: "cle", "vote_meme_metier" | first %}

{% include graphiques/vise-metier.svg %}

<p class="legende-figure">Part des bulletins visant la même famille de métier.</p>

{{ t.observe }} % contre {{ t.attendu }} % — {{ t.ecart_types }} écarts-types,
p ajustée {{ t.p_ajustee }}. **Retenu, et petit** : on vise un peu moins sa
propre famille de métier que le hasard ne le voudrait. Si on la vise
**rarement**, c’est d’abord parce que peu de gens la partagent dans un camp de
vingt ; l’écart au hasard, lui, est mince.

## L’âge : à peine

{% assign t = reg | where: "cle", "vote_ecart_age" | first %}

{% include graphiques/vise-age.svg %}

<p class="legende-figure">Écart d’âge moyen entre le votant et sa cible.</p>

{{ t.observe }} ans contre {{ t.attendu }} attendus. L’écart existe —
{{ t.ecart_types }} écarts-types — mais il ne franchit pas la correction pour
tests multiples (p ajustée {{ t.p_ajustee }}), et **il est minuscule**. Il n’y a
rien à en tirer.

## Le voisin : peut-être

{% assign td = site.data.stats.modeles.registre | where: "cle", "vote_meme_departement" | first %}

Quatre traits étaient testés jusqu’ici. En voici un cinquième, qu’on n’avait
jamais posé : **épargne-t-on celui qui vit dans le même département ?** Les
aventuriers ne se connaissent pas avant le tournage, mais un voisin est un
voisin — on se découvre du pays commun, et l’on suppose que cela crée quelque
chose.

{% include graphiques/vise-departement.svg %}

<p class="legende-figure">Part des bulletins visant quelqu’un du même
département, contre {{ td.tirages }} redistributions des bulletins à
l’intérieur de chaque conseil.</p>

<div class="constat">
  <p><b>{{ td.observe }} %</b> des bulletins visent quelqu’un du même
  département, pour <b>{{ td.attendu }} %</b> attendus : l’observé est
  <b>sous</b> l’attendu, {{ td.ecart_types }} écarts-types, p brute {{ td.p }},
  p ajustée <b>{{ td.p_ajustee }}</b>. <b>Non concluant, de justesse.</b></p>
  <p>On vise le voisin un peu moins souvent que le partage des bulletins ne le
  voudrait, mais l’écart ne franchit pas la correction pour tests multiples.
  On ne peut ni l’affirmer ni l’écarter.</p>
</div>

<p class="note"><strong>Cette section a été écrite deux fois trop vite.</strong>
Elle concluait d’abord « non concluant », sur une p ajustée de 0,077. Les
<a href="{{ '/sources/' | relative_url }}">bulletins sans votant</a> — vote noir,
pénalité, malédiction — ont rendu cinquante-huit conseils dépouillés, et le test
descend à {{ td.p_ajustee }}. La section a alors écrit « retenu » : c’était
faux, le seuil n’est pas franchi. Les couples de même département restent
rares dans un camp de huit, et le test manque de bulletins pour trancher.</p>

## Le bandeau de départ : celui qui compte vraiment

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
