---
layout: home
title: Accueil
description: >-
  Vingt-cinq ans de Koh-Lanta mis en données : chaque participation, chaque
  épreuve, chaque bulletin de vote, et ce que les chiffres disent du jeu.
---

{% assign g = site.data.stats.general %}
{% assign v = site.data.stats.vainqueurs %}
{% assign i = site.data.stats.indicateurs %}

<p class="oeil">
  <span>Vingt-cinq ans de jeu</span>
  <span class="oeil-rang">{{ g.premiere_annee }}<i>–{{ g.derniere_annee }}</i></span>
</p>

{% assign sb = site.data.stats.survie_bandeau %}
<h1 class="accueil-titre">Tout le monde sort, sauf un</h1>

<p class="accueil-chapeau">Chaque aventurier de Koh-Lanta tient un certain
nombre de jours, puis s’en va. Voici à quelle vitesse le camp se vide — et la
première chose qu’on y voit est une chose qui n’arrive pas.</p>

{% include graphiques/accueil-survie.svg %}

<p class="peigne-legende">Part des aventuriers encore en jeu, jour par jour, sur
les {{ sb.effectif }} participations des saisons classiques achevées. La courbe
jaune et la courbe rouge ne se croisent pas : <b>elles se confondent</b>. Les
deux bandeaux ont la même médiane, le jour {{ sb.mediane }}, à la journée près,
et leurs deux courbes ne s’écartent que de <b>{{ sb.ecart_moyen }} points</b> en
moyenne — {{ sb.ecart_maximal }} au plus fort de leur écart. C’est le résultat
le plus répété de ce site.
[Jaune contre rouge]({{ '/statistiques/tribus/' | relative_url }}) le démontre ;
[Âge et longévité]({{ '/statistiques/longevite/' | relative_url }}) montre la
même courbe dessinée avec ses {{ g.participations }} individus, un trait par
aventurier.</p>

<ul class="chiffres">
  <li class="chiffre"><b>{{ g.saisons_diffusees }}</b><span>saisons diffusées</span></li>
  <li class="chiffre"><b>{{ g.participations }}</b><span>participations</span></li>
  <li class="chiffre"><b>{{ g.personnes }}</b><span>aventuriers différents</span></li>
  <li class="chiffre"><b>{{ site.data.stats.epreuves.epreuves }}</b><span>épreuves relevées</span></li>
  <li class="chiffre"><b>{{ site.data.stats.conseils.bulletins }}</b><span>bulletins dépouillés</span></li>
  <li class="chiffre"><b>{{ site.data.stats.colliers.colliers }}</b><span>colliers suivis</span></li>
</ul>

## Trois idées reçues que les chiffres démentent

**Le jaune ne bat pas le rouge.** On lit souvent que la tribu jaune l’emporte
plus souvent. Sur les saisons classiques, c’est
**{{ site.data.stats.couleurs[0].victoires }} victoires partout** : la couleur
de départ ne décide de rien.
[Jaune contre rouge]({{ '/statistiques/tribus/' | relative_url }}).

**Le vainqueur type n’a pas trente ans tout rond.** Il en a
**{{ v.age_moyen }}** en moyenne, et près d’un sur quatre
({{ v.part_40_et_plus }} %) a **quarante ans ou plus** au moment du sacre.
[Le profil du vainqueur]({{ '/statistiques/vainqueurs/' | relative_url }}).

**Les femmes tiennent moins longtemps et gagnent autant.** Elles quittent le jeu
plus tôt que les hommes en moyenne — et remportent pourtant
{{ v.par_genre[0].effectif }} finales sur {{ v.effectif }}.
[Âge et longévité]({{ '/statistiques/longevite/' | relative_url }}).

## Ce que les chiffres révèlent

