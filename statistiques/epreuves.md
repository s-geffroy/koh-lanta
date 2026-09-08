---
layout: page
title: Les épreuves
permalink: /statistiques/epreuves/
chapeau: >-
  Les meilleurs ratios, les totaux de carrière, le profil qui domine vraiment — et une nature d’épreuve qui, elle, ne trie personne.
---

{% assign e = site.data.stats.epreuves %}

C’est la question qui revient le plus souvent, et celle sur laquelle circulent
le plus de chiffres invérifiables : **qui domine les épreuves ?**

**{{ e.epreuves }} épreuves** ont été relevées sur **{{ e.saisons_couvertes }}
saisons** — {{ e.immunites }} d’immunité, {{ e.conforts }} de confort ;
{{ e.collectives }} remportées par une tribu, {{ e.individuelles }} par une
personne.

<ul class="chiffres">
  <li class="chiffre"><b>{{ e.epreuves }}</b><span>épreuves relevées</span></li>
  <li class="chiffre"><b>{{ e.individuelles }}</b><span>individuelles</span></li>
  <li class="chiffre"><b>{{ e.collectives }}</b><span>collectives</span></li>
  <li class="chiffre"><b>{{ e.saisons_couvertes }}</b><span>saisons couvertes sur 34</span></li>
</ul>

## Le classement des ratios

<p class="note">Le dénominateur n’est pas le nombre d’épreuves de la saison,
mais celui des épreuves individuelles <strong>disputées avant sa sortie</strong> :
un aventurier éliminé au jour 9 n’a pas rendez-vous avec les épreuves du jour
30. Un seuil de {{ e.seuil_classement }} épreuves disputées écarte les
parcours trop courts, où une seule victoire suffirait à afficher un ratio
spectaculaire. {{ e.classement_effectif }} aventuriers passent ce seuil.</p>

{% include graphiques/epreuves-ratios.svg %}

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th class="nombre">#</th><th>Aventurier</th><th>Saison</th>
  <th class="nombre">Gagnées</th><th class="nombre">Disputées</th><th class="nombre">Ratio</th>
</tr></thead>
<tbody>
{% for x in e.classement_ratio %}
<tr>
  <td class="nombre">{{ forloop.index }}</td>
  <td><strong>{{ x.personne }}</strong></td>
  <td>{{ x.titre }} ({{ x.annee }}){% if x.speciale %} <em>— édition spéciale</em>{% endif %}</td>
  <td class="nombre">{{ x.gagnees }}</td>
  <td class="nombre">{{ x.disputees }}</td>
  <td class="nombre">{{ x.ratio }} %</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

## Les totaux d’une carrière

Le ratio récompense l’efficacité sur une saison. Le cumul, lui, récompense la
longévité : revenir jouer quatre ou cinq fois donne quatre ou cinq fois plus
d’occasions.

{% include graphiques/epreuves-cumuls.svg %}

**{{ e.meilleurs_cumuls[0].personne }}** est en tête avec
**{{ e.meilleurs_cumuls[0].victoires }} victoires individuelles**, devant
{{ e.meilleurs_cumuls[1].personne }} ({{ e.meilleurs_cumuls[1].victoires }}).
Les deux comptent parmi les aventuriers les plus rappelés du programme : leur
total dit autant leur nombre de participations que leur niveau.

## Le classement que ce tableau ne pouvait pas voir

{% assign pa = site.data.stats.palmares %}

Tout ce qui précède repose sur le **bilan épisode par épisode**, et ce bilan
ignore {{ e.saisons_sans_donnee | size }} saisons entières
({{ e.saisons_sans_donnee | join: ", " }}). Conséquence directe : un vainqueur
de l’une d’elles n’apparaît nulle part sur cette page, quel qu’ait été son
parcours.

Les fiches individuelles du wiki Fandom, elles, portent un total d’épreuves
**par édition**, sur {{ pa.renseignees }} participations — dont les cinq saisons
manquantes. Voici le classement qu’elles donnent.

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th class="nombre">#</th><th>Aventurier</th>
  <th class="nombre">Saisons</th>
  <th class="nombre">Individuelles</th><th class="nombre">Collectives</th>
