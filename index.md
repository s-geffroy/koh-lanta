---
layout: home
# Le H1 et le chapeau de l'accueil sont ICI, dans `accroche` et `chapeau` :
# _includes/entete-page.html les pose dans le bandeau de nuit, au-dessus du
# rail, ou le contenu de cette page n'a pas acces.
accroche: Tout le monde sort, sauf un
chapeau: >-
  Chaque aventurier de Koh-Lanta tient un certain nombre de jours, puis s’en
  va. Voici à quelle vitesse le camp se vide.
# « Accueil » etait le pire titre du site : la page la plus importante ne
# disait rien a un moteur. Ce titre-ci n'apparait NULLE PART a l'ecran -- le
# H1 de l'accueil est `.accueil-titre`, ecrit depuis `accroche` ci-dessus, et
# `layout: home` ne lit jamais `page.title`. Seul jekyll-seo-tag le lit, et il
# y colle « | Koh-Lanta en chiffres ».
title: Statistiques, classement et records
description: >-
  Vingt-cinq ans de Koh-Lanta mis en données : chaque participation, chaque
  épreuve, chaque bulletin de vote, et ce que les chiffres disent du jeu.
---
{%- comment -%}
  L'accueil depuis la refonte du 19 octobre 2026 (titre et chapeau dans le
  front matter, voir plus haut) : une figure, une ligne de
  mesures, huit constats d'une phrase, les portes d'entree. Chaque constat
  renvoie a la page qui le demontre -- la demonstration n'est plus ici.

  Les nombres viennent tous de _data/stats.yml, et aucune phrase ne pose de
  rapport ECRIT EN DUR entre deux d'entre eux (« deux fois et demie »,
  « trois sur quatre ») : un rapport fige ment des que la saison suivante
  deplace l'un des deux termes.
{%- endcomment -%}
{% assign g = site.data.stats.general %}
{% assign sb = site.data.stats.survie_bandeau %}

{% include graphiques/accueil-survie.svg %}

<p class="peigne-legende">Part des aventuriers encore en jeu, jour par jour, sur
les {{ sb.effectif }} participations des saisons classiques achevées. Les
courbes jaune et rouge <b>se confondent</b> : même médiane, le jour
{{ sb.mediane }}, et {{ sb.ecart_moyen }} points d’écart en moyenne. C’est le
résultat le plus répété de ce site.</p>

<p class="accueil-mesures"><b>{{ g.saisons_diffusees }}</b> saisons diffusées,
<b>{{ g.participations }}</b> participations, <b>{{ g.personnes }}</b>
aventuriers, <b>{{ site.data.stats.epreuves.epreuves }}</b> épreuves,
<b>{{ site.data.stats.conseils.bulletins }}</b> bulletins dépouillés,
<b>{{ site.data.stats.colliers.colliers }}</b> colliers.</p>

## Ce que les chiffres disent

