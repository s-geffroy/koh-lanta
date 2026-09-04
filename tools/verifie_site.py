#!/usr/bin/env python3
"""Controle les pages du site sans construire le site.

`CLAUDE.md` interdit d'installer Ruby et Jekyll sur cet hote : le rendu ne peut
donc pas etre essaye ici. Ce script verifie a la place ce qui casse SANS BRUIT
chez Jekyll -- une page qui disparait, une figure qui ne s'affiche pas, un
chiffre qui sort vide -- et qu'on ne verrait qu'en ligne, une fois publie :

  * front matter present et complet (layout, title, permalink) ;
  * chaque {% include %} pointe sur un fichier qui existe ;
  * chaque chemin site.data.x.y.z existe vraiment dans _data/ ;
  * pas de _site/ commite, liste `exclude:` intacte.

    tools/atelier python3 tools/verifie_site.py
"""
import ast
import html
import math
import os
import re
import subprocess
import sys

import yaml

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

RE_FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
RE_INCLUDE = re.compile(r"\{%\s*include\s+([^\s%]+)")
RE_DATA = re.compile(r"site\.data\.([A-Za-z0-9_.]+)")
RE_ASSIGN = re.compile(r"\{%\s*assign\s+(\w+)\s*=\s*site\.data\.([A-Za-z0-9_.]+)\s*%\}")
RE_VAR = re.compile(r"\{\{\s*([a-z_][A-Za-z0-9_]*)\.([A-Za-z0-9_.]+)")

EXCLUS_ATTENDUS = {"CLAUDE.md", "README.md", "app.yaml", "compose.yaml", "specs/"}


class Controle:
    def __init__(self):
        self.erreurs, self.avertissements = [], []

    def erreur(self, m):
        self.erreurs.append(m)

    def avertir(self, m):
        self.avertissements.append(m)


def controler_reproductibilite(c):
    """Une construction doit rendre deux fois le meme fichier.

    L'ordre d'iteration d'un ensemble de chaines change d'un processus a
    l'autre : l'empreinte des chaines est tiree au hasard au demarrage de
    Python. Boucler sur un ensemble non trie dans un script de construction
    fait donc varier _data/stats.yml sans qu'aucune donnee ait bouge, et le
    site change tout seul entre deux publications. Le defaut a deja ete paye
    une fois, sur le classement des familles de metiers.

    Le controle passe par l'arbre syntaxique et non par une expression
    reguliere : cherchee dans le texte, la faute se trouvait jusque dans les
    commentaires qui l'expliquent.
    """
    for base, _, fichiers in os.walk(os.path.join(RACINE, "tools")):
        for f in sorted(fichiers):
            if not f.endswith(".py"):
                continue
            chemin = os.path.join(base, f)
            try:
                arbre = ast.parse(open(chemin, encoding="utf-8").read(), filename=chemin)
            except SyntaxError as e:
                c.erreur(f"{os.path.relpath(chemin, RACINE)} : ne compile pas — {e}")
                continue
            for n in ast.walk(arbre):
                if isinstance(n, (ast.For, ast.comprehension)):
                    it = n.iter
                    if isinstance(it, (ast.Set, ast.SetComp)):
                        rel = os.path.relpath(chemin, RACINE)
                        c.erreur(f"{rel}:{it.lineno} : boucle sur un ensemble non "
                                 f"trie — l'ordre change d'une execution a "
                                 f"l'autre ; enfermer dans sorted()")


