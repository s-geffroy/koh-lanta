---
name: seo-koh-lanta
description: Les conventions de referencement du site Koh-Lanta en chiffres - gabarits de titre et de description, regle du H1, maillage des noms propres, donnees structurees page par page, questions frequentes, identifiants et ligatures, poids des polices, controle avant push. A lire avant de toucher un front matter, un gabarit de fiche, un identifiant, _config.yml ou le <head>.
---

# Referencement de « Koh-Lanta en chiffres »

Ce fichier n'est pas publie : `.claude/` est dans `exclude:` de `_config.yml`.

## La cible, et ce qu'elle n'est pas

Le site ne passera pas devant TF1, MYTF1, Wikipedia et Fandom sur la requete
« koh-lanta » seule. Ce n'est pas la cible et ce n'est pas un echec.

Ce qui est gagnable, et ou le site a le contenu le plus chiffre du web
francophone : le nom d'un aventurier, le nom d'une saison, « statistiques koh
lanta », « classement aventuriers koh lanta », « qui a gagne koh lanta X ».
**Toute decision se juge la-dessus**, pas sur la requete generique.

## La regle qui rend tout le reste possible

Sur les 565 fiches, **le H1 ne vient PAS de `page.title`** :

| Gabarit | H1 rendu | D'ou vient `page.title` |
|---|---|---|
| `fiche-aventurier` | `{{ a.nom }}` (`_data/fiches.yml`) | lu par jekyll-seo-tag SEUL |
| `fiche-saison` | `{{ s.titre }}` (`_data/fiches.yml`) | lu par jekyll-seo-tag SEUL |
| `page` | `{{ page.title }}` | **s'affiche** — tout changement se voit |
| `home` | `.accueil-titre`, ecrit dans `index.md` | lu par le greffon seul |

Consequence : sur une fiche, `title:` s'enrichit librement, rien ne bouge a
l'ecran. Sur une page en `layout: page`, un titre ne se retouche que s'il
reste juste et lisible comme H1.

## Les deux longueurs

`jekyll-seo-tag` colle **`  | Koh-Lanta en chiffres `** (24 caracteres) a tout
titre. C'est ce qu'on oublie en relisant un front matter, ou le titre parait
court.

- titre rendu, suffixe compris : **62 caracteres** — donc `title:` <= 38 ;
- description : **155 caracteres** visees, 160 refuses.

C'est aussi pourquoi les titres de fiche **ne repetent pas « Koh-Lanta »** :
le suffixe le porte deja. Les descriptions, elles, le portent — c'est le texte
que le moteur affiche.

## Les gabarits

Fabriques en Python, jamais a la main : `titre_seo_aventurier`,
`description_seo_aventurier`, `titre_seo_saison`, `description_seo_saison`
dans `tools/build_fiches.py`.

| | Forme |
|---|---|
| Fiche, une saison | `Adrien Torrin — Palawan (2007)` |
| Fiche, plusieurs | `Claude Dartois — 4 saisons jouees` |
| Saison | `Palawan (2007) — saison 7` |
| Description fiche | `Nom, Koh-Lanta Saison (annee) : <verbe> le Ne jour, Ne sur N, N epreuves gagnees. Ne sur 531 au classement des aventuriers.` |
| Description saison | `Koh-Lanta Titre, saison N diffusee en AAAA (pays) : N aventuriers, N jours, N conseils, N bulletins. Victoire de X.` |

Trois pieges deja payes :

1. **Le sort se dit au present, sans accord** (`VERBE_SORT`) : « sort au
   conseil », pas « Elimine au conseil ». Les libelles de `LIBELLE_SORT` sont
   au masculin ; les reprendre imposerait d'accorder 531 fiches.
2. **`avec_marque()` avant tout prefixe** : la saison 1 s'appelle « Les
   Aventuriers de Koh-Lanta », et la description commencait par « Koh-Lanta
   Les Aventuriers de Koh-Lanta ».
3. **On ne tronque pas, on retombe** : `premier_qui_tient()` choisit une
   formule plus pauvre mais entiere plutot que « Clarisse Cresseveur — Les
   Reliqu ».

## Le maillage

Tout nom d'aventurier rendu dans un tableau **doit** etre un lien vers sa
fiche :