{% assign fv = i.fantomes_issue | where: "sort", "vainqueur" | first %}
<div class="constat">
  <p>Sur {{ site.data.stats.conseils.bulletins }} bulletins dépouillés,
  <b>{{ i.nb_fantomes }} aventuriers ont traversé au moins
  {{ i.seuil_fantome }} conseils sans que personne n’écrive jamais leur
  nom</b>.</p>
  <p>Ils gagnent dans <b>{{ fv.part_fantomes }} %</b> des cas, contre
  {{ fv.part_endurants }} % pour ceux qui ont tenu aussi longtemps qu’eux :
  <b>deux fois et demie plus</b>.</p>
  <p>Mais ce n’est pas le premier prédicteur. Mis en concurrence avec lui,
  <b>être du côté de la majorité au conseil pèse cinq fois plus</b>. On ne dure
  pas en se faisant oublier : on dure en étant du côté qui compte les voix.</p>
  <p><a href="{{ '/statistiques/alliances/' | relative_url }}">Les alliances</a>
  · <a href="{{ '/statistiques/jeu-social/' | relative_url }}">Le jeu social</a></p>
</div>

## Et un piège que les chiffres tendent

<div class="constat">
  <p>{% assign rv = site.data.stats.revenants %}Les aventuriers rappelés pour
  une seconde saison tiennent en moyenne plus longtemps que les autres. On en
  conclut volontiers que <b>l’expérience paie</b>. C’est faux.</p>
  <p>Ils tenaient déjà <b>{{ rv.paradoxe[1].survie_moyenne }} %</b> de la saison
  lors de leur <b>première</b> aventure, contre
  {{ rv.paradoxe[0].survie_moyenne }} % pour ceux qui n’ont jamais été
  rappelés — et quand ils reviennent, ils redescendent à
  <b>{{ rv.paradoxe[2].survie_moyenne }} %</b>. Le tri s’est fait avant le
  retour ; le retour lui-même se passe moins bien.</p>
  <p><a href="{{ '/statistiques/revenants/' | relative_url }}">Les revenants</a></p>
</div>

## Et une chose que la production ne dit pas

{% assign tp = site.data.stats.modeles.registre | where: "cle", "parite" | first %}
<div class="constat">
  <p>On lit partout que la production « vise l’équilibre » entre femmes et
  hommes. La mesure est plus dure que la formule.</p>
  <p>Un casting s’écarte de la parité de <b>{{ tp.observe }} personne</b> en
  moyenne. En redistribuant les mêmes {{ site.data.stats.modeles.casting.effectif }}
  aventuriers au hasard entre les mêmes saisons, {{ tp.tirages }} fois, l’écart
  serait de <b>{{ tp.attendu }}</b>. Soit {{ tp.ecart_types }} écarts-types en
  dessous du hasard.</p>
  <p>Ce n’est pas une tendance : la plupart des saisons partent
  <b>exactement</b> à égalité. Et ce casting tenu au cordeau
  <b>ne prédit rien</b> du vainqueur.</p>
  <p><a href="{{ '/statistiques/casting/' | relative_url }}">La recette du casting</a>
  · <a href="{{ '/statistiques/pronostic/' | relative_url }}">Le pronostic</a></p>
</div>

## Et une chose qu’on ne voit pas à l’écran

{% assign geo = site.data.geographie %}
<div class="constat">
  <p>Comparé à la France qui vivait là ces années-là, le recrutement
  <b>n’épouse pas la géographie</b> : la dispersion des origines par région vaut
  {{ geo.regions_dispersion_observee }} contre
  {{ geo.regions_dispersion_attendue }} attendus d’un tirage dans la population
  des 20-59 ans.</p>
  <p>Provence-Alpes-Côte d’Azur fournit <b>une fois et trois quarts sa part</b>,
  la Corse près de trois fois. À l’autre bout, <b>l’outre-mer pèse
  {{ geo.outremer.observe }} aventuriers pour {{ geo.outremer.attendu }}
  attendus</b> — La Réunion n’en a jamais fourni un seul.</p>
  <p>Sur les prénoms, le même casting collait pourtant de très près à sa
  génération. Ce n’est donc pas la France entière qu’on regarde le mardi soir.</p>
  <p><a href="{{ '/statistiques/geographie/' | relative_url }}">D’où ils viennent</a>
  · <a href="{{ '/statistiques/prenoms/' | relative_url }}">Les prénoms</a></p>
</div>

## Et une chose que tout le monde raconte à l’envers

