---
layout: page
title: Avant et après la réunification
description: "Avant et après la réunification, Koh-Lanta est deux jeux. On élimine le faible avant et le fort après, dit-on. Les bulletins ne le montrent pas."
permalink: /statistiques/reunification/
redirect_from:
  - /statistiques/fusion/
chapeau: >-
  La réunification coupe la saison en deux jeux. On dit qu’avant on élimine le
  faible et qu’après on élimine le fort. Les bulletins ne montrent ni l’un ni
  l’autre.
---

{% assign m = site.data.stats.modeles %}
{% assign a = m.avant_apres %}
{% assign reg = m.registre %}
{% assign tf = reg | where: "cle", "fusion_force" | first %}
{% assign ts = reg | where: "cle", "fusion_serre" | first %}
{% assign tx = reg | where: "cle", "fusion_sexe" | first %}
{% assign ta = reg | where: "cle", "ambassadeurs_force" | first %}

Jusqu’à la réunification, on vote **par tribu** : le camp doit gagner les
épreuves collectives, et perdre un bon joueur coûte cher. Après, chacun joue
pour soi et un bon joueur devient une menace. Le raisonnement est si naturel
qu’il est répété partout : **avant on élimine le faible, après on élimine le
fort.**

C’est mesurable, et la mesure ne le confirme pas.

<p class="note"><strong>Où tombe la coupure.</strong> Elle ne se devine pas :
après la réunification, les immunités sont individuelles. Le dernier épisode
portant une immunité <em>collective</em> est donc le dernier d’avant la réunification.
Le repère fonctionne sur {{ a.saisons }} saisons classiques, et
<a href="{{ '/statistiques/grille/' | relative_url }}">La grille</a> montre
qu’il tombe presque toujours au même épisode — le {{ a.episode_median }}<sup>e</sup>.</p>

## Deux jeux, {{ site.data.stats.mots.avant_apres_tests }} mesures

{% include graphiques/fusion-avant-apres.svg %}

<p class="legende-figure">{{ a.avant.conseils }} conseils avant la
réunification, {{ a.apres.conseils }} après, sur {{ a.saisons }} saisons. Le
rang de force va de 0 — le plus faible du camp ce soir-là — à 100, le plus
fort.</p>

<div class="tableau-large">
<table>
<thead><tr><th>Mesure</th><th class="nombre">Avant</th><th class="nombre">Après</th></tr></thead>
<tbody>
<tr><td>Conseils</td><td class="nombre">{{ a.avant.conseils }}</td><td class="nombre">{{ a.apres.conseils }}</td></tr>
<tr><td>Présents en moyenne</td><td class="nombre">{{ a.avant.presents_moyen }}</td><td class="nombre">{{ a.apres.presents_moyen }}</td></tr>
<tr><td>Conseils serrés</td><td class="nombre">{{ a.avant.part_serres }} %</td><td class="nombre">{{ a.apres.part_serres }} %</td></tr>
<tr><td>Femmes parmi les éliminés</td><td class="nombre">{{ a.avant.part_femmes }} %</td><td class="nombre">{{ a.apres.part_femmes }} %</td></tr>
<tr><td>Âge moyen des éliminés</td><td class="nombre">{{ a.avant.age_moyen }} ans</td><td class="nombre">{{ a.apres.age_moyen }} ans</td></tr>
<tr><td>Rang de force de l’éliminé</td><td class="nombre">{{ a.rang_force_avant }}</td><td class="nombre">{{ a.rang_force_apres }}</td></tr>
</tbody>
</table>
</div>

## La force ne décide pas de qui part

{% include graphiques/fusion-force-nulle.svg %}

<p class="legende-figure">Écart entre le rang de force de l’éliminé après la
réunification et avant. La silhouette est celle de {{ tf.tirages }} tirages où
l’éliminé de chaque conseil est pris au hasard parmi les présents.</p>

