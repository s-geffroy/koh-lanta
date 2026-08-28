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

<h1 class="accueil-titre">Tout le monde sort, sauf un</h1>

<p class="accueil-chapeau">Chaque aventurier de Koh-Lanta tient un certain
nombre de jours, puis s’en va. Voici les {{ g.participations }} d’entre eux,
rangés du séjour le plus court au plus long.</p>

{% include graphiques/peigne-torches.svg %}

<p class="peigne-legende">Un trait, un aventurier ; sa longueur, ses jours de
jeu ; sa couleur, son bandeau de départ. La bordure droite de cette figure est
la courbe de survie du programme — dessinée avec ses individus plutôt qu’avec
une moyenne. Les traits les plus courts sont ceux des premiers conseils, le bloc
plein du bas celui des finalistes. Dix-huit participations manquent : leur jour
de sortie n’est établi par aucune source. Les éditions spéciales, plus courtes,
y figurent avec leur durée réelle.</p>

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

## Par où commencer

<ul class="cartes">
  <li class="carte">
    <a href="{{ '/statistiques/' | relative_url }}">
      <span class="carte-rang">VINGT ENTRÉES</span>
      <span class="carte-titre">Les statistiques</span>
      <span class="carte-resume">Les vainqueurs, les tribus, les métiers, les
        prénoms, la longévité, les sorties, les épreuves, les colliers, le jeu
        social, les conseils, les revenants — puis neuf pages où les modèles
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
    <a href="{{ '/sources/' | relative_url }}">
      <span class="carte-rang">TRAÇABILITÉ</span>
      <span class="carte-titre">Les sources</span>
      <span class="carte-resume">D’où vient chaque champ, comment les
        contradictions ont été tranchées, et ce qui manque encore.</span>
    </a>
  </li>
</ul>
