---
layout: page
title: L’audience
description: "L’audience de Koh-Lanta depuis 2001 : une forte chute, sans date démontrable. La seule grandeur du jeu que la production ne décide pas."
permalink: /statistiques/audience/
chapeau: >-
  La seule grandeur du jeu que la production ne décide pas. Elle a fortement
  chuté — mais rien ne prouve que cette chute ait une date plutôt qu’une pente.
---

{% assign m = site.data.stats.modeles %}
{% assign a = m.audience %}
{% assign reg = m.registre %}
{% assign tr = reg | where: "cle", "audience_rupture" | first %}
{% assign tg = reg | where: "cle", "audience_glissement" | first %}
{% assign tf = reg | where: "cle", "audience_retournement" | first %}
{% assign ts = reg | where: "cle", "audience_format" | first %}

Ce site a longtemps écrit qu’aucune donnée d’audience n’existait en source
publique. **C’était faux.** L’article général de Wikipédia porte un tableau
complet : lancement, finale, moyenne et part de marché pour chaque saison, avec
ses références de presse. {{ site.data.stats.mots.audience_courbes_maj }} articles de saison donnent en plus le
détail épisode par épisode.

C’est la seule grandeur de ce jeu de données que la production ne décide pas :
elle la subit. À ce titre, c’est la plus intéressante.

<ul class="chiffres">
  <li class="chiffre"><b>{{ a.saisons }}</b><span>saisons mesurées sur {{ site.data.stats.general.saisons_diffusees }}</span></li>
  <li class="chiffre"><b>{{ a.sommet.moyenne_millions }} M</b><span>au sommet, en {{ a.sommet.annee }}</span></li>
  <li class="chiffre"><b>{{ a.derniere.moyenne_millions }} M</b><span>en {{ a.derniere.annee }}</span></li>
  <li class="chiffre"><b>−{{ a.chute }} %</b><span>depuis le sommet</span></li>
</ul>

{% include graphiques/audience-serie.svg %}

<p class="legende-figure">Audience moyenne par saison, en millions de
téléspectateurs. Sous l’axe, deux rangs : le jour de diffusion — <b>V</b> vendredi, <b>M</b> mardi, <b>S</b> samedi — puis les mois de diffusion, en chiffres. La bascule au mardi tombe au milieu de la chute, et c’est tout le problème de cette page ; le glissement de l’été vers le printemps, lui, se lit sur le second rang. Source : Wikipédia, article général et
articles de saison.</p>

## Une chute réelle, une date qui ne se prouve pas

La page [La grille]({{ '/statistiques/grille/' | relative_url }}) cherche une
rupture dans le **format** et n’en trouve pas la date : le profil des coupures
possibles y est un plateau. La même méthode, appliquée à l’audience, donne un
profil bien plus serré — sans pour autant prouver une date.

{% include graphiques/audience-nulle.svg %}

<p class="legende-figure">Qualité de la meilleure coupure de la série
d’audience, face à celle obtenue sur des saisons remises dans un ordre au
hasard.</p>

<div class="constat">
  <p>La meilleure coupure tombe sur <b><i>{{ a.premiere_apres.titre }}</i>
  ({{ a.premiere_apres.annee }})</b>, {{ tr.ecart_types }} {{ tr.ecart_types_mot }}
  au-dessus d’une coupure au hasard, p ajustée {{ tr.p_ajustee }} : l’audience
  n’est pas stable, et c’est solide.</p>
  <p><b>Mais un déclin régulier produirait une coupure aussi nette</b> :
  contre des séries de même pente, {{ tg.ecart_types }} {{ tg.ecart_types_mot }},
  p ajustée {{ tg.p_ajustee }}. Que la chute ait une date plutôt qu’une
  pente, ces données ne le montrent pas.</p>
  <p>Avant : <b>{{ a.moyenne_avant_millions }}
  millions</b> de téléspectateurs en moyenne, sur {{ a.avant }} saisons.
  Après : <b>{{ a.moyenne_apres_millions }}
  millions</b>, sur {{ a.apres }}. D’un régime à l’autre, le programme a perdu
  {{ a.perte_regimes }} % de son public.</p>