</tr></thead>
<tbody>
{% for x in pa.classement %}
<tr>
  <td class="nombre">{{ forloop.index }}</td>
  <td>{{ x.personne }}</td>
  <td class="nombre">{{ x.saisons }}</td>
  <td class="nombre">{{ x.individuelles }}</td>
  <td class="nombre">{{ x.collectives }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

Le podium change. {{ pa.classement[2].personne }} monte à la troisième place
avec {{ pa.classement[2].individuelles }} victoires individuelles en
{{ pa.classement[2].saisons }} éditions — il était invisible plus haut, parce
que la saison qu’il a gagnée n’a pas de bilan par épisode.

<p class="note"><strong>Les deux comptes ne mesurent pas la même chose, et il
faut le savoir avant de les comparer.</strong> Le total d’une fiche englobe les
duels de l’île des bannis et les épreuves de finale, que le bilan par épisode
n’enregistre pas. Là où les deux existent, ils sont <strong>identiques dans
{{ pa.part_identiques }} % des cas</strong> ({{ pa.identiques }} sur
{{ pa.compares }}) et l’écart médian, quand il y en a un, vaut
{{ pa.ecart_median }}. C’est assez pour lire ce classement, pas pour le
substituer au précédent — et surtout pas pour nourrir un modèle : la
<a href="{{ '/statistiques/force/' | relative_url }}">force réelle</a> continue
de se calculer sur les seuls plateaux reconstruits.</p>

## Les épreuves ont des noms, et une nature

{% assign en = site.data.epreuves_nommees %}

Cette page a longtemps affirmé que **la nature d’une épreuve — endurance,
équilibre, précision — n’était donnée nulle part de façon exploitable**. La
première moitié de la phrase était fausse : le wiki Fandom tient
**{{ en.nb_epreuves }} pages d’épreuves récurrentes**, chacune avec son type et
la liste des saisons où elle a été disputée. {{ en.nb_apparitions }} apparitions
au total.

{% include graphiques/epreuves-natures.svg %}

<p class="legende-figure">Nombre d’épreuves récurrentes portant chaque
qualificatif. Une épreuve peut en porter deux — le parcours du combattant est
« rapidité, force ».</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Épreuve</th><th>Type</th>
  <th class="nombre">Apparitions</th><th class="nombre">Saisons</th>
</tr></thead>
<tbody>
{% for x in en.epreuves %}{% if x.apparitions > 0 %}
<tr>
  <td>{{ x.nom }}</td>
  <td>{{ x.type }}</td>
  <td class="nombre">{{ x.apparitions }}</td>
  <td class="nombre">{{ x.saisons | size }}</td>
</tr>
{% endif %}{% endfor %}
</tbody>
</table>
</div>

Le parcours du combattant a été couru **{{ en.epreuves[0].apparitions }} fois**,
les flambeaux {{ en.epreuves[1].apparitions }} ; le tir à l’arc et l’épreuve de
la boue une vingtaine chacun. Voilà pour le catalogue.

## Pourquoi ce catalogue ne se raccorde pas aux épisodes

C’est la seconde moitié de la phrase qui tenait, et il valait mieux la mesurer
que l’affirmer.

<div class="constat">
  <p>Ce catalogue donne la <b>saison</b>, le vainqueur et le gain. Il ne donne
  pas l’<b>épisode</b>. Or {{ e.epreuves }} épreuves relevées le sont épisode par
  épisode — et un aventurier gagne souvent plusieurs épreuves du même genre dans
  la même saison.</p>
  <p>Résultat : sur les {{ en.raccord.epreuves_relevees }} épreuves relevées,
  <b>{{ en.raccord.epreuves_raccordees }} seulement</b> peuvent recevoir une
  nature — <b>{{ en.raccord.part_raccordee }} %</b>.</p>
</div>

<div class="tableau-large">
<table>
<thead><tr><th>Ce qui arrive à chaque citation du catalogue</th><th class="nombre">Effectif</th></tr></thead>
<tbody>
{% for m in en.raccord.motifs %}
<tr><td>{{ m.motif }}</td><td class="nombre">{{ m.effectif }}</td></tr>
{% endfor %}
</tbody>
</table>
</div>

**Et ces {{ en.raccord.part_raccordee }} % ne sont pas un échantillon.** Ce sont
exactement les épreuves dont l’ensemble des vainqueurs ne se retrouve qu’une
fois dans la saison — c’est-à-dire, en grande partie, les vainqueurs les moins
dominants. Chercher là si la nature d’une épreuve change qui la gagne
reviendrait à ne regarder que les joueurs qui gagnent peu. Aucune nature n’est
donc attachée à une épreuve **datée**, et aucun modèle épisode par épisode n’en
reçoit.

<p class="note"><strong>L’appariement a été resserré, et il a gagné trois
points.</strong> Il cherchait le vainqueur cité <em>un nom à la fois</em> : une
épreuve qui en cite deux — le meilleur homme et la meilleure femme du parcours
du combattant — rencontrait alors toutes les épreuves que l’un <em>ou</em>
l’autre avait gagnées, et ne tranchait jamais. Exiger que <strong>l’ensemble
complet des vainqueurs coïncide</strong> est une condition plus stricte, pas une
devinette de plus : le raccord passe de 11,0 % à
{{ en.raccord.part_raccordee }} %, et les épreuves individuelles — les seules qui
comptent ici — de 74 à {{ en.raccord.individuelles_raccordees }}.</p>

<p class="note"><strong>Le plafond, lui, a été vérifié à la source.</strong> La
catégorie « Épreuves » du wiki compte <strong>57 pages et aucune
sous-catégorie</strong> : ce n’est pas un extrait, c’est tout ce qui existe. Ce
qu’il faudrait pour aller plus loin : le nom de l’épreuve dans le bilan par
épisode, ou le numéro d’épisode dans la fiche de l’épreuve. Les résumés
détaillés de Wikipédia décrivent bien les épreuves une à une — « les candidats
doivent plonger, monter sur le voilier, récupérer un maximum d’éléments » — mais
en prose, sans jamais les nommer ni les qualifier. En tirer une nature
demanderait de juger ; ce site ne juge pas ses sources.</p>

## La question se posait autrement

{% assign n = site.data.stats.natures %}

L’épisode manquait ; le **nom** ne manquait pas. Le catalogue dit la saison et
le vainqueur, et cela suffit à écrire « untel a gagné telle épreuve, de nature
force » — sans savoir quel soir. Or c’est tout ce qu’il fallait pour poser la
question. Le biais du paragraphe précédent disparaît avec elle : on ne garde
plus les seules citations décidables, on les garde **toutes**.

<ul class="chiffres">
  <li class="chiffre"><b>{{ n.attribuees }}</b><span>citations rattachées à une personne, sur {{ n.citations }}</span></li>
  <li class="chiffre"><b>{{ n.personnes }}</b><span>aventuriers concernés</span></li>
  <li class="chiffre"><b>{{ n.victoires }}</b><span>victoires portant une nature</span></li>
</ul>

<p class="note">Le reste des citations n’est pas perdu, il est ailleurs :
{{ n.citations | minus: n.attribuees }} reviennent à une <em>tribu</em> — une
épreuve collective n’a pas de vainqueur individuel — ou portent un prénom que la
saison ne connaît pas. Et l’on compte ici des <strong>citations</strong>, pas des
victoires distinctes : le parcours du combattant est force <em>et</em> rapidité,
et une seule victoire alimente alors deux compteurs.</p>

## Et elle ne sépare rien

{% include graphiques/natures-femmes.svg %}

<p class="legende-figure">Part des victoires revenant à une femme, nature par
nature, avec son intervalle. Le trait vertical est la part observée toutes
natures confondues : {{ n.part_femmes }} %.</p>

{% include graphiques/natures-bout.svg %}

<p class="legende-figure">La même chose pour les victoires revenant à quelqu’un
qui ira au bout — finaliste, vainqueur, ou éliminé aux poteaux. Le repère est
{{ n.part_au_bout }} %.</p>

<div class="tableau-large">
<table data-triable>
<thead><tr>
  <th>Nature</th><th class="nombre">Victoires</th>
  <th class="nombre">Part femmes</th><th class="nombre">Intervalle</th>
  <th class="nombre">Part allés au bout</th><th class="nombre">Âge moyen</th>
</tr></thead>
<tbody>
{% for x in n.par_nature %}
<tr>
  <td>{{ x.libelle }}</td>
  <td class="nombre">{{ x.effectif }}</td>
  <td class="nombre">{{ x.femmes.probabilite }} %</td>
  <td class="nombre">{{ x.femmes.bas }} – {{ x.femmes.haut }} %</td>
  <td class="nombre">{{ x.au_bout.probabilite }} %</td>
  <td class="nombre">{{ x.age_moyen }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>

<div class="constat">
  <p><b>Aucun intervalle ne s’écarte de sa référence.</b> Ni pour le sexe, ni
  pour la distance parcourue dans le jeu. L’équilibre revient à une femme
  {{ n.par_nature[4].femmes.probabilite }} % du temps contre
  {{ n.part_femmes }} % en général, la précision {{ n.par_nature[1].femmes.probabilite }} % —
  et les deux intervalles contiennent la référence.</p>
  <p>L’âge ne trie pas davantage : de {{ n.par_nature[4].age_moyen }} ans pour
  l’équilibre à {{ n.par_nature[1].age_moyen }} pour la précision, autour d’une
  moyenne de {{ n.age_moyen }}.</p>
  <p><b>La nature d’une épreuve ne dit pas qui la gagne.</b> C’était la question
  que ce catalogue promettait de rendre posable ; elle l’est, et la réponse est
  non.</p>
</div>

<p class="note">Deux réserves, et la seconde est la plus lourde. Les natures
au-delà de la cinquième reposent sur moins de {{ n.seuil }} victoires : elles
figurent au tableau mais aucune figure ne les montre, leurs intervalles étant
trop larges pour dire quoi que ce soit. Et surtout, <strong>la nature vient du
wiki, pas d’une mesure</strong> : c’est le mot qu’un rédacteur a choisi pour
qualifier une épreuve, pas une propriété observée. Si ces étiquettes sont
approximatives, l’absence d’écart mesurée ici l’est aussi.</p>

## Quel profil gagne les épreuves

C’est ici que les données deviennent intéressantes, parce qu’elles contredisent
ce que la page sur les [métiers]({{ '/statistiques/professions/' | relative_url }})
laissait entendre.

{% include graphiques/epreuves-metier.svg %}

<p class="legende-figure">Nombre moyen d’épreuves individuelles remportées par
aventurier de chaque famille — rapporté à l’effectif, donc comparable.</p>

**{{ e.par_metier[0].libelle }}** arrive en tête avec
{{ e.par_metier[0].victoires_par_aventurier }} victoire par personne. Rien de
surprenant. Mais le fait notable est ailleurs : cette domination athlétique
**ne se convertit pas en victoires finales**. Le sport gagne les épreuves et
perd le jury.

{% include graphiques/epreuves-age.svg %}

L’âge trace une courbe nette : les **25-34 ans** remportent environ une épreuve
par personne, les **45 ans et plus** trois fois moins. C’est le seul domaine où
l’âge pèse aussi franchement — et il éclaire la page
[longévité]({{ '/statistiques/longevite/' | relative_url }}) : si les plus âgés
sortent plus tôt, c’est d’abord qu’ils gagnent moins d’immunités.

{% include graphiques/epreuves-genre.svg %}

L’écart entre femmes et hommes est le plus marqué de tout ce site :
**{{ e.par_genre[1].victoires_par_aventurier }}** épreuve par aventurier contre
**{{ e.par_genre[0].victoires_par_aventurier }}** par aventurière, sur des
effectifs pourtant identiques. Rapproché du fait que les deux gagnent la finale
aussi souvent, cela dit une chose simple : **la domination sportive n’est pas
ce qui fait gagner Koh-Lanta.**

## Gagner la première mène-t-il plus loin ?

{% assign pe = site.data.stats.premiere_epreuve %}
La première épreuve individuelle d’une saison marque le début du jeu personnel.
Celui qui la remporte tient en moyenne **{{ pe.survie_gagnants }} %** de la
saison, contre **{{ pe.survie_ensemble }} %** pour l’ensemble des aventuriers.

L’écart est réel, et il est modeste : neuf points. Surtout, il repose sur
**{{ pe.effectif }} cas seulement** — une saison ne fournit qu’une première
épreuve individuelle, et {{ pe.saisons_couvertes }} saisons en ont une de
relevée. À cette taille, l’écart resterait compatible avec le hasard : il est
donné pour ce qu’il est, une indication, pas une loi.

## Ce que cette page ne dit pas

**Cinq saisons manquent** — {{ e.saisons_sans_donnee | join: ", " }} — faute de
source donnant leurs épreuves épisode par épisode. Les totaux et les ratios
portent donc sur {{ e.saisons_couvertes }} saisons, pas sur les 34.

**Les épreuves de finale sont exclues.** Dans les dernières émissions, les
tableaux sources changent de colonnes et y listent les qualifiés plutôt que le
vainqueur : les lire comme des victoires en fabriquerait de fausses. Orientation
et poteaux ne sont donc pas comptés.

**La nature des épreuves n’est pas connue** — endurance, équilibre, précision,
aquatique. Les sources ne la donnent pas de façon exploitable. Tant qu’elle
manquera, aucune analyse par type d’épreuve ne figurera ici.

## Gagner le confort rend-il cible ? Non

{% assign cf = site.data.stats.modeles.confort_maudit %}

L’idée court depuis vingt-cinq ans : celui qui gagne le confort, qui part manger
et dormir au sec pendant que les autres ont faim, se fait écrire au conseil du
soir. Elle se teste sur le conseil du **même épisode**.

{% include graphiques/confort-maudit.svg %}

<p class="legende-figure">Part des bulletins visant un gagnant du confort du
même épisode. Le trait vertical marque la part que ces gagnants représentent
parmi les présents — c’est-à-dire ce qu’on attendrait s’ils n’étaient ni plus ni
moins visés que les autres.</p>

Sur **{{ cf.conseils }} conseils** et {{ cf.bulletins }} bulletins,
{{ cf.observe }} % visent un gagnant du confort — intervalle
{{ cf.bas }} à {{ cf.haut }} — pour {{ cf.attendu }} % attendus. p =
{{ cf.p }}. **La malédiction du confort n’existe pas.**

L’intervalle laisse encore place à un écart de trois points dans un sens ou dans
l’autre : ce qu’on peut affirmer, c’est qu’il n’y a pas d’effet marqué.

{% assign cw = site.data.stats.modeles.autour_du_feu.confort | first %}
{% assign cn = site.data.stats.modeles.autour_du_feu.confort | last %}
{% assign tcf = site.data.stats.modeles.registre | where: "cle", "confort_sortie" | first %}
<p class="note"><strong>La même question posée en sortie, et non en
bulletins.</strong> Sachant qu’on vient de gagner le confort de l’épisode, on est
éliminé le soir même dans <b>{{ cw.probabilite }} %</b> des cas
({{ cw.cas }} sur {{ cw.effectif }}), contre {{ cn.probabilite }} % pour ceux qui
n’ont rien gagné — {{ tcf.observe | round: 1 }} points, {{ tcf.ecart_types }}
écarts-types, p ajustée {{ tcf.p_ajustee }}. L’écart va cette fois dans le sens
de la légende, mais il reste <em>non concluant</em> : à {{ cw.effectif }}
présences, on ne peut pas le distinguer d’un tirage. Deux mesures de la même
idée, deux verdicts prudents et un seul enseignement — la malédiction n’est pas
établie.
<a href="{{ '/statistiques/autour-du-feu/' | relative_url }}">Sachant qui est autour du feu</a>.</p>

<p class="note">Un total de victoires mélange le niveau et le temps passé en
jeu, et une victoire au premier épisode ne vaut pas une victoire à
l’avant-dernier. <a href="{{ '/statistiques/force/' | relative_url }}">La force
réelle</a> sépare les deux par un modèle, et publie le classement avec ses
intervalles.</p>