def controler_aleatoire(c):
    """Un tirage au hasard non graine est la meme faute que l'ensemble non trie.

    Les modeles de tools/modeles.py reposent sur des tests de permutation et
    sur des bootstraps : des dizaines de milliers de tirages. Sans graine
    fixee, _data/stats.yml change a chaque construction et le site publie des
    chiffres differents sans qu'aucune donnee ait bouge -- exactement le defaut
    deja paye sur le classement des familles de metiers.

    Le controle refuse donc trois choses : l'appel direct aux fonctions du
    module `random`, l'ancienne interface `np.random.<fonction>()`, et tout
    estimateur scikit-learn construit sans `random_state`. La graine du projet
    est GRAINE, dans tools/modeles.py ; tout generateur en derive.

    Comme le controle voisin, il passe par l'arbre syntaxique : cherchee dans
    le texte, la faute se trouverait jusque dans cette docstring.
    """
    # Ce qui est deterministe dans `random` et dans `numpy.random` : construire
    # un generateur graine, ou lire l'etat. Le reste tire.
    SANS_TIRAGE = {"Random", "SystemRandom", "default_rng", "Generator",
                   "RandomState", "seed", "PCG64", "Philox", "SFC64", "MT19937",
                   # SeedSequence ne tire rien : elle FABRIQUE une graine a
                   # partir de nombres donnes. C'est le geste meme qu'on exige.
                   "SeedSequence"}
    # Estimateurs et utilitaires scikit-learn dont le resultat depend d'un
    # tirage : ils doivent tous recevoir random_state.
    A_GRAINER = {"KMeans", "MiniBatchKMeans", "PCA", "TruncatedSVD", "NMF",
                 "RandomForestClassifier", "RandomForestRegressor",
                 "GradientBoostingClassifier", "GradientBoostingRegressor",
                 "HistGradientBoostingClassifier", "HistGradientBoostingRegressor",
                 "ExtraTreesClassifier", "ExtraTreesRegressor",
                 "LogisticRegression", "SGDClassifier", "SGDRegressor",
                 "KFold", "StratifiedKFold", "GroupKFold", "ShuffleSplit",
                 "GroupShuffleSplit", "train_test_split", "permutation_importance",
                 "TSNE", "MDS"}

    for base, _, fichiers in os.walk(os.path.join(RACINE, "tools")):
        for f in sorted(fichiers):
            if not f.endswith(".py"):
                continue
            chemin = os.path.join(base, f)
            rel = os.path.relpath(chemin, RACINE)
            try:
                arbre = ast.parse(open(chemin, encoding="utf-8").read(), filename=chemin)
            except SyntaxError:
                continue  # deja signale par controler_reproductibilite
            for n in ast.walk(arbre):
                if not isinstance(n, ast.Call):
                    continue
                fn = n.func
                nom = fn.attr if isinstance(fn, ast.Attribute) else (
                    fn.id if isinstance(fn, ast.Name) else None)
                if nom is None:
                    continue
                # random.shuffle(...) / np.random.normal(...)
                if isinstance(fn, ast.Attribute):
                    racine_appel = fn.value
                    chemin_appel = []
                    while isinstance(racine_appel, ast.Attribute):
                        chemin_appel.append(racine_appel.attr)
                        racine_appel = racine_appel.value
                    if isinstance(racine_appel, ast.Name):
                        chemin_appel.append(racine_appel.id)
                    if "random" in chemin_appel and nom not in SANS_TIRAGE:
                        c.erreur(f"{rel}:{n.lineno} : tirage au hasard non graine "
                                 f"(`{'.'.join(reversed(chemin_appel))}.{nom}`) — "
                                 f"passer par un generateur derive de GRAINE")
                        continue
                if nom in A_GRAINER:
                    mots = {k.arg for k in n.keywords if k.arg}
                    if "random_state" not in mots and not any(
                            k.arg is None for k in n.keywords):
                        c.erreur(f"{rel}:{n.lineno} : `{nom}(...)` sans "
                                 f"`random_state` — le resultat depend d'un "
                                 f"tirage, la construction cesse d'etre "
                                 f"reproductible")