```liquid
<a href="{{ '/aventuriers/' | append: l.id | append: '/' | relative_url }}">{{ l.nom }}</a>
```

L'identifiant est toujours disponible : `poser_les_identifiants()` dans
`tools/build_stats.py` parcourt l'arbre fini et pose `id` a cote de tout nom
d'aventurier, dans les vingt-trois listes qui n'en avaient pas. Un homonyme
n'est pas resolu — mieux vaut un nom sans lien qu'un lien vers la mauvaise
fiche. Si un `id` manque, la reparation est dans cette fonction, pas dans le
gabarit : **aucun calcul en Liquid**, le site ne peut pas etre essaye avant le
push.

## Les photos : jamais sans leur credit

Les portraits viennent de **Wikimedia Commons**, jamais de la presse, et
uniquement sous licence libre (domaine public, CC0, CC BY, CC BY-SA). La liste
`LICENCES_LIBRES` de `tools/extraction/wikidata.py` est FERMEE : une licence
inconnue n'est pas presumee libre.

**L'auteur et la licence s'affichent SOUS la photo**, sur la fiche. Ce n'est
pas negociable et ce n'est pas allegeable : CC BY et CC BY-SA exigent
l'attribution, et une photo republiee sans son auteur ne l'est pas legalement.
`controler_portraits()` refuse une photo sans credit complet, un fichier absent
du depot, et un gabarit qui n'afficherait plus `portrait.auteur`.

**Chaque portrait porte `largeur` et `hauteur`, et le gabarit les pose en
`width`/`height`.** Sans eux la fiche s'affiche puis SAUTE : credit, comptes
et chiffres descendent d'un coup quand l'image se pose. Cela ne se corrige pas
en CSS -- les quatorze portraits vont de 500x313 a 500x794, et les recadrer a
un rapport commun couperait des visages. Les dimensions sont MESUREES sur le
fichier par Pillow, jamais lues dans la reponse de Commons : l'API renvoie la
largeur DEMANDEE (`iiurlwidth=480`) quand elle sert un fichier de 500.
`controler_portraits()` confronte les deux et refuse l'ecart.

**Le nom ne prouve pas l'identite.** Trente et un aventuriers ont un homonyme
exact sur la Wikipedia francophone -- parmi eux une danseuse ukrainienne et un
avocat. Un element Wikidata n'est retenu que s'il est un etre humain ET que le
jeu est ecrit dans ses declarations ou dans le texte de l'article. Sans preuve,
pas de photo : une fiche nue vaut mieux qu'une fiche qui montre quelqu'un
d'autre. Meme regle pour les comptes de reseaux sociaux, tires des memes
elements.

## Les questions frequentes

Sur les deux sortes de fiche, ecrites en Python et VISIBLES sur la page :
six par aventurier (`faq_aventurier`), cinq a sept par saison
(`faq_saison`, 231 en tout). Ne pas en attendre l'affichage enrichi : depuis
2023 Google le reserve aux sites gouvernementaux et de sante. C'est le texte
de la page qui travaille.

**Un titre de saison ne se met JAMAIS en sujet d'un verbe.** « Combien de
jours a dure Les Aventuriers de Koh-Lanta ? » demanderait un accord par
titre. Il reste complement, derriere `a_designation()` ou `de_designation()`
qui contractent l'article : « aux Aventuriers de Koh-Lanta », « des
Aventuriers de Koh-Lanta ». Une seule saison sur 34 declenche la contraction
-- la premiere, la seule dont le titre porte deja la marque et n'est donc pas
prefixe par `avec_marque()`.

**On ne qualifie pas ce que les donnees ne disent pas.** Trois saisons
portent deux noms au champ `vainqueurs` ; la reponse les nomme tous les deux,
comme la fiche. « Ex aequo » serait une these : sur Bocas del Toro les deux
noms n'ont pas le meme classement. « 1 vainqueur » n'est pas mieux -- on ne
compte pas ce qu'on nomme.

Cinq pieges de redaction, tous payes en ligne :

1. `_edition()` passe par l'annee pour ne pas ecrire « lors de Les
   Aventuriers ».
2. `de_()` elide devant voyelle, sinon 138 fiches publiaient « le metier de
   Abdellah ».