</div>

{% include graphiques/audience-profil.svg %}

<p class="legende-figure">Le même profil que sur la page de la grille, pour
comparaison. Ici, un pic — là, un plateau.</p>

La comparaison se fait en deux chiffres, et c’est le second qui compte.
L’avance de la meilleure coupure sur la deuxième vaut **{{ a.avance }} %** ici,
contre {{ m.ruptures.avance }} % pour le format : dans les deux cas, une avance
trop mince pour désigner une année à elle seule. Mais les
coupures qui tiennent à 10 % près sont **{{ a.nb_proches }}, étalées sur
{{ a.fenetre.etendue }} an**, de {{ a.fenetre.debut }} à {{ a.fenetre.fin }} —
contre {{ m.ruptures.nb_proches }} sur {{ m.ruptures.fenetre.etendue }} ans pour
le format.

Si date il y a, elle est donc bien localisée : ses concurrentes sérieuses
sont toutes au même endroit. Mais localiser la meilleure coupure n’est pas
prouver qu’il y en a une. Cette page affirmait jusqu’au 22 octobre 2026 que
« la chute a une date » ; le test contre un déclin régulier, ajouté ce jour-là,
ne le confirme pas.

## Ce qui change exactement cette saison-là

<div class="tableau-large">
<table data-triable>
<thead><tr><th>Soir de diffusion</th><th class="nombre">Saisons</th>
<th class="nombre">Audience moyenne</th><th class="nombre">De</th><th class="nombre">À</th></tr></thead>
<tbody>
{% for j in a.jours %}
<tr>
  <td>{{ j.jour }}</td>
  <td class="nombre">{{ j.saisons }}</td>
  <td class="nombre" data-val="{{ j.moyenne }}">{{ j.moyenne_millions }} M</td>
  <td class="nombre">{{ j.premiere }}</td>
  <td class="nombre">{{ j.derniere }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

*{{ a.bascule_jour.titre }}* ({{ a.bascule_jour.annee }}) ouvre **la diffusion
du mardi**, que le programme n’a plus quittée, après {{ site.data.stats.mots.annees_de_vendredi }} ans
où le vendredi dominait{% if a.meme_soir_avant.size > 0 %} — une édition spéciale,
*{{ a.meme_soir_avant[0].titre }}* ({{ a.meme_soir_avant[0].annee }}), était déjà
passée le mardi, sans suite{% endif %}. C’est aussi la saison sur laquelle tombe
la meilleure coupure de l’audience.

<p class="note"><strong>Et c’est précisément pourquoi on ne peut pas conclure.</strong>
Le soir de diffusion change <em>une fois</em>, et il change là où l’audience
chute. Statistiquement, « après {{ a.annee_rupture }} » et « le mardi » sont la même
variable : aucun modèle, sur {{ site.data.stats.mots.audience_saisons }} saisons,
ne peut les séparer. D’autres
explications tombent au même endroit — l’érosion générale de la télévision
linéaire, l’affaire de tricherie de cette saison-là, le report d’une part
croissante de l’audience sur le rattrapage, que ces chiffres ne comptent pas.
On donne la coïncidence ; on ne donne pas de cause.</p>

Un détail va d’ailleurs contre la lecture simple : *{{ a.sommet.titre }}*
({{ a.sommet.annee }}) était déjà diffusé le mardi, et c’est **la meilleure audience de toute
l’histoire du programme**. Le mardi n’a rien de fatal en soi.

## La finale ne tient plus

Pendant les premières saisons, la finale faisait beaucoup mieux que le
lancement : on venait voir qui gagnait. Ce n’est plus vrai.

{% include graphiques/audience-lancement-finale.svg %}

<p class="legende-figure">Audience du premier et du dernier épisode de chaque
saison. Les deux courbes se croisent, puis s’inversent. Sous l’axe, le jour de
diffusion — <b>V</b> vendredi, <b>M</b> mardi, <b>S</b> samedi — puis les mois,
en chiffres.</p>

<div class="constat">
  <p>Avant <i>{{ a.retournement.bascule.titre }}</i>
  ({{ a.retournement.bascule.annee }}), la finale valait en moyenne
  <b>×{{ a.retournement.ratio_avant }}</b> le lancement. Depuis :
  <b>×{{ a.retournement.ratio_apres }}</b>.</p>
  <p>La corrélation entre l’année et ce rapport vaut
  <b>{{ tf.observe }}</b> — {{ tf.ecart_types }} {{ tf.ecart_types_mot }}, p ajustée {{ tf.p_ajustee }}. <b>Le public ne reste plus jusqu’au bout.</b></p>
</div>

C’est une information sur le programme que le programme ne donne pas, et qu’un
téléspectateur ne peut pas voir : chacun sait ce qu’il regarde, personne ne voit
la courbe.

## Le format suit-il l’audience ? Un piège, et ce qu’il en reste

La question évidente : quand l’audience baisse, la production réagit-elle ? On
peut la poser en confrontant l’audience d’une saison à la taille du casting de
la **suivante**.

La corrélation brute vaut **{{ a.format_correlation_brute }}** — forte,
négative, exactement ce qu’on espérait trouver. Et elle ne vaut rien.

<p class="note"><strong>Deux séries qui dérivent avec le temps se corrèlent
toujours.</strong> L’audience baisse d’année en année ; le casting grossit
d’année en année. Les mettre face à face ne mesure que le passage du temps. La
seule question honnête est : <em>une saison moins regardée que son époque ne le
laissait attendre est-elle suivie d’un casting plus large que son époque ne le
laissait attendre ?</em> On retire donc de chaque série sa tendance temporelle,
et on ne compare que les écarts.</p>

<div class="constat">
  <p>Une fois la tendance retirée, la corrélation tombe de
  {{ a.format_correlation_brute }} à <b>{{ ts.observe }}</b> —
  {{ ts.ecart_types }} {{ ts.ecart_types_mot }}, p ajustée {{ ts.p_ajustee }}.
  <b>Il ne reste rien.</b></p>
  <p>Rien ne dit ici que la production réagit à ses audiences en changeant la
  taille du casting. Rien ne dit non plus le contraire : à
  {{ a.saisons }} saisons, un effet réel mais modeste passerait inaperçu.</p>
</div>

C’est le troisième résultat spectaculaire que ce site jette après vérification.
Les deux autres sont racontés sur
[Qui vise qui]({{ '/statistiques/qui-vise-qui/' | relative_url }}) et
[La recette du casting]({{ '/statistiques/casting/' | relative_url }}).

## Ce que ces chiffres ne mesurent pas

<p class="note"><strong>C’est l’audience « veille », en direct.</strong> Elle
ignore le rattrapage, que ces données ne mesurent pas. Une part de la chute
mesurée ici peut donc être un déplacement, pas une disparition — et cette part grandit avec les années, ce
qui exagère la pente.</p>

<p class="note"><strong>Un épisode ne vaut pas un épisode.</strong> Depuis 2022,
un épisode est coupé en deux et mesuré deux fois. Les
{{ a.courbes | size }} saisons au détail épisode par épisode mélangent donc des
mesures d’épisode entier et de demi-épisode. Le contrôle est fait : sur les
{% assign ac = site.data.stats.audience_controle %}{{ ac.saisons }} saisons où
l’on a à la fois le détail et la moyenne annoncée, {{ ac.concordantes }}
concordent à 0,5 % près. Les autres — {{ ac.discordantes_texte }} — s’en
écartent jusqu’à {{ ac.ecart_max }} %, et l’écart vient de la source elle-même, qui ne s’accorde pas avec sa propre moyenne.</p>

<p class="note"><strong>Aucune audience n’existe pour la saison en cours</strong>
au moment de la construction, ni pour les épisodes non encore diffusés.</p>
