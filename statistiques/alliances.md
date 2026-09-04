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

## La trahison protège moins qu’on ne croit — parce qu’elle est rare

{% assign tr = m.trahison %}{% assign tt = tr.test %}

Le programme met en scène le retournement à chaque saison. Il se compte : sur
les {{ tr.bulletins }} bulletins dont l’auteur avait déjà un allié à ce
moment-là, combien visent cet allié ?

{% include graphiques/trahison.svg %}

<p class="legende-figure">Part des bulletins visant quelqu’un avec qui l’auteur
avait déjà voté. La silhouette est le même brassage que plus haut, à jeu de
cibles constant.</p>

<div class="constat">
  <p><b>{{ tt.observe }} %</b> des bulletins visent un ancien allié — contre
  <b>{{ tt.attendu }} %</b> attendus. {{ tt.ecart_types }} écarts-types.</p>
  <p>L’alliance ne se contente donc pas de faire voter ensemble : elle
  <b>protège</b>. À jeu de cibles identique, on écrit le nom d’un ancien allié
  nettement moins souvent qu’on ne le devrait.</p>
</div>

{% assign ef = tr.effet %}
Et quand on trahit quand même ? **Rien.** Passer de « jamais » à « toujours »
viser un ancien allié fait gagner {{ ef.estimation }} points de saison —
intervalle {{ ef.bas }} à {{ ef.haut }}, p = {{ ef.p }}. La trahison ne paie
pas ; elle ne coûte pas non plus. Sur {{ ef.effectif }} participations, elle est
simplement **sans effet mesurable**.

## Après la fusion, un camp tombe en série

{% assign de = m.decimation %}{% assign dt = de.test %}

Si les blocs survivent à la réunification, cela doit se voir dans **l’ordre** des
sorties : le camp majoritaire démonte l’autre un par un, au lieu que les
départs alternent.

{% include graphiques/decimation.svg %}

<p class="legende-figure">Nombre de fois où deux sorties consécutives viennent
du même bandeau de départ, sur {{ de.saisons }} saisons et {{ de.sorties }}
sorties d’après-fusion. La silhouette est ce que donne un ordre de sortie tiré
au sort, à composition de camps identique.</p>

<div class="constat">
  <p>{{ dt.observe }} enchaînements observés contre {{ dt.attendu }} attendus,
  <b>{{ dt.ecart_types }} écarts-types</b>, p ajustée {{ dt.p_ajustee }}.</p>
  <p>Les sorties d’après-fusion ne se répartissent pas au hasard entre les deux
  anciens camps : <b>elles se suivent</b>. Le bandeau qu’on a porté les six
  premiers épisodes décide encore de l’ordre dans lequel on part.</p>
</div>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Saison</th><th class="nombre">Année</th>
  <th class="nombre">Sorties après fusion</th>
  <th class="nombre">Plus longue série</th><th>Ordre des sorties</th>
</tr></thead>
<tbody>
{% for d in de.detail %}
<tr>
  <td>{{ d.titre }}</td>
  <td class="nombre">{{ d.annee }}</td>
  <td class="nombre">{{ d.joueurs }}</td>
  <td class="nombre">{{ d.plus_longue_serie }}</td>
  <td><code>{{ d.suite }}</code></td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<p class="note">Chaque lettre est le bandeau de départ d’un sortant, dans
l’ordre : <code>J</code> pour jaune, <code>R</code> pour rouge. Sept sorties
jaunes d’affilée en 2021 ne prouvent rien à elles seules — c’est l’accumulation
sur {{ de.saisons }} saisons qui fait le résultat.</p>

<p class="note"><strong>Ce que l’alliance vaut, en probabilité de survie.</strong>
Cette page mesure l’existence et la durée des alliances. Leur <em>rendement</em>
se lit ailleurs : sachant qu’il ne reste plus un seul des gens avec qui on a
déjà voté, le risque de partir au conseil monte à
{% assign pp = site.data.stats.modeles.pire_place %}<b>{{ pp.isolement[0].probabilite }} %</b>
pour qui n’a jamais voté avec personne, contre
{{ pp.isolement[3].probabilite }} % pour qui garde trois alliés ou plus.
<a href="{{ '/statistiques/pire-place/' | relative_url }}">La pire place au conseil</a>.</p>

<p class="note">Ce que cette page ne dit pas. Elle ne distingue pas <em>former</em>
une majorité de <em>la rejoindre</em> : les bulletins ne portent pas d’heure, et
rien dans ces données ne dit qui a proposé le nom. Un suiveur discipliné et un
meneur ont ici exactement le même score. Elle ne porte par ailleurs que sur les
{{ a.conseils }} conseils au dépouillement garanti complet, sur les
{{ site.data.stats.conseils.conseils }} relevés : les saisons les mieux
documentées y pèsent plus que les autres.</p>