<div class="constat">
  <p>Avant la réunification, l’éliminé se situe en moyenne au rang
  <b>{{ a.rang_force_avant }} sur 100</b> de son camp ; après, au rang
  <b>{{ a.rang_force_apres }}</b>. Dans les deux cas, <b>autour de la
  médiane</b> : ni le plus faible avant, ni le plus fort après.</p>
  <p>L’écart entre les deux vaut {{ tf.observe }} points de rang (écart réduit
  {{ tf.ecart_types }}, p ajustée {{ tf.p_ajustee }}) : un tirage au sort parmi
  les présents le produit couramment. <b>Le test n’est pas retenu.</b></p>
  <p>Ce n’est pas la preuve que la force ne compte jamais : avant la réunification,
  elle n’est estimable que sur {{ a.force_effectif_avant }} conseils, et un
  effet modéré passerait inaperçu. Mais l’idée reçue, telle qu’on la raconte,
  ne se voit pas dans les bulletins.</p>
</div>

<p class="note"><strong>Le modèle nul fait tout le travail ici.</strong> À
chaque conseil, on tire l’éliminé <em>au hasard parmi les présents de ce
soir-là</em>. Après la réunification, tout ce qui tient à la composition du
camp — son âge, son sexe, son niveau — est donc neutralisé. Avant, un défaut
subsiste : les « présents » sont tous ceux qui restent en jeu, les deux tribus
réunies, et non la seule tribu qui vote. Les comparaisons d’avant la
réunification se lisent avec cette réserve.</p>

### Une estimation trop floue ?

La force est estimée sur les épreuves individuelles disputées. Un aventurier
éliminé avant la réunification en a disputé peu, quand ceux qui
restent seront jugés sur toute une saison. **On comparerait donc une estimation
vague à des estimations informées** : le flou pourrait masquer un effet, ou en
fabriquer un.

Deux vérifications.

<div class="constat">
  <p><b>L’exposition n’explique pas la force.</b> La corrélation de rang entre
  le nombre d’épreuves disputées et la force estimée vaut
  <b>{{ a.robustesse.correlation_exposition_force }}</b> : à peine plus que
  zéro. Un joueur peu exposé n’est pas mécaniquement classé haut.</p>
  <p><b>À finesse d’estimation égale, rien ne change.</b> En ne comparant
  l’éliminé qu’aux présents ayant disputé un nombre d’épreuves comparable — à
  trois près — le rang vaut <b>{{ a.robustesse.apparie.avant }}</b> avant
  ({{ a.robustesse.apparie.avant_effectif }} conseils) contre
  <b>{{ a.robustesse.apparie.apres }}</b> après
  ({{ a.robustesse.apparie.apres_effectif }}) : les deux restent proches.</p>
</div>

Autrement dit : **le flou de l’estimation ne cache pas l’effet qu’on attendait.
Avant comme après la réunification, l’éliminé n’est choisi ni parmi les plus faibles
ni parmi les plus forts.**

## Le vote se divise après la réunification

{% include graphiques/fusion-serre-nulle.svg %}

<p class="legende-figure">Différence de part de conseils serrés, après moins
avant. Le hasard est ici une redistribution des étiquettes « avant » et
« après » entre les mêmes conseils.</p>

<div class="constat">
  <p>Un conseil est <b>serré</b> quand l’éliminé ne rassemble pas plus de la
  moitié des voix exprimées. Avant la réunification : {{ a.avant.part_serres }} %.
  Après : <b>{{ a.apres.part_serres }} %</b>.</p>
  <p>+{{ ts.observe }} points, {{ ts.ecart_types }} {{ ts.ecart_types_mot }}, p ajustée
  {{ ts.p_ajustee }}. Le camp réuni ne se retourne pas d’un bloc : il se
  partage.</p>
</div>

C’est cohérent avec ce que montre
[Les alliances]({{ '/statistiques/alliances/' | relative_url }}) : après la
réunification, plusieurs groupes coexistent et chacun écrit son nom. Avant, une tribu
qui vient de perdre une épreuve a souvent déjà tranché sur le chemin du retour.

## L’âge bascule dans le même sens, mais on ne peut pas l’affirmer

{% assign ag = site.data.stats.modeles.age_au_conseil %}
{% assign tag = reg | where: "cle", "age_bascule_fusion" | first %}

La force ne désigne pas l’éliminé. L’âge, peut-être ? La mesure est directe : de combien d’années l’éliminé s’écarte de
la moyenne d’âge de son camp, ce soir-là.

<div class="tableau-large">
<table>
<thead><tr><th></th><th class="nombre">Conseils</th><th class="nombre">Écart d’âge de l’éliminé</th></tr></thead>
<tbody>
<tr><td>Avant la réunification</td><td class="nombre">{{ ag.conseils_avant }}</td>
    <td class="nombre"><b>{{ ag.ecart_avant }} an</b></td></tr>
