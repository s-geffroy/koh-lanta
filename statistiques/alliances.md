---
layout: page
title: Les alliances
permalink: /statistiques/alliances/
chapeau: >-
  Le programme raconte des alliances à chaque épisode. Rien n’oblige à ce
  qu’elles existent au-delà du récit. Les bulletins permettent de trancher.
---

{% assign m = site.data.stats.modeles %}
{% assign a = m.alliances %}
{% assign t = a.test %}

Un conseil où six personnes écrivent le même nom peut être une alliance — ou un
simple ralliement du moment, refait à neuf chaque semaine. La différence n’est
pas dans le montage, elle est dans la **suite** : une alliance, c’est ce qui
survit d’un conseil au suivant.

<p class="note"><strong>La mesure.</strong> On prend chaque paire d’aventuriers
présente à deux conseils consécutifs, et on compare deux probabilités : voter
ensemble <em>après</em> avoir voté ensemble, et voter ensemble après avoir voté
séparément. L’écart entre les deux est la persistance. À zéro, chaque conseil
repart de rien. Base : {{ a.bulletins }} bulletins, {{ a.conseils }} conseils au
dépouillement complet, {{ a.saisons }} saisons, {{ a.paires_suivies }} paires
suivies d’un conseil à l’autre.</p>

## Les alliances existent, et elles sont solides

{% include graphiques/alliances-persistance.svg %}

<p class="legende-figure">Écart entre les deux probabilités, en points. La
silhouette est ce que donnent {{ t.tirages }} redistributions des bulletins à
l’intérieur de chaque conseil — chaque conseil gardant exactement sa
répartition de voix.</p>

<div class="constat">
  <p>Deux aventuriers qui ont voté ensemble votent encore ensemble au conseil
  suivant dans <b>{{ a.apres_ensemble }} %</b> des cas. Deux aventuriers qui ont
  voté séparément : <b>{{ a.apres_separes }} %</b>.</p>
  <p>{{ t.observe }} points d’écart, contre {{ t.attendu }} attendus si les
  bulletins n’étaient que du bruit — soit <b>{{ t.ecart_types }} écarts-types</b>.
  C’est de très loin le signal le plus fort de tout ce site.</p>
</div>

Le modèle nul mérite une phrase, parce que c’est lui qui donne son sens au
résultat. On ne compare pas à « personne ne vote pareil » : on rebat les
bulletins **à l’intérieur de chaque conseil**, en gardant intacte la répartition
des voix — quatre contre l’un, deux contre l’autre. Ce qui disparaît est le seul
lien entre conseils. Tout ce qui reste après ce brassage est donc de la
coordination qui traverse le temps.

## Ce que ça vaut, en jours de jeu

L’appartenance au camp majoritaire est une variable que le programme montre en
permanence sans jamais la mesurer. On peut la chiffrer : pour chaque aventurier,
la part de ses conseils passés du côté du nom qui sort.

{% include graphiques/alliances-majorite.svg %}

<p class="legende-figure">Points de saison gagnés ou perdus, le nombre de
conseils traversés tenu constant.</p>

{% assign v0 = a.majorite.variables[0] %}{% assign v1 = a.majorite.variables[1] %}

<div class="constat">
  <p>Passer de « jamais du bon côté » à « toujours du bon côté » vaut
  <b>{{ v0.estimation }} points de saison</b> — intervalle
  {{ v0.bas }} à {{ v0.haut }}.</p>
  <p>Dans le même modèle, recevoir une voix de plus par conseil coûte
  {{ v1.estimation }} points ({{ v1.bas }} à {{ v1.haut }}).
  <b>Être du bon côté pèse cinq fois plus que ne pas être visé.</b></p>
</div>

C’est un déplacement du meilleur prédicteur connu de ce site. La page
[Le jeu social]({{ '/statistiques/jeu-social/' | relative_url }}) désignait
l’invisibilité — n’être jamais écrit sur un bulletin. Mis en concurrence, les
deux survivent, mais l’invisibilité passe seconde. On ne dure pas à Koh-Lanta
en se faisant oublier : on dure en étant du côté qui compte les voix.

<p class="note"><strong>Une réserve importante, et elle joue contre le
résultat.</strong> Le modèle tient constant le nombre de conseils traversés.
C’est un contrôle trop sévère : traverser beaucoup de conseils, c’est déjà avoir
survécu, si bien qu’une part de ce qu’on cherche à expliquer est absorbée par le
contrôle. Les {{ v0.estimation }} points sont donc une <strong>borne
basse</strong>. Sans ce contrôle on publierait une tautologie déguisée ; avec
lui, on sous-estime. La vérité est au-dessus du chiffre affiché.</p>

## Ceux qui ne se sont jamais trompés de camp

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Aventurier</th><th>Saison</th><th class="nombre">Conseils</th>
  <th class="nombre">Du bon côté</th><th class="nombre">Voix reçues</th>
  <th class="nombre">Saison tenue</th>
</tr></thead>
<tbody>
{% for x in a.les_plus_souvent_du_bon_cote %}
<tr>
  <td><strong>{{ x.nom }}</strong></td>
  <td>{{ x.saison }}</td>
  <td class="nombre">{{ x.conseils }}</td>
  <td class="nombre" data-val="{{ x.part }}">{{ x.part }} %</td>
  <td class="nombre">{{ x.voix }}</td>
  <td class="nombre">{{ x.survie }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Ce que cette page ne dit pas. Elle ne distingue pas <em>former</em>
une majorité de <em>la rejoindre</em> : les bulletins ne portent pas d’heure, et
rien dans ces données ne dit qui a proposé le nom. Un suiveur discipliné et un
meneur ont ici exactement le même score. Elle ne porte par ailleurs que sur les
{{ a.conseils }} conseils au dépouillement garanti complet, sur les
{{ site.data.stats.conseils.conseils }} relevés : les saisons les mieux
documentées y pèsent plus que les autres.</p>
