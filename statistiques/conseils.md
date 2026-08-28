---
layout: page
title: Les conseils
permalink: /statistiques/conseils/
chapeau: >-
  Le vote est presque toujours serré, l’unanimité rarissime, et le sexe du votant joue — à la marge.
---

{% assign c = site.data.stats.conseils %}

Le conseil est le cœur du jeu, et le seul endroit où l'on peut lire une
stratégie plutôt que la deviner. **{{ c.conseils }} conseils** ont été
dépouillés, pour **{{ c.bulletins }} bulletins**.

<ul class="chiffres">
  <li class="chiffre"><b>{{ c.conseils }}</b><span>conseils relevés</span></li>
  <li class="chiffre"><b>{{ c.bulletins }}</b><span>bulletins</span></li>
  <li class="chiffre"><b>{{ c.part_serres }} %</b><span>de conseils serrés</span></li>
  <li class="chiffre"><b>{{ c.voix_annulees_par_collier }}</b><span>voix annulées par un collier</span></li>
</ul>

## Le vote est presque toujours serré

Sur les {{ c.conseils_avec_decompte }} conseils dont le décompte est connu,
**{{ c.part_serres }} % se jouent à une voix près ou à peine plus** : le
nombre de bulletins contre la personne éliminée n'y dépasse pas la moitié des
votes exprimés.

À l'autre bout, l'unanimité est **rarissime** : {{ c.part_unanimes }} % des
conseils seulement. L'image du camp entier se retournant d'un bloc contre un
aventurier est une image de fiction — dans les faits, le vote se divise presque
toujours.

## Les colliers

**{{ c.voix_annulees_par_collier }} voix** ont été annulées par un collier
d'immunité, réparties sur **{{ c.conseils_avec_collier_joue }} conseils**. Cela
fait un peu plus de quatre voix annulées par collier joué : quand un collier
sort du sac, il ne renverse pas une voix, il en efface un paquet.

## Qui vote contre qui

{% include graphiques/conseils-genre.svg %}

<p class="legende-figure">Répartition des bulletins selon le sexe du votant et
celui de sa cible, sur les conseils dont le dépouillement est complet.</p>

Si le sexe ne jouait aucun rôle, les quatre combinaisons pèseraient 25 % chacune
— le casting étant paritaire. Ce n'est pas tout à fait le cas : les bulletins
d'**un homme contre une femme** sont les plus nombreux
({{ c.vote_par_genre[0].part }} %), et ceux d'**une femme contre une femme** les
moins nombreux ({{ c.vote_par_genre[3].part }} %). L'écart est réel mais
modeste, de l'ordre de huit points entre les deux extrêmes.

<p class="note">Cette dernière analyse ne porte que sur les
{{ c.conseils_complets }} conseils dont le dépouillement est complet, c'est-à-dire
ceux où le nombre de bulletins lus dans les sources correspond exactement au
nombre de voix annoncé. Les autres conseils restent comptés dans les agrégats
— qui part, avec combien de voix — mais pas dans les analyses bulletin par
bulletin.</p>
