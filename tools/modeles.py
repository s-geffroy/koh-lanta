#!/usr/bin/env python3
"""Modeles et inference sur le jeu Koh-Lanta.

Les autres modules de `tools/` decrivent : ils comptent, ils font des parts et
des moyennes. Celui-ci modelise -- il estime des variables qu'aucune colonne ne
porte, et il teste les ecarts au lieu de se contenter de les afficher.

Trois regles heritees du depot :

  * **aucune valeur devinee** — une valeur manquante reste absente ;
  * **reproductibilite** — jamais de boucle sur un ensemble non trie ;
  * **une seule verite** — ce qui est calcule ici entre dans `_data/stats.yml`,
    commite, et le site ne fait que l'afficher.

Trois regles propres a ce module :

  * **jamais de p-value sans taille d'effet**, jamais de taille d'effet sans
    intervalle. Un « c'est significatif » sans ampleur ne dit rien ;
  * **tous les tests sont declares** dans le registre rendu par `tout()`, et
    corriges ensemble par Benjamini-Hochberg. Une quinzaine de tests sortent
    un « resultat » par pur hasard : annoncer la liste d'avance est ce qui
    rend la correction honnete ;
  * **tout tirage derive de GRAINE.** Sans cela la construction n'est pas
    reproductible et le site changerait tout seul d'une publication a l'autre.
    `tools/verifie_site.py` le controle par arbre syntaxique.
"""
import numpy as np

GRAINE = 20260828

# Nombre de tirages des tests de permutation. 10 000 donne une p-value au
# millieme, ce qui suffit largement : au-dela, la limite n'est plus le nombre
# de tirages mais les 26 saisons du jeu de donnees.
N_PERMUTATIONS = 10_000

# Nombre de reechantillonnages bootstrap pour les intervalles.
N_BOOTSTRAP = 2_000

ABANDONS = ("abandon_medical", "abandon_volontaire")


def rng(nom):
    """Un generateur par usage, tous derives de GRAINE.

    Chaque usage a sa propre suite : ajouter un test quelque part ne deplace
    donc pas les chiffres d'un autre, et un resultat publie ne bouge pas parce
    qu'on a ajoute une analyse a cote.
    """
    return np.random.default_rng(
        np.random.SeedSequence([GRAINE, *(ord(c) for c in nom)]))


def _arr(x, n=1):
    return None if x is None else round(float(x), n)


def _classiques(par_saison, parts):
    """Les participations des saisons classiques achevees.

    Les editions speciales font revenir les memes personnes : les melanger au
    casting ordinaire fausserait tout ce qui suit. Elles ont leur propre page.
    """
    out = []
    for p in parts:
        s = par_saison.get(p["saison"]) or {}
        if s.get("annulee") or s.get("en_cours") or s.get("speciale"):
            continue
        out.append(p)
    return out


def benjamini_hochberg(pvaleurs):
    """Rend les p-values ajustees, dans l'ordre d'entree.

    Sur quinze tests au seuil de 5 %, on attend presque un « resultat » qui
    n'en est pas un. La procedure controle la part de fausses decouvertes
    parmi les tests declares significatifs -- elle ne supprime pas le risque,
    elle le borne.
    """
    n = len(pvaleurs)
    if not n:
        return []
    ordre = sorted(range(n), key=lambda i: pvaleurs[i])
    ajustees = [0.0] * n
    precedent = 1.0
    for rang, i in enumerate(reversed(ordre), start=1):
        k = n - rang + 1
        precedent = min(precedent, pvaleurs[i] * n / k)
        ajustees[i] = min(1.0, precedent)
    return ajustees


def _p_bilaterale(observe, nulle):
    """p-value de permutation, bilaterale, avec la correction de continuite.

    Le +1 au numerateur et au denominateur evite d'annoncer p = 0, qui serait
    faux : avec 10 000 tirages on ne sait rien en dessous de 1/10 001.
    """
    nulle = np.asarray(nulle, dtype=float)
    centre = float(np.mean(nulle))
    extremes = int(np.sum(np.abs(nulle - centre) >= abs(observe - centre) - 1e-12))
    return (extremes + 1) / (len(nulle) + 1)


def _histogramme(nulle, observe, cases=28):
    """Distribution nulle prete a dessiner : des cases, et le repere observe."""
    nulle = np.asarray(nulle, dtype=float)
    bas = min(float(nulle.min()), observe)
    haut = max(float(nulle.max()), observe)
    if haut - bas < 1e-12:
        haut = bas + 1.0
    marge = (haut - bas) * 0.05
    bas, haut = bas - marge, haut + marge
    effectifs, bords = np.histogram(nulle, bins=cases, range=(bas, haut))
    return {
        "bornes": [_arr(bas, 4), _arr(haut, 4)],
        "cases": [int(x) for x in effectifs],
        "largeur_case": _arr((haut - bas) / cases, 6),
        "observe": _arr(observe, 4),
        "moyenne_nulle": _arr(float(nulle.mean()), 4),
    }


def _test(cle, libelle, question, observe, nulle, unite="", lecture=""):
    """Un test de permutation, sous la forme publiee.

    `ecart_relatif` est la taille d'effet : de combien l'observe s'ecarte de ce
    qu'un tirage au hasard produirait, en ecarts-types de la distribution
    nulle. C'est elle qui dit si le resultat compte, la p-value ne disant que
    s'il est distinguable du hasard.
    """
    nulle = np.asarray(nulle, dtype=float)
    ecart_type = float(nulle.std(ddof=1)) or float("nan")
    return {
        "cle": cle,
        "libelle": libelle,
        "question": question,
        "observe": _arr(observe, 3),
        "attendu": _arr(float(nulle.mean()), 3),
        "unite": unite,
        "ecart_types": _arr((observe - float(nulle.mean())) / ecart_type, 2),
        "p": _arr(_p_bilaterale(observe, nulle), 4),
        "tirages": int(len(nulle)),
        "lecture": lecture,
        "nulle": _histogramme(nulle, observe),
    }


# --- A. La recette du casting ---------------------------------------------

TRANCHES_AGE = [(18, 24, "18-24 ans"), (25, 29, "25-29 ans"), (30, 34, "30-34 ans"),
                (35, 39, "35-39 ans"), (40, 44, "40-44 ans"), (45, 99, "45 ans et plus")]


def _tranche(age):
    for bas, haut, libelle in TRANCHES_AGE:
        if bas <= age <= haut:
            return libelle
    return None


def _acm(modalites):
    """Analyse des correspondances multiples, par decomposition en valeurs singulieres.

    Quatre variables qualitatives -- age, sexe, metier, couleur -- ne se
    projettent pas dans un plan par une moyenne : il faut passer par le tableau
    disjonctif et le decomposer. L'ACM rend des axes latents, c'est-a-dire les
    directions selon lesquelles les castings se distinguent reellement, sans
    qu'aucune colonne ne les porte.

    Rend (coordonnees des individus, inertie de chaque axe, noms des modalites,
    coordonnees des modalites).
    """
    noms = []
    for i in range(len(modalites[0])):
        vues = sorted({ligne[i] for ligne in modalites})
        noms.extend((i, v) for v in vues)
    position = {nv: j for j, nv in enumerate(noms)}

    n, q = len(modalites), len(modalites[0])
    Z = np.zeros((n, len(noms)))
    for a, ligne in enumerate(modalites):
        for i, v in enumerate(ligne):
            Z[a, position[(i, v)]] = 1.0

    total = Z.sum()
    P = Z / total
    masses_l = P.sum(axis=1)
    masses_c = P.sum(axis=0)
    attendu = np.outer(masses_l, masses_c)
    S = (P - attendu) / np.sqrt(np.outer(masses_l, masses_c))
    U, sigma, Vt = np.linalg.svd(S, full_matrices=False)

    # Signe fixe : la SVD ne definit chaque axe qu'au signe pres, et un axe
    # retourne d'une execution a l'autre ferait basculer toute la figure. On
    # impose que la premiere coordonnee non nulle soit positive.
    for k in range(len(sigma)):
        premiere = next((x for x in U[:, k] if abs(x) > 1e-9), 0.0)
        if premiere < 0:
            U[:, k] *= -1
            Vt[k, :] *= -1

    coord_l = U * sigma / np.sqrt(masses_l)[:, None]
    coord_c = (Vt.T * sigma) / np.sqrt(masses_c)[:, None]
    inerties = sigma ** 2
    inerties = inerties / inerties.sum() * 100 if inerties.sum() else inerties
    return coord_l, inerties, noms, coord_c


def _repartition(valeurs, univers):
    total = len(valeurs) or 1
    compte = {u: 0 for u in univers}
    for v in valeurs:
        compte[v] = compte.get(v, 0) + 1
    return np.array([compte[u] / total for u in univers])