<tr><td>Après la réunification</td><td class="nombre">{{ ag.conseils_apres }}</td>
    <td class="nombre"><b>{{ ag.ecart_apres }} an</b></td></tr>
<tr><td>Sur l’ensemble</td><td class="nombre">{{ ag.conseils }}</td>
    <td class="nombre">{{ ag.ecart_tout }} an</td></tr>
</tbody>
</table>
</div>

{% include graphiques/age-bascule-nulle.svg %}

<p class="legende-figure">Écart d’âge de l’éliminé à la moyenne de son camp,
avant la réunification moins après, contre {{ tag.tirages }} tirages où
l’éliminé de chaque conseil est pris au hasard parmi les présents.</p>

<div class="constat">
  <p>Avant la réunification, celui qui part a en moyenne <b>{{ ag.ecart_avant }} an de
  plus</b> que son camp. Après, <b>{{ ag.ecart_apres }}</b> — il est un peu plus
  jeune que la moyenne.</p>
  <p>La bascule vaut {{ tag.observe_arrondi }} an{% if tag.observe_arrondi_pluriel %}s{% endif %}, {{ tag.ecart_types }}
  {{ tag.ecart_types_mot }}, p brute {{ tag.p }}, p ajustée {{ tag.p_ajustee }}.
  <b>Non concluant.</b></p>
  <p>C’est le sens de la bascule de la force. Sur {{ ag.conseils }} conseils,
  l’écart ne passe pas le seuil, de peu : un tirage au hasard parmi les
  présents le produit encore trop souvent pour qu’on l’affirme.</p>
</div>

<p class="note"><strong>Cette conclusion a changé deux fois.</strong>
Jusqu’au 20 octobre 2026, la page titrait déjà « mais on ne peut pas
l’affirmer » : 1,3 an sur 372 conseils, 1,44 écart-type, p ajustée 0,22. Ce
jour-là, le relevé des épreuves a été corrigé et complété — cinq saisons
ajoutées depuis le wiki <em>Survivor</em>, des épisodes remis à leur place —
et la date de la réunification a bougé avec lui : 222 conseils comptés avant,
150 après. La bascule a alors passé le seuil, de justesse (2 ans,
p ajustée 0,045), et la page l’a annoncée retenue en prévenant qu’une
saison mal relevée suffirait à la faire repasser dessous. Le
21 octobre, trente sorties par épreuve éliminatoire, comptées jusque-là
comme des conseils sans bulletin, ont été rendues à leur vraie nature. Le
résultat est repassé sous le seuil : {{ ag.conseils_avant }} conseils
avant, {{ ag.conseils_apres }} après, p ajustée {{ tag.p_ajustee }}. Il est
publié tel quel, avec les conclusions précédentes en regard.</p>

<p class="note">Le doyen du camp, lui, est traité comme une catégorie sur
<a href="{{ '/statistiques/autour-du-feu/' | relative_url }}">Sachant qui est
autour du feu</a>, et il y reste non concluant. Deux façons de poser la
question de l’âge au conseil, et aucune ne passe le seuil : ni l’écart moyen,
ni la catégorie du plus âgé.</p>

## Le sexe, lui, bascule

<div class="constat">
  <p>{{ a.avant.part_femmes }} % de femmes parmi les éliminés avant la réunification,
  {{ a.apres.part_femmes }} % après — {{ tx.observe_arrondi }} points d’écart, soit
  {{ tx.ecart_types }} {{ tx.ecart_types_mot }}, p ajustée {{ tx.p_ajustee }}.
  <b>Retenu.</b></p>
  <p>Le hasard tire ici l’éliminé parmi les présents de chaque conseil : la
  composition du camp est donc déjà prise en compte. <b>À la réunification, la
  part de femmes parmi les éliminés baisse bien plus que le changement des
  camps ne l’explique.</b> Le test compare l’avant et l’après ; il ne dit pas
  lequel des deux s’écarte de son propre hasard. La mesure dit qui part, pas pourquoi : épreuves
  par équipe, alliances, choix des tribus, elle ne départage pas.</p>
</div>

## Les ambassadeurs