def controler_navigation(c, permaliens):
    """Toute page publiee doit etre atteignable, et toute entree doit exister.

    `_data/navigation.yml` est la seule source du rail, du fil de lecture et
    des cartes du sommaire. Une page dont le permalink n'y figure pas est en
    ligne mais introuvable : aucun lien du site n'y mene, et rien ne le
    signale. L'inverse -- une entree qui pointe vers une page absente -- donne
    un lien mort.

    Le seul cas tolere est une page volontairement hors navigation ; elle doit
    alors etre listee ici, explicitement, pour que l'omission soit un choix et
    non un oubli.
    """
    HORS_NAVIGATION = {"/404.html"}

    chemin = os.path.join(RACINE, "_data", "navigation.yml")
    if not os.path.exists(chemin):
        c.erreur("_data/navigation.yml : absent")
        return
    sections = yaml.safe_load(open(chemin, encoding="utf-8")) or []
    listees = {}
    for groupe in sections:
        for entree in groupe.get("entrees") or []:
            url = entree.get("url")
            if url in listees:
                c.erreur(f"navigation.yml : « {url} » listee deux fois")
            listees[url] = entree.get("titre")

    for url in sorted(set(permaliens) - set(listees) - HORS_NAVIGATION):
        c.erreur(f"{url} : page publiee mais absente de navigation.yml — "
                 f"aucun lien du site n'y mene")
    for url in sorted(set(listees) - set(permaliens)):
        c.erreur(f"navigation.yml : « {url} » ({listees[url]}) ne correspond "
                 f"a aucune page — lien mort dans le rail")


def controler_sass(c):
    """Le piege du vieux Sass, qui a deja fait echouer une construction.

    GitHub Pages compile le SCSS avec Sass 3.7. Cette version ne connait pas
    `clamp()`, `min()` ni `max()` : elle prend leurs arguments pour de
    l'arithmetique Sass et s'arrete sur « Incompatible units: 'vw' and 'rem' ».
    Seul `calc()` est recopie sans etre evalue.

    L'echec est invisible cote visiteur -- le site continue de servir la
    version d'avant -- et ce depot n'a pas le droit de construire en local.
    D'ou ce controle : la regle est simple, autant la faire tenir par un
    script plutot que par la memoire.
    """
    chemin = os.path.join(RACINE, "assets", "css", "style.scss")
    if not os.path.exists(chemin):
        return
    texte = open(chemin, encoding="utf-8").read()
    for m in re.finditer(r"\b(clamp|min|max)\(([^;{}]*)\)\s*;", texte):
        ligne = texte[:m.start()].count("\n") + 1
        # On ote les calc() : leur contenu est justement ce qui echappe a Sass.
        reste = re.sub(r"calc\([^()]*\)", "", m.group(2))
        if re.search(r"[a-z%\d]\s*[-+*/]\s*[.\d]", reste):
            c.erreur(f"style.scss:{ligne} : arithmetique nue dans "
                     f"{m.group(1)}() — Sass 3.7 va l'evaluer et refuser de "
                     f"melanger les unites ; enfermer l'expression dans calc()")



def pages():
    for base, dossiers, fichiers in os.walk(RACINE):
        # _layouts/ et _includes/ ne sont pas des pages : ce sont les gabarits
        # QUI RENDENT les pages. Leur demander un `layout` ou un `permalink`
        # n'aurait aucun sens. Tout ce qui commence par un point non plus :
        # Jekyll ignore ces repertoires, et .claude/ est un outil de travail.
        dossiers[:] = [d for d in dossiers
                       if not d.startswith(".")
                       and d not in {"_site", "_data", "_includes", "_layouts",
                                     "specs", "tools", "atelier", "node_modules"}]
        for f in fichiers:
            if f.endswith((".md", ".html")) and f not in ("CLAUDE.md", "README.md"):
                yield os.path.join(base, f)


def charger_donnees():
    donnees = {}
    dossier = os.path.join(RACINE, "_data")
    for f in os.listdir(dossier):
        if f.endswith((".yml", ".yaml")):
            with open(os.path.join(dossier, f), encoding="utf-8") as fh:
                donnees[os.path.splitext(f)[0]] = yaml.safe_load(fh)
    return donnees


def resoudre(racine, chemin):
    """Suit un chemin pointe dans les donnees. Rend (trouve, valeur)."""
    courant = racine
    for morceau in chemin.split("."):
        if isinstance(courant, list):
            if not courant:
                return True, None          # liste vide : chemin plausible
            courant = courant[0]
        if isinstance(courant, dict):
            if morceau not in courant:
                return False, None
            courant = courant[morceau]
        elif morceau.isdigit():
            return True, None
        else:
            return False, None
    return True, courant