def recette_casting(par_saison, parts):
    """Le casting est-il une recette ?

    Quatre questions, quatre tests de permutation. Chacune compare ce qu'on
    observe a ce qu'un tirage au hasard, a effectifs de saison identiques,
    produirait. Ce n'est PAS une comparaison a la population francaise : c'est
    une comparaison au meme vivier, rebattu.
    """
    lignes = []
    for p in _classiques(par_saison, parts):
        age, genre, csp, couleur = (p.get("age"), p.get("genre"),
                                    p.get("_csp"), p.get("couleur"))
        tranche = _tranche(age) if age else None
        if not (tranche and genre and csp and couleur):
            continue
        lignes.append({
            "saison": p["saison"], "nom": p.get("nom_complet") or p.get("nom"),
            "annee": p["_annee"], "titre": (p["_saison"] or {}).get("titre"),
            "age": age, "genre": genre, "csp": csp, "couleur": couleur,
            "tranche": tranche,
        })
    if len(lignes) < 100:
        return {}

    saisons = sorted({l["saison"] for l in lignes})
    index_saison = {s: i for i, s in enumerate(saisons)}
    appartenance = np.array([index_saison[l["saison"]] for l in lignes])
    tailles = np.array([int((appartenance == i).sum()) for i in range(len(saisons))])

    # --- les archetypes -----------------------------------------------------
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    # Trois variables, et pas quatre : le bandeau est exclu. Ce n'est pas un
    # trait de la personne recrutee, c'est une place donnee a l'arrivee -- et
    # comme les couleurs en jeu changent d'une saison a l'autre, l'y laisser
    # rendrait le « melange de profils » different par construction d'une
    # saison a l'autre. Le test qui suit n'aurait plus rien mesure du casting.
    coord, inerties, noms_mod, coord_mod = _acm(
        [(l["tranche"], l["genre"], l["csp"]) for l in lignes])
    plan = coord[:, :4]

    meilleur_k, meilleur_score = 2, -2.0
    silhouettes = []
    # On balaie jusqu'a dix groupes, pas jusqu'a six : s'arreter a l'endroit
    # ou la silhouette est encore en train de monter donnerait un maximum de
    # bord, qu'on lirait a tort comme un nombre naturel de familles.
    # Un decoupage qui isole deux personnes n'est pas un archetype : il gonfle
    # la silhouette en mettant a part des points extremes. On exige donc que le
    # plus petit groupe pese au moins 2 % du casting.
    plancher = max(3, int(0.02 * len(plan)))
    for k in range(2, 11):
        etiquettes = KMeans(n_clusters=k, n_init=25, random_state=GRAINE).fit_predict(plan)
        score = float(silhouette_score(plan, etiquettes))
        petit = int(np.bincount(etiquettes).min())
        silhouettes.append({"k": k, "score": _arr(score, 3), "plus_petit": petit})
        if petit >= plancher and score > meilleur_score + 1e-9:
            meilleur_k, meilleur_score = k, score
    groupes = KMeans(n_clusters=meilleur_k, n_init=25,
                     random_state=GRAINE).fit_predict(plan)

    # Un groupe se nomme par ce qui l'y distingue le plus du reste : la
    # modalite dont la part interne depasse le plus sa part generale.
    archetypes = []
    for g in range(meilleur_k):
        dedans = [l for l, e in zip(lignes, groupes) if e == g]
        traits = []
        # Les memes trois variables que la classification, et pas le bandeau :
        # nommer un groupe par une couleur qu'il n'a pas servi a former ferait
        # croire a un lien qui n'existe pas.
        for champ in ("tranche", "genre", "csp"):
            univers = sorted({l[champ] for l in lignes})
            part_g = _repartition([l[champ] for l in dedans], univers)
            part_t = _repartition([l[champ] for l in lignes], univers)
            j = int(np.argmax(part_g - part_t))
            if part_g[j] - part_t[j] > 0.05:
                traits.append((univers[j], float(part_g[j] * 100)))
        archetypes.append({
            "code": int(g),
            "libelle": " · ".join(m for m, _ in traits) if traits else "le tout-venant",
            "traits": [{"modalite": m, "part": _arr(v)} for m, v in traits],
            "effectif": len(dedans),
            "part": _arr(100.0 * len(dedans) / len(lignes)),
            "age_median": _arr(float(np.median([l["age"] for l in dedans]))),
            "part_femmes": _arr(100.0 * sum(1 for l in dedans if l["genre"] == "f") / len(dedans)),
        })
    archetypes.sort(key=lambda a: (-a["effectif"], a["code"]))

    tests = []

    # --- 1. la parite est-elle trop reguliere ? -----------------------------
    femmes = np.array([sum(1 for l, s in zip(lignes, appartenance)
                           if s == i and l["genre"] == "f") for i in range(len(saisons))])
    ecart_observe = float(np.mean(np.abs(femmes - tailles / 2)))
    g = rng("parite")
    nulle = np.array([float(np.mean(np.abs(g.binomial(tailles, 0.5) - tailles / 2)))
                      for _ in range(N_PERMUTATIONS)])
    tests.append(_test(
        "parite", "L'equilibre hommes-femmes",
        "L'ecart a la parite est-il plus petit que ce qu'un tirage a pile ou face donnerait ?",
        ecart_observe, nulle, unite="personnes",
        lecture="Un ecart observe plus PETIT que l'attendu est la signature d'un quota : "
                "le hasard, lui, produit des castings desequilibres de temps en temps."))

    # --- 2. l'etendue des ages est-elle voulue ? ----------------------------
    ages = np.array([l["age"] for l in lignes], dtype=float)
    def ecart_intra(vecteur):
        return float(np.mean([vecteur[appartenance == i].std(ddof=1)
                              for i in range(len(saisons)) if tailles[i] > 1]))
    g = rng("ages")
    observe = ecart_intra(ages)
    nulle = np.array([ecart_intra(g.permutation(ages)) for _ in range(N_PERMUTATIONS)])
    tests.append(_test(
        "etendue_ages", "L'ecart d'age dans un meme casting",
        "Un casting melange-t-il les ages plus qu'un tirage au hasard ne le ferait ?",
        observe, nulle, unite="annees",
        lecture="Rebattre les aventuriers entre saisons donne l'ecart-type general. "
                "Un ecart observe PLUS GRAND veut dire qu'on place expres un jeune "
                "et un ancien dans chaque casting."))

    # --- 3. faut-il un representant de chaque famille de metier ? -----------
    familles = sorted({l["csp"] for l in lignes})
    csp_vec = np.array([familles.index(l["csp"]) for l in lignes])
    def couverture(vecteur):
        return float(sum(len(set(vecteur[appartenance == i])) for i in range(len(saisons))))
    g = rng("metiers")
    observe = couverture(csp_vec)
    nulle = np.array([couverture(g.permutation(csp_vec)) for _ in range(N_PERMUTATIONS)])
    tests.append(_test(
        "familles_metiers", "La variete des metiers",
        "Un casting couvre-t-il plus de familles de metiers qu'un tirage au hasard ?",
        observe, nulle, unite="cases remplies",
        lecture="On compte, pour chaque saison, le nombre de familles de metiers "
                "representees. Un total observe PLUS GRAND veut dire qu'on veille "
                "a n'oublier aucune famille."))

    # --- 4. les saisons se ressemblent-elles trop ? -------------------------
    codes = np.array(groupes)
    univers = list(range(meilleur_k))
    global_ = _repartition(list(codes), univers)
    def distance(vecteur):
        d = 0.0
        for i in range(len(saisons)):
            p = _repartition(list(vecteur[appartenance == i]), univers)
            d += float(np.sum((p - global_) ** 2 / np.where(global_ > 0, global_, 1)))
        return d / len(saisons)
    g = rng("archetypes")
    observe = distance(codes)
    nulle = np.array([distance(g.permutation(codes)) for _ in range(N_PERMUTATIONS)])
    tests.append(_test(
        "melange_archetypes", "Le melange d'archetypes",
        "Chaque saison contient-elle toujours le meme melange de profils ?",
        observe, nulle, unite="",
        lecture="Distance entre le melange de profils d'une saison et le melange "
                "general. Un observe PLUS PETIT que l'attendu veut dire que les "
                "saisons se ressemblent plus que le hasard ne l'expliquerait."))

    # --- 5 et 6. les deux tribus sont-elles construites a l'equilibre ? -----
    # Une saison classique part sur deux tribus. Si elles etaient tirees au
    # hasard dans le casting, elles differeraient regulierement -- par leur
    # part de femmes, par leur age moyen. Un ecart observe trop PETIT veut dire
    # qu'elles sont composees, pas tirees. C'est un geste de production que
    # rien n'annonce a l'ecran.
    tribus_extremes = []
    duos = []
    for s_id in saisons:
        dedans = [l for l in lignes if l["saison"] == s_id]
        couleurs = sorted({l["couleur"] for l in dedans})
        if len(couleurs) != 2 or min(sum(1 for l in dedans if l["couleur"] == c)
                                     for c in couleurs) < 4:
            continue
        duos.append((dedans, couleurs))

    if duos:
        def ecart_femmes(tirage):
            total = 0.0
            for (dedans, couleurs), affectation in zip(duos, tirage):
                parts = []
                for c in couleurs:
                    membres = [l for l, a in zip(dedans, affectation) if a == c]
                    parts.append(sum(1 for l in membres if l["genre"] == "f") / len(membres))
                total += abs(parts[0] - parts[1])
            return 100.0 * total / len(duos)

        def _ecarts_age(tirage):
            ecarts = []
            for (dedans, couleurs), affectation in zip(duos, tirage):
                moyennes = []
                for c in couleurs:
                    membres = [l for l, a in zip(dedans, affectation) if a == c]
                    moyennes.append(float(np.mean([l["age"] for l in membres])))
                ecarts.append(abs(moyennes[0] - moyennes[1]))
            return ecarts

        def ecart_age(tirage):
            return float(np.mean(_ecarts_age(tirage)))

        # La moyenne se laisse emporter par trois saisons dont les tribus
        # opposent franchement deux generations. La mediane, elle, ne bouge pas
        # pour trois valeurs sur vingt : si l'ecart etait une regle generale et
        # non l'affaire de quelques editions, elle le montrerait aussi.
        def ecart_age_median(tirage):
            return float(np.median(_ecarts_age(tirage)))

        reel = [[l["couleur"] for l in dedans] for dedans, _ in duos]
        g = rng("tribus")
        tirages = [[g.permutation(np.array(a, dtype=object)).tolist() for a in reel]
                   for _ in range(N_PERMUTATIONS)]
        tests.append(_test(
            "tribus_femmes", "La composition des deux tribus",
            "Les deux tribus de depart sont-elles plus semblables en part de "
            "femmes qu'un tirage au hasard ne les ferait ?",
            ecart_femmes(reel), np.array([ecart_femmes(t) for t in tirages]),
            unite="points de %",
            lecture="On rebat les bandeaux a l'interieur de chaque saison. Un ecart "
                    "observe PLUS PETIT que l'attendu veut dire que les tribus sont "
                    "composees a l'equilibre, pas tirees au sort."))
        tests.append(_test(
            "tribus_ages", "L'age moyen des deux tribus",
            "Les deux tribus de depart ont-elles des ages moyens plus proches "
            "qu'un tirage au hasard ne les ferait ?",
            ecart_age(reel), np.array([ecart_age(t) for t in tirages]),
            unite="annees",
            lecture="Meme methode, sur l'age moyen de chaque bandeau. Un ecart "
                    "observe PLUS GRAND que l'attendu veut dire l'inverse d'un "
                    "equilibre : deux tribus construites pour differer."))
        tests.append(_test(
            "tribus_ages_mediane", "L'age des deux tribus, a la mediane",
            "Le meme ecart, mesure a la mediane : est-il general, ou porte par "
            "quelques saisons ?",
            ecart_age_median(reel), np.array([ecart_age_median(t) for t in tirages]),
            unite="annees",
            lecture="La mediane ignore les valeurs extremes. Si elle ne s'ecarte "
                    "pas, c'est que l'ecart moyen tient a quelques editions et non "
                    "a une regle de composition."))
        ecarts_reels = sorted(zip(_ecarts_age(reel), [d[0][0]["saison"] for d in duos]),
                              reverse=True)
        tribus_extremes = [{"saison": s_id, "ecart": _arr(e),
                            "titre": (par_saison.get(s_id) or {}).get("titre"),
                            "annee": (par_saison.get(s_id) or {}).get("annee")}
                           for e, s_id in ecarts_reels[:3]]

    # --- sensibilite : permuter a l'interieur de chaque decennie ------------
    # Le casting a derive en vingt-cinq ans. Rebattre toutes les saisons
    # ensemble melange donc deux choses : la recette, et l'epoque. On refait
    # l'essentiel des tests en ne rebattant qu'a l'interieur d'une decennie.
    decennie = np.array([(l["annee"] // 10) * 10 for l in lignes])
    g = rng("sensibilite")
    def permuter_par_bloc(vecteur):
        sortie = vecteur.copy()
        for d in sorted(set(decennie.tolist())):
            m = decennie == d
            sortie[m] = g.permutation(vecteur[m])
        return sortie
    sensibilite = []
    for cle, vecteur, fonction in (("etendue_ages", ages, ecart_intra),
                                   ("familles_metiers", csp_vec, couverture),
                                   ("melange_archetypes", codes, distance)):
        obs = fonction(vecteur)
        nulle_b = np.array([fonction(permuter_par_bloc(vecteur)) for _ in range(1000)])
        sensibilite.append({
            "cle": cle,
            "p": _arr(_p_bilaterale(obs, nulle_b), 4),
            "attendu": _arr(float(nulle_b.mean()), 3),
            "observe": _arr(obs, 3),
        })

    return {
        "effectif": len(lignes),
        "saisons": len(saisons),
        "duos_de_tribus": len(duos),
        "tribus_les_plus_contrastees": tribus_extremes,
        "archetypes": archetypes,
        "nb_archetypes": meilleur_k,
        "silhouette": _arr(meilleur_score, 3),
        "silhouettes": silhouettes,
        "inertie_axes": [_arr(float(x)) for x in inerties[:2]],
        "carte": [{"x": _arr(float(coord[i, 0]), 3), "y": _arr(float(coord[i, 1]), 3),
                   "groupe": int(groupes[i]), "nom": lignes[i]["nom"],
                   "detail": f'{lignes[i]["nom"]} — {lignes[i]["tranche"]}, '
                             f'{lignes[i]["csp"]}'}
                  for i in range(len(lignes))],
        "modalites": [{"x": _arr(float(coord_mod[j, 0]), 3),
                       "y": _arr(float(coord_mod[j, 1]), 3),
                       "libelle": str(noms_mod[j][1])}
                      for j in range(len(noms_mod))],
        "tests": tests,
        "sensibilite": sensibilite,
    }


# --- B. Ce qui est joue au casting ----------------------------------------

def _matrice_casting(par_saison, parts):
    """Les seules variables connues le jour du casting.

    Aucune information de jeu n'entre ici : ni epreuve gagnee, ni voix recue,
    ni jour de sortie. La question est de savoir ce qu'on pourrait pronostiquer
    en ne connaissant que la fiche d'inscription.
    """
    lignes = []
    for p in _classiques(par_saison, parts):
        if not (p.get("age") and p.get("genre") and p.get("_csp")
                and p.get("couleur") and p.get("_survie") is not None):
            continue
        lignes.append(p)
    if not lignes:
        return None

    cspx = sorted({p["_csp"] for p in lignes})
    couleurs = sorted({p["couleur"] for p in lignes})
    tailles = {}
    for p in lignes:
        tailles[p["saison"]] = tailles.get(p["saison"], 0) + 1

    noms = (["age", "age_centre_carre", "femme", "taille_casting", "annee"]
            + [f"metier:{c}" for c in cspx] + [f"couleur:{c}" for c in couleurs])
    X, y_vainqueur, y_survie, groupes = [], [], [], []
    for p in lignes:
        age = float(p["age"])
        v = [age, (age - 34.0) ** 2 / 100.0, 1.0 if p["genre"] == "f" else 0.0,
             float(tailles[p["saison"]]), float(p["_annee"])]
        v += [1.0 if p["_csp"] == c else 0.0 for c in cspx]
        v += [1.0 if p["couleur"] == c else 0.0 for c in couleurs]
        X.append(v)
        y_vainqueur.append(1 if p.get("sort") == "vainqueur" else 0)
        y_survie.append(float(p["_survie"]))
        groupes.append(p["saison"])
    return (np.array(X), np.array(y_vainqueur), np.array(y_survie),
            np.array(groupes), noms, lignes)


def _rang_du_vainqueur(scores, groupes, y):
    """Rang moyen du vrai vainqueur dans le classement de son propre casting.

    C'est la metrique lisible : le modele ordonne les vingt candidats d'une
    saison, on regarde a quelle place il a mis celui qui a gagne. Le hasard
    donne (n+1)/2 ; 1 serait une prediction parfaite.
    """
    rangs, hasards = [], []
    for s in sorted(set(groupes.tolist())):
        m = groupes == s
        if y[m].sum() < 1:
            continue
        ordre = np.argsort(-scores[m], kind="stable")
        classement = np.empty(int(m.sum()), dtype=int)
        classement[ordre] = np.arange(1, int(m.sum()) + 1)
        rangs.append(float(np.mean(classement[y[m] == 1])))
        hasards.append((int(m.sum()) + 1) / 2.0)
    return float(np.mean(rangs)), float(np.mean(hasards)), rangs


def pronostic(par_saison, parts):
    """Peut-on pronostiquer une saison avec la seule fiche d'inscription ?

    Validation « une saison exclue a chaque tour » : on entraine sur toutes les
    saisons sauf une et on predit celle-la. Un decoupage au hasard serait
    tricher -- deux aventuriers d'un meme casting ne sont pas independants, et
    la moitie de la saison suffirait a deviner l'autre.
    """
    donnees = _matrice_casting(par_saison, parts)
    if donnees is None:
        return {}
    X, y_v, y_s, groupes, noms, lignes = donnees

    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.preprocessing import StandardScaler

    saisons = sorted(set(groupes.tolist()))
    scores_v = np.zeros(len(y_v))
    predits_s = np.zeros(len(y_s))
    predits_arbre = np.zeros(len(y_s))

    for s in saisons:
        test = groupes == s
        train = ~test
        echelle = StandardScaler().fit(X[train])
        Xa, Xe = echelle.transform(X[train]), echelle.transform(X[test])
        # 26 vainqueurs pour une vingtaine de variables : sans penalisation le
        # modele apprendrait le bruit par coeur. C = 0,1 est une penalisation
        # franche, choisie d'avance et non ajustee sur le resultat.
        scores_v[test] = LogisticRegression(
            C=0.1, max_iter=2000, random_state=GRAINE).fit(
                Xa, y_v[train]).decision_function(Xe)
        predits_s[test] = Ridge(alpha=10.0).fit(Xa, y_s[train]).predict(Xe)
        predits_arbre[test] = GradientBoostingRegressor(
            n_estimators=200, max_depth=2, learning_rate=0.05,
            random_state=GRAINE).fit(X[train], y_s[train]).predict(X[test])

    rang, hasard, rangs = _rang_du_vainqueur(scores_v, groupes, y_v)

    # Le modele nul : rebattre les scores a l'interieur de chaque saison. On
    # garde ainsi la structure des castings et on ne detruit que le lien entre
    # la fiche d'inscription et le resultat.
    g = rng("pronostic")
    nulle = []
    for _ in range(N_PERMUTATIONS):
        melange = scores_v.copy()
        for s in saisons:
            m = groupes == s
            melange[m] = g.permutation(scores_v[m])
        nulle.append(_rang_du_vainqueur(melange, groupes, y_v)[0])
    nulle = np.array(nulle)

    # Intervalle : on reechantillonne les SAISONS, pas les aventuriers. C'est
    # la saison qui est l'unite independante.
    g = rng("pronostic-bootstrap")
    tirs = g.integers(0, len(rangs), size=(N_BOOTSTRAP, len(rangs)))
    moyennes = np.array([float(np.mean([rangs[i] for i in t])) for t in tirs])
    intervalle = [_arr(float(np.percentile(moyennes, 2.5)), 2),
                  _arr(float(np.percentile(moyennes, 97.5)), 2)]

    def r2(vrai, predit):
        reste = float(np.sum((vrai - predit) ** 2))
        total = float(np.sum((vrai - vrai.mean()) ** 2))
        return 1.0 - reste / total if total else 0.0

    r2_lineaire, r2_arbre = r2(y_s, predits_s), r2(y_s, predits_arbre)

    # Importance par permutation, mesuree sur la metrique publiee : de combien
    # le rang du vainqueur se degrade quand on brouille une seule colonne.
    g = rng("importances")
    importances = []
    for j, nom in enumerate(noms):
        pertes = []
        for _ in range(30):
            Xb = X.copy()
            Xb[:, j] = g.permutation(Xb[:, j])
            sc = np.zeros(len(y_v))
            for s in saisons:
                test = groupes == s
                echelle = StandardScaler().fit(Xb[~test])
                sc[test] = LogisticRegression(
                    C=0.1, max_iter=2000, random_state=GRAINE).fit(
                        echelle.transform(Xb[~test]), y_v[~test]).decision_function(
                            echelle.transform(Xb[test]))
            pertes.append(_rang_du_vainqueur(sc, groupes, y_v)[0])
        importances.append({"variable": nom,
                            "perte": _arr(float(np.mean(pertes)) - rang, 2)})
    importances.sort(key=lambda d: (-(d["perte"] or 0), d["variable"]))

    test_rang = _test(
        "pronostic_vainqueur", "Pronostiquer le vainqueur au casting",
        "En ne connaissant que l'age, le sexe, le metier et la couleur, place-t-on "
        "le futur vainqueur plus haut que le hasard ne le ferait ?",
        rang, nulle, unite="rang moyen",
        lecture="Le modele classe les candidats d'une saison ; on releve la place "
                "qu'il donne a celui qui a gagne. Plus BAS que l'attendu veut dire "
                "qu'une part du resultat se joue au recrutement.")

    return {
        "effectif": len(lignes),
        "saisons": len(saisons),
        "vainqueurs": int(y_v.sum()),
        "variables": noms,
        "rang_moyen": _arr(rang, 2),
        "rang_hasard": _arr(hasard, 2),
        "rang_intervalle": intervalle,
        "r2_survie_lineaire": _arr(r2_lineaire, 3),
        "r2_survie_arbre": _arr(r2_arbre, 3),
        "importances": importances[:8],
        "tests": [test_rang],
        "classement": [
            {"nom": lignes[i].get("nom_complet") or lignes[i].get("nom"),
             "saison": lignes[i]["saison"],
             "score": _arr(float(scores_v[i]), 3),
             "vainqueur": bool(y_v[i])}
            for i in np.argsort(-scores_v)[:12]],
    }


# --- C. La force reelle, contre celle qu'on montre ------------------------

SEUIL_PLATEAUX = 8       # nombre minimal d'epreuves disputees pour etre classe
COUVERTURE_MINIMALE = 0.8  # part du casting dont on connait l'episode de sortie


def _plateaux(par_saison, parts, conseils, epreuves):
    """Reconstruit qui etait encore en jeu a chaque epreuve individuelle.

    `epreuves.yml` ne porte que les vainqueurs : aucune liste de participants
    n'existe dans les sources. Or un rapport « 7 victoires » ne veut rien dire
    sans savoir contre combien de monde, ni combien de fois. Le plateau se
    reconstruit donc a partir de l'episode de sortie de chacun.

    La reconstruction se controle elle-meme : le vainqueur d'une epreuve DOIT
    figurer dans le plateau qu'on lui reconstruit. Le taux d'echec est rendu
    avec le reste, et publie.
    """
    from indicateurs import _episode_de_sortie

    sortie, _ = _episode_de_sortie(conseils, parts, epreuves)
    par_s = {}
    for p in parts:
        par_s.setdefault(p["saison"], []).append(p)

    retenues = []
    for s_id, membres in par_s.items():
        s = par_saison.get(s_id) or {}
        if s.get("annulee") or s.get("en_cours"):
            continue
        connus = sum(1 for p in membres if (s_id, p["id"]) in sortie)
        if connus / len(membres) >= COUVERTURE_MINIMALE:
            retenues.append(s_id)
    retenues = sorted(retenues)

    plateaux, hors_plateau, sans_saison = [], 0, 0
    for e in epreuves:
        if e.get("forme") != "individuelle":
            continue
        if e["saison"] not in retenues:
            sans_saison += 1
            continue
        gagnants = [v["id"] for v in (e.get("vainqueurs") or [])
                    if v.get("type") == "personne" and v.get("id")]
        if len(gagnants) != 1:
            continue
        episode = int(e["episode"])
        champ = sorted(p["id"] for p in par_s[e["saison"]]
                       if sortie.get((e["saison"], p["id"]), -1) >= episode)
        if len(champ) < 3:
            continue
        if gagnants[0] not in champ:
            hors_plateau += 1
            continue
        plateaux.append({"saison": e["saison"], "episode": episode,
                         "champ": champ, "gagnant": gagnants[0]})
    return plateaux, hors_plateau, sans_saison, retenues


def _luce(plateaux, joueurs, alpha=0.5, beta=0.5, tours=500):
    """Modele de Luce : un gagnant parmi K, ajuste par l'algorithme MM.

    Chaque joueur recoit une force theta. La probabilite qu'il gagne une
    epreuve vaut sa force divisee par la somme des forces presentes. Le
    classement qui en sort est donc corrige de l'exposition ET de l'adversaire :
    gagner deux fois sur trois face aux finalistes ne vaut pas gagner deux fois
    sur trois au premier episode.

    La loi a priori Gamma(1+alpha, beta) est indispensable : sans elle, un
    joueur a zero victoire n'a pas d'estimation finie, et un joueur invaincu
    part a l'infini. Elle ramene doucement vers 1, la force moyenne.
    """
    index = {j: i for i, j in enumerate(joueurs)}
    victoires = np.zeros(len(joueurs))
    champs = []
    for p in plateaux:
        victoires[index[p["gagnant"]]] += 1
        champs.append(np.array([index[j] for j in p["champ"]], dtype=int))

    theta = np.ones(len(joueurs))
    for _ in range(tours):
        denominateur = np.full(len(joueurs), beta, dtype=float)
        for c in champs:
            s = theta[c].sum()
            if s > 0:
                denominateur[c] += 1.0 / s
        neuf = (victoires + alpha) / denominateur
        if np.max(np.abs(neuf - theta)) < 1e-10:
            theta = neuf
            break
        theta = neuf
    return theta, victoires, champs


def force(par_saison, parts, conseils, epreuves):
    """Le classement des athletes, corrige de l'exposition et de l'adversaire."""
    plateaux, hors_plateau, sans_saison, retenues = _plateaux(
        par_saison, parts, conseils, epreuves)
    if len(plateaux) < 50:
        return {}

    joueurs = sorted({j for p in plateaux for j in p["champ"]})
    theta, victoires, champs = _luce(plateaux, joueurs)

    disputees = np.zeros(len(joueurs))
    for c in champs:
        disputees[c] += 1
    # L'exposition sert aussi de decalage aux regressions qui suivent, et
    # celles-ci raisonnent par PARTICIPATION. Un aventurier de quatre saisons a
    # quatre expositions distinctes, pas une seule : les confondre attribuerait
    # a chacune de ses saisons le total de sa carriere.
    index_j = {j: i for i, j in enumerate(joueurs)}
    par_participation = {}
    for p_ in plateaux:
        for j in p_["champ"]:
            cle = (p_["saison"], j)
            par_participation[cle] = par_participation.get(cle, 0) + 1

    # Intervalle par reechantillonnage des EPREUVES : c'est l'epreuve qui est
    # l'evenement independant, pas l'aventurier.
    g = rng("force-bootstrap")
    tirages = np.zeros((400, len(joueurs)))
    for b in range(400):
        choix = g.integers(0, len(plateaux), size=len(plateaux))
        tirages[b] = _luce([plateaux[i] for i in choix], joueurs, tours=200)[0]

    noms = {}
    for p in parts:
        noms[p["id"]] = p.get("nom_complet") or p.get("nom")

    classement = []
    for i, j in enumerate(joueurs):
        if disputees[i] < SEUIL_PLATEAUX:
            continue
        classement.append({
            "id": j, "nom": noms.get(j, j),
            "force": _arr(float(theta[i]), 2),
            "bas": _arr(float(np.percentile(tirages[:, i], 2.5)), 2),
            "haut": _arr(float(np.percentile(tirages[:, i], 97.5)), 2),
            "victoires": int(victoires[i]),
            "disputees": int(disputees[i]),
            "ratio": _arr(100.0 * victoires[i] / disputees[i]),
        })
    classement.sort(key=lambda d: (-d["force"], d["nom"]))

    # Le classement brut, celui que tout le monde lit : le nombre de victoires.
    brut = sorted(classement, key=lambda d: (-d["victoires"], d["nom"]))
    rang_brut = {d["id"]: i + 1 for i, d in enumerate(brut)}
    rang_force = {d["id"]: i + 1 for i, d in enumerate(classement)}
    # Le graphique de pentes montre les deux sens : ceux que le modele remonte
    # et ceux qu'il fait redescendre. Ne prendre que le haut d'un seul des deux
    # classements masquerait la moitie de ce qu'il y a a voir.
    vus, retenus = set(), []
    for d in classement[:10] + brut[:10]:
        if d["id"] not in vus:
            vus.add(d["id"])
            retenus.append(d)
    pentes = [{"nom": d["nom"], "rang_force": rang_force[d["id"]],
               "rang_victoires": rang_brut[d["id"]],
               "force": d["force"], "victoires": d["victoires"]}
              for d in retenus]
    pentes.sort(key=lambda d: d["rang_force"])
    # Une « montee » est un aventurier que le modele place PLUS HAUT que son
    # simple total de victoires : son rang de force est meilleur, donc plus
    # petit, que son rang au nombre de victoires.
    montees = sorted(pentes, key=lambda d: d["rang_victoires"] - d["rang_force"])

    return {
        "epreuves_retenues": len(plateaux),
        "saisons_retenues": len(sorted({p["saison"] for p in plateaux})),
        "epreuves_ecartees_saison": sans_saison,
        "vainqueur_hors_plateau": hors_plateau,
        "taux_echec_reconstruction": _arr(
            100.0 * hors_plateau / max(1, hors_plateau + len(plateaux)), 2),
        "joueurs": len(joueurs),
        "seuil": SEUIL_PLATEAUX,
        "classes": len(classement),
        "classement": classement[:20],
        "pentes": pentes,
        "plus_forte_montee": montees[-1] if montees else None,
        "plus_forte_chute": montees[0] if montees else None,
        "_theta": {j: float(theta[i]) for i, j in enumerate(joueurs)},
        "_disputees": {j: int(disputees[i]) for i, j in enumerate(joueurs)},
        "_exposition": {f"{s_}|{j}": int(n) for (s_, j), n in
                        sorted(par_participation.items())},
    }


def force_et_jeu(par_saison, parts, conseils, epreuves, bloc_force):
    """Ce que le jeu fait aux forts.

    Deux questions que le classement seul ne repond pas : un athlete attire-t-il
    davantage de bulletins, et sa force le mene-t-elle plus loin ? Les deux
    demandent de tenir l'exposition constante -- rester longtemps, c'est a la
    fois disputer plus d'epreuves et assister a plus de conseils.
    """
    theta = bloc_force.get("_theta") or {}
    exposition = bloc_force.get("_exposition") or {}
    if not theta:
        return {}

    import statsmodels.api as sm

    lignes = []
    for p in parts:
        s = par_saison.get(p["saison"]) or {}
        if s.get("annulee") or s.get("en_cours"):
            continue
        j = p["id"]
        expo_p = exposition.get(f'{p["saison"]}|{j}', 0)
        if j not in theta or expo_p < 3:
            continue
        if p.get("votes_recus") is None or p.get("_survie") is None:
            continue
        lignes.append((float(np.log(theta[j])), float(p["votes_recus"]),
                       float(p["_survie"]), float(expo_p),
                       1.0 if p.get("genre") == "f" else 0.0,
                       float(p.get("age") or 34)))
    if len(lignes) < 60:
        return {}

    a = np.array(lignes)
    log_force, voix, survie, expo, femme, age = a.T

    # 1. Les voix recues. Modele de Poisson, l'exposition en decalage : on
    #    compare des taux de bulletins, pas des totaux.
    X = sm.add_constant(np.column_stack([log_force, femme, (age - 34) / 10]))
    poisson = sm.GLM(voix, X, family=sm.families.Poisson(),
                     offset=np.log(np.maximum(expo, 1))).fit(cov_type="HC1")
    ic_p = poisson.conf_int()

    # 2. La survie. Moindres carres, meme jeu de variables de controle.
    lineaire = sm.OLS(survie, X).fit(cov_type="HC1")
    ic_l = lineaire.conf_int()

    def _coef(modele, ic, i, exponentiel):
        f = (lambda x: float(np.exp(x))) if exponentiel else float
        return {"estimation": _arr(f(modele.params[i]), 3),
                "bas": _arr(f(ic[i][0]), 3), "haut": _arr(f(ic[i][1]), 3),
                "p": _arr(float(modele.pvalues[i]), 4)}

    return {
        "effectif": len(lignes),
        "voix": {
            "libelle": "Bulletins recus, par epreuve disputee",
            "force": _coef(poisson, ic_p, 1, True),
            "femme": _coef(poisson, ic_p, 2, True),
            "age": _coef(poisson, ic_p, 3, True),
            "lecture": "Rapport de taux par doublement de la force. Au-dessus de "
                       "1, un athlete attire davantage de bulletins.",
        },
        "survie": {
            "libelle": "Part de la saison tenue",
            "force": _coef(lineaire, ic_l, 1, False),
            "femme": _coef(lineaire, ic_l, 2, False),
            "age": _coef(lineaire, ic_l, 3, False),
            "lecture": "Points de pourcentage gagnes quand la force double.",
        },
    }


# --- D. Le jeu tenu serre --------------------------------------------------

def equilibre(par_saison, parts, conseils, epreuves):
    """Le jeu se rattrape-t-il tout seul, et qui sort quand ?

    Deux mesures sans rapport de methode, mais une meme question : ce que le
    format impose, et ce qu'il laisse au hasard.
    """
    from indicateurs import _episode_de_sortie
    import statsmodels.api as sm

    sortie, _ = _episode_de_sortie(conseils, parts, epreuves)
    par_s = {}
    for p in parts:
        par_s.setdefault(p["saison"], []).append(p)

    # --- 1. la tribu en inferiorite gagne-t-elle plus souvent ? -------------
    # Seules les immunites collectives entrent : apres la reunification, les
    # immunites sont individuelles. La forme du format garantit donc que ces
    # epreuves sont d'avant la fusion, sans avoir a deviner le jour de fusion.
    ecarts, gagne_jaune, details = [], [], []
    for e in epreuves:
        if e.get("type") != "immunite" or e.get("forme") != "collective":
            continue
        s = par_saison.get(e["saison"]) or {}
        if s.get("annulee") or s.get("en_cours"):
            continue
        tribus = {t["nom"]: t.get("couleur") for t in (s.get("tribus") or [])
                  if not t.get("apres_fusion")}
        if sorted(set(v for v in tribus.values() if v)) != ["jaune", "rouge"]:
            continue
        membres = par_s.get(e["saison"]) or {}
        connus = sum(1 for p in membres if (e["saison"], p["id"]) in sortie)
        if not membres or connus / len(membres) < COUVERTURE_MINIMALE:
            continue
        episode = int(e["episode"])
        effectif = {}
        for couleur in ("jaune", "rouge"):
            effectif[couleur] = sum(
                1 for p in membres
                if p.get("couleur") == couleur
                and sortie.get((e["saison"], p["id"]), -1) >= episode)
        if min(effectif.values()) < 2:
            continue
        gagnantes = [v.get("libelle") for v in (e.get("vainqueurs") or [])
                     if v.get("type") == "tribu"]
        couleurs_g = sorted({tribus.get(x) for x in gagnantes} - {None})
        if len(couleurs_g) != 1 or couleurs_g[0] not in ("jaune", "rouge"):
            continue
        ecarts.append(effectif["jaune"] - effectif["rouge"])
        gagne_jaune.append(1 if couleurs_g[0] == "jaune" else 0)
        details.append({"saison": e["saison"], "episode": episode,
                        "ecart": effectif["jaune"] - effectif["rouge"]})

    rattrapage = {}
    if len(ecarts) >= 40:
        X = sm.add_constant(np.array(ecarts, dtype=float))
        modele = sm.Logit(np.array(gagne_jaune, dtype=float), X).fit(disp=0)
        ic = modele.conf_int()
        rattrapage = {
            "effectif": len(ecarts),
            "saisons": len(sorted({d["saison"] for d in details})),
            "ecart_max": int(max(abs(x) for x in ecarts)),
            "rapport_de_cotes": _arr(float(np.exp(modele.params[1])), 3),
            "bas": _arr(float(np.exp(ic[1][0])), 3),
            "haut": _arr(float(np.exp(ic[1][1])), 3),
            "p": _arr(float(modele.pvalues[1]), 4),
            "lecture": "Cote de victoire de la tribu jaune quand elle compte un "
                       "aventurier de plus. Au-dessus de 1, l'avantage du nombre "
                       "joue ; en dessous, la tribu en difficulte se rattrape ; "
                       "a 1, l'effectif ne change rien.",
        }

    # --- 2. qui sort, a age, metier et epoque egaux ? -----------------------
    # Modele de duree de Cox, stratifie par saison : chaque saison a sa propre
    # cadence d'elimination, et on ne compare que des aventuriers du meme
    # plateau. Les abandons ne sont pas des eliminations : ils sont censures,
    # comme les finalistes et les vainqueurs.
    ELIMINE = ("elimine_conseil", "elimine_poteaux", "elimine_orientation",
               "elimine_ambassadeurs", "elimine_duel", "elimine_exil")
    nb_saisons = {}
    for p in parts:
        nb_saisons[p["id"]] = nb_saisons.get(p["id"], 0) + 1

    duree, evenement, strate, covariables = [], [], [], []
    familles = sorted({p["_csp"] for p in _classiques(par_saison, parts) if p.get("_csp")})
    principales = [f for f in familles if sum(
        1 for p in _classiques(par_saison, parts) if p.get("_csp") == f) >= 30]
    for p in _classiques(par_saison, parts):
        if not (p.get("jour_sortie") and p.get("age") and p.get("genre")
                and p.get("_csp") and p.get("couleur")):
            continue
        duree.append(float(p["jour_sortie"]))
        evenement.append(1 if p.get("sort") in ELIMINE else 0)
        strate.append(p["saison"])
        ligne = [1.0 if p["genre"] == "f" else 0.0,
                 (float(p["age"]) - 34.0) / 10.0,
                 1.0 if p["couleur"] == "jaune" else 0.0,
                 1.0 if nb_saisons.get(p["id"], 1) > 1 else 0.0]
        ligne += [1.0 if p["_csp"] == f else 0.0 for f in principales]
        covariables.append(ligne)

    noms_cox = ["Femme", "Age (par decennie)", "Bandeau jaune",
                "Deja venu"] + [f"Metier : {f}" for f in principales]
    cox = {}
    if len(duree) >= 200:
        modele = sm.PHReg(np.array(duree), np.array(covariables),
                          status=np.array(evenement),
                          strata=np.array(strate), ties="efron").fit()
        ic = modele.conf_int()
        cox = {
            "effectif": len(duree),
            "eliminations": int(sum(evenement)),
            "censures": int(len(evenement) - sum(evenement)),
            "coefficients": [
                {"variable": noms_cox[i],
                 "rapport": _arr(float(np.exp(modele.params[i])), 3),
                 "bas": _arr(float(np.exp(ic[i][0])), 3),
                 "haut": _arr(float(np.exp(ic[i][1])), 3),
                 "p": _arr(float(modele.pvalues[i]), 4)}
                for i in range(len(noms_cox))],
            "lecture": "Rapport de risque d'elimination, a saison identique. "
                       "Au-dessus de 1, on sort plus vite que la reference ; en "
                       "dessous, plus lentement. L'intervalle qui contient 1 veut "
                       "dire que ces donnees ne permettent pas de conclure.",
        }
    return {"rattrapage": rattrapage, "cox": cox}


def hasard_mecanique(par_saison, parts, conseils, epreuves):
    """La montee du risque est-elle une propriete du jeu, ou de l'arithmetique ?

    `/statistiques/sorties/` publie une courbe de risque qui monte de 7,6 % au
    premier dixieme de saison a 25,2 % au neuvieme, et la commente : « tenir
    n'allege rien ». La lecture est tentante -- et elle merite d'etre testee,
    parce qu'un conseil fait sortir UNE personne quel que soit le nombre de
    presents. Le risque par conseil vaut donc mecaniquement 1/k, et 1/k monte
    tout seul a mesure que le camp se vide.

    On compare ici le risque observe a ce seul calcul. S'ils se superposent, la
    courbe ne dit rien du jeu : elle dit qu'il reste moins de monde.
    """
    from indicateurs import _episode_de_sortie, eliminations

    sortie, _ = _episode_de_sortie(conseils, parts, epreuves)
    par_s = {}
    for p in parts:
        par_s.setdefault(p["saison"], []).append(p)

    observes, mecaniques, effectifs = [], [], []
    for c in eliminations(conseils):
        s = par_saison.get(c["saison"]) or {}
        if s.get("annulee") or s.get("en_cours") or s.get("speciale"):
            continue
        membres = par_s.get(c["saison"]) or []
        connus = sum(1 for p in membres if (c["saison"], p["id"]) in sortie)
        if not membres or connus / len(membres) < COUVERTURE_MINIMALE:
            continue
        try:
            episode = int(c["episode"])
        except (TypeError, ValueError):
            continue
        presents = [p for p in membres
                    if sortie.get((c["saison"], p["id"]), -1) >= episode]
        if len(presents) < 2:
            continue
        partants = sum(1 for p in presents
                       if sortie.get((c["saison"], p["id"])) == episode)
        avancement = 1.0 - (len(presents) - 1) / max(1, len(membres) - 1)
        observes.append((avancement, partants / len(presents)))
        mecaniques.append((avancement, 1.0 / len(presents)))
        effectifs.append(len(presents))

    if len(observes) < 80:
        return {}

    paliers = []
    for k in range(10):
        bas, haut = k / 10.0, (k + 1) / 10.0
        dans = [i for i, (a, _) in enumerate(observes) if bas <= a < haut or (k == 9 and a == 1.0)]
        if not dans:
            continue
        paliers.append({
            "palier": f"{int(bas*100)}-{int(haut*100)} %",
            "observe": _arr(100.0 * float(np.mean([observes[i][1] for i in dans])), 1),
            "mecanique": _arr(100.0 * float(np.mean([mecaniques[i][1] for i in dans])), 1),
            "conseils": len(dans),
            "presents_moyen": _arr(float(np.mean([effectifs[i] for i in dans])), 1),
        })

    for x in paliers:
        x["rapport"] = _arr(x["observe"] / x["mecanique"], 2) if x["mecanique"] else None

    # La courbe publiee sur /statistiques/sorties/ exclut la finale, et pour une
    # bonne raison : au dernier dixieme, tout le monde sort le meme jour. On
    # compare donc sur le meme perimetre, et on rend le reste a part.
    avant = [i for i, (a, _) in enumerate(observes) if a < 0.8]
    o = np.array([observes[i][1] for i in avant])
    m = np.array([mecaniques[i][1] for i in avant])
    return {
        "conseils": len(observes),
        "conseils_hors_finale": len(avant),
        "paliers": paliers,
        "ecart_moyen": _arr(float(np.mean(np.abs(o - m))) * 100, 2),
        "rapport_moyen": _arr(float(np.mean(o) / np.mean(m)), 2),
        "correlation": _arr(float(np.corrcoef(o, m)[0, 1]), 3),
        "lecture": "Risque observe de sortir a un conseil, et risque qu'un simple "
                   "1/nombre-de-presents predit. Les deux derniers paliers sont "
                   "ceux de la finale : tout le monde y sort le meme jour, et la "
                   "comparaison n'y a plus de sens.",
    }


def effet_des_mecaniques(par_saison, parts, conseils, indicateurs_saison):
    """Ce que chaque regle nouvelle a change, une fois l'epoque tenue constante.

    Les mecaniques (`saisons.mecaniques`) sont le seul endroit du jeu de donnees
    ou un choix de production est explicitement date. Elles sont calculees
    depuis le debut du projet et n'ont jamais ete publiees.

    Le controle par l'annee est indispensable : les mecaniques recentes sont
    correlees a tout ce qui a change par ailleurs, a commencer par la taille des
    castings.
    """
    import statsmodels.api as sm

    lignes = []
    for s in indicateurs_saison:
        meta = par_saison.get(s.get("id")) or {}
        if meta.get("annulee") or meta.get("en_cours") or s.get("speciale"):
            continue
        if s.get("taux_abandon") is None or s.get("dispersion_votes") is None:
            continue
        lignes.append((meta.get("mecaniques") or [], float(s["annee"]),
                       float(s["taux_abandon"]), float(s["dispersion_votes"])))
    if len(lignes) < 15:
        return {}

    presentes = sorted({m for l in lignes for m in l[0]})
    retenues = [m for m in presentes
                if 4 <= sum(1 for l in lignes if m in l[0]) <= len(lignes) - 4]
    annees = np.array([l[1] for l in lignes])
    sorties = {"taux_abandon": np.array([l[2] for l in lignes]),
               "dispersion_votes": np.array([l[3] for l in lignes])}

    effets = []
    for m in retenues:
        presence = np.array([1.0 if m in l[0] else 0.0 for l in lignes])
        for cle, y in sorties.items():
            X = sm.add_constant(np.column_stack([presence, (annees - 2013) / 10]))
            r = sm.OLS(y, X).fit(cov_type="HC1")
            ic = r.conf_int()
            effets.append({
                "mecanique": m, "sur": cle, "saisons": int(presence.sum()),
                "effet": _arr(float(r.params[1]), 2),
                "bas": _arr(float(ic[1][0]), 2), "haut": _arr(float(ic[1][1]), 2),
                "p": _arr(float(r.pvalues[1]), 4),
            })
    effets.sort(key=lambda d: (d["p"], d["mecanique"], d["sur"]))
    return {"saisons": len(lignes), "mecaniques_testees": retenues,
            "effets": effets,
            "lecture": "Effet de la presence d'une mecanique, l'annee tenue "
                       "constante. Un intervalle qui contient zero veut dire que "
                       "ces vingt-six saisons ne permettent pas de conclure."}


# --- E. Les alliances : ce que le reseau des bulletins contient -------------

SEUIL_CONSEILS_SAISON = 6   # nombre de conseils complets pour etudier une saison


def _scrutins(par_saison, conseils):
    """Les conseils au depouillement complet, ranges par saison et ordonnes.

    Un bulletin annule par un collier reste un bulletin : il dit avec qui son
    auteur votait. On le garde -- c'est l'intention qui fait l'alliance, pas
    son effet.
    """
    from indicateurs import eliminations

    par_s = {}
    for c in eliminations(conseils):
        s = par_saison.get(c["saison"]) or {}
        if s.get("annulee") or s.get("en_cours"):
            continue
        if not c.get("complet") or not c.get("votes"):
            continue
        bulletins = [(b["votant"], b["cible"]) for b in c["votes"]
                     if b.get("votant_rattache") and b.get("cible_rattachee")]
        if len(bulletins) < 4:
            continue
        par_s.setdefault(c["saison"], []).append((c["numero"], bulletins))
    for s in sorted(par_s):
        par_s[s].sort(key=lambda x: x[0])
    return {s: l for s, l in sorted(par_s.items()) if len(l) >= SEUIL_CONSEILS_SAISON}


def _persistance(scrutins_saison):
    """« Ceux qui ont vote ensemble votent-ils encore ensemble ? »

    On regarde chaque paire presente a deux conseils consecutifs, et on compare
    deux probabilites : voter ensemble sachant qu'on votait ensemble la fois
    d'avant, et voter ensemble sachant qu'on ne votait pas ensemble. L'ecart
    entre les deux EST la persistance des alliances.
    """
    apres_ensemble = apres_ensemble_n = 0
    apres_contre = apres_contre_n = 0
    for _, scrutins in sorted(scrutins_saison.items()):
        for i in range(len(scrutins) - 1):
            a = dict(scrutins[i][1])
            b = dict(scrutins[i + 1][1])
            communs = sorted(set(a) & set(b))
            for x in range(len(communs)):
                for y in range(x + 1, len(communs)):
                    u, v = communs[x], communs[y]
                    avant = a[u] == a[v]
                    apres = b[u] == b[v]
                    if avant:
                        apres_ensemble_n += 1
                        apres_ensemble += 1 if apres else 0
                    else:
                        apres_contre_n += 1
                        apres_contre += 1 if apres else 0
    if not apres_ensemble_n or not apres_contre_n:
        return None
    return (apres_ensemble / apres_ensemble_n, apres_contre / apres_contre_n,
            apres_ensemble_n, apres_contre_n)


def _permuter_sans_soi(votants, cibles, g, essais=40):
    """Redistribue les bulletins d'un conseil SANS qu'un votant recoive son nom.

    Sans cette contrainte, le modele nul fabrique des couples qui n'existent
    pas : 12,5 % des bulletins tires voyaient un aventurier voter contre
    lui-meme, alors qu'on n'en compte aucun dans les donnees reelles. Comme un
    tel couple partage forcement le sexe, le metier et le bandeau, l'attendu
    s'en trouvait gonfle et tout ecart observe paraissait plus grand qu'il
    n'est.

    On tire, puis on repare : chaque position fautive est echangee avec une
    position ou l'echange ne recree pas la faute.
    """
    m = g.permutation(np.array(cibles, dtype=object)).tolist()
    for _ in range(essais):
        fautes = [i for i in range(len(m)) if m[i] == votants[i]]
        if not fautes:
            return m
        for i in fautes:
            candidats = [j for j in range(len(m))
                         if j != i and m[j] != votants[i] and m[i] != votants[j]]
            if not candidats:
                continue
            j = int(g.integers(0, len(candidats)))
            j = candidats[j]
            m[i], m[j] = m[j], m[i]
    return None   # conseil impossible a rebattre : l'appelant l'ecarte


def _melanger(scrutins_saison, g):
    """Le modele nul : a chaque conseil, on redistribue les bulletins.

    Chaque conseil garde EXACTEMENT sa repartition de voix -- quatre contre
    l'un, deux contre l'autre -- mais on tire au sort qui a ecrit quoi. Ce qui
    disparait est le seul lien entre conseils : l'alliance.
    """
    melange = {}
    for s, scrutins in sorted(scrutins_saison.items()):
        neufs = []
        for numero, bulletins in scrutins:
            votants = [v for v, _ in bulletins]
            cibles = [c for _, c in bulletins]
            m = _permuter_sans_soi(votants, cibles, g)
            neufs.append((numero, list(zip(votants, m if m else cibles))))
        melange[s] = neufs
    return melange


def alliances(par_saison, parts, conseils):
    """Le reseau des bulletins : y a-t-il vraiment des camps ?

    Le programme raconte des alliances a chaque episode. Rien n'oblige a ce
    qu'elles existent au-dela du recit : un conseil ou six personnes ecrivent
    le meme nom peut n'etre qu'un ralliement du moment. La difference se
    mesure -- une alliance, c'est ce qui SURVIT d'un conseil au suivant.
    """
    scrutins = _scrutins(par_saison, conseils)
    if len(scrutins) < 8:
        return {}

    observe = _persistance(scrutins)
    if observe is None:
        return {}
    p_ensemble, p_contre, n_ensemble, n_contre = observe

    g = rng("alliances")
    nulle = []
    for _ in range(2000):
        r = _persistance(_melanger(scrutins, g))
        if r:
            nulle.append(r[0] - r[1])
    nulle = np.array(nulle)

    test = _test(
        "persistance_alliances", "La persistance des alliances",
        "Deux aventuriers qui ont vote ensemble votent-ils encore ensemble au "
        "conseil suivant, plus souvent que le hasard ne le voudrait ?",
        100.0 * (p_ensemble - p_contre), 100.0 * nulle, unite="points de %",
        lecture="Ecart entre deux probabilites : voter ensemble apres avoir vote "
                "ensemble, et voter ensemble apres avoir vote separement. A zero, "
                "chaque conseil repart de zero et il n'y a pas d'alliance.")

    # L'appartenance au bloc majoritaire, conseil par conseil : la variable
    # latente que le programme montre sans jamais la nommer.
    noms = {}
    for p in parts:
        noms[p["id"]] = p.get("nom_complet") or p.get("nom")
    cote = {}
    for s, liste in sorted(scrutins.items()):
        for numero, bulletins in liste:
            compte = {}
            for _, c in bulletins:
                compte[c] = compte.get(c, 0) + 1
            majorite = max(compte.values())
            gagnantes = sorted(c for c, n in compte.items() if n == majorite)
            for v, c in bulletins:
                d = cote.setdefault((s, v), [0, 0])
                d[1] += 1
                if c in gagnantes:
                    d[0] += 1

    survie = {(p["saison"], p["id"]): p.get("_survie") for p in parts}
    voix = {(p["saison"], p["id"]): p.get("votes_recus") for p in parts}
    lignes = [(v / n, survie.get(k), noms.get(k[1], k[1]), k[0], n,
               voix.get(k))
              for k, (v, n) in sorted(cote.items()) if n >= 5]
    lignes = [x for x in lignes if x[1] is not None and x[5] is not None]

    coefficient = {}
    if len(lignes) >= 60:
        import statsmodels.api as sm
        part = np.array([x[0] for x in lignes])
        y = np.array([x[1] for x in lignes], dtype=float)
        n = np.array([x[4] for x in lignes], dtype=float)
        menace = np.array([x[5] for x in lignes], dtype=float) / n
        # Trois variables en concurrence : etre du bon cote, ne pas etre vise,
        # et le nombre de conseils traverses.
        #
        # Ce dernier controle est TROP severe et on le sait : traverser
        # beaucoup de conseils, c'est deja avoir survecu. Il absorbe donc une
        # part de ce qu'on cherche a expliquer, et les deux coefficients qui
        # suivent sont des BORNES BASSES. On le garde quand meme : sans lui,
        # on publierait une tautologie deguisee.
        X = sm.add_constant(np.column_stack([part, menace, n]))
        r = sm.OLS(y, X).fit(cov_type="HC1")
        ic = r.conf_int()
        coefficient = {
            "effectif": len(lignes),
            "variables": [
                {"libelle": "Toujours du côté de la majorité",
                 "estimation": _arr(float(r.params[1]), 2),
                 "bas": _arr(float(ic[1][0]), 2), "haut": _arr(float(ic[1][1]), 2),
                 "p": _arr(float(r.pvalues[1]), 4)},
                {"libelle": "Une voix reçue de plus par conseil",
                 "estimation": _arr(float(r.params[2]), 2),
                 "bas": _arr(float(ic[2][0]), 2), "haut": _arr(float(ic[2][1]), 2),
                 "p": _arr(float(r.pvalues[2]), 4)},
            ],
            "r2": _arr(float(r.rsquared), 3),
            "lecture": "Points de saison gagnes ou perdus, le nombre de conseils "
                       "traverses tenu constant. Ce controle etant trop severe, "
                       "les deux effets sont des bornes basses.",
        }

    classement = sorted(lignes, key=lambda x: (-x[0], -x[4], x[2]))
    return {
        "saisons": len(scrutins),
        "conseils": sum(len(l) for l in scrutins.values()),
        "bulletins": sum(len(b) for l in scrutins.values() for _, b in l),
        "paires_suivies": n_ensemble + n_contre,
        "apres_ensemble": _arr(100.0 * p_ensemble),
        "apres_separes": _arr(100.0 * p_contre),
        "test": test,
        "majorite": coefficient,
        "les_plus_souvent_du_bon_cote": [
            {"nom": x[2], "saison": x[3], "part": _arr(100.0 * x[0]),
             "conseils": x[4], "survie": _arr(x[1]), "voix": x[5]}
            for x in classement[:12]],
    }


# --- F. La grille : ce que le calendrier decide ----------------------------

def fusion(par_saison, parts, conseils, epreuves):
    """La reunification tombe-t-elle a un nombre de joueurs, ou a une date ?

    C'est le choix de production le plus lourd d'une saison, et il n'est jamais
    annonce. Deux logiques s'opposent : reunir quand il reste assez peu de
    monde pour que le jeu individuel commence (une regle de JEU), ou reunir a
    un episode fixe pour que la seconde moitie de saison tienne dans la grille
    (une regle de PROGRAMME). Les deux se distinguent, parce que la taille des
    castings a change : de seize aux premieres saisons a vingt-quatre aux
    recentes.

    La reunification se repere sans avoir a la deviner : apres elle, les
    immunites sont individuelles. Le dernier episode portant une immunite
    COLLECTIVE est donc le dernier episode d'avant la fusion.
    """
    from indicateurs import _episode_de_sortie

    sortie, _ = _episode_de_sortie(conseils, parts, epreuves)
    par_s = {}
    for p in parts:
        par_s.setdefault(p["saison"], []).append(p)
    collectives = {}
    for e in epreuves:
        if e.get("type") == "immunite" and e.get("forme") == "collective":
            try:
                episode = int(e["episode"])
            except (TypeError, ValueError):
                continue
            collectives[e["saison"]] = max(collectives.get(e["saison"], 0), episode)

    lignes, ecartees = [], []
    for s_id in sorted(collectives):
        s = par_saison.get(s_id) or {}
        if s.get("annulee") or s.get("en_cours") or s.get("speciale"):
            continue
        membres = par_s.get(s_id) or []
        connus = sum(1 for p in membres if (s_id, p["id"]) in sortie)
        if not membres or connus / len(membres) < COUVERTURE_MINIMALE:
            continue
        episode = collectives[s_id]
        restants = sum(1 for p in membres
                       if sortie.get((s_id, p["id"]), -1) > episode)
        ligne = {"saison": s_id, "titre": s.get("titre"), "annee": s.get("annee"),
                 "casting": len(membres), "episode": episode, "restants": restants}
        # Un repere qui laisse moins de six joueurs ou plus des trois quarts du
        # casting n'est pas une reunification : c'est une epreuve collective
        # d'apres-fusion, ou un bilan d'episode incomplet. On l'ecarte, et on
        # le dit.
        if restants < 6 or restants > 0.75 * len(membres):
            ecartees.append(ligne)
            continue
        lignes.append(ligne)

    if len(lignes) < 12:
        return {}

    episodes = np.array([l["episode"] for l in lignes], dtype=float)
    restants = np.array([l["restants"] for l in lignes], dtype=float)
    castings = np.array([l["casting"] for l in lignes], dtype=float)

    def variation(x):
        return float(np.std(x, ddof=1) / np.mean(x))

    import statsmodels.api as sm
    pentes = {}
    for nom, y in (("episode", episodes), ("restants", restants)):
        r = sm.OLS(y, sm.add_constant(castings)).fit(cov_type="HC1")
        ic = r.conf_int()
        pentes[nom] = {"pente": _arr(float(r.params[1]), 3),
                       "bas": _arr(float(ic[1][0]), 3),
                       "haut": _arr(float(ic[1][1]), 3),
                       "p": _arr(float(r.pvalues[1]), 4)}

    return {
        "saisons": len(lignes),
        "ecartees": [{"saison": l["saison"], "titre": l["titre"],
                      "episode": l["episode"], "restants": l["restants"]}
                     for l in ecartees],
        "lignes": lignes,
        "episode_median": _arr(float(np.median(episodes))),
        "episode_variation": _arr(100.0 * variation(episodes)),
        "restants_median": _arr(float(np.median(restants))),
        "restants_variation": _arr(100.0 * variation(restants)),
        "casting_min": int(castings.min()), "casting_max": int(castings.max()),
        "pente_episode": pentes["episode"],
        "pente_restants": pentes["restants"],
        "lecture": "Pente : de combien l'episode de fusion, puis le nombre de "
                   "joueurs restants, bougent quand le casting gagne un membre. "
                   "Une pente nulle sur l'episode et une pente de 1 sur les "
                   "restants signent une fusion calee sur la GRILLE.",
    }


def ruptures(par_saison, indicateurs_saison):
    """Le jeu a-t-il change, et quand ? Personne ne l'a annonce.

    On cherche une date de rupture par segmentation binaire : la coupure qui
    separe le mieux la serie des saisons en deux regimes, sur plusieurs
    indicateurs a la fois. La date sort des donnees, elle n'est pas choisie.

    La question de fond est de savoir si cette coupure vaut mieux qu'une
    coupure au hasard -- d'ou le test de permutation sur l'ORDRE des saisons.
    """
    champs = [("effectif", "Taille du casting"),
              ("duree_jours", "Durée de la saison"),
              ("age_moyen", "Âge moyen du casting"),
              ("taux_abandon", "Taux d'abandon"),
              ("conseils", "Nombre de conseils"),
              ("colliers", "Objets d'immunité en jeu")]

    lignes = []
    for s in indicateurs_saison:
        meta = par_saison.get(s.get("id")) or {}
        if meta.get("annulee") or meta.get("en_cours") or s.get("speciale"):
            continue
        if any(s.get(c) is None for c, _ in champs):
            continue
        lignes.append((s["annee"], s.get("titre"), [float(s[c]) for c, _ in champs]))
    if len(lignes) < 16:
        return {}
    lignes.sort(key=lambda x: x[0])

    Y = np.array([l[2] for l in lignes])
    Y = (Y - Y.mean(axis=0)) / np.where(Y.std(axis=0) > 0, Y.std(axis=0), 1)

    def cout(matrice):
        """Somme des ecarts au centre de chaque segment."""
        return float(np.sum((matrice - matrice.mean(axis=0)) ** 2))

    def meilleure_coupure(matrice, marge=4):
        total = cout(matrice)
        meilleur, gain = None, 0.0
        for k in range(marge, len(matrice) - marge + 1):
            g = total - cout(matrice[:k]) - cout(matrice[k:])
            if g > gain:
                meilleur, gain = k, g
        return meilleur, gain

    k, gain = meilleure_coupure(Y)
    if k is None:
        return {}

    # Le gain de CHAQUE coupure possible, et pas seulement de la meilleure.
    # Le test dit qu'une coupure existe ; il ne dit pas ou elle tombe. Si le
    # profil est plat, la date n'est pas identifiee, et le taire serait mentir.
    total = cout(Y)
    profil = []
    for i in range(4, len(Y) - 3):
        profil.append({"annee": int(lignes[i][0]), "titre": lignes[i][1],
                       "gain": _arr(total - cout(Y[:i]) - cout(Y[i:]), 2)})
    ordonne = sorted(profil, key=lambda x: -x["gain"])
    # Sont « indiscernables » les coupures dont le gain tient dans 2 % de la
    # meilleure : l'ecart y est plus petit que ce qu'une saison de plus ou de
    # moins deplacerait.
    seuil = ordonne[0]["gain"] * 0.98
    exaequo = [x for x in ordonne if x["gain"] >= seuil]

    g = rng("ruptures")
    nulle = np.array([meilleure_coupure(g.permutation(Y))[1]
                      for _ in range(N_PERMUTATIONS)])

    avant, apres = Y[:k], Y[k:]
    brut = np.array([l[2] for l in lignes])
    detail = []
    for i, (_, libelle) in enumerate(champs):
        detail.append({
            "libelle": libelle,
            "avant": _arr(float(brut[:k, i].mean()), 2),
            "apres": _arr(float(brut[k:, i].mean()), 2),
            "ecart_types": _arr(float(apres[:, i].mean() - avant[:, i].mean()), 2),
        })
    detail.sort(key=lambda d: -abs(d["ecart_types"]))

    return {
        "saisons": len(lignes),
        "serie": [{"annee": int(l[0]), "titre": l[1],
                   "effectif": int(l[2][0]), "conseils": int(l[2][4])}
                  for l in lignes],
        "annee_rupture": int(lignes[k][0]),
        "derniere_avant": {"annee": int(lignes[k - 1][0]), "titre": lignes[k - 1][1]},
        "premiere_apres": {"annee": int(lignes[k][0]), "titre": lignes[k][1]},
        "avant": k, "apres": len(lignes) - k,
        "detail": detail,
        "profil": profil,
        "exaequo": exaequo,
        "nb_exaequo": len(exaequo),
        "second": ordonne[1] if len(ordonne) > 1 else None,
        "test": _test(
            "rupture", "La rupture de régime",
            "Existe-t-il une date qui sépare les saisons en deux régimes mieux "
            "qu'une date tirée au sort ?",
            gain, nulle, unite="",
            lecture="Gain de la meilleure coupure, comparé au gain de la meilleure "
                    "coupure sur des saisons remises dans un ordre au hasard. Une "
                    "coupure existe toujours ; la question est de savoir si "
                    "celle-ci vaut mieux que n'importe quelle autre."),
    }


# --- H. L'homophilie du vote : ecrit-on le nom de qui ne nous ressemble pas ? --

def homophilie(par_saison, parts, conseils):
    """Parmi les presents, vise-t-on de preference celui qui nous ressemble le moins ?

    Le modele nul est le meme que pour les alliances, et c'est lui qui fait la
    solidite du resultat : on redistribue les bulletins d'un conseil entre ses
    votants, en gardant EXACTEMENT le meme jeu de cibles. La popularite d'une
    cible -- le fait que tout le camp l'ait dans le viseur ce soir-la -- est
    donc parfaitement neutralisee. Ne subsiste que la question posee : qui, de
    ceux qui ont ecrit ce nom, l'a ecrit plutot qu'un autre.
    """
    scrutins = _scrutins(par_saison, conseils)
    if not scrutins:
        return {}

    fiche = {}
    for p in parts:
        fiche[(p["saison"], p["id"])] = p

    couples = []
    for s, liste in sorted(scrutins.items()):
        for numero, bulletins in liste:
            couples.append((s, numero, bulletins))

    # Avant la reunification, un conseil ne reunit qu'une tribu : tous les
    # bulletins y sont forcement « meme bandeau ». Ces conseils ne peuvent rien
    # dire de la question posee -- et comme le modele nul rebat A L'INTERIEUR
    # d'un conseil, ils ne la faussent pas non plus : ils la diluent seulement.
    # On mesure donc le bandeau sur les seuls conseils ou plusieurs bandeaux
    # sont presents, pour que le pourcentage affiche soit lisible.
    mixtes = []
    for s, numero, bulletins in couples:
        couleurs = sorted({(fiche.get((s, v)) or {}).get("couleur")
                           for v, _ in bulletins} - {None})
        if len(couleurs) > 1:
            mixtes.append((s, numero, bulletins))

    def traits(s, votant, cible):
        a, b = fiche.get((s, votant)), fiche.get((s, cible))
        if not a or not b:
            return None
        meme_sexe = (1.0 if a.get("genre") and a.get("genre") == b.get("genre")
                     else 0.0 if a.get("genre") and b.get("genre") else None)
        ecart_age = (abs(a["age"] - b["age"]) if a.get("age") and b.get("age")
                     else None)
        meme_metier = (1.0 if a.get("_csp") and a.get("_csp") == b.get("_csp")
                       else 0.0 if a.get("_csp") and b.get("_csp") else None)
        meme_bandeau = (1.0 if a.get("couleur") and a.get("couleur") == b.get("couleur")
                        else 0.0 if a.get("couleur") and b.get("couleur") else None)
        return meme_sexe, ecart_age, meme_metier, meme_bandeau

    def mesures(jeu):
        cumuls = [[0.0, 0] for _ in range(4)]
        for s, _, bulletins in jeu:
            for votant, cible in bulletins:
                t = traits(s, votant, cible)
                if t is None:
                    continue
                for i, v in enumerate(t):
                    if v is not None:
                        cumuls[i][0] += v
                        cumuls[i][1] += 1
        return [(c / n if n else None) for c, n in cumuls], [n for _, n in cumuls]

    observe, effectifs = mesures(couples)
    observe_mixte, effectifs_mixte = mesures(mixtes)
    g = rng("homophilie")
    nulles = [[] for _ in range(4)]
    nulle_mixte = []
    for _ in range(4000):
        melange, melange_mixte = [], []
        for s, numero, bulletins in mixtes:
            votants = [v for v, _ in bulletins]
            cibles = [c for _, c in bulletins]
            m = _permuter_sans_soi(votants, cibles, g)
            if m is not None:
                melange_mixte.append((s, numero, list(zip(votants, m))))
        nulle_mixte.append(mesures(melange_mixte)[0][3])
        for s, numero, bulletins in couples:
            votants = [v for v, _ in bulletins]
            cibles = [c for _, c in bulletins]
            m = _permuter_sans_soi(votants, cibles, g)
            if m is None:
                continue   # conseil qu'on ne peut pas rebattre sans faute
            melange.append((s, numero, list(zip(votants, m))))
        vals, _ = mesures(melange)
        for i, v in enumerate(vals):
            nulles[i].append(v)

    definitions = [
        ("vote_meme_sexe", "Viser quelqu'un du même sexe",
         "Parmi les présents, écrit-on plutôt le nom de quelqu'un de son sexe ?",
         "part sur 1", 1),
        ("vote_ecart_age", "L'écart d'âge avec sa cible",
         "Écrit-on plutôt le nom de quelqu'un de sa génération, ou d'une autre ?",
         "années", 0),
        ("vote_meme_metier", "Viser la même famille de métier",
         "Le métier rapproche-t-il ou éloigne-t-il du bulletin ?",
         "part sur 1", 1),
        ("vote_meme_bandeau", "Viser son propre bandeau de départ",
         "Le camp d'origine protège-t-il, une fois les tribus mélangées ?",
         "part sur 1", 1),
    ]
    tests = []
    for i, (cle, libelle, question, unite, pourcent) in enumerate(definitions):
        if observe[i] is None or not nulles[i]:
            continue
        facteur = 100.0 if pourcent else 1.0
        tests.append(_test(
            cle, libelle, question,
            observe[i] * facteur, np.array(nulles[i]) * facteur,
            unite="%" if pourcent else unite,
            lecture="On rebat les bulletins d'un conseil entre ses votants, en "
                    "gardant le meme jeu de cibles : la popularite d'une cible est "
                    "donc neutralisee. Un observe au-dessus de l'attendu veut dire "
                    "qu'on vise ses semblables plus souvent que le simple partage "
                    "des cibles ne l'expliquerait."))
        tests[-1]["bulletins"] = effectifs[i]

    # Le bandeau, mesure la ou la question se pose : apres la reunification.
    if observe_mixte[3] is not None and nulle_mixte:
        t = _test(
            "vote_bandeau_apres_fusion", "Épargner son bandeau de départ",
            "Une fois les tribus mélangées, écrit-on moins souvent le nom de "
            "quelqu'un de son camp d'origine ?",
            observe_mixte[3] * 100.0, np.array(nulle_mixte) * 100.0, unite="%",
            lecture="Mesuré sur les seuls conseils réunissant plusieurs bandeaux. "
                    "Un observé SOUS l'attendu veut dire que le camp de départ "
                    "protège encore, longtemps après avoir cessé d'exister.")
        t["bulletins"] = effectifs_mixte[3]
        tests.append(t)

    return {"bulletins": max(effectifs) if effectifs else 0,
            "conseils": len(couples), "conseils_mixtes": len(mixtes),
            "bulletins_mixtes": effectifs_mixte[3] if effectifs_mixte else 0,
            "tests": tests}


# --- I. Le jury final : le vote de ceux qu'on a sortis ---------------------

def jury_final(par_saison, parts, conseils):
    """Le jure vote-t-il pour celui qui l'a elimine, ou contre lui ?

    Le vote du jury est le seul scrutin du jeu ou ecrire un nom veut dire « qu'il
    gagne ». Il est aussi le seul rendu par des gens qu'on a fait sortir. Deux
    reponses circulent -- on respecte celui qui a ose, on ne pardonne jamais --
    et aucune n'a jamais ete mesuree.

    Le jure choisit parmi les finalistes : c'est un choix contraint, qui se
    modelise par un logit conditionnel. Chaque jure forme son propre groupe de
    comparaison, ce qui absorbe d'un coup la saison, l'annee et tout ce qui est
    propre au jure lui-meme.
    """
    from indicateurs import eliminations, votes_du_jury
    import statsmodels.api as sm

    # Qui a ecrit le nom de qui, au fil des conseils d'elimination.
    ecrit = set()
    covote = {}
    for c in eliminations(conseils):
        bulletins = [(b["votant"], b["cible"]) for b in (c.get("votes") or [])
                     if b.get("votant_rattache") and b.get("cible_rattachee")]
        for votant, cible in bulletins:
            ecrit.add((c["saison"], votant, cible))
        for i in range(len(bulletins)):
            for j in range(len(bulletins)):
                if i == j:
                    continue
                a, b = bulletins[i], bulletins[j]
                if a[1] == b[1]:
                    cle = (c["saison"], a[0], b[0])
                    covote[cle] = covote.get(cle, 0) + 1

    finalistes = {}
    for p in parts:
        if p.get("sort") in ("vainqueur", "finaliste"):
            finalistes.setdefault(p["saison"], []).append(p["id"])

    groupes, y, X, detail = [], [], [], []
    numero = 0
    for c in votes_du_jury(conseils):
        s = par_saison.get(c["saison"]) or {}
        if s.get("annulee"):
            continue
        candidats = sorted(finalistes.get(c["saison"], []))
        if len(candidats) < 2:
            continue
        for b in c.get("votes") or []:
            if not (b.get("votant_rattache") and b.get("cible_rattachee")):
                continue
            jure, choisi = b["votant"], b["cible"]
            if choisi not in candidats or jure in candidats:
                continue
            numero += 1
            for cand in candidats:
                groupes.append(numero)
                y.append(1.0 if cand == choisi else 0.0)
                X.append([
                    1.0 if (c["saison"], cand, jure) in ecrit else 0.0,
                    float(covote.get((c["saison"], jure, cand), 0)),
                ])
            detail.append((c["saison"], jure, choisi, len(candidats)))

    if len(detail) < 60:
        return {}

    modele = sm.ConditionalLogit(np.array(y), np.array(X),
                                 groups=np.array(groupes)).fit(disp=0)
    ic = modele.conf_int()
    noms = ("A écrit le nom du juré au conseil", "A voté avec le juré, par conseil partagé")
    coefficients = [
        {"libelle": noms[i],
         "rapport": _arr(float(np.exp(modele.params[i])), 3),
         "bas": _arr(float(np.exp(ic[i][0])), 3),
         "haut": _arr(float(np.exp(ic[i][1])), 3),
         "p": _arr(float(modele.pvalues[i]), 4)}
        for i in range(len(noms))]

    # La lecture brute, sans modele : la part de bulletins de jury qui vont a
    # quelqu'un qui avait ecrit le nom du jure.
    vers_bourreau = sum(1 for s, jure, choisi, _ in detail
                        if (s, choisi, jure) in ecrit)
    dispo = sum(1 for s, jure, choisi, _ in detail
                if any((s, cand, jure) in ecrit
                       for cand in finalistes.get(s, [])))
    return {
        "bulletins": len(detail),
        "saisons": len(sorted({d[0] for d in detail})),
        "coefficients": coefficients,
        "part_vers_bourreau": _arr(100.0 * vers_bourreau / len(detail)),
        "bulletins_avec_bourreau_disponible": dispo,
        "part_quand_disponible": _arr(100.0 * vers_bourreau / dispo) if dispo else None,
        "lecture": "Rapport de cotes : au-dessus de 1, le jure vote plus souvent "
                   "pour ce finaliste ; en dessous, moins souvent. Un intervalle "
                   "qui contient 1 veut dire qu'on ne peut pas conclure.",
    }


# --- J. La trahison, le confort, la decimation -----------------------------

def _allies_avant(bulletins):
    """Qui a deja vote avec qui, conseil apres conseil.

    Rend, pour chaque conseil, l'etat des alliances tel qu'il etait AVANT ce
    conseil. Une alliance se noue en ecrivant le meme nom ; elle ne se defait
    jamais dans ce calcul -- ce qu'on mesure est donc « a-t-il deja ete mon
    allie », pas « l'est-il encore ».
    """
    etats = []
    allies = {}
    for numero, bull in bulletins:
        etats.append({v: set(allies.get(v, ())) for v, _ in bull})
        par_cible = {}
        for v, c in bull:
            par_cible.setdefault(c, []).append(v)
        for _, groupe in sorted(par_cible.items()):
            for x in groupe:
                for y in groupe:
                    if x != y:
                        allies.setdefault(x, set()).add(y)
    return etats


def trahison(par_saison, parts, conseils):
    """Ecrire le nom de quelqu'un avec qui on a deja vote.

    C'est le geste que le programme met en scene a chaque saison. Reste a
    savoir s'il est frequent, et s'il paie. Le modele nul est le meme que
    partout ailleurs : on rebat les bulletins d'un conseil entre ses votants,
    sans qu'un votant recoive son nom. La question devient donc : parmi ceux
    qui ont ecrit ces noms-la, est-ce plutot un ancien allie de la cible ?
    """
    scrutins = _scrutins(par_saison, conseils)
    if not scrutins:
        return {}

    contextes = []
    for s, liste in sorted(scrutins.items()):
        etats = _allies_avant(liste)
        for (numero, bull), etat in zip(liste, etats):
            contextes.append((s, numero, bull, etat))

    def taux(jeu):
        n = t = 0
        for _, _, bull, etat in jeu:
            for v, c in bull:
                if etat.get(v):
                    n += 1
                    t += 1 if c in etat[v] else 0
        return (100.0 * t / n if n else None), n

    observe, base = taux(contextes)
    if observe is None or base < 200:
        return {}

    g = rng("trahison")
    nulle = []
    for _ in range(4000):
        melange = []
        for s, numero, bull, etat in contextes:
            votants = [v for v, _ in bull]
            cibles = [c for _, c in bull]
            m = _permuter_sans_soi(votants, cibles, g)
            if m is None:
                continue
            melange.append((s, numero, list(zip(votants, m)), etat))
        v, _ = taux(melange)
        if v is not None:
            nulle.append(v)

    test = _test(
        "trahison", "Écrire le nom d'un ancien allié",
        "Quand on a déjà voté avec quelqu'un, écrit-on son nom plus ou moins "
        "souvent qu'un autre ?",
        observe, np.array(nulle), unite="%",
        lecture="Part des bulletins visant quelqu'un avec qui l'auteur avait déjà "
                "voté. Un observé SOUS l'attendu veut dire que l'alliance protège ; "
                "au-dessus, qu'elle expose.")

    # La trahison paie-t-elle ? On compte, par participation, la part de ses
    # bulletins qui visent un ancien allie, et on regarde ce qu'elle devient.
    survie = {(p["saison"], p["id"]): p.get("_survie") for p in parts}
    noms = {p["id"]: (p.get("nom_complet") or p.get("nom")) for p in parts}
    compte = {}
    for s, _, bull, etat in contextes:
        for v, c in bull:
            if not etat.get(v):
                continue
            d = compte.setdefault((s, v), [0, 0])
            d[1] += 1
            if c in etat[v]:
                d[0] += 1

    lignes = [(t / n, survie.get(k), noms.get(k[1], k[1]), k[0], n)
              for k, (t, n) in sorted(compte.items()) if n >= 4]
    lignes = [x for x in lignes if x[1] is not None]
    effet = {}
    if len(lignes) >= 60:
        import statsmodels.api as sm
        X = sm.add_constant(np.column_stack([
            np.array([x[0] for x in lignes]),
            np.array([x[4] for x in lignes], dtype=float)]))
        r = sm.OLS(np.array([x[1] for x in lignes], dtype=float), X).fit(cov_type="HC1")
        ic = r.conf_int()
        effet = {"effectif": len(lignes),
                 "estimation": _arr(float(r.params[1]), 2),
                 "bas": _arr(float(ic[1][0]), 2), "haut": _arr(float(ic[1][1]), 2),
                 "p": _arr(float(r.pvalues[1]), 4),
                 "lecture": "Points de saison gagnes ou perdus quand on passe de "
                            "« jamais » a « toujours » viser un ancien allie, le "
                            "nombre de bulletins emis tenu constant."}
    classement = sorted(lignes, key=lambda x: (-x[0], -x[4], x[2]))
    return {"bulletins": base, "conseils": len(contextes), "test": test,
            "effet": effet,
            "les_plus_infideles": [
                {"nom": x[2], "saison": x[3], "part": _arr(100.0 * x[0]),
                 "bulletins": x[4], "survie": _arr(x[1])}
                for x in classement[:10]]}


def confort_maudit(par_saison, parts, conseils, epreuves):
    """Gagner le confort attire-t-il les bulletins du soir meme ?

    L'idee court depuis vingt-cinq ans : celui qui gagne le confort devient une
    cible. Elle se teste sur le conseil du MEME episode -- celui ou l'on vote
    apres avoir vu qui a gagne quoi.
    """
    from indicateurs import eliminations

    gagnants = {}
    for e in epreuves:
        if e.get("type") != "confort":
            continue
        try:
            episode = int(e["episode"])
        except (TypeError, ValueError):
            continue
        for v in (e.get("vainqueurs") or []):
            if v.get("type") == "personne" and v.get("id"):
                gagnants.setdefault((e["saison"], episode), set()).add(v["id"])

    contextes = []
    for c in eliminations(conseils):
        s = par_saison.get(c["saison"]) or {}
        if s.get("annulee") or s.get("en_cours"):
            continue
        if not c.get("complet") or not c.get("votes"):
            continue
        try:
            episode = int(c["episode"])
        except (TypeError, ValueError):
            continue
        bull = [(b["votant"], b["cible"]) for b in c["votes"]
                if b.get("votant_rattache") and b.get("cible_rattachee")]
        if len(bull) < 4:
            continue
        gagne = gagnants.get((c["saison"], episode), set())
        presents = sorted({v for v, _ in bull} | {x for _, x in bull})
        dedans = sorted(gagne & set(presents))
        if not dedans:
            continue
        contextes.append((bull, presents, set(dedans)))

    if len(contextes) < 40:
        return {}

    def part(jeu):
        vises = total = 0
        for bull, presents, dedans in jeu:
            for _, c in bull:
                total += 1
                vises += 1 if c in dedans else 0
        return 100.0 * vises / total if total else None

    observe = part(contextes)
    g = rng("confort")
    nulle = []
    for _ in range(4000):
        melange = []
        for bull, presents, dedans in contextes:
            votants = [v for v, _ in bull]
            cibles = [c for _, c in bull]
            m = _permuter_sans_soi(votants, cibles, g)
            melange.append((list(zip(votants, m if m else cibles)), presents, dedans))
        nulle.append(part(melange))

    # Le modele nul par permutation garde le meme jeu de cibles : il ne peut
    # donc RIEN dire ici, la part de bulletins allant aux gagnants du confort y
    # est identique par construction. La bonne reference est la part que
    # representent ces gagnants parmi les presents.
    attendu = float(np.mean([100.0 * len(d) / len(p) for _, p, d in contextes]))
    n_bulletins = sum(len(b) for b, _, _ in contextes)
    vises = sum(1 for b, _, d in contextes for _, c in b if c in d)

    from scipy import stats as st
    binom = st.binomtest(vises, n_bulletins, attendu / 100.0)
    ic = binom.proportion_ci(confidence_level=0.95)
    return {
        "conseils": len(contextes),
        "bulletins": n_bulletins,
        "observe": _arr(100.0 * vises / n_bulletins),
        "attendu": _arr(attendu),
        "bas": _arr(100.0 * ic.low), "haut": _arr(100.0 * ic.high),
        "p": _arr(float(binom.pvalue), 4),
        "lecture": "Part des bulletins visant un gagnant du confort du meme "
                   "episode, comparee a la part que ces gagnants representent "
                   "parmi les presents.",
    }


def decimation(par_saison, parts, conseils, epreuves):
    """Apres la fusion, un camp est-il elimine en serie ?

    C'est le scenario que la serie americaine a baptise « pagonging » : le camp
    majoritaire sort le camp minoritaire un par un, sans jamais se diviser. Il
    laisse une trace mesurable -- les sorties se suivent par couleur au lieu
    d'alterner.
    """
    from indicateurs import _episode_de_sortie

    sortie, _ = _episode_de_sortie(conseils, parts, epreuves)
    par_s = {}
    for p in parts:
        par_s.setdefault(p["saison"], []).append(p)
    collectives = {}
    for e in epreuves:
        if e.get("type") == "immunite" and e.get("forme") == "collective":
            try:
                collectives[e["saison"]] = max(collectives.get(e["saison"], 0),
                                               int(e["episode"]))
            except (TypeError, ValueError):
                pass

    suites = []
    for s_id in sorted(collectives):
        s = par_saison.get(s_id) or {}
        if s.get("annulee") or s.get("en_cours") or s.get("speciale"):
            continue
        membres = par_s.get(s_id) or []
        if not membres:
            continue
        if sum(1 for p in membres if (s_id, p["id"]) in sortie) / len(membres) < COUVERTURE_MINIMALE:
            continue
        apres = [p for p in membres
                 if sortie.get((s_id, p["id"]), -1) > collectives[s_id] and p.get("couleur")]
        if len(apres) < 6 or len(sorted({p["couleur"] for p in apres})) != 2:
            continue
        apres.sort(key=lambda p: (sortie[(s_id, p["id"])], p["id"]))
        suites.append((s_id, s.get("titre"), s.get("annee"),
                       [p["couleur"] for p in apres]))

    if len(suites) < 10:
        return {}

    def enchainements(listes):
        return float(sum(1 for l in listes for i in range(len(l) - 1)
                         if l[i] == l[i + 1]))

    observe = enchainements([l for _, _, _, l in suites])
    g = rng("decimation")
    nulle = np.array([
        enchainements([g.permutation(np.array(l, dtype=object)).tolist()
                       for _, _, _, l in suites])
        for _ in range(N_PERMUTATIONS)])

    detail = []
    for s_id, titre, annee, l in suites:
        streak = maxi = 1
        for i in range(1, len(l)):
            streak = streak + 1 if l[i] == l[i - 1] else 1
            maxi = max(maxi, streak)
        detail.append({"saison": s_id, "titre": titre, "annee": annee,
                       "joueurs": len(l), "plus_longue_serie": maxi,
                       "suite": "".join(x[0].upper() for x in l)})
    detail.sort(key=lambda d: (-d["plus_longue_serie"], d["saison"]))

    return {
        "saisons": len(suites),
        "sorties": sum(len(l) for _, _, _, l in suites),
        "detail": detail[:10],
        "test": _test(
            "decimation", "L'élimination en série d'un camp",
            "Après la réunification, les sorties se suivent-elles par bandeau "
            "plus souvent que le hasard ne le voudrait ?",
            observe, nulle, unite="enchaînements",
            lecture="Nombre de fois où deux sorties consécutives viennent du même "
                    "bandeau de départ. Un observé AU-DESSUS de l'attendu est la "
                    "signature d'un camp démonté un par un."),
    }


# --- assemblage ------------------------------------------------------------

def tout(par_saison, parts, conseils, epreuves, indicateurs_saison):
    """Lance les quatre axes et corrige l'ensemble des tests d'un seul coup.

    La correction ne vaut que si la liste des tests est arretee AVANT de
    regarder les resultats : c'est pourquoi elle porte sur tout ce que ce
    module produit, et pas sur une selection faite apres coup. `/methode/`
    publie la liste.
    """
    casting = recette_casting(par_saison, parts)
    pron = pronostic(par_saison, parts)
    f = force(par_saison, parts, conseils, epreuves)
    fj = force_et_jeu(par_saison, parts, conseils, epreuves, f) if f else {}
    eq = equilibre(par_saison, parts, conseils, epreuves)
    hm = hasard_mecanique(par_saison, parts, conseils, epreuves)
    mec = effet_des_mecaniques(par_saison, parts, conseils, indicateurs_saison)
    al = alliances(par_saison, parts, conseils)
    ho = homophilie(par_saison, parts, conseils)
    tr = trahison(par_saison, parts, conseils)
    cf = confort_maudit(par_saison, parts, conseils, epreuves)
    de = decimation(par_saison, parts, conseils, epreuves)
    ju = jury_final(par_saison, parts, conseils)
    fu = fusion(par_saison, parts, conseils, epreuves)
    ru = ruptures(par_saison, indicateurs_saison)

    # Les cles techniques du modele de force n'ont rien a faire dans le fichier
    # publie : elles servent aux regressions de suivi, pas au site.
    for cle in ("_theta", "_disputees", "_exposition"):
        f.pop(cle, None)

    registre = []
    for bloc, origine in ((casting, "casting"), (pron, "pronostic"),
                          (ho, "homophilie")):
        for t in bloc.get("tests", []):
            t["origine"] = origine
            registre.append(t)
    # La geographie est calculee a part -- elle depend d'un fichier INSEE
    # telecharge -- mais ses tests entrent dans le MEME registre : la
    # correction pour tests multiples ne vaut que si elle les couvre tous.
    import os
    chemin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "_data", "geographie.yml")
    geo = {}
    if os.path.exists(chemin):
        import yaml
        geo = yaml.safe_load(open(chemin, encoding="utf-8")) or {}
    for t in geo.get("tests") or []:
        t["origine"] = "geographie"
        registre.append(t)

    for bloc, origine in ((al, "alliances"), (ru, "ruptures"),
                          (tr, "trahison"), (de, "decimation")):
        t = bloc.get("test")
        if t:
            t["origine"] = origine
            registre.append(t)
    ajustees = benjamini_hochberg([t["p"] for t in registre])
    for t, pa in zip(registre, ajustees):
        t["p_ajustee"] = _arr(pa, 4)
        t["retenu"] = bool(pa < 0.05)

    return {
        "graine": GRAINE,
        "permutations": N_PERMUTATIONS,
        "bootstrap": N_BOOTSTRAP,
        "casting": casting,
        "pronostic": pron,
        "force": f,
        "force_et_jeu": fj,
        "equilibre": eq,
        "hasard_mecanique": hm,
        "mecaniques": mec,
        "alliances": al,
        "homophilie": ho,
        "trahison": tr,
        "confort_maudit": cf,
        "decimation": de,
        "jury_final": ju,
        "fusion": fu,
        "ruptures": ru,
        "registre": [{k: t[k] for k in
                      ("cle", "libelle", "question", "origine", "observe",
                       "attendu", "unite", "ecart_types", "p", "p_ajustee",
                       "retenu", "tirages", "lecture", "nulle")}
                     for t in registre],
        "nb_tests": len(registre),
        "nb_retenus": sum(1 for t in registre if t["retenu"]),
    }