{% assign amb = a.ambassadeurs %}

C’est la seule élimination sans conseil : deux aventuriers, un de chaque tribu,
se retrouvent seuls et doivent désigner un partant. S’ils ne s’accordent pas,
un tirage au sort tranche entre eux deux.

<ul class="chiffres">
  <li class="chiffre"><b>{{ amb.effectif }}</b><span>ambassades reconstituées</span></li>
  <li class="chiffre"><b>{{ amb.episode_median }}</b><span>épisode médian</span></li>
  <li class="chiffre"><b>{{ amb.age_moyen }}</b><span>âge moyen de l’éliminé</span></li>
  <li class="chiffre"><b>{{ amb.part_femmes }} %</b><span>de femmes parmi eux</span></li>
</ul>

L’ambassade tombe **juste avant la réunification** — épisode
{{ amb.episode_median }} en médiane, quand la réunification tombe au
{{ a.episode_median }}<sup>e</sup>. Ce n’est pas un hasard de calendrier : elle
sert précisément à équilibrer les tribus avant de les réunir.

{% include graphiques/ambassadeurs-nulle.svg %}

<p class="legende-figure">Rang de force de l’éliminé par les ambassadeurs, face
à un tirage au hasard parmi les présents.</p>

<div class="constat">
  <p>Sur les {{ amb.effectif_force }} ambassades où la force des présents est
  estimable, l’éliminé se situe au rang <b>{{ amb.rang_moyen }} sur 100</b> —
  {{ ta.ecart_types }} {{ ta.ecart_types_mot }} du hasard, p ajustée {{ ta.p_ajustee }}.</p>
  <p><b>Deux ambassadeurs qui décident seuls choisissent comme un tirage.</b>
  Du moins sur ce critère-là, et à cette taille-là :
  {{ amb.effectif_force }} cas ne permettent de détecter qu’un effet énorme.</p>
</div>

C’est un résultat en creux, et il vaut d’être dit : le seul moment du jeu où
l’élimination échappe au vote collectif est aussi celui où l’on ne détecte
aucune logique de force — ni le fort, ni le faible. Le sexe et l’âge de
l’éliminé sont décrits plus haut, ils ne sont pas testés.

### Qui part en ambassade ? On l’a cherché dans la prose

{% assign ng = a.negociateurs %}

Aucune table ne donne le nom des ambassadeurs. Il n’apparaît que dans une note
de bas de page accrochée à la ligne d’élimination : « <em>Les deux ambassadeurs
(Léa et Pauline) se mettent d’accord pour éliminer Ricky.</em> » C’est de la
prose, donc une lecture faillible — et c’est pourquoi elle est **mesurée**.

<div class="constat">
  <p><b>{{ ng.lues }} ambassades sur {{ ng.total }}</b> livrent le nom de leurs
  ambassadeurs, soit {{ ng.part_lues }} % — {{ ng.distincts }} personnes
  distinctes.</p>
  <p>Là où les <b>deux sources</b> les nomment, elles s’accordent
  {{ ng.sources_accord }} fois sur {{ ng.sources_communes }}.
  La seule divergence porte sur <i>Les Reliques du destin</i> : Wikipédia
  compte Jade parmi les ambassadeurs, Fandom compte Cynthia. Aucun des
  deux n’est retenu.</p>
</div>

Trois contrôles écartent une lecture douteuse : chaque nom doit désigner un
participant de la saison sans homonyme, chaque ambassadeur doit être **encore
en jeu** à cet épisode, et le nombre de noms lus doit correspondre à celui que
la note annonce. C’est ce dernier qui écarte <i>Les Armes secrètes</i> : la note
parle de « deux ambassadeurs » puis ajoute une « ambassadrice secrète », ce qui
en fait trois. La règle du dépôt est de s’abstenir plutôt que d’arbitrer.

<p class="note">Les {{ ng.muettes }} ambassades muettes ne le sont pas par hasard : ce sont
les plus anciennes éditions et les saisons spéciales, celles dont les articles
sont les plus courts. Comme partout sur ce site, ce qui manque manque du même
côté.</p>

### Quand ils ne s’accordent pas, l’un des deux part

