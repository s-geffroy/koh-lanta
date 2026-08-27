# koh-lanta

Site **Jekyll** publie par **GitHub Pages**. **Rien n'est heberge ici.**

## Ce que ce depot est

Un espace de travail versionne, isole des autres applications du VPS, avec son
propre Claude Code authentifie. Le site, lui, est construit par GitHub a chaque
`git push` et servi depuis les serveurs de GitHub.

`sudo appctl validate` repondra « 0 service », et c'est normal : `app.yaml` et
`compose.yaml` declarent explicitement qu'il n'y a rien a demarrer.

Si quelqu'un demande de « deployer le site ici », c'est qu'il s'est trompe de
template : `static` est celui d'un site servi par ce VPS.

## Prerequis, a trancher AVANT de creer le depot distant

GitHub Pages est disponible :

- sur un depot **public**, avec un compte **GitHub Free** ;
- sur un depot **prive**, seulement a partir de **GitHub Pro** (payant).

Et dans les deux cas, **le site publie est public**. Un depot prive protege les
sources, pas le site. Restreindre l'acces au site lui-meme demande une
organisation sur GitHub Enterprise Cloud.

C'est a decider avant l'etape « Rattacher un depot GitHub prive ? » de
`workon new` : apres, le depot existe.

## Activer Pages

1. Creer le depot sur GitHub, y pousser ce projet.
2. Depot > **Settings** > **Pages**.
3. **Source** : *Deploy from a branch*.
4. **Branch** : `main`, dossier `/ (root)`.

Aucun workflow GitHub Actions n'est necessaire : le constructeur Jekyll natif
fait le travail.

## Publier

```bash
git add -A
git commit -m "..."
git push
```

C'est tout. La construction prend une a deux minutes ; son deroulement et ses
echecs sont visibles dans l'onglet **Actions** du depot, meme sans workflow --
le constructeur natif s'y affiche.

## Organisation

```
_config.yml        reglages du site (titre, url, baseurl, greffons, exclusions)
index.md           page d'accueil
404.html           page servie sur une adresse inconnue
_posts/            articles : AAAA-MM-JJ-titre.md
_drafts/           brouillons : jamais publies (a creer au besoin)
assets/            images, fichiers joints
specs/             specifications du projet, exclues du site
```

Un article porte un front matter :

```markdown
---
layout: post
title: "Titre de l'article"
date: 2026-08-25
categories: [notes]
---
```

## Domaine personnalise

Saisir le domaine dans **Settings > Pages** : GitHub cree lui-meme le commit du
fichier `CNAME`. Cote DNS, chez le registrar :

- apex (`exemple.fr`) : quatre enregistrements **A** vers `185.199.108.153`,
  `185.199.109.153`, `185.199.110.153`, `185.199.111.153` ;
- sous-domaine (`www`) : un **CNAME** vers `<utilisateur>.github.io`.

Puis cocher **Enforce HTTPS** -- disponible jusqu'a 24 h apres la
configuration, le temps que le certificat soit emis.

**Rien de tout cela ne passe par ce VPS** : ni Traefik, ni `app.yaml`, ni
`app-exposure.py`, ni la zone publique de `/opt/infra/.env`.

Ne pas oublier de vider `baseurl` dans `_config.yml` en meme temps.

## Ce que le constructeur natif ne sait pas faire

- Il tourne en **safe mode** : les greffons deposes dans `_plugins/` sont
  **ignores**, sans erreur ni avertissement.
- Seule la liste blanche de <https://pages.github.com/versions.json> est
  chargeable -- `jekyll-feed`, `jekyll-seo-tag`, `jekyll-sitemap`,
  `jekyll-redirect-from`, `jekyll-remote-theme` et quelques autres.
- La version de Jekyll est **3.10**, pas Jekyll 4. Les recettes du web qui
  supposent Jekyll 4 ne marchent pas ici.
- Pour changer de theme sans sortir du constructeur natif : `remote_theme:`,
  qui est dans la liste blanche.

## Commandes

`sudo appctl validate` repond « 0 service » ; `build`, `up`, `down`, `rebuild`
et `restart` sortent en 0 sans rien faire.

## L'atelier de travail

Tout ce qui fabrique des donnees ou des graphiques tourne dans un conteneur
jetable, declare dans `compose.yaml` sous le profil `cli`. Rien ne s'installe
sur l'hote.

    tools/atelier python3 tools/verifie.py           # coherence des donnees
    tools/atelier python3 tools/verifie_site.py      # front matter, inclusions
    tools/atelier python3 tools/build_stats.py       # _data/stats.yml
    tools/atelier python3 tools/build_graphiques.py  # _includes/graphiques/

Il ne construit PAS le site : GitHub Pages s'en charge. Consequence assumee, le
rendu ne peut pas etre essaye ici ; il se decouvre en ligne.

**Apres toute modification de `atelier/Dockerfile`, incrementer l'etiquette
`image:` dans `compose.yaml`.** `appctl build` et `appctl rebuild` ne voient pas
les services du profil `cli` : sans changement d'etiquette, l'image resterait
figee a sa premiere construction.

## Publier

Pousser suffit a mettre a jour le site. Mais Pages doit avoir ete ACTIVE une
fois sur le depot, ce qui passe par l'API GitHub -- la cle SSH du depot est une
cle de deploiement, elle autorise le push et rien d'autre.

    tools/atelier python3 tools/publier.py             # etat du site
    tools/atelier python3 tools/publier.py --activer   # activer Pages
    tools/atelier python3 tools/publier.py --attendre  # suivre la construction

### Le jeton

L'outil lit `.secrets/github.token`. Ce fichier n'est PAS dans Git.

1. Sur GitHub : **Settings > Developer settings > Personal access tokens >
   Fine-grained tokens > Generate new token**.
2. **Repository access** : *Only select repositories* -> `s-geffroy/koh-lanta`.
   Rien d'autre.
3. **Repository permissions** :
   - *Pages* : **Read and write**
   - *Administration* : **Read and write** (exigee pour CREER le site Pages)
4. Deposer le jeton sur le VPS, **depuis votre propre terminal** et non par un
   collage dans une conversation :

       install -m 600 /dev/null /srv/apps/koh-lanta/.secrets/github.token
       cat > /srv/apps/koh-lanta/.secrets/github.token
       # coller le jeton, puis Entree et Ctrl-D

Un jeton colle dans une conversation ou dans un journal doit etre considere
comme compromis, et revoque.

### Les trois verrous sur les secrets

`.secrets/` est sous le repertoire du projet parce qu'`appctl` refuse tout
montage exterieur au projet -- et le depot y est deja monte sur `/depot`. Trois
verrous evitent qu'un jeton parte en ligne :

1. `.gitignore` contient `.secrets/` ;
2. `_config.yml` l'exclut de la construction Jekyll ;
3. `tools/verifie_site.py` **echoue** si l'un des deux manque, si un fichier de
   `.secrets/` est suivi par Git, ou si ses permissions sont trop larges.

Un depot Pages est public et son historique est definitif.