# Des mots dont la graphie sans accent n'existe pas en francais. Ils servent a
# reperer un texte PUBLIE ecrit en ASCII : les titres et descriptions des
# figures sont lus a voix haute par les lecteurs d'ecran, et le registre des
# tests s'affiche sur /methode/. La regle « sans accents » de ce depot vise les
# fichiers d'infrastructure, pas ce que lisent les visiteurs.
#
# La liste est volontairement courte et sans ambiguite : « observe », « compare »
# ou « elimine » sont de vrais mots francais et n'y figurent pas, meme quand ils
# tiennent la place d'un participe accentue.
MOTS_SANS_ACCENT = """
ecart ecarts ecarte ecartent age ages mediane medianes metier metiers
general generale generaux depart departs meme memes melange melanges
archetype archetypes variete varietes representee representees expres
desequilibre desequilibres modele modeles correlation correlations
annee annees negative reduit regardee epoque epoques retiree retirees
serie series precaution precautions probabilite probabilites apres
separement zero identifiee identifiees extremes edition editions regle regles
interieur composees tirees equilibre differer methode methodes neutralisee
popularite telespectateurs episode episodes etendue reunification deroulement
resultat resultats categorie categories reference references annulee annulees
elimination eliminations moitie moitiee sejour sejours defaite victoire
"""
MOTS_SUSPECTS = set(MOTS_SANS_ACCENT.split())
RE_MOT = re.compile(r"[A-Za-z][A-Za-z'-]*")
RE_BALISE_TEXTE = re.compile(r"<(title|desc)>(.*?)</\1>", re.S)


def controler_accents(c):
    """Refuse un texte publie ecrit sans ses accents.

    Deux gisements : les <title>/<desc> des figures, et le registre des tests
    publie sur /methode/. Quarante chaines du registre etaient dans ce cas --
    lues telles quelles par un lecteur d'ecran.
    """
    fautes = []

    def examiner(origine, texte):
        mots = {m.group(0).lower() for m in RE_MOT.finditer(texte or "")}
        trouves = sorted(mots & MOTS_SUSPECTS)
        if trouves:
            fautes.append((origine, trouves[:5]))

    dossier = os.path.join(RACINE, "_includes", "graphiques")
    for nom in sorted(os.listdir(dossier)) if os.path.isdir(dossier) else []:
        if not nom.endswith(".svg"):
            continue
        texte = open(os.path.join(dossier, nom), encoding="utf-8").read()
        for balise, contenu in RE_BALISE_TEXTE.findall(texte):
            examiner(f"{nom} <{balise}>", html.unescape(contenu))

    chemin = os.path.join(RACINE, "_data", "stats.yml")
    if os.path.exists(chemin):
        stats = yaml.safe_load(open(chemin, encoding="utf-8")) or {}
        for t in ((stats.get("modeles") or {}).get("registre") or []):
            for champ in ("libelle", "question", "lecture"):
                examiner(f"registre « {t.get('cle')} » / {champ}", t.get(champ))

    for origine, mots in fautes:
        c.avertir(f"{origine} : texte publie sans accents — {', '.join(mots)}")
    return len(fautes)


# Un identifiant du code -- « artisanat_btp », « age_centre_carre » -- affiche
# tel quel dans une infobulle ou une colonne de tableau. C'est la meme faute
# que l'absence d'accents : du code qui a fui dans le texte.
RE_IDENTIFIANT = re.compile(r"\b[a-zA-Z]+_[a-zA-Z_]+\b")


