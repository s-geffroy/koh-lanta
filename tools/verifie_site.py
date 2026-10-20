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
import collections
import html
import json
import math
import os
import re
import subprocess
import sys

import yaml
import donnees

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

RE_FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
RE_INCLUDE = re.compile(r"\{%\s*include\s+([^\s%]+)")
RE_DATA = re.compile(r"site\.data\.([A-Za-z0-9_.]+)")
RE_ASSIGN = re.compile(r"\{%\s*assign\s+(\w+)\s*=\s*site\.data\.([A-Za-z0-9_.]+)\s*%\}")
RE_VAR = re.compile(r"\{\{\s*([a-z_][A-Za-z0-9_]*)\.([A-Za-z0-9_.]+)")
RE_COMMENTAIRE = re.compile(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}",
                            re.S)


# Les balises que Liquid ouvre et qu'il faut refermer. Ecrites DANS un
# commentaire, elles ne sont pas inertes : Liquid decoupe les balises avant de
# savoir qu'il est dans un commentaire, et l'ouverture reste ouverte. Une
# construction entiere est tombee sur un `if` cite en exemple dans un
# commentaire de _layouts/fiche-aventurier.html -- « 'endcomment' is not a
# valid delimiter for if tags ». Les exemples s'ecrivent en toutes lettres.
BALISES_BLOQUANTES = ("if", "unless", "for", "case", "capture", "tablerow",
                      "raw", "comment", "assign", "include")
RE_BALISE = re.compile(r"\{%-?\s*(\w+)")


def balises_en_commentaire(corps):
    """Les balises Liquid ecrites a l'interieur d'un bloc `comment`."""
    trouvees = []
    for m in RE_COMMENTAIRE.finditer(corps):
        for b in RE_BALISE.finditer(m.group(0)[m.group(0).index("%}") + 2:]):
            if b.group(1) in BALISES_BLOQUANTES:
                trouvees.append(b.group(1))
    return trouvees


def sans_commentaires(corps):
    """Retire les blocs `{% comment %}` avant tout controle de gabarit.

    Un commentaire n'est pas du code, et ce depot commente beaucoup : les
    gabarits expliquent la regle qu'ils appliquent, `where_exp` compris. Sans
    ce nettoyage, l'interdiction de `where_exp` se declenchait sur la phrase
    qui explique pourquoi `where_exp` est interdit.
    """
    return RE_COMMENTAIRE.sub("", corps)

# Le Liquid qu'on n'ecrit pas ici, et pourquoi. Le site ne peut pas etre
# construit sur cet hote -- Jekyll 3.10 en safe mode, decision assumee du
# depot -- donc une erreur de gabarit ne se decouvre qu'APRES le push, dans
# l'onglet Actions. On s'interdit donc le Liquid dont le comportement se
# discute, et `where_exp` est le premier de la liste : il a fait echouer une
# construction entiere sur une « Liquid syntax error » sans que rien n'ait pu
# le voir venir. Un calcul sur une liste se fait en Python, dans
# tools/build_stats.py, et le gabarit ne fait qu'afficher. La regle etait deja
# ecrite dans _layouts/page.html ; elle est maintenant verifiee.
LIQUID_INTERDIT = (
    ("where_exp", "filtrer une liste se fait en Python, pas dans le gabarit "
                  "— publie le resultat dans stats.yml"),
)

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


# Les fiches engendrees par tools/build_fiches.py : une page par aventurier,
# une par saison. Elles ne peuvent pas figurer dans navigation.yml -- 565
# entrees dans le rail n'auraient aucun sens -- mais elles ne sont pas pour
# autant dispensees d'etre atteignables. Chacune l'est par sa PAGE MERE, qui
# doit a la fois figurer au sommaire et construire des liens vers la famille.
# C'est cette seconde condition que le controle verifie : sans elle, 531 pages
# seraient en ligne et introuvables, et l'exemption serait un trou.
FAMILLES_DE_FICHES = {
    "fiche-aventurier": "/aventuriers/",
    "fiche-saison": "/saisons/",
    "fiche-epreuve": "/epreuves/",
}


def entrees_a_plat(groupe):
    """Les entrees d'une section, themes compris, DANS L'ORDRE du sommaire.

    Une section peut ranger ses entrees en `themes` -- « Les resultats » en a
    cinq. Un controle qui ne lirait que `entrees` verrait la section vide et
    declarerait ses vingt-sept pages introuvables.
    """
    out = list(groupe.get("entrees") or [])
    for theme in groupe.get("themes") or []:
        out.extend(theme.get("entrees") or [])
    return out


