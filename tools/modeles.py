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

    coord, inerties, noms_mod, coord_mod = _acm(
        [(l["tranche"], l["genre"], l["csp"], l["couleur"]) for l in lignes])
    plan = coord[:, :4]

    meilleur_k, meilleur_score = 2, -2.0
    silhouettes = []
    for k in range(2, 7):
        etiquettes = KMeans(n_clusters=k, n_init=25, random_state=GRAINE).fit_predict(plan)
        score = float(silhouette_score(plan, etiquettes))
        silhouettes.append({"k": k, "score": _arr(score, 3)})
        if score > meilleur_score + 1e-9:
            meilleur_k, meilleur_score = k, score
    groupes = KMeans(n_clusters=meilleur_k, n_init=25,
                     random_state=GRAINE).fit_predict(plan)

    # Un groupe se nomme par ce qui l'y distingue le plus du reste : la
    # modalite dont la part interne depasse le plus sa part generale.
    archetypes = []
    for g in range(meilleur_k):
        dedans = [l for l, e in zip(lignes, groupes) if e == g]
        traits = []
        for champ, etiquette in (("tranche", ""), ("genre", ""), ("csp", ""), ("couleur", "")):
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

    # Les cles techniques du modele de force n'ont rien a faire dans le fichier
    # publie : elles servent aux regressions de suivi, pas au site.
    for cle in ("_theta", "_disputees", "_exposition"):
        f.pop(cle, None)

    registre = []
    for bloc, origine in ((casting, "casting"), (pron, "pronostic")):
        for t in bloc.get("tests", []):
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
        "registre": [{k: t[k] for k in
                      ("cle", "libelle", "question", "origine", "observe",
                       "attendu", "unite", "ecart_types", "p", "p_ajustee",
                       "retenu", "tirages", "lecture", "nulle")}
                     for t in registre],
        "nb_tests": len(registre),
        "nb_retenus": sum(1 for t in registre if t["retenu"]),
    }