{% assign aa = site.data.stats.modeles.avant_apres %}
{% assign tfu = site.data.stats.modeles.registre | where: "cle", "fusion_force" | first %}
<div class="constat">
  <p>On répète partout qu’<b>avant la réunification on élimine le faible</b> —
  la tribu doit gagner ses épreuves — et qu’<b>après on élimine le fort</b>,
  devenu une menace.</p>
  <p>C’est l’inverse. Avant la fusion, l’éliminé se situe au rang
  <b>{{ aa.rang_force_avant }} sur 100</b> de son camp : au-dessus de la
  médiane. Après, il tombe à <b>{{ aa.rang_force_apres }}</b> —
  {{ tfu.ecart_types }} écarts-types sous ce qu’un tirage donnerait, p ajustée
  {{ tfu.p_ajustee }}.</p>
  <p>La tribu qui perd sacrifie le joueur qu’elle a vu gagner. Le camp réuni,
  lui, choisit au milieu du classement.</p>
  <p><a href="{{ '/statistiques/fusion/' | relative_url }}">Avant et après la fusion</a></p>
</div>

## Et une chose que le conseil d’avant annonce

{% assign co = site.data.stats.modeles.conditionnelles %}
{% assign tmv = site.data.stats.modeles.registre | where: "cle", "menace_voix" | first %}
{% assign tms = site.data.stats.modeles.registre | where: "cle", "menace_sommet" | first %}
<div class="constat">
  <p>Sachant qu’on n’a reçu <b>aucune voix</b> au conseil précédent, on part
  dans {{ co.par_voix[0].probabilite }} % des cas. Sachant qu’on en a reçu
  <b>deux</b>, dans <b>{{ co.par_voix[2].probabilite }} %</b> —
  {{ tmv.ecart_types }} écarts-types au-dessus du hasard, p ajustée
  {{ tmv.p_ajustee }}.</p>
  {% assign gr = co.par_voix | where: "modalite", "5 voix et plus" | first %}
  <p>Mais la menace a un <b>sommet</b>. À cinq voix et plus, la probabilité
  retombe à <b>{{ gr.probabilite }} %</b>, sous le hasard : qui a encaissé un
  vote massif et se trouve encore là au conseil suivant a nécessairement été
  protégé, et cette protection ne s’évapore pas.</p>
  <p><a href="{{ '/statistiques/conditionnelles/' | relative_url }}">Sachant le conseil d’avant</a></p>
</div>

## Et une chose que le bandeau décide encore

{% assign af = site.data.stats.modeles.autour_du_feu %}
{% assign tba = site.data.stats.modeles.registre | where: "cle", "bandeau_minoritaire" | first %}
<div class="constat">
  <p>La couleur de départ ne décide rien du palmarès — douze victoires jaunes,
  douze rouges. Elle décide en revanche <b>qui part</b> : sachant que son
  bandeau d’origine est le moins représenté du camp présent, on est éliminé dans
  <b>{{ af.bandeau[0].probabilite }} %</b> des cas, contre
  {{ af.bandeau[1].probabilite }} % quand il est le plus représenté.</p>
  <p>{{ tba.ecart_types }} écarts-types au-dessus d’un tirage au sort parmi les
  présents, p ajustée {{ tba.p_ajustee }}. Et l’écart est <b>plus fort avant la
  réunification qu’après</b> : c’est le sort réservé à celui qu’un échange de
  tribus vient de déposer chez les autres.</p>
  <p><a href="{{ '/statistiques/autour-du-feu/' | relative_url }}">Sachant qui est autour du feu</a>
  · <a href="{{ '/statistiques/tribus/' | relative_url }}">Jaune contre rouge</a></p>
</div>

## Et une chose que le conseil rend prévisible