def controler_identifiants(c):
    """Refuse un identifiant snake_case dans un texte publie."""
    fautes = []

    def examiner(origine, texte):
        trouves = sorted({m.group(0) for m in RE_IDENTIFIANT.finditer(texte or "")})
        if trouves:
            fautes.append((origine, trouves[:4]))

    dossier = os.path.join(RACINE, "_includes", "graphiques")
    for nom in sorted(os.listdir(dossier)) if os.path.isdir(dossier) else []:
        if not nom.endswith(".svg"):
            continue
        texte = open(os.path.join(dossier, nom), encoding="utf-8").read()
        for balise, contenu in RE_BALISE_TEXTE.findall(texte):
            examiner(f"{nom} <{balise}>", html.unescape(contenu))

    chemin = os.path.join(RACINE, "_data", "stats.yml")
    if os.path.exists(chemin):
        stats = yaml.safe_load(open(chemin, encoding="utf-8")) or {}
        m = stats.get("modeles") or {}
        for t in (m.get("registre") or []):
            for champ in ("libelle", "question", "lecture"):
                examiner(f"registre « {t.get('cle')} » / {champ}", t.get(champ))
        for x in ((m.get("equilibre") or {}).get("cox") or {}).get("coefficients") or []:
            examiner("coefficients de Cox", x.get("variable"))
        for a in (m.get("casting") or {}).get("archetypes") or []:
            examiner("archetypes du casting", a.get("libelle"))

    for origine, mots in fautes:
        c.avertir(f"{origine} : identifiant du code dans un texte publie — "
                  f"{', '.join(mots)}")
    return len(fautes)


def controler_modeles_nuls(c):
    """Refuse un test dont le modele nul ne bouge pas.

    Le piege est silencieux et il a ete paye une fois : un modele nul mal
    choisi peut laisser la statistique observee RIGOUREUSEMENT inchangee a
    chaque tirage. Le test rend alors p = 1 et zero ecart-type -- ce qui se lit
    « non concluant », alors que la verite est « ce test ne teste rien ». La
    faute etait de rebattre les bulletins pour interroger un nombre de voix :
    la permutation change qui a ecrit, jamais combien de voix chacun recoit.

    Deux signatures suffisent a l'attraper : un ecart-type non fini, et une
    distribution nulle dont toute la masse tient dans une seule case.
    """
    chemin = os.path.join(RACINE, "_data", "stats.yml")
    if not os.path.exists(chemin):
        return 0
    stats = yaml.safe_load(open(chemin, encoding="utf-8")) or {}
    fautes = 0
    for t in ((stats.get("modeles") or {}).get("registre") or []):
        cle = t.get("cle")
        ecarts = t.get("ecart_types")
        if ecarts is None or not math.isfinite(float(ecarts)):
            c.erreur(f"test « {cle} » : ecart-type non fini — le modele nul ne "
                     f"produit aucune variation, le test ne teste rien")
            fautes += 1
            continue
        cases = [x for x in ((t.get("nulle") or {}).get("cases") or []) if x]
        if len(cases) == 1:
            c.erreur(f"test « {cle} » : tous les tirages tombent dans la meme "
                     f"case — modele nul sans variation")
            fautes += 1
    return fautes


