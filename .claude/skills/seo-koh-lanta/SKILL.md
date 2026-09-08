---
name: seo-koh-lanta
description: Les conventions de referencement du site Koh-Lanta en chiffres - gabarits de titre et de description, regle du H1, maillage des noms propres, controle avant push. A lire avant de toucher un front matter, un gabarit de fiche, _config.yml ou le <head>.
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

**Le nom ne prouve pas l'identite.** Trente et un aventuriers ont un homonyme
exact sur la Wikipedia francophone -- parmi eux une danseuse ukrainienne et un
avocat. Un element Wikidata n'est retenu que s'il est un etre humain ET que le
jeu est ecrit dans ses declarations ou dans le texte de l'article. Sans preuve,
pas de photo : une fiche nue vaut mieux qu'une fiche qui montre quelqu'un
d'autre. Meme regle pour les comptes de reseaux sociaux, tires des memes
elements.

## Les questions frequentes

Six par fiche, ecrites en Python (`faq_aventurier`), VISIBLES sur la page. Ne
pas en attendre l'affichage enrichi : depuis 2023 Google le reserve aux sites
gouvernementaux et de sante. C'est le texte de la page qui travaille.

Trois pieges de redaction, deja payes : `_edition()` passe par l'annee pour ne
pas ecrire « lors de Les Aventuriers » ; `de_()` elide devant voyelle, sinon
138 fiches publiaient « le metier de Abdellah » ; et `.capitalize()` minuscule
les noms propres -- ne jamais l'employer sur une phrase qui en contient.

## Les pages d'epreuve

Un seuil, pas un catalogue : `tools/build_epreuves.py` ne publie que les
epreuves ayant au moins cinq apparitions ET quatre vainqueurs nommes -- 19 sur
53. Le raccord entre le nom cite par le wiki et l'epreuve relevee ne tient que
sur 14,3 % des cas ; publier les 53 donnerait des coquilles vides, ce qu'un
moteur compte contre le site ENTIER. Si le seuil bouge, la page /epreuves/ dit
le nombre et sa raison : la mettre a jour aussi.

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

## Le controle, avant chaque push

    tools/atelier python3 tools/verifie_site.py

`controler_seo()` refuse une description manquante, une description partagee
par deux pages, un titre ou une description trop longs.
`controler_donnees_structurees()` relit `_includes/donnees-structurees.html`
comme du JSON, clauses posees ET clauses absentes — un bloc `ld+json` casse ne
fait echouer ni la construction ni l'affichage : le moteur le jette en
silence.