3. **`.capitalize()` minuscule les noms propres.** Ne jamais l'employer sur
   une phrase qui en contient : 43 fiches ont publie « En 2007 (palawan) »,
   « (viêtnam) », « (la revanche des 4 terres) ». `affichable()` existe et ne
   fait que la premiere lettre.
4. **`ordinal()` ne s'accorde pas.** Seul le rang 1 s'accorde en francais, et
   15 fiches publiaient « 1er sur 18 [...] ou ELLE gagne la saison ».
   `ordinal_rang(n, genre)` pour un RANG ; `ordinal()` reste bon pour un jour,
   dont le mot accorde est masculin.
5. **Le titre d'une saison n'est jamais sujet** (voir ci-dessus).

Deux controles tiennent les deux fautes de casse et d'accord, et ils cherchent
le RESULTAT, pas l'appel fautif : `controler_titres_minuscules()` confronte la
prose publiee aux titres de `_data/saisons.yml`, `controler_accord_rang()`
confronte l'ordinal au genre de la fiche. Le premier a ete mis au point par
ses faux positifs : cherche dans le texte brut de `fiches.yml`, il signalait
les 34 slugs -- « koh-lanta-palawan » est une adresse, pas une phrase. D'ou
`CLES_PROSE`.

## Les trois egalites du jury

Trois saisons ont deux vainqueurs : Bocas del Toro (2003), Palawan (2007) et
Le Totem maudit (2022). **Ce ne sont pas des doublons de donnees**, et les
sources sont nettes : la page Fandom de Bocas del Toro raconte le conseil
final et enumere les trois occurrences ; Wikipedia donne « winner = X & Y »
avec le partage de la cagnotte. `/statistiques/vainqueurs/` l'annonce depuis
toujours -- « 29 vainqueurs, plus que de saisons ».

Le decompte des voix ne s'ecrit PAS a la main : `fiches_des_saisons` le lit
dans les conseils de type `jury`, un par finaliste, et ne pose `egalite_jury`
que si les vainqueurs ont le MEME nombre de voix.

**Un vainqueur termine premier, et c'est une regle de la chaine d'extraction**
(`vainqueur_premier` dans `fusionner.py`), pas un constat de source :
l'infobox Fandom ne sait pas ecrire une egalite et rangeait les deux gagnantes
de Bocas del Toro 1 et 2 -- la fiche publiait « 2e sur 18 [...] ou elle gagne
la saison ». La regle est posee APRES `completer_depuis_pages` : avant, elle
s'appliquait aux 36 vainqueurs et effacait la provenance des 29 que le wiki
atteste correctement.

## Les nombres se mettent en forme en Python

Liquid n'a pas de filtre de milliers, et ce depot ne calcule pas dans un
gabarit. Les audiences sortaient donc brutes : « 8127000 telespectateurs »,
« 39.5 % ». Les champs `_texte` (`audience_moyenne_texte`,
`audience_pdm_texte`...) sont fabriques par `milliers()` et `decimal()` dans
`tools/build_fiches.py` ; le gabarit n'affiche plus que ceux-la. L'espace est
insecable, la virgule decimale est francaise, et un entier perd son zero
-- « 37 ans », pas « 37,0 ans ».

## Les donnees structurees, page par page

`_includes/donnees-structurees.html`, lu dans le `<head>` de toutes les pages.
Acces par cle uniquement, jamais de calcul : le site ne peut pas etre essaye
avant le push.

| Page | Ce qui est pose EN PLUS de jekyll-seo-tag |
|---|---|
| Fiche aventurier | `ProfilePage` + `Person`, fil d'Ariane, `FAQPage` |
| Fiche saison | `TVSeason`, fil d'Ariane, `FAQPage` |
| Page d'epreuve | fil d'Ariane |
| Les 27 pages d'analyse | fil d'Ariane, sur test de `page.url` |
| Accueil | **rien** : le greffon y emet deja `WebSite` et non `WebPage` |

Le test des pages d'analyse porte sur `page.url` et non sur une cle de front
matter : rien a poser sur 27 fichiers, et rien a regler dans `defaults:`, dont
la portee `path:` se compare par PREFIXE -- « statistiques » y attrape aussi
`statistiques.md`. Cette page-la s'exclut explicitement : son fil se reduirait
a « Accueil > Les statistiques », dont le dernier maillon serait elle-meme.

## Les pages d'epreuve