def main():
    c = Controle()
    donnees = charger_donnees()

    permaliens = {}
    for chemin in sorted(pages()):
        rel = os.path.relpath(chemin, RACINE)
        texte = open(chemin, encoding="utf-8").read()

        m = RE_FRONT.match(texte)
        if not m:
            c.erreur(f"{rel} : pas de front matter — Jekyll ne rendra pas cette page")
            continue
        try:
            entete = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            c.erreur(f"{rel} : front matter illisible — {e}")
            continue

        if not entete.get("layout"):
            c.erreur(f"{rel} : `layout` manquant")
        if not entete.get("title"):
            c.avertir(f"{rel} : `title` manquant")
        lien = entete.get("permalink")
        if lien:
            if not lien.startswith("/") or not lien.endswith("/"):
                c.avertir(f"{rel} : permalink « {lien} » sans barre oblique initiale ou finale")
            if lien in permaliens:
                c.erreur(f"{rel} : permalink « {lien} » deja pris par {permaliens[lien]}")
            permaliens[lien] = rel
        elif rel == "index.md":
            # L'accueil n'a pas de permalink : son URL est la racine. Il figure
            # bien dans navigation.yml, sous « / ».
            permaliens["/"] = rel
        elif rel != "404.html":
            c.avertir(f"{rel} : pas de permalink explicite, l'URL suivra le chemin du fichier")

        corps = texte[m.end():]

        for inc in RE_INCLUDE.findall(corps):
            if not os.path.exists(os.path.join(RACINE, "_includes", inc)):
                c.erreur(f"{rel} : inclusion introuvable — _includes/{inc}")

        # chemins ecrits en toutes lettres
        for parcours in RE_DATA.findall(corps):
            ok, _ = resoudre(donnees, parcours)
            if not ok:
                c.erreur(f"{rel} : site.data.{parcours} n'existe pas dans _data/")

        # chemins passant par un {% assign %}
        alias = {nom: cible for nom, cible in RE_ASSIGN.findall(corps)}
        for nom, suite in RE_VAR.findall(corps):
            if nom not in alias:
                continue
            parcours = f"{alias[nom]}.{suite.rstrip('.')}"
            parcours = re.sub(r"\.(first|last|size)$", "", parcours)
            ok, _ = resoudre(donnees, parcours)
            if not ok:
                c.erreur(f"{rel} : {nom}.{suite} → site.data.{parcours} n'existe pas")

    # configuration
    config = yaml.safe_load(open(os.path.join(RACINE, "_config.yml"), encoding="utf-8"))
    exclus = set(config.get("exclude") or [])
    for attendu in EXCLUS_ATTENDUS:
        if attendu not in exclus:
            c.erreur(f"_config.yml : « {attendu} » a disparu de `exclude:` — "
                     f"ce fichier serait publie en ligne")
    if config.get("url", "").find("CHANGEME") != -1:
        c.avertir("_config.yml : `url` vaut encore CHANGEME — a renseigner avant publication")

    # --- secrets : trois verrous, verifies a chaque passage
    dossier_secrets = os.path.join(RACINE, ".secrets")
    if os.path.isdir(dossier_secrets):
        if ".secrets/" not in exclus:
            c.erreur("_config.yml : .secrets/ absent de `exclude:` — "
                     "le jeton serait publie sur le site")
        gitignore = os.path.join(RACINE, ".gitignore")
        contenu = open(gitignore, encoding="utf-8").read() if os.path.exists(gitignore) else ""
        if ".secrets/" not in contenu:
            c.erreur(".gitignore : .secrets/ absent — le jeton entrerait dans "
                     "l'historique Git, qui est definitif")
        try:
            suivis = subprocess.run(["git", "ls-files", ".secrets"], cwd=RACINE,
                                    capture_output=True, text=True).stdout.strip()
        except FileNotFoundError:
            suivis = ""
            c.avertir("git absent : impossible de verifier qu'aucun secret "
                      "n'est suivi par l'index")
        if suivis:
            c.erreur("des fichiers de .secrets/ sont SUIVIS PAR GIT : "
                     + suivis.replace("\n", ", ")
                     + " — a retirer de l'index et a considerer comme compromis")
        for nom in os.listdir(dossier_secrets):
            chemin = os.path.join(dossier_secrets, nom)
            if os.path.isfile(chemin) and os.stat(chemin).st_mode & 0o077:
                c.erreur(f".secrets/{nom} est lisible par d'autres — "
                         f"chmod 600 .secrets/{nom}")

    controler_navigation(c, permaliens)
    controler_sass(c)
    controler_reproductibilite(c)
    controler_aleatoire(c)
    controler_accents(c)
    controler_identifiants(c)
    controler_modeles_nuls(c)

    if os.path.isdir(os.path.join(RACINE, "_site")):
        c.avertir("_site/ existe : verifier qu'il est bien ignore par Git")

    figures = os.path.join(RACINE, "_includes", "graphiques")
    nb = len(os.listdir(figures)) if os.path.isdir(figures) else 0
    print(f"pages controlees : {len(permaliens) + 1}")
    print(f"figures          : {nb}")
    print(f"jeux de donnees  : {', '.join(sorted(donnees))}")

    if c.avertissements:
        print(f"\n{len(c.avertissements)} avertissement(s) :")
        for a in c.avertissements:
            print(f"  ~ {a}")
    if c.erreurs:
        print(f"\n{len(c.erreurs)} ERREUR(S) :")
        for e in c.erreurs:
            print(f"  ! {e}")
        return 1
    print("\nOK  rien qui casserait le rendu")
    return 0


if __name__ == "__main__":
    sys.exit(main())
