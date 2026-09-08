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

## Ce qu'on ne fait pas

- **Aucun permalien ne change.** `/saisons/s01/` reste opaque : le titre et le
  H1 portent le vrai nom, et deplacer une URL casse des liens ailleurs.
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