Un seuil, pas un catalogue : `tools/build_epreuves.py` ne publie que les
epreuves ayant au moins cinq apparitions ET quatre vainqueurs nommes -- 19 sur
53. Le raccord entre le nom cite par le wiki et l'epreuve relevee ne tient que
sur 14,3 % des cas ; publier les 53 donnerait des coquilles vides, ce qu'un
moteur compte contre le site ENTIER. Si le seuil bouge, la page /epreuves/ dit
le nombre et sa raison : la mettre a jour aussi.

## Les identifiants : la ligature qu'on perd

`unicodedata.normalize("NFKD", ...)` suivi d'un filtre ASCII decompose « e »
accentue en « e » plus un accent, et garde le « e ». Une LIGATURE n'est pas
une lettre accentuee : NFKD la laisse telle quelle, et le filtre l'efface.
D'ou /aventuriers/frank-leb-uf/, un nom qui avalait sa propre lettre.

La table `LIGATURES` est posee aux DEUX endroits qui fabriquent un
identifiant, et il faut penser aux deux : `slug()` dans
`tools/extraction/parse_fandom.py`, d'ou viennent les ids des personnes, et
`identifiant()` dans `tools/build_fiches.py`, qui nomme les epreuves et les
saisons.

**Un identifiant se retrouve dans des NOMS DE FICHIER.** Le changer en
demande trois renommages, et le premier s'est signale a l'execution : le
wikitexte de la page individuelle
(`specs/sources/personnes/<id>.fandom.wiki`) n'etant plus trouve, la
regeneration a rendu une fiche amputee de sa localisation, de son parcours et
de son classement. Les deux autres sont le portrait Commons
(`assets/portraits/<id>.jpg`) et la vignette de partage
(`assets/partage/aventuriers/<id>.png`). Apres renommage, `fusionner.py` ne
doit plus changer qu'UNE ligne par fichier : verifier le diff, c'est la seule
preuve.

L'ancienne adresse reste vivante par `ANCIENNES_ADRESSES` dans
`build_fiches.py`, qui ecrit le `redirect_from` de la fiche.

## Les noms que le wiki a corriges

Un lien de tableau de saison, `[[Lola Besse|Lola]]`, ne prouve pas que la page
porte ce titre : ce peut etre une REDIRECTION. Onze noms du site en sont une,
compte sur les 531 :

Dix sont adoptees, une seule est refusee :

| Le site publiait | Titre canonique Fandom | |
|---|---|---|
| Carinne Fossey Elka | Carinne Elka-Dioza | adopte |
| Charlene Hoffness | Charlene Hoffsess | adopte |
| Fouzi de la Fuente | Fouzi Ould Bouamama | adopte |
| Francois-Xavier Arguillere | Francois-Xavier Renou | adopte |
| Julie Navarro-Camilleri | Julie Navarro | adopte |
| Lola Besse | Lola Labesse | adopte |
| Marie Boyer | Marie Besnier | adopte |
| Marta Morino | Marta Molino | adopte |
| Matteo Real | Mattéo Real | adopte, **sans changer d'adresse** |
| Nicolas Leoni | Nicolas Roy | adopte |
| Philippe Bizet | Phil Bizet | **REFUSE** |

« Matteo » et « Mattéo » donnent tous deux l'identifiant `matteo-real` : la
translitteration efface l'accent. Seul le nom affiche bouge, aucune
redirection n'est necessaire.

**`NOMS_CANONIQUES` dans `fusionner.py` est une TABLE, pas une regle, et il
faut que cela reste ainsi.** Le titre canonique n'est pas toujours le meilleur
nom a publier : « Philippe Bizet » redirige vers « Phil Bizet » -- meme
personne, mais un diminutif ne remplace pas un prenom dans un H1. Adopter
mecaniquement le titre canonique rebaptiserait onze fiches, dont celle-la.

Ne JAMAIS deduire le titre canonique de `_categories.json` en rattachant par
le prenom : l'essai proposait « Philippe Bizet -> Philippe Duron », deux
personnes differentes, et Philippe Duron est 7e au classement. Une
redirection se verifie a la source :

    action=query&titles=<nom>&redirects=1   sur kohlanta.fandom.com/fr/api.php

