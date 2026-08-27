---
layout: home
title: Accueil
---

{% assign g = site.data.stats.general %}
{% assign v = site.data.stats.vainqueurs %}

**Vingt-cinq ans de Koh-Lanta, mis en chiffres.** Ce site rassemble les
{{ g.participations }} participations des {{ g.saisons_diffusees }} saisons
diffusées entre {{ g.premiere_annee }} et {{ g.derniere_annee }}, et en tire ce
que les données disent vraiment du jeu.

<ul class="chiffres">
  <li class="chiffre"><b>{{ g.saisons_diffusees }}</b><span>saisons diffusées</span></li>
  <li class="chiffre"><b>{{ g.participations }}</b><span>participations</span></li>
  <li class="chiffre"><b>{{ g.personnes }}</b><span>aventuriers</span></li>
  <li class="chiffre"><b>{{ g.pays }}</b><span>pays de tournage</span></li>
  <li class="chiffre"><b>{{ v.age_moyen }}</b><span>âge moyen des vainqueurs</span></li>
</ul>

## Trois choses que les chiffres démentent

**Le jaune ne bat pas le rouge.** On lit souvent que la tribu jaune l'emporte
plus souvent. Sur les saisons classiques, c'est **{{ site.data.stats.couleurs[0].victoires }} victoires partout** :
la couleur de départ ne décide de rien.

**Le vainqueur type n'a pas trente ans tout rond.** Il en a
**{{ v.age_moyen }}** en moyenne, et près d'un sur quatre
({{ v.part_40_et_plus }} %) a **40 ans ou plus** au moment du sacre.

**Les femmes tiennent moins longtemps mais gagnent autant.** Elles quittent le
jeu plus tôt que les hommes en moyenne — et remportent pourtant
{{ v.par_genre[0].effectif }} finales sur {{ v.effectif }}.

{% assign i = site.data.stats.indicateurs %}

## Et une chose que les chiffres révèlent

Sur {{ site.data.stats.conseils.bulletins }} bulletins dépouillés,
{{ i.nb_fantomes }} aventuriers ont traversé leur saison **sans que personne
n'écrive jamais leur nom**. Ils gagnent dans
**{{ i.fantomes_issue[0].part_fantomes }} %** des cas, contre
{{ i.fantomes_issue[0].part_ensemble }} % pour l'ensemble — cinq fois et demie
plus. C'est le meilleur prédicteur de victoire de tout ce jeu de données :
[le jeu social]({{ '/statistiques/jeu-social/' | relative_url }}).

## Par où commencer

<ul class="sommaire">
  <li><a href="{{ '/statistiques/' | relative_url }}">Les statistiques</a>
      <p>Le profil des vainqueurs, les tribus, les métiers, la longévité,
         les épreuves, les colliers, les conseils, le jeu social.</p></li>
  <li><a href="{{ '/saisons/' | relative_url }}">Les saisons</a>
      <p>Les {{ g.saisons_diffusees }} éditions, leur lieu, leur casting, leur vainqueur.</p></li>
  <li><a href="{{ '/aventuriers/' | relative_url }}">Les aventuriers</a>
      <p>Les {{ g.participations }} participations, avec âge, métier, tribu et sortie.</p></li>
  <li><a href="{{ '/sources/' | relative_url }}">Les sources</a>
      <p>D'où viennent ces données, et comment elles ont été constituées.</p></li>
</ul>