<div class="constat">
  <p>Sur les {{ ng.lues }} ambassades lues, <b>{{ ng.par_tirage }} se sont
  terminées par un tirage au sort</b> faute d’accord. Dans les
  {{ ng.par_tirage }} cas, <b>c’est un des deux ambassadeurs qui est parti</b>.</p>
  <p>Ce n’est pas une découverte statistique, c’est la règle du jeu — mais elle
  chiffre le risque : sur {{ ng.lues }} ambassades lues,
  {{ ng.elimine_ambassadeur }} ont coûté sa place à l’un des ambassadeurs.</p>
</div>

### Et ils sortent plus tôt — sur le fil

{% include graphiques/ambassadeurs-survie.svg %}

<p class="legende-figure">Rang de l’ambassadeur parmi les présents du jour, sur
le jour de sortie. Le hasard, ici, c’est désigner les ambassadeurs au sort parmi
les présents.</p>

{% assign tn = reg | where: "cle", "ambassadeurs_survie" | first %}
<div class="constat">
  <p>Sur les {{ ng.ambassades }} ambassades où le camp est reconstituable —
  {{ ng.ambassadeurs }} ambassadeurs — le rang moyen vaut
  <b>{{ ng.rang_moyen }} sur 100</b>, contre {{ tn.attendu }} attendus.
  {{ tn.ecart_types }} {{ tn.ecart_types_mot }}, p ajustée {{ tn.p_ajustee }}.</p>
  <p><b>Retenu, de justesse : l’ambassadeur sort plus tôt que s’il avait été
  désigné au hasard parmi les présents.</b> Le résultat tient sur le seuil, et
  il l’a franchi quatre fois en deux jours : il se lit avec cette réserve.</p>
  <p>Une partie de l’écart peut être la règle elle-même : un ambassadeur
  parti au tirage sort le soir même, au plus bas rang possible. Et la mesure
  repose sur {{ ng.ambassadeurs }} ambassadeurs.</p>
</div>

<p class="note"><strong>Ce résultat a changé quatre fois en deux jours.</strong>
Retenu jusqu’au 21 octobre 2026 (p ajustée 0,047), il est d’abord repassé
sous le seuil (0,056) quand vingt-quatre colonnes de la matrice des votes,
qui passaient pour des conseils, ont été rendues à leur nature de sorties
sans vote. Il l’a repassé dans l’autre sens (0,04) quand huit revenants ont
retrouvé leur sortie définitive : Quentin, au <i>Feu sacré</i>, comptait comme
sorti au vingt-troisième jour, à l’ambassade qu’il a perdue au tirage ; il est
revenu, et n’est sorti qu’au trente-huitième. Le 22 octobre 2026, la correction
pour tests multiples a été étendue aux p-values de régression que le site
publiait sans correction (<a href="{{ '/methode/' | relative_url }}">la
méthode</a>) : le seuil s’est déplacé, et le résultat est repassé dessous
(0,059, puis 0,09 quand les ambassades ont toutes été traitées comme des
sorties et que trois ambassades de revenants ont été lues). Il est enfin
repassé au-dessus (p ajustée {{ tn.p_ajustee }}) quand l’ambassade de Jonathan,
aux <i>Reliques du destin</i>, a été tranchée : les deux wikis n’en nommaient
pas les mêmes ambassadeurs, et la presse a départagé. Un écart qui bascule à
chaque correction ne s’affirme qu’avec sa réserve.</p>

## Ce que cette page ne dit pas

<p class="note"><strong>La force est celle d’une carrière, pas d’un soir.</strong>
Le modèle de <a href="{{ '/statistiques/force/' | relative_url }}">force
réelle</a> estime un niveau constant sur toute la participation. Il ne sait pas
qu’un aventurier était blessé au douzième jour, ni qu’il a progressé. Le
classement d’un soir est donc approché — et l’approximation, mesurée
ci-dessus, ne suffit pas à expliquer l’écart.</p>

<p class="note"><strong>Les éditions spéciales sont écartées</strong> : leurs
revenants faussent la comparaison des forces.</p>

<p class="note"><strong>Le nom des ambassadeurs vient de la prose</strong>, pas
d’un tableau : {{ a.negociateurs.part_lues }} % des ambassades seulement, et
l’extraction s’abstient dès qu’un doute apparaît. Les {{ a.negociateurs.muettes }} manquantes sont les
plus anciennes éditions et les saisons spéciales — le trou n’est pas
aléatoire.</p>