def controler_navigation(c, permaliens, gabarits):
    """Toute page publiee doit etre atteignable, et toute entree doit exister.

    `_data/navigation.yml` est la seule source du rail, du fil de lecture et
    des cartes du sommaire. Une page dont le permalink n'y figure pas est en
    ligne mais introuvable : aucun lien du site n'y mene, et rien ne le
    signale. L'inverse -- une entree qui pointe vers une page absente -- donne
    un lien mort.

    Deux cas toleres, et un seul est un choix a la main : une page
    volontairement hors navigation, listee ici explicitement ; et une fiche
    engendree, atteignable par sa page mere -- ce que ce controle verifie.
    """
    HORS_NAVIGATION = {"/404.html"}

    chemin = os.path.join(RACINE, "_data", "navigation.yml")
    if not os.path.exists(chemin):
        c.erreur("_data/navigation.yml : absent")
        return
    sections = donnees.charger(open(chemin, encoding="utf-8")) or []
    listees = {}
    for groupe in sections:
        for entree in entrees_a_plat(groupe):
            url = entree.get("url")
            if url in listees:
                c.erreur(f"navigation.yml : « {url} » listee deux fois")
            listees[url] = entree.get("titre")

    # Une famille de fiches n'est exemptee que si sa page mere est au sommaire
    # ET construit reellement des liens vers ses fiches. Le marqueur cherche
    # est la construction du lien elle-meme : `'/aventuriers/' | append:`.
    exemptes = set()
    for gabarit, mere in FAMILLES_DE_FICHES.items():
        fiches = {u for u, g in gabarits.items() if g == gabarit}
        if not fiches:
            continue
        if mere not in listees:
            c.erreur(f"{len(fiches)} fiches en `{gabarit}` mais leur page mere "
                     f"« {mere} » n'est pas dans navigation.yml — elles seraient "
                     f"toutes introuvables")
            continue
        source = permaliens.get(mere)
        texte = ""
        if source and os.path.exists(os.path.join(RACINE, source)):
            texte = open(os.path.join(RACINE, source), encoding="utf-8").read()
            # Le lien peut etre construit dans un `include` plutot que dans la
            # page -- c'est le cas des saisons, dont l'adresse passe par une
            # table de traduction. On lit donc aussi ce que la page inclut,
            # sinon le controle refuserait une page qui lie parfaitement.
            for inc in RE_INCLUDE.findall(texte):
                chemin_inc = os.path.join(RACINE, "_includes", inc)
                if os.path.exists(chemin_inc):
                    texte += open(chemin_inc, encoding="utf-8").read()
        if f"'{mere}' | append:" not in texte:
            c.erreur(f"{source} ne construit aucun lien vers ses {len(fiches)} "
                     f"fiches (`'{mere}' | append:` introuvable) — les fiches "
                     f"seraient en ligne et sans un seul lien qui y mene")
            continue
        exemptes |= fiches

    for url in sorted(set(permaliens) - set(listees) - HORS_NAVIGATION - exemptes):
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
    jeux = {}
    dossier = os.path.join(RACINE, "_data")
    for f in os.listdir(dossier):
        if f.endswith((".yml", ".yaml")):
            with open(os.path.join(dossier, f), encoding="utf-8") as fh:
                jeux[os.path.splitext(f)[0]] = donnees.charger(fh)
    return jeux


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
# Un mot n'entre ici que si sa forme SANS accent n'est pas du francais. « victoire »
# y figurait a tort -- il n'a pas d'accent -- et le controle elargi aux modalites
# des tableaux l'a fait apparaitre comme une fausse alerte.
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
elimination eliminations elimine elimines eliminee eliminees
moitie moitiee sejour sejours defaite disqualifie
ecrivent etiquette etiquettes modalite modalites separent separe athlete athletes
corrigee corrigees disputee disputees epreuve epreuves egale egales estimee
estimees censuree censurees melangerait etre region regions present presents
presente presentes detectee detectees regime regimes sante medias
recu recus recue recues gagnes
controle controles etant severe severes emis emise calee calees cinquieme
decide reunification reunifiee apres hotêl équikibre graîné vainqueures
réunifiiée réunifée immunite
"""
MOTS_SUSPECTS = set(MOTS_SANS_ACCENT.split())
# Un mot : des lettres, accentuees comprises, coupees a l'apostrophe et au
# trait d'union. L'ancien decoupage (ASCII, apostrophe incluse) ne voyait ni
# « graîné » ni « d'epreuves ».
RE_MOT = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿœŒ]+")
# Tout le texte LU d'une figure : les infobulles et la description, mais aussi
# les etiquettes posees sur le dessin (<text>, <tspan>). Les seules
# <title>/<desc> laissaient passer « 1ᵉ une fois corrige ».
RE_BALISE_TEXTE = re.compile(r"<(title|desc|text|tspan)\b[^>]*>([^<]*)", re.S)


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
        stats = donnees.charger(open(chemin, encoding="utf-8")) or {}
        # Tout ce que les modeles publient comme etiquette est du contenu : les
        # libelles de tests, mais aussi les modalites des tableaux de
        # probabilites conditionnelles, ou un code de sort (« elimine
        # orientation ») s'etait deja glisse.
        def parcourir(noeud, chemin_lisible):
            if isinstance(noeud, dict):
                for cle, valeur in noeud.items():
                    if cle in ("libelle", "question", "lecture", "modalite",
                               "mesure", "denominateur", "unite") \
                            and isinstance(valeur, str):
                        examiner(f"{chemin_lisible}.{cle}", valeur)
                    elif isinstance(valeur, (dict, list)):
                        parcourir(valeur, f"{chemin_lisible}.{cle}")
            elif isinstance(noeud, list):
                for valeur in noeud:
                    parcourir(valeur, chemin_lisible)

        parcourir(stats.get("modeles") or {}, "modeles")
        # Le classement des joueurs publie lui aussi des libelles -- le nom
        # d'une facette, la question qu'elle pose, la mesure qui la fonde.
        # C'est du contenu, au meme titre que celui des modeles.
        parcourir(stats.get("classement") or {}, "classement")

    # Le sommaire, les fiches et les pages : la revue d'orthographe du 19
    # octobre 2026 y a trouve des fautes que les deux gisements ci-dessus ne
    # couvraient pas (« On elimine le fort AVANT la reunification »).
    nav = os.path.join(RACINE, "_data", "navigation.yml")
    if os.path.exists(nav):
        def chaines(v, ch):
            if isinstance(v, str):
                # un code (« elimine_conseil », « s07 ») n'est pas du texte
                if not re.fullmatch(r"[a-z0-9_:/.-]+", v):
                    examiner(ch, v)
            elif isinstance(v, dict):
                for k, x in v.items():
                    if k not in ("url", "badge"):
                        chaines(x, f"{ch}.{k}")
            elif isinstance(v, list):
                for x in v:
                    chaines(x, ch)
        chaines(donnees.charger(open(nav, encoding="utf-8")), "navigation")
        fiches = os.path.join(RACINE, "_data", "fiches.yml")
        if os.path.exists(fiches):
            chaines(donnees.charger(open(fiches, encoding="utf-8")), "fiches")
    for chemin in pages():
        texte = open(chemin, encoding="utf-8").read()
        m = RE_FRONT.match(texte)
        entete = (yaml.safe_load(m.group(1)) or {}) if m else {}
        # Le texte lu seulement : ni le front matter technique (layout,
        # permalink), ni les balises, ni les adresses des liens.
        lu = [str(entete.get(k) or "") for k in ("title", "description", "chapeau")]
        corps = sans_commentaires(texte[m.end():] if m else texte)
        corps = re.sub(r"\{%.*?%\}|\{\{.*?\}\}", " ", corps, flags=re.S)
        # ... ni les attributs kramdown, « {: .references} ».
        corps = re.sub(r"<[^>]+>|\]\([^)]*\)|`[^`]*`|\{:[^}]*\}", " ", corps)
        examiner(os.path.relpath(chemin, RACINE), " ".join(lu) + " " + corps)

    for origine, mots in fautes:
        c.erreur(f"{origine} : texte publie sans accents ou mal orthographie — "
                 f"{', '.join(mots)}")
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
        stats = donnees.charger(open(chemin, encoding="utf-8")) or {}
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
    stats = donnees.charger(open(chemin, encoding="utf-8")) or {}
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


# Le suffixe que jekyll-seo-tag colle a TOUT titre de page : « | » plus le
# titre du site. Il compte dans ce qu'un moteur affiche, et c'est ce qu'on
# oublie en relisant un front matter -- ou le titre parait court.
SUFFIXE_TITRE = " | Koh-Lanta en chiffres"
TITRE_RENDU_MAX = 62
DESCRIPTION_MAX = 160


def controler_seo(c, entetes):
    """Refuse ce qu'un moteur de recherche lit comme une page sans valeur.

    Les 592 pages du site ont longtemps servi la MEME meta-description, celle
    de `_config.yml` : faute de `description:` en front matter, jekyll-seo-tag
    y retombe sans rien signaler. Rien ne casse, rien ne s'affiche de travers,
    et un moteur n'indexe qu'une fraction de pages qu'il croit interchangeables.
    C'est exactement le genre de panne que ce script existe pour attraper.

    Trois refus, donc : la description absente, la description partagee, et la
    longueur au-dela de laquelle le moteur coupe la phrase.
    """
    par_description = collections.defaultdict(list)
    for rel, entete in sorted(entetes.items()):
        titre = entete.get("title")
        description = entete.get("description")
        if not description:
            c.erreur(f"{rel} : `description` manquante — la page servira celle "
                     f"du site, comme toutes les autres")
            continue
        description = " ".join(str(description).split())
        par_description[description].append(rel)
        if len(description) > DESCRIPTION_MAX:
            c.avertir(f"{rel} : description de {len(description)} caracteres — "
                      f"coupee a l'affichage au-dela de {DESCRIPTION_MAX}")
        if titre:
            rendu = len(str(titre)) + len(SUFFIXE_TITRE)
            if rendu > TITRE_RENDU_MAX:
                c.avertir(f"{rel} : titre rendu de {rendu} caracteres "
                          f"(« {titre}{SUFFIXE_TITRE} ») — coupe au-dela de "
                          f"{TITRE_RENDU_MAX}")

    for description, pages_ in sorted(par_description.items()):
        if len(pages_) > 1:
            c.erreur(f"{len(pages_)} pages partagent la meme description "
                     f"(« {description[:60]}… ») — {', '.join(pages_[:3])}"
                     f"{' …' if len(pages_) > 3 else ''}")


# Une accolade Liquid, avec ce qu'elle contient. Sert a neutraliser le gabarit
# de donnees structurees pour le lire comme du JSON.
RE_LIQUID_VALEUR = re.compile(r"\{\{-?\s*.*?\s*-?\}\}")
RE_LIQUID_BLOC = re.compile(r"\{%-?\s*(?:if|unless|elsif|else|endif|endunless|for|"
                            r"endfor|assign|comment|endcomment)\b.*?-?%\}", re.S)
RE_OUVRE = re.compile(r"\{%-?\s*(?:if|unless)\b")
RE_FERME = re.compile(r"\{%-?\s*end(?:if|unless)\b")
# Le separateur d'une boucle : ce que Liquid n'ecrit PAS au dernier tour. On
# simule un seul tour, donc il ne s'ecrit jamais -- et c'est ce qui fait la
# difference entre du JSON valide et une virgule orpheline avant un crochet.
RE_SEPARATEUR = re.compile(r"\{%-?\s*unless\s+forloop\.last\s*-?%\}.*?"
                           r"\{%-?\s*endunless\s*-?%\}", re.S)


def _rendre_sans_liquid(texte, toutes_posees):
    """Rend le gabarit comme si toutes ses clauses etaient vraies, ou fausses.

    Une clause peut tenir sur une ligne -- `{%- if x %},"cle":{{ x }}{% endif -%}`
    -- ou s'etendre sur plusieurs. Les deux se simulent differemment : la
    premiere se jette d'un bloc, la seconde demande de compter les ouvertures
    jusqu'a sa fermeture. Sans ce comptage, le controle lisait le contenu d'un
    `{% if %}` multi-lignes comme s'il etait toujours ecrit, et ne verifiait
    donc jamais la branche fausse.
    """
    rendu = []
    profondeur = 0
    saut = None
    for ligne in texte.split("\n"):
        ouvertures = len(RE_OUVRE.findall(ligne))
        fermetures = len(RE_FERME.findall(ligne))
        if saut is not None:
            profondeur += ouvertures - fermetures
            if profondeur <= saut:
                saut = None
            continue
        if not toutes_posees and ouvertures:
            if ouvertures > fermetures:
                saut = profondeur
                profondeur += ouvertures - fermetures
            continue
        profondeur += ouvertures - fermetures
        rendu.append(RE_LIQUID_VALEUR.sub('"x"', RE_LIQUID_BLOC.sub("", ligne)))
    return "\n".join(rendu)


# CE QUE PYYAML ECRIT COMME UNE CHAINE ET QUE LE YAML DE RUBY RELIT COMME UN
# NOMBRE. Les scripts de ce depot ecrivent avec PyYAML ; Jekyll relit avec
# Psych, qui suit YAML 1.1. Les deux ne resolvent pas les memes formes :
#
#   « 39,9 »  -- YAML 1.1 accepte la virgule comme separateur de milliers dans
#                un entier : Psych y lit 399. PyYAML n'y voit qu'une chaine et
#                l'ecrit donc sans guillemets. Paye en ligne : une part de
#                marche publiee « 395 % » au lieu de « 39,5 % ».
#   « 1:30 »  -- YAML 1.1 lit un sexagesimal : Psych y lit 90.
#
# Aucune des deux ne fait echouer quoi que ce soit : la construction passe, le
# controle passe, la page s'affiche -- avec un nombre faux. D'ou ce controle,
# qui relit le TEXTE et non l'arbre : vu par PyYAML, il n'y a rien a voir.
RE_YAML_AMBIGU = re.compile(r"^[-+]?[0-9][0-9_]*(?:,[0-9_]+)+(?:\.[0-9_]*)?$"
                            r"|^[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+$")
# `cle: valeur` ou `- valeur`, la valeur nue -- ni guillemets, ni apostrophes,
# ni bloc.
RE_YAML_SCALAIRE = re.compile(r"^\s*(?:-\s+)?(?:[A-Za-z_][A-Za-z0-9_]*:\s+)?"
                              r"(?P<valeur>[^\s'\"#|>&*].*?)\s*$")


# Les cles de _data/fiches.yml et du front matter qui portent de la PROSE.
# Le controle ci-dessous ne regarde que celles-la : un titre de saison en
# minuscules est fautif dans une phrase, et parfaitement normal dans un
# identifiant -- l'adresse d'une saison EST « koh-lanta-palawan ». Chercher
# dans le texte brut du fichier confondait les deux, et le premier essai a
# signale les 34 slugs avant de signaler la vraie faute.
CLES_PROSE = ("q", "r", "title", "description", "chapeau", "libelle_sort")


def controler_titres_minuscules(c):
    """Refuse un titre de saison publie dans une autre casse que la sienne.

    `.capitalize()` met la premiere lettre en capitale et MINUSCULE TOUT LE
    RESTE. Employe sur une phrase qui contient un nom propre, il le detruit :
    « en 2007 (Palawan) » devenait « En 2007 (palawan) ». C'etait publie sur
    43 fiches -- « (viêtnam) », « (la revanche des 4 terres) » -- et rien ne
    le signalait : la page s'affichait, le front matter etait valide, et la
    faute ne se voit qu'en lisant la phrase.

    Le controle ne cherche pas l'appel fautif dans le code -- il y en aura
    d'autres, et la competence du projet le rappelle deja. Il cherche le
    RESULTAT : un titre de saison, tel que _data/saisons.yml l'ecrit, present
    dans un texte publie avec une casse differente.
    """
    chemin = os.path.join(RACINE, "_data", "saisons.yml")
    if not os.path.exists(chemin):
        return
    saisons = donnees.charger(open(chemin, encoding="utf-8")) or []
    titres = sorted({s["titre"] for s in saisons
                     if isinstance(s, dict) and s.get("titre")})

    phrases = []

    def recolter(noeud, origine):
        if isinstance(noeud, dict):
            for cle, valeur in sorted(noeud.items()):
                if cle in CLES_PROSE and isinstance(valeur, str):
                    phrases.append((origine, valeur))
                elif isinstance(valeur, (dict, list)):
                    recolter(valeur, origine)
        elif isinstance(noeud, list):
            for valeur in noeud:
                recolter(valeur, origine)

    fiches = os.path.join(RACINE, "_data", "fiches.yml")
    if os.path.exists(fiches):
        recolter(donnees.charger(open(fiches, encoding="utf-8")) or {},
                 "_data/fiches.yml")
    for dossier in ("aventuriers", "saisons", "epreuves"):
        chemin_d = os.path.join(RACINE, dossier)
        for nom in sorted(os.listdir(chemin_d)) if os.path.isdir(chemin_d) else []:
            if not nom.endswith(".md"):
                continue
            texte = open(os.path.join(chemin_d, nom), encoding="utf-8").read()
            m = RE_FRONT.match(texte)
            if not m:
                continue
            try:
                recolter(donnees.charger(m.group(1)) or {}, f"{dossier}/{nom}")
            except yaml.YAMLError:
                continue

    fautes = collections.Counter()
    exemples = {}
    for origine, phrase in phrases:
        for titre in titres:
            # Deux casses fautives, et aucune n'est le titre : celle que
            # `.capitalize()` fabrique, et le tout-minuscules.
            for faux in sorted({titre[:1].upper() + titre[1:].lower(),
                                titre.lower()}):
                if faux == titre or faux not in phrase:
                    continue
                fautes[titre] += 1
                exemples.setdefault(titre, (origine, faux, phrase))

    for titre, n in sorted(fautes.items()):
        origine, faux, phrase = exemples[titre]
        c.erreur(f"« {faux} » publie a la place de « {titre} », {n} fois "
                 f"— {origine} : « {phrase[:70]}… » ; un nom propre minuscule, "
                 f"probablement un `.capitalize()` applique a une phrase")


def controler_accord_rang(c):
    """Refuse « 1er » sur la fiche d'une femme, et « 1re » sur celle d'un homme.

    Quinze fiches publiaient « Son meilleur parcours : 1er sur 18 [...] ou
    ELLE gagne la saison ». Seul le rang 1 s'accorde en francais -- « 2e » ne
    bouge pas -- et c'est donc le seul cas a surveiller. Le genre est dans la
    fiche : la confrontation est directe.

    Le controle ne regarde PAS « le 1er jour », ou le mot accorde est masculin
    quel que soit le sujet. D'ou le « sur » exige derriere l'ordinal : c'est ce
    qui distingue un rang (« 1er sur 18 ») d'une date (« le 1er jour »).
    """
    chemin = os.path.join(RACINE, "_data", "fiches.yml")
    if not os.path.exists(chemin):
        return
    aventuriers = (donnees.charger(open(chemin, encoding="utf-8")) or {}) \
        .get("aventuriers") or {}
    fautes = []
    for cid, a in sorted(aventuriers.items()):
        genre = a.get("genre")
        if genre not in ("f", "h"):
            continue
        attendu, fautif = ("1re", "1er") if genre == "f" else ("1er", "1re")
        for q in a.get("faq") or []:
            for champ in ("q", "r"):
                if f"{fautif} sur" in (q.get(champ) or ""):
                    fautes.append((cid, a.get("nom"), fautif, attendu))
    for cid, nom, fautif, attendu in fautes:
        c.erreur(f"fiches.yml / {cid} : « {fautif} sur … » sur la fiche de "
                 f"{nom} — le rang 1 s'accorde, il faut « {attendu} »")


def controler_yaml_ambigu(c):
    """Refuse un scalaire nu que Jekyll relirait comme un nombre."""
    dossier = os.path.join(RACINE, "_data")
    for nom in sorted(os.listdir(dossier)) if os.path.isdir(dossier) else []:
        if not nom.endswith(".yml"):
            continue
        with open(os.path.join(dossier, nom), encoding="utf-8") as f:
            for numero, ligne in enumerate(f, 1):
                if ligne.lstrip().startswith("#"):
                    continue
                trouve = RE_YAML_SCALAIRE.match(ligne.rstrip("\n"))
                if trouve and RE_YAML_AMBIGU.match(trouve.group("valeur")):
                    c.erreur(f"_data/{nom}:{numero} : « {trouve.group('valeur')} » "
                             f"est ecrit sans guillemets — PyYAML y voit une "
                             f"chaine, le YAML de Ruby un nombre, et c'est "
                             f"Ruby qui publie")


# Les filtres de calcul de Liquid. Ils rendent un decimal a point (« 8.1 »), et
# ils ne savent pas lire un decimal a la francaise (« 54,2 » -> 54) : depuis
# que _data/ s'ecrit avec la virgule, le calcul se fait en Python.
RE_FILTRE_CALCUL = re.compile(r"\|\s*(round|divided_by|times|ceil|floor|at_least|at_most)\b")
RE_TEXTE_SVG = re.compile(r"<(?:text|tspan|title|desc)\b[^>]*>([^<]*)|aria-label=\"([^\"]*)\"")
RE_DECIMAL_POINT = re.compile(r"\d\.\d")


def controler_virgule_decimale(c):
    """Refuse tout chemin par lequel un decimal a point atteindrait le lecteur.

    Le 19 octobre 2026, 701 nombres de 34 pages et 2 023 textes de figures
    s'affichaient « 54.2 % ». Trois chemins y menaient, et chacun a sa garde :

      * un flottant ecrit nu dans _data/ -- Liquid l'affiche avec son point.
        Tout passe par `donnees.ecrire` (tools/donnees.py) ;
      * un filtre de calcul dans un gabarit -- il fabrique un point, et il
        lirait « 54,2 » comme 54 ;
      * un texte de figure -- `graphiques.virgule_decimale` le corrige a
        l'ecriture ; une figure ecrite autrement le laisserait passer.
    """
    dossier = os.path.join(RACINE, "_data")
    for nom in sorted(os.listdir(dossier)):
        if not nom.endswith(".yml"):
            continue
        brut = yaml.safe_load(open(os.path.join(dossier, nom), encoding="utf-8"))
        flottants = []

        def parcourir(v, chemin):
            if isinstance(v, float) and math.isfinite(v):
                flottants.append(chemin)
            elif isinstance(v, dict):
                for k, x in v.items():
                    parcourir(x, f"{chemin}.{k}")
            elif isinstance(v, list):
                for i, x in enumerate(v):
                    parcourir(x, f"{chemin}[{i}]")
        parcourir(brut, nom[:-4])
        if flottants:
            c.erreur(f"_data/{nom} : {len(flottants)} decimaux ecrits avec un point "
                     f"(premier : {flottants[0]}) — le fichier doit etre ecrit par "
                     f"donnees.ecrire, Liquid les publierait tels quels")

    for chemin in list(pages()) + [
            os.path.join(RACINE, d, f) for d in ("_layouts", "_includes")
            for f in os.listdir(os.path.join(RACINE, d)) if f.endswith(".html")]:
        corps = sans_commentaires(open(chemin, encoding="utf-8").read())
        for m in RE_FILTRE_CALCUL.finditer(corps):
            c.erreur(f"{os.path.relpath(chemin, RACINE)} : filtre `{m.group(1)}` — "
                     f"un calcul de gabarit publie un point decimal et ne lit pas "
                     f"« 54,2 » ; le faire en Python (build_stats.champs_d_affichage)")

    figures = os.path.join(RACINE, "_includes", "graphiques")
    for nom in sorted(os.listdir(figures)) if os.path.isdir(figures) else []:
        texte = open(os.path.join(figures, nom), encoding="utf-8").read()
        fautes = [t for m in RE_TEXTE_SVG.finditer(texte)
                  for t in m.groups() if t and RE_DECIMAL_POINT.search(t)]
        if fautes:
            c.erreur(f"_includes/graphiques/{nom} : {len(fautes)} textes avec un point "
                     f"decimal (« {fautes[0].strip()[:50]} ») — la figure doit "
                     f"passer par graphiques.ecrire")


# Ce que des PHRASES du site affirment d'un test du registre : (retenu ?, ou).
# Un chiffre suit les donnees, la phrase qui l'entoure non. Le 19 octobre 2026,
# le sommaire, l'accueil, /statistiques/fusion/ et /statistiques/top/ ecrivaient
# « on elimine le fort AVANT la reunification » -- un test NON retenu
# (p ajustee 0,37). Changer une de ces phrases, c'est changer cette table.
AFFIRMATIONS_PAGES = {
    "fusion_force": (False, "index.md, statistiques/fusion.md, statistiques/top.md "
                            "et le resume du sommaire ecrivent que la force ne "
                            "decide pas de qui part"),
    "fusion_sexe": (True, "statistiques/fusion.md titre « Le sexe, lui, bascule »"),
    "menace_voix": (True, "statistiques/conditionnelles.md ecrit que la menace "
                          "fraiche, visee la derniere fois, compte"),
    "menace_deux_pas": (False, "statistiques/conditionnelles.md ecrit que la menace "
                               "deux conseils plus tard n'est pas retenue"),
    "talent_stable": (False, "sources.md ecrit que la stabilite reste trop mince "
                             "pour etre retenue"),
    "ambassadeurs_survie": (True, "statistiques/fusion.md ecrit que l'ambassadeur "
                                  "sort plus tot"),
    "vote_meme_sexe": (True, "statistiques/qui-vise-qui.md et le resume du "
                             "sommaire ecrivent « le sexe : un peu »"),
    "vote_meme_metier": (True, "statistiques/qui-vise-qui.md et le resume du "
                               "sommaire ecrivent « le metier : un peu aussi »"),
    "vote_ecart_age": (False, "statistiques/qui-vise-qui.md ecrit « l'age : a peine »"),
    "vote_meme_departement": (False, "statistiques/qui-vise-qui.md ecrit « le voisin : "
                                     "peut-etre », non concluant"),
    "bandeau_minoritaire": (True, "statistiques/autour-du-feu.md ecrit « quatre "
                                  "tests, deux retenus » et le resume du sommaire"),
    "sexe_minoritaire": (True, "statistiques/autour-du-feu.md ecrit « quatre "
                               "tests, deux retenus » et le resume du sommaire"),
    "doyen_du_camp": (False, "statistiques/autour-du-feu.md et le resume du "
                             "sommaire ecrivent que le doyen ne part pas plus"),
    "confort_sortie": (False, "statistiques/autour-du-feu.md ecrit « quatre "
                              "tests, deux retenus »"),
    "menace_sommet": (False, "statistiques/conditionnelles.md, le chapeau et "
                             "statistiques/jeu-social.md ecrivent que le "
                             "retournement n'est pas confirme"),
}

# Ce qu'une phrase ecrite suppose d'une valeur hors registre : le chemin dans
# _data/stats.yml, la condition, et les pages a relire si elle tombe. Le
# registre ne couvre pas tout ce que les pages affirment -- un intervalle
# qui exclut 1, un maximum, un compte qu'une phrase nomme.
def _sous_un(x):
    return x["haut"] < 1


def _contient_un(x):
    return x["bas"] <= 1 <= x["haut"]


AFFIRMATIONS_VALEURS = [
    (("modeles", "force_et_jeu", "voix", "force"), _sous_un,
     "statistiques/force.md ecrit que l'intervalle reste sous 1"),
    (("modeles", "force_et_jeu", "voix", "age"), _contient_un,
     "statistiques/force.md ecrit que l'intervalle de l'age contient 1"),
    (("modeles", "force_et_jeu", "survie", "force"),
     lambda x: x["bas"] <= 0 <= x["haut"],
     "statistiques/force.md ecrit que la force ne mene pas plus loin"),
    (("modeles", "autour_du_feu", "immunite"),
     lambda x: x[0]["cas"] == 0,
     "statistiques/autour-du-feu.md, conditionnelles.md et sources.md ecrivent "
     "que la probabilite de partir sous immunite vaut zero"),
    (("modeles", "conditionnelles", "par_voix"),
     lambda x: max(x, key=lambda v: v["probabilite"])["modalite"] == "2 voix"
     and all(v["probabilite"] > v["hasard"] for v in x[1:]),
     "statistiques/conditionnelles.md et jeu-social.md ecrivent que la courbe "
     "culmine a deux voix sans repasser sous le hasard"),
    (("modeles", "alliances", "majorite", "rapport"), lambda x: x > 1,
     "statistiques/alliances.md et jeu-social.md ecrivent qu'etre du bon cote "
     "pese plus que ne pas etre vise"),
    (("indicateurs", "fantomes_issue"),
     lambda x: all(v["rapport"] > 1 for v in x
                   if v["sort"] in ("vainqueur", "abandon_medical")),
     "statistiques/jeu-social.md ecrit « N fois plus » de vainqueurs et "
     "d'abandons medicaux chez les fantomes"),
    (("indicateurs", "menace_rapport"), lambda x: x > 1,
     "statistiques/jeu-social.md ecrit « N fois moins » de voix pour un vainqueur"),
    (("epreuves", "par_metier_par_ratio"), lambda x: x[0]["code"] == "sport",
     "statistiques/epreuves.md ecrit que le sport arrive en tete, « rien de "
     "surprenant », et parle d'avantage athletique"),
    (("premiere_epreuve", "ecart"), lambda x: x > 0,
     "statistiques/epreuves.md ecrit que gagner la premiere epreuve va plus loin"),
    (("finale", "par_rang"),
     lambda x: (x[2]["gagne_la_saison"]["cas"], x[2]["gagne_la_saison"]["effectif"]) == (11, 17),
     "statistiques/finale.md ecrit « onze victoires sur dix-sept » dans sa "
     "description et son chapeau"),
    (("modeles", "pire_place", "isolement"),
     lambda x: x[0]["bas"] <= x[1]["haut"] and x[1]["bas"] <= x[0]["haut"],
     "statistiques/pire-place.md ecrit que les deux formes de l'isolement ne se "
     "distinguent pas"),
    (("modeles", "pire_place", "cumul_rapport"), lambda x: x > 1,
     "statistiques/pire-place.md ecrit que les deux signaux multiplient le risque"),
    (("modeles", "autour_du_feu", "age_ecart"), lambda x: x > 0,
     "statistiques/longevite.md ecrit que le doyen part plus souvent, en brut"),
    (("modeles", "jury_final", "coefficients"), lambda x: x[0]["haut"] < 1,
     "statistiques/jury.md ecrit qu'avoir elimine le jure divise la cote"),
    (("epreuves", "saisons_sans_donnee"),
     lambda x: sorted(x) == ["s03", "s09", "s12", "s14", "sp2"],
     "sources.md et force.md nomment les cinq saisons sans bilan d'epreuves"),
    (("modeles", "registre"),
     lambda x: abs(next(t for t in x if t["cle"] == "menace_sommet")["ecart_types"]) < 1,
     "sources.md ecrit qu'il ne reste rien du sommet de la menace"),
    (("rattachement",), lambda x: x["colliers"] == x["colliers_rattaches"]
     and x["vainqueurs_restants_personnes"] == 0,
     "sources.md ecrit qu'il ne reste aucun nom de personne non rattache"),
    (("conseils", "retours_en_jeu"), lambda x: x == 7,
     "sources.md raconte les retours en jeu un par un (Linda, Francis, Tania deux "
     "fois, Martin, Christina, Andre)"),
    (("conseils", "part_serres"), lambda x: 33 <= x < 75,
     "statistiques/conseils.md ecrit que le vote est « souvent serre »"),
    (("jury", "decomptes_discordants"), lambda x: x == 0,
     "sources.md ecrit que le decompte annonce et les bulletins du jury "
     "coincident partout ou la source annonce un decompte"),
    (("conseils", "elimines_non_rattaches"), lambda x: x == 2,
     "sources.md attribue les conseils non rattaches aux deux Jerome de "
     "La Revanche des 4 Terres"),
    (("modeles",), lambda x: x["nb_retenus"] - x["retenus_avec_vingt_nuls"] <= 2,
     "methode.md ecrit que, vingt tests nuls ajoutes, presque tous les "
     "resultats retenus tiennent et que ce n'est pas une raison de s'arreter"),
    # Lot 4b : les phrases, titres et descriptions qui gardent un nombre ecrit.
    (("modeles","ruptures","detail"), lambda x: next(v for v in x if v["libelle"]=="Objets d'immunité en jeu")["avant"]==0, "statistiques/grille.md ecrit que les objets d'immunite etaient a zero avant la rupture"),
    (("modeles","audience"), lambda x: x["premiere"]["annee"]==2001 and x["sommet"]["jour"]=="Mardi", "statistiques/audience.md ecrit « depuis 2001 » (description) et que le sommet etait deja diffuse le mardi"),
    (("palmares","classement"), lambda x: x[2]["personne"]=="Ugo Lartiche", "statistiques/force.md nomme Ugo Lartiche troisieme palmares de l'histoire"),
    (("modeles","registre"), lambda x: (lambda s: s[0]["cle"]=="persistance_alliances" and s[0]["ecart_types"] >= 1.5*s[1]["ecart_types"])(sorted(x, key=lambda t: -abs(t.get("ecart_types") or 0))), "statistiques/alliances.md ecrit que la persistance des alliances est de tres loin le signal le plus fort"),
    (("modeles","decimation","detail"), lambda x: ("J" * x[0]["plus_longue_serie"]) in x[0]["suite"], "statistiques/alliances.md ecrit que la plus longue serie est jaune"),
    (("completude_saisons",), lambda x: x["saisons"]==34 and len(x["colonnes"])==19, "completude.md (description, chapeau) et le sommaire ecrivent 34 editions et 19 types de donnees"),
    (("general",), lambda x: x["saisons_diffusees"]==34 and x["premiere_annee"]==2001 and x["derniere_annee"]==2026 and x["saisons_annulees"]==2 and x["etendue_annees"]==25, "saisons.md (titre, description, chapeau), index.md, sorties.md : 34 saisons, 2001 a 2026, deux interrompues, vingt-cinq ans"),
    (("general","parite_ecart_max"), lambda x: x <= 2, "saisons.md ecrit que l'ecart a la parite tient au plus a un ou deux aventuriers"),
    (("classement","facettes"), lambda x: next(f for f in x if f["cle"]=="epreuves")["top"][0]["nom"]=="Claude Dartois", "saisons.md accorde « est premier » au premier de la facette epreuves"),
    (("modeles","registre"), lambda x: next(t for t in x if t["cle"]=="parite")["observe"] < 1, "statistiques/pronostic.md et casting.md ecrivent « la parite au candidat pres »"),
    (("modeles","jury_final","part_quand_disponible"), lambda x: x > 50, "statistiques/jury.md ecrit que les jures couronnent le plus souvent celui qui les a sortis"),
    (("modeles","registre"), lambda x: (lambda v: v[0]["cle"] in ("vote_meme_bandeau","vote_bandeau_apres_fusion"))(sorted([t for t in x if t["cle"].startswith("vote_") and t["cle"]!="vote_isole"], key=lambda t: -abs(t["ecart_types"]))), "statistiques/jury.md ecrit que le bandeau est le resultat le plus net de Qui vise qui"),
    (("geographie",), lambda x: x["reunion_observe"]==0 and x["martinique_observe"]==x["outremer_observe"]==2 and x["premiere_region"]=="Corse", "statistiques/geographie.md : la Reunion n'a fourni personne, les deux viennent de Martinique, la Corse a le plus fort indice"),
    (("revenants","vainqueurs_multiples"), lambda x: len(x)==1, "statistiques/vainqueurs.md ecrit « une seule, sacree... la seule a avoir gagne deux fois »"),
    (("vainqueurs","par_metier"), lambda x: x[0]["part"]==x[1]["part"]==x[2]["part"] > x[3]["part"] and {y["code"] for y in x[:3]}=={"encadrement","commerce","sport"}, "statistiques/vainqueurs.md nomme les trois premieres familles, a egalite"),
    (("finale","par_rang"), lambda x: 40 <= x[0]["elimine_aux_poteaux"]["probabilite"] < 50, "statistiques/finale.md ecrit « presque une fois sur deux » pour le premier sorti aux poteaux"),
    (("classement",), lambda x: len(x["facettes"])==4 and x["joueurs_classes"]==531, "top.md (description, chapeau), index.md et le sommaire ecrivent « quatre facettes » et 531 aventuriers"),
    (("modeles","casting","archetypes"), lambda x: [a["libelle"] for a in x]==["25-29 ans · femme · Commerce et vente","30-34 ans · homme · Agriculture et nature","40-44 ans · homme · Artisanat et bâtiment","45 ans et plus · Sans activité déclarée","18-24 ans","18-24 ans · femme · Étudiants"], "statistiques/casting.md decrit les six archetypes un par un (« la femme de la fin de la vingtaine, dans le commerce »...)"),
    (("modeles","casting"), lambda x: max(x["silhouettes"], key=lambda s: s["score"])["k"] == x["nb_archetypes"], "statistiques/casting.md ecrit que la silhouette monte jusqu'au nombre retenu puis redescend"),
    (("modeles","conditionnelles","inverse"), lambda x: x["vise_si_sorti"] < 50, "statistiques/conditionnelles.md ecrit que la majorite des elimines n'avaient pas ete vises la fois d'avant"),
    (("modeles","avant_apres","negociateurs"), lambda x: x["sources_desaccord"]==1, "statistiques/fusion.md ecrit « La seule divergence porte sur Les Reliques du destin »"),
    (("couleurs",), lambda x: {c["couleur"]: c["victoires"] for c in x}.get("jaune") == {c["couleur"]: c["victoires"] for c in x}.get("rouge"), "statistiques/autour-du-feu.md ecrit que la couleur ne decide rien du palmares (autant de victoires jaunes que rouges)"),
    (("conseils","conseils_unanimes"), lambda x: x == 0, "statistiques/conseils.md (description, chapeau) ecrit que l'unanimite n'existe pas"),
    (("modeles","rappel","par_sort"), lambda x: sum(v["cas"] for v in x[-2:]) == 1, "statistiques/revenants.md ecrit « un seul retour » parmi les abandons"),
    (("revenants","vainqueurs_regagnants"), lambda x: x == 1, "statistiques/revenants.md titre « Un seul a gagne deux fois » et ecrit « Un seul a regagne »"),
    (("modeles","equilibre","cox","coefficients"), lambda x: max(x, key=lambda v: abs(math.log(v["rapport"])))["variable"] == "Déjà venu", "statistiques/revenants.md et equilibre.md ecrivent que « deja venu » est le plus gros coefficient du modele"),
    (("sorties",), lambda x: len(x["repartition"])==9 and x["par_decennie"][0]["ambassadeurs"]==0 and max(x["par_decennie"], key=lambda d: d["ambassadeurs"])["decennie"]=="2010s" and [r["sort"] for r in x["repartition"][:2]]==["elimine_conseil","abandon_medical"], "statistiques/sorties.md : neuf facons de partir (description, chapeau), conseil puis abandon medical en tete, ambassadeurs absents des annees 2000 et au sommet dans les annees 2010"),
    (("prenoms","alexandra"), lambda x: x == 7, "statistiques/prenoms.md (description, chapeau) et le sommaire ecrivent qu'Alexandra revient sept fois"),
    (("age",), lambda x: max(x, key=lambda a: a["survie_moyenne"])["tranche"]=="30-34 ans" and max(x, key=lambda a: a["taux_finale"])["tranche"]=="30-34 ans" and x[5]["victoires"]==1, "statistiques/longevite.md, revenants.md et pronostic.md : les 30-34 ans tiennent le plus longtemps et accedent le plus a la finale ; une seule victoire chez les 45 ans et plus"),
    (("colliers",), lambda x: 28 <= x["issues"][1]["part_des_trouves"] <= 38 and 12 <= x["issues"][3]["part_des_trouves"] <= 16 and x["palmares"][0]["trouves"] > x["palmares"][1]["trouves"], "statistiques/colliers.md : « un collier sur trois joue pour rien », « un sur sept part avec son proprietaire », un seul a faire le plein"),
    (("classement","top"), lambda x: x[0]["nom"]=="Claude Dartois", "statistiques/colliers.md nomme Claude Dartois premier du classement, une seule de ses saisons couverte"),
    (("sommaire",), lambda x: (x["entrees"], x["descriptives"], x["testees"]) == (27, 11, 16), "statistiques.md (chapeau), index.md et le sommaire ecrivent vingt-sept entrees, onze qui decrivent, seize qui testent"),
    (("indicateurs","saisons"), lambda x: all(30 <= s["age_moyen"] < 40 for s in x if not s["speciale"] and s.get("age_moyen") is not None), "statistiques.md ecrit que l'age moyen reste autour de la trentaine"),
    (("couleurs",), lambda x: all(c["effectif"] > 200 for c in x if c["couleur"] in ("jaune","rouge")), "statistiques/tribus.md ecrit « plus de deux cents aventuriers chacun »"),
    (("general","metiers_distincts"), lambda x: 450 <= x < 500, "statistiques/professions.md (description, chapeau) ecrit « pres de cinq cents » metiers"),
    (("metiers",), lambda x: [m_["code"] for m_ in x[:3]]==["encadrement","commerce","sport"] and min((m_ for m_ in x if m_["effectif"] >= 15), key=lambda m_: m_["taux_finale"])["code"]=="encadrement", "statistiques/professions.md : encadrement, commerce, sport en tete du casting ; l'encadrement dernier en acces a la finale"),
    (("general","participations"), lambda x: x == 645, "aventuriers.md (description) ecrit « Les 645 participations »"),
    (("croisement_divergents",), lambda x: x == 2, "sources.md et conseils.md ecrivent que les divergences sont « toutes deux » le meme probleme (deux Jerome)"),
    (("risque", "jours_les_plus_meurtriers"), lambda x: x[2]["jour"] <= 5 and x[0]["jour"] >= 35 and x[1]["jour"] >= 35,
     "statistiques/sorties.md ecrit que, hors finale, on sort le plus en tout debut de saison"),
    (("geographie", "lacunaires"), lambda x: all(v["annee"] < 2010 for v in x),
     "statistiques/geographie.md ecrit que les saisons lacunaires sont celles "
     "des premieres annees"),
]


def controler_affirmations_pages(c):
    """Refuse une page dont l'affirmation ecrite ne tient plus dans le registre."""
    chemin = os.path.join(RACINE, "_data", "stats.yml")
    stats = donnees.charger(open(chemin, encoding="utf-8")) or {}
    registre = {t["cle"]: t for t in
                (stats.get("modeles") or {}).get("registre") or []}
    for chemin_cle, tient, ou in AFFIRMATIONS_VALEURS:
        valeur = stats
        for cle in chemin_cle:
            valeur = (valeur or {}).get(cle)
        try:
            ok = valeur is not None and tient(valeur)
        except (KeyError, IndexError, TypeError, ValueError):
            ok = False
        if not ok:
            c.erreur(f"stats : `{'.'.join(chemin_cle)}` ne soutient plus la "
                     f"phrase — {ou} : relire avant de publier")
    for cle, (retenu, ou) in AFFIRMATIONS_PAGES.items():
        test = registre.get(cle)
        if test is None:
            c.erreur(f"registre : test `{cle}` absent — {ou}")
        elif bool(test.get("retenu")) != retenu:
            c.erreur(f"registre : `{cle}` est desormais "
                     f"{'retenu' if test.get('retenu') else 'non retenu'} — {ou} : "
                     f"relire ces phrases avant de publier")