{% assign i = site.data.stats.indicateurs %}
{% assign fv = i.fantomes_issue | where: "sort", "vainqueur" | first %}
{% assign rv = site.data.stats.revenants %}
{% assign aa = site.data.stats.modeles.avant_apres %}
{% assign co = site.data.stats.modeles.conditionnelles %}
{% assign af = site.data.stats.modeles.autour_du_feu %}
{% assign jeui = site.data.stats.prevision.jeux | last %}
{% assign cl = site.data.stats.classement %}
<ul class="constats">
  <li>
    <p><b>Le jaune ne bat pas le rouge.</b> Sur les saisons classiques,
    {{ site.data.stats.couleurs[0].victoires }} victoires de chaque côté : la
    couleur de départ ne décide pas du vainqueur.</p>
    <p><a href="{{ '/statistiques/tribus/' | relative_url }}">Jaune contre rouge</a></p>
  </li>
  <li>
    <p><b>On ne dure pas en se faisant oublier.</b> Les {{ i.nb_fantomes }}
    aventuriers jamais visés en {{ i.seuil_fantome }} conseils gagnent dans
    {{ fv.part_fantomes }} % des cas, contre {{ fv.part_endurants }} % ; mais
    être du côté de la majorité au conseil pèse bien davantage.</p>
    <p><a href="{{ '/statistiques/alliances/' | relative_url }}">Les alliances</a></p>
  </li>
  <li>
    <p><b>L’expérience ne paie pas.</b> Les revenants tenaient déjà
    {{ rv.paradoxe[1].survie_moyenne }} % de la saison à leur première
    aventure ; à leur retour, ils redescendent à
    {{ rv.paradoxe[2].survie_moyenne }} %. Le tri s’était fait avant.</p>
    <p><a href="{{ '/statistiques/revenants/' | relative_url }}">Les revenants</a></p>
  </li>
  <li>
    <p><b>Après la fusion, on n’élimine pas le plus fort.</b> L’éliminé se
    situe au rang {{ aa.rang_force_avant }} sur 100 de son camp avant la
    réunification, {{ aa.rang_force_apres }} après : un écart que le hasard
    suffit à expliquer.</p>
    <p><a href="{{ '/statistiques/fusion/' | relative_url }}">Avant et après la fusion</a></p>
  </li>
  <li>
    <p><b>Le conseil d’avant annonce le suivant.</b> Sans voix reçue la fois
    précédente, on part dans {{ co.par_voix[0].probabilite }} % des cas ; avec
    deux voix, dans {{ co.par_voix[2].probabilite }} %.</p>
    <p><a href="{{ '/statistiques/conditionnelles/' | relative_url }}">Sachant le conseil d’avant</a></p>
  </li>
  <li>
    <p><b>Le bandeau décide qui part.</b> Quand son bandeau d’origine est le
    moins représenté du camp, on est éliminé dans
    {{ af.bandeau[0].probabilite }} % des cas, contre
    {{ af.bandeau[1].probabilite }} % quand il est le plus représenté.</p>
    <p><a href="{{ '/statistiques/autour-du-feu/' | relative_url }}">Sachant qui est autour du feu</a></p>
  </li>
  <li>
    <p><b>Le jeu se devine mal.</b> Un modèle qui n’a jamais vu la saison
    désigne le bon éliminé dans {{ jeui.premiers }} % des conseils, le hasard
    dans {{ jeui.premiers_hasard }} %.</p>
    <p><a href="{{ '/statistiques/pronostic/' | relative_url }}">Le pronostic</a></p>
  </li>
  <li>
    <p><b>« Meilleur joueur » ne désigne pas une qualité.</b> {{ site.data.stats.mots.facettes_maj }} façons de
    bien jouer, et aucune ne prédit les autres :
    {{ cl.robustesse.candidats }} aventuriers différents entrent dans le top
    {{ cl.taille }} selon le poids donné à chacune.</p>
    <p><a href="{{ '/statistiques/top/' | relative_url }}">Le top des joueurs</a></p>
  </li>
</ul>

## Par où commencer

<ul class="cartes">
  <li class="carte">
    <a href="{{ '/statistiques/' | relative_url }}">
      <span class="carte-rang">{{ site.data.stats.mots.sommaire_entrees_maj }} entrées</span>
      <span class="carte-titre">Les statistiques</span>
      <span class="carte-resume">Vainqueurs, tribus, longévité, épreuves,
        conseils, alliances : les comptages, puis les modèles.</span>
    </a>
  </li>
  <li class="carte">
    <a href="{{ '/saisons/' | relative_url }}">
      <span class="carte-rang">{{ g.saisons_diffusees }} éditions</span>
      <span class="carte-titre">Les saisons</span>
      <span class="carte-resume">Chaque édition, son lieu, sa durée, son
        casting et son vainqueur.</span>
    </a>
  </li>
  <li class="carte">
    <a href="{{ '/aventuriers/' | relative_url }}">
      <span class="carte-rang">{{ g.participations }} participations</span>
      <span class="carte-titre">Les aventuriers</span>
      <span class="carte-resume">Âge, métier, tribu et sortie de chacun. Le
        tableau se cherche, se filtre et se trie.</span>
    </a>
  </li>
  <li class="carte">
    <a href="{{ '/completude/' | relative_url }}">
      <span class="carte-rang">{{ site.data.stats.completude_saisons.cases }} croisements</span>
      <span class="carte-titre">La complétude</span>
      <span class="carte-resume">Ce qui est vraiment renseigné, édition par
        édition et donnée par donnée.</span>
    </a>
  </li>
  <li class="carte">
    <a href="{{ '/sources/' | relative_url }}">
      <span class="carte-rang">Traçabilité</span>
      <span class="carte-titre">Les sources</span>
      <span class="carte-resume">D’où vient chaque champ, et comment les
        contradictions ont été tranchées.</span>
    </a>
  </li>
</ul>