{% assign pp = site.data.stats.modeles.pire_place %}
{% assign tvi = site.data.stats.modeles.registre | where: "cle", "vote_isole" | first %}
<div class="constat">
  <p>Deux choses se savent <b>avant</b> qu’un bulletin ne soit écrit : le nom
  qui est sorti de l’urne la fois d’avant, et le nombre de gens, encore assis
  là, avec qui on a déjà voté.</p>
  <p>Aucun des deux signaux : <b>{{ pp.cumul[0].probabilite }} %</b> de risque
  de partir. Un seul : {{ pp.cumul[1].probabilite }} %. <b>Les deux</b> :
  <b>{{ pp.cumul[2].probabilite }} %</b> — presque un sur deux. Et les deux
  survivent dans le même modèle, à conseil égal : ce ne sont pas deux façons de
  dire la même chose.</p>
  <p><a href="{{ '/statistiques/pire-place/' | relative_url }}">La pire place au conseil</a></p>
</div>

## Et une chose que le programme subit

{% assign au = site.data.stats.modeles.audience %}
{% assign tra = site.data.stats.modeles.registre | where: "cle", "audience_rupture" | first %}
<div class="constat">
  <p>L’audience est la seule grandeur de ce jeu de données que la production ne
  décide pas. Elle est passée de
  <b>{{ au.sommet.moyenne | divided_by: 100000 | divided_by: 10.0 }} millions</b>
  de téléspectateurs en {{ au.sommet.annee }} à
  <b>{{ au.derniere.moyenne | divided_by: 100000 | divided_by: 10.0 }} millions</b>
  en {{ au.derniere.annee }} — <b>−{{ au.chute }} %</b>.</p>
  <p>Et sa chute a une <b>date</b> : elle tombe sur
  <i>{{ au.premiere_apres.titre }}</i> ({{ au.premiere_apres.annee }}),
  {{ tra.ecart_types }} écarts-types au-dessus d’une coupure au hasard. C’est
  aussi la première saison diffusée le mardi après vingt ans de vendredi. Les
  deux dates sont la même date — et c’est exactement pourquoi on ne peut pas
  conclure.</p>
  <p><a href="{{ '/statistiques/audience/' | relative_url }}">L’audience</a>
  · <a href="{{ '/statistiques/grille/' | relative_url }}">La grille</a></p>
</div>

## Par où commencer

<ul class="cartes">
  <li class="carte">
    <a href="{{ '/statistiques/' | relative_url }}">
      <span class="carte-rang">VINGT-CINQ ENTRÉES</span>
      <span class="carte-titre">Les statistiques</span>
      <span class="carte-resume">Les vainqueurs, les tribus, les métiers, les
        prénoms, la longévité, les sorties, les épreuves, les colliers, le jeu
        social, les conseils, les revenants — puis quatorze pages où les modèles
        prennent le relais des comptages.</span>
    </a>
  </li>
  <li class="carte">
    <a href="{{ '/saisons/' | relative_url }}">
      <span class="carte-rang">{{ g.saisons_diffusees }} ÉDITIONS</span>
      <span class="carte-titre">Les saisons</span>
      <span class="carte-resume">Chaque édition avec son lieu, sa durée, son
        casting et son vainqueur — et quatre indicateurs qui disent ce qu’elle
        a été.</span>
    </a>
  </li>
  <li class="carte">
    <a href="{{ '/aventuriers/' | relative_url }}">
      <span class="carte-rang">{{ g.participations }} LIGNES</span>
      <span class="carte-titre">Les aventuriers</span>
      <span class="carte-resume">Toutes les participations, avec âge, métier,
        tribu et sortie. Le tableau se cherche, se filtre et se trie.</span>
    </a>
  </li>
  <li class="carte">
    <a href="{{ '/completude/' | relative_url }}">
      <span class="carte-rang">{{ site.data.stats.completude_saisons.cases }} CROISEMENTS</span>
      <span class="carte-titre">La complétude</span>
      <span class="carte-resume">Le tableau complet : chaque édition en ligne,
        chaque type de donnée en colonne, et à l’intersection ce qui est
        vraiment renseigné.</span>
    </a>
  </li>
  <li class="carte">
    <a href="{{ '/sources/' | relative_url }}">
      <span class="carte-rang">TRAÇABILITÉ</span>
      <span class="carte-titre">Les sources</span>
      <span class="carte-resume">D’où vient chaque champ, comment les
        contradictions ont été tranchées, et ce qui manque encore.</span>
    </a>
  </li>
</ul>