def controler_donnees_structurees(c):
    """Verifie que le JSON-LD reste du JSON, branches posees ou non.

    Un bloc `application/ld+json` casse ne fait echouer NI la construction NI
    l'affichage : le moteur jette le bloc en silence, et le travail est perdu
    sans que rien ne le dise. Une virgule en trop derriere une clause `{% if %}`
    suffit -- c'est pourquoi les deux etats de chaque clause sont essayes.
    """
    chemin = os.path.join(RACINE, "_includes", "donnees-structurees.html")
    if not os.path.exists(chemin):
        return
    texte = RE_SEPARATEUR.sub("", RE_COMMENTAIRE.sub(
        "", open(chemin, encoding="utf-8").read()))

    for toutes_posees in (True, False):
        rendu = _rendre_sans_liquid(texte, toutes_posees)
        for morceau in re.findall(r"<script[^>]*>(.*?)</script>", rendu, re.S):
            try:
                json.loads(morceau)
            except ValueError as e:
                etat = "toutes clauses posees" if toutes_posees else "clauses absentes"
                c.erreur(f"_includes/donnees-structurees.html : JSON invalide "
                         f"({etat}) — {e}")


# Les nombres ecrits en toutes lettres, jusqu'a quarante : au-dela, le site
# ecrit en chiffres. La table sert a relire ce que trois pages ANNONCENT et a
# le comparer a ce que _data/navigation.yml CONTIENT.
_UNITES = ["zero", "un", "deux", "trois", "quatre", "cinq", "six", "sept",
           "huit", "neuf", "dix", "onze", "douze", "treize", "quatorze",
           "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
_DIZAINES = {20: "vingt", 30: "trente", 40: "quarante"}


def _en_lettres():
    mots = {mot: n for n, mot in enumerate(_UNITES)}
    for base, mot in _DIZAINES.items():
        mots[mot] = base
        mots[f"{mot} et un"] = base + 1
        for n in range(2, 10):
            mots[f"{mot}-{_UNITES[n]}"] = base + n
    return mots


# « zero » et « un » sortent de la table : « un » est d'abord un article, et
# le controle le relevait dans « on ne teste bien qu'un ecart ». Aucun compte
# de ce fichier ne vaudra jamais 0 ou 1. Les composes qui le contiennent
# -- « vingt et un » -- restent, eux, sans ambiguite.
NOMBRES_EN_LETTRES = {m: n for m, n in _en_lettres().items() if m not in ("zero", "un")}
# La limite de mot est indispensable : sans elle « six » se trouve dans
# « dix-six »... et surtout « un » dans « aucun », « chacun », « commun ».
RE_NOMBRE_LETTRES = re.compile(
    r"\b(?:%s)\b" % "|".join(sorted((re.escape(m) for m in NOMBRES_EN_LETTRES),
                                     key=len, reverse=True)), re.I)


# Les filtres Liquid qui calculent ou mettent en forme. La regle du depot est
# l'acces par cle : le site ne peut pas etre essaye avant le push, et un
# calcul dans un gabarit echoue en silence (une chaine « 54,2 » n'est pas un
# nombre pour Liquid). `capitalize` minuscule en outre la suite, noms propres
# compris. Les filtres d'adresse et d'echappement -- relative_url, jsonify,
# markdownify -- ne sont pas vises.
RE_CALCUL_LIQUID = re.compile(
    r"\|\s*(plus|minus|times|divided_by|modulo|round|ceil|floor|abs|"
    r"capitalize|downcase|upcase)\b")


def controler_calculs_liquid(c):
    """Refuse un calcul ou une mise en forme faits en Liquid."""
    for dossier, _, fichiers in os.walk(RACINE):
        rel = os.path.relpath(dossier, RACINE)
        if rel.split(os.sep)[0] in ("_site", "_drafts", ".git", ".compare", "specs",
                                    "node_modules", "vendor", ".claude"):
            continue
        for nom in fichiers:
            if not nom.endswith((".md", ".html")):
                continue
            chemin = os.path.join(dossier, nom)
            for i, ligne in enumerate(open(chemin, encoding="utf-8"), 1):
                m = RE_CALCUL_LIQUID.search(ligne)
                if m and "{" in ligne:
                    c.erreur(f"{os.path.relpath(chemin, RACINE)}:{i} : filtre Liquid "
                             f"`{m.group(1)}` — le calcul se fait en Python "
                             f"(tools/build_stats.py), le gabarit lit une cle")


def controler_comptes_annonces(c):
    """Refuse un nombre annonce en toutes lettres qui ne colle plus aux donnees.

    Le sommaire des statistiques annoncait « Vingt-six entrees », le rail « Les
    vingt entrees » et l'accueil « quatorze pages ou les modeles prennent le
    relais » -- alors que navigation.yml en portait vingt-sept, onze
    descriptives et seize a modeles. Trois textes, trois nombres faux, trois
    derives independantes : personne n'avait touche a la meme phrase, on avait
    seulement ajoute des pages. Rien ne le signalait, et le lecteur qui compte
    les cartes trouvait autre chose que ce que la page venait de lui dire.

    Le controle est volontairement grossier : dans trois zones bien delimitees,
    TOUT nombre ecrit en toutes lettres doit valoir l'un des trois comptes
    reels. Hors de ces zones on ne regarde rien -- « apres vingt ans de
    vendredi » est une phrase juste ailleurs dans l'accueil.
    """
    chemin = os.path.join(RACINE, "_data", "navigation.yml")
    if not os.path.exists(chemin):
        return
    sections = donnees.charger(open(chemin, encoding="utf-8")) or []
    fil = next((g for g in sections if g.get("fil")), None)
    if not fil:
        return
    entrees = [e for e in entrees_a_plat(fil) if not e.get("hub")]
    modeles = sum(1 for e in entrees if e.get("modeles"))
    if not modeles:
        c.erreur("_data/navigation.yml : aucune entree marquee `modeles: true` — "
                 "le partage entre pages descriptives et pages a modeles n'est "
                 "plus derivable, et les nombres annonces ne sont plus verifiables")
        return
    attendus = {len(entrees), modeles, len(entrees) - modeles}

    hub = next((e for e in entrees_a_plat(fil) if e.get("hub")), {})
    zones = [("_data/navigation.yml (resume du sommaire)", hub.get("resume") or "")]

    # Le sommaire : son chapeau, et le corps jusqu'au titre qui annonce le
    # compte. Plus bas, la page parle d'autre chose.
    chemin = os.path.join(RACINE, "statistiques.md")
    if os.path.exists(chemin):
        texte = open(chemin, encoding="utf-8").read()
        m = RE_FRONT.match(texte)
        entete = donnees.charger(m.group(1)) if m else {}
        corps = texte[m.end():] if m else texte
        coupe = re.search(r"^##\s.*$", corps, re.M)
        zones.append(("statistiques.md (chapeau)", str(entete.get("chapeau") or "")))
        zones.append(("statistiques.md (presentation)",
                      corps[:coupe.end()] if coupe else corps))

    # L'accueil : la seule carte qui pointe vers /statistiques/.
    chemin = os.path.join(RACINE, "index.md")
    if os.path.exists(chemin):
        for carte in re.findall(r"<li class=\"carte\">.*?</li>",
                                open(chemin, encoding="utf-8").read(), re.S):
            if "'/statistiques/'" in carte:
                zones.append(("index.md (carte des statistiques)", carte))

    for origine, texte in zones:
        for trouve in RE_NOMBRE_LETTRES.findall(texte or ""):
            valeur = NOMBRES_EN_LETTRES[trouve.lower()]
            if valeur not in attendus:
                c.erreur(f"{origine} : « {trouve} » ne correspond a aucun compte "
                         f"reel — navigation.yml porte {len(entrees)} entrees, "
                         f"{len(entrees) - modeles} descriptives et {modeles} "
                         f"a modeles")

def _mesurer(chemin):
    """Les dimensions d'une image, ou None si on ne sait pas les lire.

    Pillow est dans l'atelier, mais ce script doit pouvoir tourner ailleurs :
    faute de la bibliotheque, le controle des deux dimensions reste (elles
    doivent etre presentes et positives) et seule la confrontation au fichier
    est sautee. Mieux vaut un controle partiel qu'un script qui ne demarre pas.
    """
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(chemin) as image:
            return image.size
    except OSError:
        return None


def controler_portraits(c):
    """Refuse une photo publiee sans son auteur et sa licence.

    Les portraits viennent de Wikimedia Commons sous licence libre. « Libre »
    ne veut pas dire « sans condition » : CC BY et CC BY-SA exigent
    l'attribution, et une photo republiee sans son auteur ne l'est pas
    legalement. Le credit n'est donc pas un ornement qu'on peut alleger un
    jour de refonte -- ce controle existe pour que ce jour-la, la construction
    le dise.

    Il verifie les donnees ET le gabarit : un champ rempli ne sert a rien si
    plus personne ne l'affiche.
    """
    chemin = os.path.join(RACINE, "_data", "portraits.yml")
    if not os.path.exists(chemin):
        return
    portraits = (donnees.charger(open(chemin, encoding="utf-8")) or {}).get("portraits") or {}
    for cle, p in sorted(portraits.items()):
        # L'auteur peut manquer, et seulement dans ce cas : une image du
        # domaine public n'exige aucune attribution, et Commons y ecrit
        # parfois « Pas d'auteur ». La licence, elle, s'affiche toujours.
        domaine_public = "domaine public" in (p.get("licence") or "").lower() \
            or "public domain" in (p.get("licence") or "").lower()
        exiges = ["fichier", "licence", "source"]
        if not domaine_public:
            exiges.append("auteur")
        for champ in exiges:
            if not (p.get(champ) or "").strip():
                c.erreur(f"portraits.yml : « {cle} » sans `{champ}` — une photo "
                         f"ne se publie pas sans son credit complet")
        fichier = (p.get("fichier") or "").lstrip("/")
        if fichier and not os.path.exists(os.path.join(RACINE, fichier)):
            c.erreur(f"portraits.yml : « {cle} » pointe sur {p['fichier']}, "
                     f"absent du depot")
        # Les dimensions, et le fait qu'elles soient JUSTES. Posees dans
        # `width`/`height`, elles reservent la place de la photo avant qu'elle
        # arrive ; fausses, elles la reservent de travers et la page saute
        # quand meme -- au lieu de corriger le defaut, on le deplace.
        for champ in ("largeur", "hauteur"):
            if not isinstance(p.get(champ), int) or p[champ] <= 0:
                c.erreur(f"portraits.yml : « {cle} » sans `{champ}` — sans les "
                         f"deux dimensions, la fiche saute quand la photo se pose")
        if fichier and os.path.exists(os.path.join(RACINE, fichier)) \
                and isinstance(p.get("largeur"), int) \
                and isinstance(p.get("hauteur"), int):
            mesure = _mesurer(os.path.join(RACINE, fichier))
            if mesure and mesure != (p["largeur"], p["hauteur"]):
                c.erreur(f"portraits.yml : « {cle} » annonce "
                         f"{p['largeur']}x{p['hauteur']}, le fichier mesure "
                         f"{mesure[0]}x{mesure[1]}")

    gabarit = os.path.join(RACINE, "_layouts", "fiche-aventurier.html")
    texte = open(gabarit, encoding="utf-8").read() if os.path.exists(gabarit) else ""
    for champ in ("portrait.auteur", "portrait.licence",
                  "portrait.largeur", "portrait.hauteur"):
        if portraits and champ not in texte:
            if champ.endswith(("largeur", "hauteur")):
                c.erreur(f"_layouts/fiche-aventurier.html ne pose plus "
                         f"`{champ}` — {len(portraits)} fiches sauteraient au "
                         f"chargement de la photo")
            else:
                c.erreur(f"_layouts/fiche-aventurier.html n'affiche plus "
                         f"`{champ}` — {len(portraits)} photos seraient publiees "
                         f"sans leur credit")


# La largeur d'un caractere, en fraction de la taille de police. Approchee, et
# c'est assumé : il ne s'agit pas de composer au pixel pres, mais de voir qu'un
# texte part cent pixels hors du dessin.
LARGEUR_CARACTERE = 0.62
HAUTEUR_LIGNE = 1.15
# Deux pixels de tolerance : l'estimation de largeur n'est pas la mesure du
# navigateur, et on ne veut pas d'alerte pour un demi-caractere.
TOLERANCE_CADRE = 2.0

RE_SVG_TEXTE = re.compile(r"<text\b(?P<attrs>[^>]*)>(?P<contenu>[^<]*)</text>")
RE_SVG_VIEWBOX = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')
RE_SVG_ROTATE = re.compile(r"rotate\((-?[\d.]+)")


def _attribut(attrs, nom, defaut=None):
    trouve = re.search(rf'{nom}="([^"]*)"', attrs)
    return trouve.group(1) if trouve else defaut


def _boite_texte(attrs, contenu):
    """Le rectangle occupe par un <text>, rotation comprise."""
    x, y = float(_attribut(attrs, "x", 0)), float(_attribut(attrs, "y", 0))
    taille = float(_attribut(attrs, "font-size", 13))
    ancre = _attribut(attrs, "text-anchor", "start")
    tourne = RE_SVG_ROTATE.search(attrs)
    angle = math.radians(float(tourne.group(1))) if tourne else 0.0
    largeur = len(contenu) * taille * LARGEUR_CARACTERE
    hauteur = taille * HAUTEUR_LIGNE
    x0 = {"end": x - largeur, "middle": x - largeur / 2}.get(ancre, x)
    coins = [(x0 - x, -hauteur / 2), (x0 + largeur - x, -hauteur / 2),
             (x0 + largeur - x, hauteur / 2), (x0 - x, hauteur / 2)]
    points = [(x + dx * math.cos(angle) - dy * math.sin(angle),
               y + dx * math.sin(angle) + dy * math.cos(angle)) for dx, dy in coins]
    return (min(p[0] for p in points), max(p[0] for p in points),
            min(p[1] for p in points), max(p[1] for p in points))


# Pour le chevauchement, la boite d'un texte est ramenee a la hauteur reelle
# des glyphes, capitale et jambage compris -- 1.15 em est l'interligne, pas
# l'encombrement. Avec l'interligne, vingt paires d'annotations distantes de
# douze pixels etaient signalees a tort.
HAUTEUR_GLYPHE = 0.80
MARGE_CHEVAUCHEMENT = 0.5


def _coins_texte(attrs, contenu, hauteur_em):
    x, y = float(_attribut(attrs, "x", 0)), float(_attribut(attrs, "y", 0))
    taille = float(_attribut(attrs, "font-size", 13))
    ancre = _attribut(attrs, "text-anchor", "start")
    tourne = RE_SVG_ROTATE.search(attrs)
    angle = math.radians(float(tourne.group(1))) if tourne else 0.0
    largeur, hauteur = len(contenu) * taille * LARGEUR_CARACTERE, taille * hauteur_em
    x0 = {"end": x - largeur, "middle": x - largeur / 2}.get(ancre, x)
    coins = [(x0 - x, -hauteur / 2), (x0 + largeur - x, -hauteur / 2),
             (x0 + largeur - x, hauteur / 2), (x0 - x, hauteur / 2)]
    return [(x + dx * math.cos(angle) - dy * math.sin(angle),
             y + dx * math.sin(angle) + dy * math.cos(angle)) for dx, dy in coins]


def _se_touchent(A, B):
    """Deux rectangles TOURNES se recouvrent-ils ? (axes separateurs)

    Une boite alignee sur les axes ne suffit pas : sur des annees inclinees a
    quarante-cinq degres, elle conclut a trente-deux chevauchements la ou il
    n'y en a aucun.
    """
    for P in (A, B):
        for i in range(4):
            ax, ay = P[(i + 1) % 4][0] - P[i][0], P[(i + 1) % 4][1] - P[i][1]
            norme = math.hypot(ax, ay) or 1.0
            nx, ny = -ay / norme, ax / norme
            pa = [nx * x + ny * y for x, y in A]
            pb = [nx * x + ny * y for x, y in B]
            if max(pa) - MARGE_CHEVAUCHEMENT <= min(pb) \
                    or max(pb) - MARGE_CHEVAUCHEMENT <= min(pa):
                return False
    return True


def controler_figures_chevauchent(c):
    """Refuse deux etiquettes de figure ecrites l'une sur l'autre.

    Meme silence que le debordement : rien n'echoue, le texte se superpose et
    devient illisible, et on ne le voit qu'en regardant la figure publiee. Il y
    en avait soixante paires, sur six figures -- des graduations tous les dix
    sur une echelle qui va jusqu'a cinq cents, seize noms tasses en haut d'un
    graphique de pentes, deux fins de courbe a la meme hauteur.
    """
    dossier = os.path.join(RACINE, "_includes", "graphiques")
    if not os.path.isdir(dossier):
        return
    for nom in sorted(os.listdir(dossier)):
        if not nom.endswith(".svg"):
            continue
        texte = open(os.path.join(dossier, nom), encoding="utf-8").read()
        boites = []
        for m in RE_SVG_TEXTE.finditer(texte):
            contenu = html.unescape(m.group("contenu"))
            if contenu.strip():
                boites.append((contenu,
                               _coins_texte(m.group("attrs"), contenu, HAUTEUR_GLYPHE)))
        for i in range(len(boites)):
            for j in range(i + 1, len(boites)):
                if _se_touchent(boites[i][1], boites[j][1]):
                    c.erreur(f"{nom} : « {boites[i][0][:26]} » et "
                             f"« {boites[j][0][:26]} » s'ecrivent l'une sur l'autre")


def controler_portees(c):
    """Refuse que deux figures partagent une classe de portee.

    Certaines figures embarquent leur propre feuille de style -- la
    surbrillance des diagrammes en arcs, celle des courbes a plusieurs series.
    Un <style> pose dans un SVG INLINE n'est pas encapsule : ses regles
    s'appliquent a toute la page. Chaque selecteur est donc prefixe par une
    classe de portee, tiree du titre de la figure par _portee() dans
    tools/graphiques.py.

    Deux figures qui partageraient cette classe melangeraient leurs regles des
    qu'elles se trouveraient sur la meme page : la serie 0 de l'une allumerait
    la serie 0 de l'autre. Rien ne le signalerait -- ni la construction, ni le
    controle des donnees -- et on ne le verrait qu'en survolant la bonne figure
    de la bonne page.

    Le risque est reel et non theorique : _portee() TRONQUE le titre a
    quarante-quatre caracteres. Deux titres qui commencent pareil donnent la
    meme portee.
    """
    dossier = os.path.join(RACINE, "_includes", "graphiques")
    if not os.path.isdir(dossier):
        return
    vues = {}
    for nom in sorted(os.listdir(dossier)):
        if not nom.endswith(".svg"):
            continue
        texte = open(os.path.join(dossier, nom), encoding="utf-8").read()
        m = re.search(r'<svg class="graphique surbrillance ([a-z0-9-]+)"', texte)
        if not m:
            continue
        portee = m.group(1)
        if portee in vues:
            c.erreur(f"{nom} et {vues[portee]} partagent la portee "
                     f"« {portee} » : leurs feuilles de style se melangeront")
        vues[portee] = nom


def controler_figures(c):
    """Refuse un texte de figure qui sort du cadre.

    Un SVG ne mesure pas son texte et n'en rogne rien : une etiquette trop
    longue s'ecrit simplement dans le vide, hors du viewBox, ou le navigateur
    ne l'affiche pas. Rien ne le signale -- ni la construction, ni le controle
    des donnees -- et on ne le decouvre qu'en regardant la figure une fois
    publiee. Il y en avait cinquante-deux, sur vingt-huit figures.

    Le calcul est approche : la largeur d'un caractere est estimee. C'est
    suffisant pour ce qu'on cherche, et TOLERANCE_CADRE evite de crier pour un
    demi-caractere.
    """
    dossier = os.path.join(RACINE, "_includes", "graphiques")
    if not os.path.isdir(dossier):
        return
    fautes = 0
    for nom in sorted(os.listdir(dossier)):
        if not nom.endswith(".svg"):
            continue
        texte = open(os.path.join(dossier, nom), encoding="utf-8").read()
        cadre = RE_SVG_VIEWBOX.search(texte)
        if not cadre:
            continue
        large, hauteur = float(cadre.group(1)), float(cadre.group(2))
        for m in RE_SVG_TEXTE.finditer(texte):
            contenu = html.unescape(m.group("contenu"))
            if not contenu.strip():
                continue
            x0, x1, y0, y1 = _boite_texte(m.group("attrs"), contenu)
            t = TOLERANCE_CADRE
            if x0 < -t or x1 > large + t or y0 < -t or y1 > hauteur + t:
                fautes += 1
                c.erreur(f"{nom} : « {contenu[:40]} » sort du cadre "
                         f"(x {x0:.0f}..{x1:.0f}, y {y0:.0f}..{y1:.0f}, "
                         f"cadre {large:.0f}x{hauteur:.0f})")
    return fautes


def main():
    c = Controle()
    jeux = charger_donnees()

    permaliens = {}
    gabarits = {}
    entetes = {}
    for chemin in sorted(pages()):
        rel = os.path.relpath(chemin, RACINE)
        texte = open(chemin, encoding="utf-8").read()

        m = RE_FRONT.match(texte)
        if not m:
            c.erreur(f"{rel} : pas de front matter — Jekyll ne rendra pas cette page")
            continue
        try:
            entete = donnees.charger(m.group(1)) or {}
        except yaml.YAMLError as e:
            c.erreur(f"{rel} : front matter illisible — {e}")
            continue

        # La page d'erreur n'est pas une page de contenu : elle n'a rien a
        # faire dans un moteur, donc pas de description a lui reclamer.
        if rel != "404.html":
            entetes[rel] = entete
        if not entete.get("layout"):
            c.erreur(f"{rel} : `layout` manquant")
        if not entete.get("title"):
            c.avertir(f"{rel} : `title` manquant")
        lien = entete.get("permalink")
        if lien:
            # Un permalien qui designe un FICHIER (404.html, robots.txt) n'a pas
            # a finir par une barre oblique : ce n'est pas un repertoire, et
            # GitHub Pages ne servirait pas la page d'erreur sous « /404.html/ ».
            fichier = re.search(r"\.[a-z0-9]{2,4}$", lien, re.I)
            if not lien.startswith("/") or (not lien.endswith("/") and not fichier):
                c.avertir(f"{rel} : permalink « {lien} » sans barre oblique initiale ou finale")
            if lien in permaliens:
                c.erreur(f"{rel} : permalink « {lien} » deja pris par {permaliens[lien]}")
            permaliens[lien] = rel
            gabarits[lien] = entete.get("layout")
        elif rel == "index.md":
            # L'accueil n'a pas de permalink : son URL est la racine. Il figure
            # bien dans navigation.yml, sous « / ».
            permaliens["/"] = rel
        elif rel != "404.html":
            c.avertir(f"{rel} : pas de permalink explicite, l'URL suivra le chemin du fichier")

        corps = sans_commentaires(texte[m.end():])

        for inc in RE_INCLUDE.findall(corps):
            if not os.path.exists(os.path.join(RACINE, "_includes", inc)):
                c.erreur(f"{rel} : inclusion introuvable — _includes/{inc}")

        # chemins ecrits en toutes lettres
        for motif, conseil in LIQUID_INTERDIT:
            if motif in corps:
                c.erreur(f"{rel} : `{motif}` interdit dans un gabarit — {conseil}")

        for nom_balise in balises_en_commentaire(texte[m.end():]):
            c.erreur(f"{rel} : balise `{nom_balise}` ecrite DANS un commentaire "
                     f"Liquid — elle n'y est pas inerte, elle ouvre un bloc que "
                     f"`endcomment` ne ferme pas et la construction s'arrete")

        for parcours in RE_DATA.findall(corps):
            ok, _ = resoudre(jeux, parcours)
            if not ok:
                c.erreur(f"{rel} : site.data.{parcours} n'existe pas dans _data/")

        # chemins passant par un {% assign %}
        alias = {nom: cible for nom, cible in RE_ASSIGN.findall(corps)}
        for nom, suite in RE_VAR.findall(corps):
            if nom not in alias:
                continue
            parcours = f"{alias[nom]}.{suite.rstrip('.')}"
            # `first`, `last` et `size` ne sont pas des cles de donnees : ce
            # sont des acces de Liquid, et ils peuvent tomber AU MILIEU d'un
            # chemin -- `depouillement.first.part` designe la premiere ligne
            # d'une liste, puis son champ. Les retirer seulement en fin de
            # chemin faisait echouer un chemin parfaitement valide.
            parcours = ".".join(x for x in parcours.split(".")
                                if x not in ("first", "last", "size"))
            ok, _ = resoudre(jeux, parcours)
            if not ok:
                c.erreur(f"{rel} : {nom}.{suite} → site.data.{parcours} n'existe pas")

    # Les GABARITS, que la boucle ci-dessus ne voit pas -- elle ne parcourt que
    # les pages. C'etait un trou : depuis que les fiches existent, l'essentiel
    # des acces aux donnees vit dans _layouts/fiche-aventurier.html et
    # _layouts/fiche-saison.html. Une cle mal ecrite y rendrait 565 fiches
    # vides, sans une erreur de construction et sans que rien ne le signale.
    for sous in ("_layouts", "_includes"):
        dossier = os.path.join(RACINE, sous)
        if not os.path.isdir(dossier):
            continue
        for nom in sorted(os.listdir(dossier)):
            if not nom.endswith(".html"):
                continue
            rel = os.path.join(sous, nom)
            corps = sans_commentaires(
                open(os.path.join(dossier, nom), encoding="utf-8").read())
            for inc in RE_INCLUDE.findall(corps):
                if not os.path.exists(os.path.join(RACINE, "_includes", inc)):
                    c.erreur(f"{rel} : inclusion introuvable — _includes/{inc}")
            for motif, conseil in LIQUID_INTERDIT:
                if motif in corps:
                    c.erreur(f"{rel} : `{motif}` interdit dans un gabarit — {conseil}")
            for nom_balise in balises_en_commentaire(
                    open(os.path.join(dossier, nom), encoding="utf-8").read()):
                c.erreur(f"{rel} : balise `{nom_balise}` ecrite DANS un commentaire "
                         f"Liquid — elle n'y est pas inerte, elle ouvre un bloc que "
                         f"`endcomment` ne ferme pas et la construction s'arrete")
            for parcours in RE_DATA.findall(corps):
                ok, _ = resoudre(jeux, parcours)
                if not ok:
                    c.erreur(f"{rel} : site.data.{parcours} n'existe pas dans _data/")

    # configuration
    config = donnees.charger(open(os.path.join(RACINE, "_config.yml"), encoding="utf-8"))
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

    controler_seo(c, entetes)
    controler_figures(c)
    controler_figures_chevauchent(c)
    controler_portees(c)
    controler_portraits(c)
    controler_comptes_annonces(c)
    controler_calculs_liquid(c)
    controler_donnees_structurees(c)
    controler_yaml_ambigu(c)
    controler_virgule_decimale(c)
    controler_affirmations_pages(c)
    controler_titres_minuscules(c)
    controler_accord_rang(c)
    controler_navigation(c, permaliens, gabarits)
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
    print(f"jeux de donnees  : {', '.join(sorted(jeux))}")

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