Changer un nom change l'identifiant, donc l'adresse : voir la section
precedente pour les trois fichiers qui suivent, et `ANCIENNES_ADRESSES` pour
garder l'ancienne vivante. **La vignette de partage porte le nom DESSINE** :
la renommer ne suffit pas, il faut relancer `build_partage.py --tout`.

### `nom_source` : la forme que la source ecrit

**Renommer quelqu'un casse le rattachement de ses bulletins si on ne garde pas
l'ancienne forme.** Les tableaux de VOTES n'ont pas suivi le renommage du
wiki : leur libelle sort de l'extraction en « Julie Navarro-Camilleri Julie »
-- nom complet puis prenom, colles -- et `resoudre()` cherche le plus long
prefixe qui soit un nom complet connu. Publier « Julie Navarro » lui retirait
la forme par laquelle ses bulletins se reconnaissaient.

`nom_source` garde donc l'ancienne forme a cote du nom publie, et les DEUX
index qui rattachent par nom complet la connaissent : `construire_conseils` et
`finale`. Il figure dans `ORDRE`, sans quoi il ne sort pas de fusionner.

**Le controle qui valide un renommage : le classement ne doit bouger d'AUCUN
rang.** Un seul bulletin perdu -- celui de Julie a Fidji -- a deplace 380
scores et 303 rangs, jusqu'a 55 places. Les facettes sont CENTREES sur la
population : un bulletin de moins deplace la moyenne et l'ecart-type, et le
score de tout le monde glisse a la troisieme decimale. Rien n'echoue, nulle
part. Si un renommage fait bouger un rang, c'est qu'un rattachement est
tombe.

## Les adresses de saison

`/saisons/koh-lanta-palawan/`, et non `/saisons/s07/`. L'ancienne reste vivante
par `redirect_from` (greffon `jekyll-redirect-from`, liste blanche). Aucun
gabarit ne construit ce lien a la main : tout passe par
`_includes/lien-saison.html`, qui traduit l'identifiant par
`_data/saisons_urls.yml`.

## Ce qu'on ne fait pas

- **Aucun permalien ne change sans accord explicite ET sans `redirect_from`.**
  Les saisons ont ete deplacees le 8 septembre 2026, l'ancienne adresse servie
  par le greffon. Sans lui, tout lien pose ailleurs tombait en silence.
- **Aucun fichier `CNAME` ecrit a la main.** C'est GitHub qui le commite,
  depuis Settings > Pages, une fois le DNS verifie. Le poser avant fait servir
  une erreur a la place du site.
- **Aucun `_plugins/`, aucun greffon hors liste blanche, aucun workflow
  Actions.**

## Le domaine, quand il arrivera

Un seul commit, **apres** que GitHub a valide le domaine :

```yaml
url: "https://<domaine>"
baseurl: ""
```

Tant que le site vit sous `s-geffroy.github.io/koh-lanta/`, son `robots.txt`
est servi sous `/koh-lanta/robots.txt` et **aucun robot ne le lit** : ils ne
lisent que la racine du domaine, qui repond 404. Le sitemap ne se declare donc
que par Search Console, a la main.

## Les polices sont sur le chemin critique

La feuille Google Fonts du `<head>` est bloquante et vient d'un autre
domaine : tout ce qu'elle traine retarde le premier rendu de CHAQUE page.
Avant d'ajouter une graisse, un style ou un axe, verifier qu'il sert
reellement -- et mesurer, le sous-ensemble `latin` est le seul qu'une page en
francais telecharge.

Fraunces demandait l'axe SOFT en plage `0..100` alors que la feuille du site
le fixe a 0 partout : 121 Ko au lieu de 67. Il est desormais EPINGLE a 0 dans
l'URL, et Google sert le meme fichier octet pour octet qu'en retirant l'axe.
Les autres demandes servent, verifiees une par une : opsz varie de 40 a 144,
WONK bascule de 0 a 1, les quatre graisses sont employees, et l'italique de
Public Sans porte les `<em>` et `<i>`.

## Le controle, avant chaque push

    tools/atelier python3 tools/verifie_site.py

`controler_seo()` refuse une description manquante, une description partagee
par deux pages, un titre ou une description trop longs.
`controler_donnees_structurees()` relit `_includes/donnees-structurees.html`
comme du JSON, clauses posees ET clauses absentes — un bloc `ld+json` casse ne
fait echouer ni la construction ni l'affichage : le moteur le jette en
silence.
