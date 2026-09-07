#!/usr/bin/env python3
"""Le classement des joueurs : cinq facettes, un score, et ce qu'il vaut.

Un « top » est le contraire d'une mesure : c'est un ordre total impose a des
gens qui n'ont pas joue la meme partie. Ce module le construit quand meme,
mais il construit AUSSI de quoi le contester, et les deux sont publies
ensemble.

Trois principes tiennent le fichier.

  * **Le palmares n'entre pas dans le score.** Ni le titre, ni la place de
    finaliste. Un classement qui compte la victoire parmi ses ingredients
    remet les vainqueurs devant et appelle cela un resultat : c'est une
    tautologie deguisee. Le palmares est ici la chose qu'on regarde APRES,
    pour voir si le score la retrouve tout seul.

  * **Aucun seuil qui exclut.** Un taux sur trois essais ne vaut rien, mais
    ecarter celui qui n'a que trois essais fabrique un classement de
    survivants. On retrecit donc chaque taux vers la moyenne de la population,
    d'autant plus fort que les essais sont rares -- la force du retrecissement
    n'est pas choisie a la main, elle est estimee sur les donnees (methode des
    moments, prior beta ou gamma). Faute de preuve, un joueur vaut la moyenne ;
    il ne vaut ni zero, ni l'exclusion.

  * **Les poids sont arbitraires, alors on les tire tous.** Plutot que de
    defendre une ponderation, on en tire des dizaines de milliers sur le
    simplexe et on publie, pour chaque joueur, la part des ponderations qui le
    gardent dans le top. Ce qui resiste a toutes est un fait ; le reste est un
    choix d'auteur, et il est signale comme tel.

Les cinq facettes, et leur denominateur -- c'est lui qui decide de ce qu'un
chiffre veut dire :

    parcours     part du casting depassee, par participation
    epreuves     epreuves individuelles gagnees / disputees avant sa sortie
    discretion   voix recues / conseils traverses            (bas = bon)
    resistance   conseils survecus alors qu'il etait vise / conseils ou vise
    lecture      bulletins portes sur l'elimine / bulletins emis

Les trois dernieres ne se lisent que sur les conseils au depouillement
COMPLET. Ce depouillement s'effondre a l'epoque recente -- 61 % des conseils
avant 2005, 18 % entre 2020 et 2024 -- et c'est le biais principal de ce
classement. Il est mesure ici (`biais_epoque`) plutot que taise.
"""
from collections import Counter, defaultdict

import numpy as np

import indicateurs as I
import modeles

LIBELLE_SORT = {
    "vainqueur": "Vainqueur", "finaliste": "Finaliste",
    "elimine_conseil": "Éliminé au conseil",
    "elimine_poteaux": "Éliminé aux poteaux",
    "elimine_orientation": "Éliminé à l'orientation",
    "elimine_ambassadeurs": "Éliminé aux ambassadeurs",
    "elimine_duel": "Éliminé en duel", "elimine_exil": "Éliminé sur l'île",
    "abandon_medical": "Abandon médical", "abandon_volontaire": "Abandon volontaire",
    "disqualifie": "Disqualifié",
}

TIRAGES = 10000          # ponderations tirees sur le simplexe
TAILLE = 25              # taille du classement synthetique publie
TAILLE_FACETTE = 10      # taille de chaque classement par facette

# Plafond du retrecissement. Il est atteint quand la dispersion ENTRE
# joueurs n'est pas decelable : la facette ne distingue alors plus personne
# individuellement, et seul le cumul sur plusieurs saisons la fait bouger.
PLAFOND_K = 200.0

# `sens` vaut +1 quand un chiffre eleve est bon, -1 quand il est mauvais.
# `nature` dit quelle loi sert de prior : une proportion se retrecit vers une
# beta, un comptage par occasion vers une gamma.
FACETTES = [
    ("parcours", "Le parcours",
     "Aller loin, et le refaire",
     "Part du casting dépassée", "une participation",
     +1, "moyenne"),
    ("epreuves", "Les épreuves",
     "Gagner les épreuves qui se courent seul",
     "Épreuves individuelles gagnées",
     "les épreuves individuelles — confort et immunité — disputées avant sa sortie",
     +1, "proportion"),
    ("discretion", "La discrétion",
     "Traverser les conseils sans que personne n’écrive votre nom",
     "Voix reçues", "les conseils traversés",
     -1, "comptage"),
    ("resistance", "La résistance",
     "S’en sortir quand le nom écrit est le vôtre",
     "Conseils survécus alors qu’il était visé",
     "les conseils où il a reçu au moins une voix",
     +1, "proportion"),
    ("lecture", "La lecture",
     "Écrire le nom de celui qui part, conseil après conseil",
     "Bulletins portés sur l’éliminé", "les bulletins qu’il a émis",
     +1, "proportion"),
]
CLES = [f[0] for f in FACETTES]


# --- retrecissement --------------------------------------------------------

def _rho(x, y):
    """Correlation de rang, AVEC rangs moyens sur les ex aequo.

    Le `_spearman` de tools/modeles.py suppose des valeurs distinctes, et le
    dit. Ici l'hypothese tombe : le retrecissement pose EXACTEMENT la moyenne
    de la population sur tous ceux qui n'ont aucune preuve -- cent
    quatre-vingt-douze joueurs sur la facette des epreuves. Departager ces
    ex aequo par leur ordre d'arrivee dans la liste fabriquerait une
    correlation qui ne vient que de cet ordre.
    """
    def rangs(v):
        v = np.asarray(v, dtype=float)
        ordre = np.argsort(v, kind="stable")
        r = np.empty(len(v), dtype=float)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[ordre[j + 1]] == v[ordre[i]]:
                j += 1
            r[ordre[i:j + 1]] = (i + j) / 2.0 + 1.0
            i = j + 1
        return r
    a, b = rangs(x), rangs(y)
    a, b = a - a.mean(), b - b.mean()
    d = float(np.sqrt((a * a).sum() * (b * b).sum()))
    return float((a * b).sum() / d) if d else 0.0


def _auc(scores, positifs):
    """Probabilite qu'un vainqueur soit mieux classe qu'un non-vainqueur.

    C'est la bonne mesure du lien entre le score et le palmares : elle se lit
    directement (0,5 = aucun lien, 1 = separation parfaite) et elle traite les
    ex aequo par une demi-victoire, ce qu'une correlation sur une variable
    presque constante ne fait pas.
    """
    a = [s for s, p in zip(scores, positifs) if p]
    b = [s for s, p in zip(scores, positifs) if not p]
    if not a or not b:
        return None
    gagne = sum(1.0 if x > y else 0.5 if x == y else 0.0 for x in a for y in b)
    return gagne / (len(a) * len(b))


def _prior_normal(paires):
    """(mu, K) pour une note continue moyennee sur les participations.

    Le parcours n'est pas une proportion d'essais reussis : c'est une note par
    saison, entre 0 et 1. Sa loi n'est ni binomiale ni de Poisson, et lui
    appliquer le prior beta donnerait une variance attendue fausse. On ajuste
    donc un modele normal-normal : K est le rapport de la variance INTRA
    joueur -- ce que sa note bouge d'une saison a l'autre -- a la variance
    ENTRE joueurs. Plus un joueur varie d'une saison a l'autre, moins une
    seule saison en dit sur lui, et plus on le ramene vers la moyenne.

    Ce rapport se lit : sur ces donnees, la variance intra depasse la variance
    entre. Autrement dit, aucun ecart stable entre joueurs n'est decelable sur
    cette facette, et K monte au plafond. Ce n'est pas un accident de calcul,
    c'est le meme constat que le test de stabilite -- et il est publie.
    """
    valeurs = defaultdict(list)
    for (num, den), cle in paires:
        if den:
            valeurs[cle].append(num / den)
    toutes = [v for lot in valeurs.values() for v in lot]
    if not toutes:
        return 0.0, 1.0
    mu = float(np.mean(toutes))
    repetes = [lot for lot in valeurs.values() if len(lot) >= 2]
    if len(repetes) < 8:
        return mu, 8.0
    intra = float(np.mean([np.var(lot, ddof=1) for lot in repetes]))
    entre = float(np.var(toutes, ddof=1)) - intra
    if entre <= 1e-9:
        return mu, PLAFOND_K
    return mu, float(min(max(intra / entre, 1.0), PLAFOND_K))


def _prior_beta(paires):
    """(mu, K) d'une beta ajustee par la methode des moments.

    K est le nombre d'essais fictifs que vaut la moyenne de la population.
    L'estimer plutot que le choisir evite la constante magique : c'est la
    dispersion reelle des taux qui decide de la force du retrecissement.
    """
    utiles = [(n, d) for n, d in paires if d > 0]
    tot_n = sum(n for n, _ in utiles)
    tot_d = sum(d for _, d in utiles)
    if not utiles or not tot_d:
        return 0.0, 1.0
    mu = tot_n / tot_d
    if len(utiles) < 8 or mu <= 0 or mu >= 1:
        return mu, 8.0
    # Variance des taux ponderee par l'effectif, moins la part purement
    # binomiale : ce qui reste est la vraie dispersion entre joueurs.
    poids = [d for _, d in utiles]
    taux = [n / d for n, d in utiles]
    p_tot = sum(poids)
    var = sum(w * (t - mu) ** 2 for w, t in zip(poids, taux)) / p_tot
    attendue = mu * (1 - mu) * sum(w / d for w, (_, d) in zip(poids, utiles)) / p_tot
    entre = var - attendue
    if entre <= 1e-9:
        return mu, PLAFOND_K    # aucune dispersion decelable : tout vaut la moyenne
    k = mu * (1 - mu) / entre - 1
    return mu, float(min(max(k, 1.0), PLAFOND_K))


def _prior_gamma(paires):
    """(mu, K) d'une gamma ajustee de la meme facon, pour un taux de comptage."""
    utiles = [(n, d) for n, d in paires if d > 0]
    tot_n = sum(n for n, _ in utiles)
    tot_d = sum(d for _, d in utiles)
    if not utiles or not tot_d:
        return 0.0, 1.0
    mu = tot_n / tot_d
    if len(utiles) < 8 or mu <= 0:
        return mu, 8.0
    poids = [d for _, d in utiles]
    taux = [n / d for n, d in utiles]
    p_tot = sum(poids)
    var = sum(w * (t - mu) ** 2 for w, t in zip(poids, taux)) / p_tot
    attendue = mu * sum(w / d for w, (_, d) in zip(poids, utiles)) / p_tot
    entre = var - attendue
    if entre <= 1e-9:
        return mu, PLAFOND_K
    k = mu / entre
    return mu, float(min(max(k, 1.0), PLAFOND_K))


def priors(mesures):
    """Un couple (mu, K) par facette, estime sur la population entiere."""
    out = {}
    for cle, _, _, _, _, _, nature in FACETTES:
        if nature == "moyenne":
            out[cle] = _prior_normal([(m[cle], k[1]) for k, m in mesures.items()])
        else:
            paires = [m[cle] for m in mesures.values()]
            out[cle] = (_prior_beta if nature == "proportion"
                        else _prior_gamma)(paires)
    return out


def retrecir(num, den, prior):
    mu, k = prior
    return (num + k * mu) / (den + k) if (den + k) else mu


# --- mesures ---------------------------------------------------------------

def mesurer(saisons, parts, conseils, epreuves):
    """(saison, personne) -> {facette: (numerateur, denominateur)}.

    Tout ce qui suit se lit une participation a la fois : c'est l'unite ou les
    denominateurs ont un sens. L'agregation par personne vient apres, et elle
    additionne les deux termes plutot que de moyenner des taux -- moyenner des
    taux donnerait le meme poids a une saison de trois jours et a une finale.
    """
    par_saison = {s["id"]: s for s in saisons}
    lignes = I.indicateurs_individuels(saisons, parts, conseils, epreuves)
    idx = {(l["saison"], l["id"]): l for l in lignes}

    taille = Counter(p["saison"] for p in parts)
    jours = defaultdict(list)
    for p in parts:
        jours[p["saison"]].append(p.get("jour_sortie"))

    # justesse et evasion se recomptent ici : indicateurs.py les rend par
    # participation avec un seuil, or le seuil doit tomber APRES l'agregation.
    justes = Counter(); emis = Counter()
    vises = Counter(); survecus = Counter()
    for c in I.eliminations(conseils):
        s = par_saison.get(c["saison"]) or {}
        if s.get("annulee") or s.get("en_cours") or not c.get("complet"):
            continue
        el = c.get("elimine") if c.get("elimine_rattache") else None
        contre = Counter()
        for b in c.get("votes") or []:
            if b.get("cible_rattachee"):
                contre[b["cible"]] += 1
            if el and b.get("votant_rattache"):
                emis[(c["saison"], b["votant"])] += 1
                if b.get("cible_rattachee") and b["cible"] == el:
                    justes[(c["saison"], b["votant"])] += 1
        for pid in contre:
            vises[(c["saison"], pid)] += 1
            if el and pid != el:
                survecus[(c["saison"], pid)] += 1

    mesures = {}
    for p in parts:
        sid, pid = p["saison"], p["id"]
        l = idx.get((sid, pid))
        if not l:
            continue
        n = taille[sid]
        rang = p.get("classement")
        if rang:
            depasses, atteste = float(n - rang), True
        else:
            j = p.get("jour_sortie")
            if j is None:
                depasses, atteste = None, False
            else:
                autres = [x for x in jours[sid] if x is not None]
                depasses = (sum(1 for x in autres if x < j)
                            + 0.5 * (sum(1 for x in autres if x == j) - 1))
                atteste = False
        part = (depasses / (n - 1)) if depasses is not None and n > 1 else None

        mesures[(sid, pid)] = {
            "parcours": (part, 1.0) if part is not None else (0.0, 0.0),
            # Sans episode de sortie -- deux homonymes non rattaches a la
            # Revanche des 4 Terres -- le denominateur est inconnu, pas nul :
            # la facette ne dit rien de ces deux-la, et c'est la moyenne qui
            # leur revient, pas un taux infini.
            "epreuves": ((float(l["epreuves_gagnees"]),
                          float(l["epreuves_disputees"]))
                         if l.get("epreuves_disputees") is not None
                         else (0.0, 0.0)),
            "discretion": (float(p.get("votes_recus") or 0),
                           float(l["conseils_assistes"])),
            "resistance": (float(survecus[(sid, pid)]), float(vises[(sid, pid)])),
            "lecture": (float(justes[(sid, pid)]), float(emis[(sid, pid)])),
            "_rang_atteste": atteste,
            "_annee": l["annee"],
            "_speciale": l["speciale"],
            "_sort": p.get("sort"),
            "_nom": p.get("nom_complet") or p.get("nom"),
            "_titre": (par_saison.get(sid) or {}).get("titre"),
        }
    return mesures


def agreger(mesures, cles):
    """Somme les numerateurs et les denominateurs sur un ensemble de cles."""
    out = {c: [0.0, 0.0] for c in CLES}
    for k in cles:
        m = mesures[k]
        for c in CLES:
            n, d = m[c]
            out[c][0] += n
            out[c][1] += d
    return {c: (v[0], v[1]) for c, v in out.items()}


# --- scores ----------------------------------------------------------------

def _z(valeurs):
    v = np.asarray(valeurs, dtype=float)
    ecart = float(v.std(ddof=0))
    return (v - float(v.mean())) / ecart if ecart > 1e-12 else np.zeros_like(v)


def noter(sujets, pr):
    """Ajoute a chaque sujet ses taux retrecis, ses cotes z et son score.

    `sujets` : [{"cle":…, "mesures": {facette: (num, den)}, …}]
    Le score est la moyenne des cinq cotes z, poids egaux. C'est la
    ponderation par defaut, et la seule qui ne demande a personne de decider
    que le physique compte plus que le vote.
    """
    for s in sujets:
        s["taux"] = {c: retrecir(*s["mesures"][c], pr[c]) for c in CLES}
        s["preuve"] = {c: s["mesures"][c][1] for c in CLES}
    for cle, _, _, _, _, sens, _ in FACETTES:
        z = _z([s["taux"][cle] for s in sujets]) * sens
        for s, x in zip(sujets, z):
            s.setdefault("z", {})[cle] = float(x)
    for s in sujets:
        s["score"] = sum(s["z"][c] for c in CLES) / len(CLES)
    sujets.sort(key=lambda s: (-s["score"], s["cle"]))
    for i, s in enumerate(sujets, 1):
        s["rang"] = i
    return sujets


# --- robustesse aux ponderations -------------------------------------------

def robustesse(sujets, tirages=TIRAGES, taille=TAILLE):
    """Ce que le classement doit aux poids, mesure en le refaisant partout.

    Les poids sont tires uniformement sur le simplexe -- une Dirichlet de
    parametres tous a 1 -- ce qui revient a n'avoir aucune opinion sur
    l'importance relative des facettes. Chaque joueur recoit alors la part des
    ponderations qui le gardent dans le top, et l'etendue de ses rangs.
    """
    rng = modeles.rng("classement-ponderations")
    z = np.array([[s["z"][c] for c in CLES] for s in sujets], dtype=float)
    poids = rng.dirichlet(np.ones(len(CLES)), size=tirages)
    scores = poids @ z.T                       # tirages x sujets
    rangs = (-scores).argsort(axis=1).argsort(axis=1) + 1
    dans = (rangs <= taille).mean(axis=0)
    for i, s in enumerate(sujets):
        s["part_top"] = round(100.0 * float(dans[i]), 1)
        s["rang_median"] = int(np.median(rangs[:, i]))
        s["rang_min"] = int(rangs[:, i].min())
        s["rang_max"] = int(rangs[:, i].max())
        # Les extremes tiennent a une ponderation sur dix mille, qui met tout
        # le poids sur une seule facette. L'intervalle central dit mieux ou le
        # joueur se tient quand on ne force rien.
        s["rang_p05"] = int(np.percentile(rangs[:, i], 5))
        s["rang_p95"] = int(np.percentile(rangs[:, i], 95))
    def combien(seuil):
        return sum(1 for s in sujets if s["part_top"] >= seuil)
    socle = [s for s in sujets if s["part_top"] >= 99.0]
    entrants = [s for s in sujets[taille:] if s["part_top"] > 0]
    return {
        "tirages": tirages, "taille": taille,
        "socle": len(socle),
        "socle_noms": [s["nom"] for s in socle],
        "paliers": [{"seuil": seuil, "effectif": combien(seuil)}
                    for seuil in (99.0, 90.0, 75.0, 50.0, 25.0, 0.01)],
        "toujours": combien(100.0),
        "hors_top_mais_parfois_dedans": len(entrants),
        "candidats": combien(0.01),
        "part_top_mediane_du_top": round(
            float(np.median([s["part_top"] for s in sujets[:taille]])), 1),
        "part_top_minimale_du_top": round(
            min(s["part_top"] for s in sujets[:taille]), 1),
    }


# --- ce que les facettes se disent entre elles -----------------------------

def correlations(sujets):
    """Les dix correlations de rang entre facettes.

    Si un « meilleur joueur » existe, ces correlations sont positives : le
    talent deborde d'une facette sur l'autre. Si elles sont nulles, le score
    synthetique ne fait que moyenner cinq choses sans rapport, et son premier
    est celui que la moyenne a favorise.

    A lire avec une reserve : le retrecissement tire vers la moyenne les
    joueurs peu documentes SUR TOUTES LES FACETTES A LA FOIS, ce qui cree a
    lui seul un peu de correlation positive. Elle est donc majoree ici.
    """
    out = []
    for i, a in enumerate(CLES):
        for b in CLES[i + 1:]:
            r = _rho([s["z"][a] for s in sujets],
                     [s["z"][b] for s in sujets])
            out.append({"a": a, "b": b,
                        "libelle_a": dict((f[0], f[1]) for f in FACETTES)[a],
                        "libelle_b": dict((f[0], f[1]) for f in FACETTES)[b],
                        "rho": round(r, 3)})
    out.sort(key=lambda x: -abs(x["rho"]))
    return out


def bornes_des_correlations(correl):
    """Les correlations rangees en deux familles, avec leurs bornes.

    Le resultat de cette page tient dans le CONTRASTE entre les deux : les
    facettes du jeu social s'accordent, celle des epreuves ne s'accorde avec
    rien. La moyenne des dix, elle, ne dit rien -- elle moyenne deux regimes
    opposes.

    Calcule ici, pas dans le gabarit. Jekyll 3.10 en safe mode n'a pas de quoi
    filtrer une liste de dictionnaires sans y laisser sa syntaxe, et ce depot
    a pour regle que les calculs sortent de Python.
    """
    def borne(lot):
        rhos = sorted(x["rho"] for x in lot)
        return {"paires": len(lot), "min": rhos[0], "max": rhos[-1],
                "moyenne": round(sum(rhos) / len(rhos), 3)} if rhos else None
    avec = [x for x in correl if "epreuves" in (x["a"], x["b"])]
    sans = [x for x in correl if "epreuves" not in (x["a"], x["b"])]
    return {"avec_epreuves": borne(avec), "sans_epreuves": borne(sans)}


def top_du_hasard(sujets, pr):
    """Le meme classement, sur des performances tirees au sort.

    Chaque joueur garde EXACTEMENT ses denominateurs -- son nombre de conseils,
    d'epreuves, de bulletins -- et ne perd que son talent : ses numerateurs
    sont retires a la moyenne de la population. Le retrecissement, les cotes z
    et la moyenne des cinq facettes sont ensuite refaits a l'identique.

    Ce qui en sort est un top 25 fabrique par le seul hasard. Il a un premier,
    un ecart entre le premier et le vingt-cinquieme, et l'air parfaitement
    convaincant. C'est la seule facon de montrer ce qu'un classement prouve.
    """
    rng = modeles.rng("classement-hasard")
    faux = []
    for s in sujets:
        m = {}
        for cle, _, _, _, _, _, nature in FACETTES:
            num, den = s["mesures"][cle]
            mu = pr[cle][0]
            if den <= 0:
                m[cle] = (0.0, 0.0)
            elif cle == "parcours":
                # Une note continue par saison : on la retire une fois PAR
                # participation. Tirer une seule fois puis multiplier donnerait
                # la bonne moyenne mais pas la bonne dispersion -- or c'est la
                # dispersion que la comparaison met en jeu.
                m[cle] = (float(sum(rng.uniform(0, 1)
                                    for _ in range(int(round(den))))), den)
            elif nature == "proportion":
                m[cle] = (float(rng.binomial(int(round(den)), min(mu, 1.0))), den)
            else:
                m[cle] = (float(rng.poisson(mu * den)), den)
        faux.append({"cle": s["cle"], "nom": s["nom"], "mesures": m})
    noter(faux, pr)
    return faux


# --- le biais d'epoque ------------------------------------------------------

def _periode(annee):
    return (int(annee) // 5) * 5 if annee else None


def biais_epoque(sujets, mesures, cles_par_sujet):
    """Le meme classement, mais chaque facette centree DANS son epoque.

    Le depouillement des conseils s'effondre apres 2020 : les facettes de vote
    y reposent sur presque rien, et le retrecissement y ramene tout le monde a
    la moyenne. Standardiser par periode ne repare pas la donnee manquante,
    mais il montre de combien le classement bouge quand on l'y contraint --
    c'est-a-dire la taille du biais.
    """
    periodes = {}
    for s in sujets:
        annees = [mesures[k]["_annee"] for k in cles_par_sujet[s["cle"]]
                  if mesures[k]["_annee"]]
        periodes[s["cle"]] = _periode(round(sum(annees) / len(annees))) if annees else None
    groupes = defaultdict(list)
    for s in sujets:
        groupes[periodes[s["cle"]]].append(s)
    z2 = {s["cle"]: {} for s in sujets}
    for cle_f, _, _, _, _, sens, _ in FACETTES:
        for _, membres in groupes.items():
            if len(membres) < 12:
                for s in membres:
                    z2[s["cle"]][cle_f] = s["z"][cle_f]
                continue
            z = _z([s["taux"][cle_f] for s in membres]) * sens
            for s, x in zip(membres, z):
                z2[s["cle"]][cle_f] = float(x)
    recale = sorted(sujets,
                    key=lambda s: -sum(z2[s["cle"]][c] for c in CLES) / len(CLES))
    rang2 = {s["cle"]: i for i, s in enumerate(recale, 1)}
    avant = [s["cle"] for s in sujets[:TAILLE]]
    apres = [s["cle"] for s in recale[:TAILLE]]
    return {
        "communs": len(set(avant) & set(apres)),
        "taille": TAILLE,
        "deplacement_median": int(np.median(
            [abs(rang2[c] - i) for i, c in enumerate(avant, 1)])),
        "sortants": [next(s["nom"] for s in sujets if s["cle"] == c)
                     for c in avant if c not in set(apres)],
        "entrants": [next(s["nom"] for s in sujets if s["cle"] == c)
                     for c in apres if c not in set(avant)],
    }


def depouillement_par_periode(saisons, conseils):
    """Part des conseils au depouillement complet, par tranche de cinq ans.

    C'est la mesure du biais principal de ce classement : trois facettes sur
    cinq ne se lisent que sur un conseil depouille, et le depouillement
    s'effondre a l'epoque recente. Le chiffre est calcule ici plutot que cite
    de memoire -- une caution qui repose sur un nombre tape a la main n'en est
    pas une.
    """
    par_id = {s["id"]: s for s in saisons}
    total = Counter()
    complets = Counter()
    for c in I.eliminations(conseils):
        s = par_id.get(c["saison"]) or {}
        if s.get("annulee") or s.get("en_cours") or not s.get("annee"):
            continue
        d = _periode(s["annee"])
        total[d] += 1
        if c.get("complet"):
            complets[d] += 1
    return [{"periode": f"{d}-{d + 4}", "conseils": total[d],
             "complets": complets[d],
             "part": round(100.0 * complets[d] / total[d], 1) if total[d] else None}
            for d in sorted(total)]


# --- le talent se retrouve-t-il d'une saison a l'autre ? -------------------

def test_stabilite(par_participation, mesures):
    """Un joueur bon une fois l'est-il deux fois ?

    C'est la question dont depend tout le reste : si la qualite est une
    propriete du JOUEUR, elle doit reapparaitre quand il rejoue. Si elle est
    une propriete de la saison -- du tirage des tribus, du casting, de qui
    l'avait dans le nez -- elle ne reapparait pas, et un classement des
    personnes n'a pas d'objet.

    Statistique : la correlation de rang entre le score de la premiere
    participation et la moyenne des suivantes. Modele nul : on rebat
    l'appariement, chaque « suite de carriere » etant recollee au hasard sur
    un premier passage. Rien d'autre ne bouge.
    """
    score = {s["cle"]: s["score"] for s in par_participation}
    carrieres = defaultdict(list)
    for (sid, pid) in mesures:
        if (sid, pid) in score:
            carrieres[pid].append((mesures[(sid, pid)]["_annee"] or 0, sid))
    premiers, suivants = [], []
    for pid, saisons in carrieres.items():
        if len(saisons) < 2:
            continue
        saisons.sort()
        premiers.append(score[(saisons[0][1], pid)])
        suivants.append(float(np.mean([score[(s, pid)] for _, s in saisons[1:]])))
    if len(premiers) < 12:
        return None
    observe = modeles._spearman(premiers, suivants)
    rng = modeles.rng("classement-stabilite")
    suiv = np.asarray(suivants, dtype=float)
    nulle = [modeles._spearman(premiers, rng.permutation(suiv))
             for _ in range(modeles.N_PERMUTATIONS)]
    return modeles._test(
        "talent_stable",
        "La qualité d’un joueur se retrouve-t-elle d’une saison à l’autre ?",
        "Le score d’un aventurier à sa première participation prédit-il celui "
        "de ses participations suivantes ?",
        observe, nulle, unite="",
        lecture=f"{len(premiers)} aventuriers ont joué au moins deux fois."), len(premiers)


# --- assemblage ------------------------------------------------------------

def _ligne_publiee(s, mesures, cles):
    p = [mesures[k] for k in cles]
    titres = sum(1 for m in p if m["_sort"] == "vainqueur")
    return {
        "rang": s["rang"], "nom": s["nom"], "id": s["cle"],
        "score": round(s["score"], 3),
        "participations": len(cles),
        "titres": titres,
        "finales": sum(1 for m in p if m["_sort"] in ("vainqueur", "finaliste")),
        "saisons": ", ".join(sorted({m["_titre"] for m in p if m["_titre"]})),
        "part_top": s.get("part_top"),
        "rang_min": s.get("rang_min"), "rang_max": s.get("rang_max"),
        "rang_median": s.get("rang_median"),
        "rang_p05": s.get("rang_p05"), "rang_p95": s.get("rang_p95"),
        "facettes": {c: round(s["z"][c], 2) for c in CLES},
        "preuve": {c: int(s["preuve"][c]) for c in CLES},
    }


def _sujets_joueurs(mesures, garder):
    par_pers = defaultdict(list)
    for k in mesures:
        if garder(mesures[k]):
            par_pers[k[1]].append(k)
    sujets = []
    for pid, cles in par_pers.items():
        sujets.append({"cle": pid, "nom": mesures[cles[0]]["_nom"],
                       "mesures": agreger(mesures, cles)})
    return sujets, par_pers


def tout(saisons, parts, conseils, epreuves):
    """Le bloc publie. Rien ici ne depend d'un choix fait apres coup."""
    mesures = mesurer(saisons, parts, conseils, epreuves)
    if not mesures:
        return {}
    pr = priors(mesures)

    # --- unite « joueur », perimetre complet
    sujets, cles_par = _sujets_joueurs(mesures, lambda m: True)
    noter(sujets, pr)
    resume_poids = robustesse(sujets)
    correl = correlations(sujets)
    epoque = biais_epoque(sujets, mesures, cles_par)

    # --- unite « saison jouee »
    parts_sujets = [{"cle": k, "nom": f'{m["_nom"]} — {m["_titre"]}',
                     "mesures": {c: m[c] for c in CLES}}
                    for k, m in mesures.items()]
    noter(parts_sujets, pr)
    robustesse(parts_sujets)

    # --- perimetre classique
    classiques, cles_cl = _sujets_joueurs(mesures, lambda m: not m["_speciale"])
    noter(classiques, pr)
    robustesse(classiques)
    rang_cl = {s["cle"]: s["rang"] for s in classiques}

    # --- ce que le score doit au palmares
    est_vainqueur = [any(mesures[k]["_sort"] == "vainqueur"
                         for k in cles_par[s["cle"]]) for s in sujets]
    auc = _auc([s["score"] for s in sujets], est_vainqueur)

    faux = top_du_hasard(sujets, pr)

    sans_titre = [s for s in sujets
                  if not any(mesures[k]["_sort"] == "vainqueur"
                             for k in cles_par[s["cle"]])]

    facettes = []
    for cle, libelle, question, mesure, denominateur, sens, _ in FACETTES:
        classement = sorted(sujets, key=lambda s: (-s["z"][cle], s["cle"]))
        mu, k = pr[cle]
        facettes.append({
            "cle": cle, "libelle": libelle, "mesure": mesure,
            "question": question, "denominateur": denominateur,
            "sens": "haut" if sens > 0 else "bas",
            "unite": " voix par conseil" if cle == "discretion" else " %",
            "moyenne": round(mu * (100 if cle != "discretion" else 1),
                             2 if cle == "discretion" else 1),
            "essais_fictifs": round(k, 1),
            "documentes": sum(1 for s in sujets if s["preuve"][cle] > 0),
            "top": [{
                "rang": i, "nom": s["nom"], "id": s["cle"],
                "valeur": round(s["taux"][cle] * (100 if cle != "discretion" else 1),
                                2 if cle == "discretion" else 1),
                "brut": (f'{int(s["mesures"][cle][0])} / {int(s["mesures"][cle][1])}'
                         if s["mesures"][cle][1] else "—"),
                "preuve": int(s["preuve"][cle]),
                "rang_general": s["rang"],
            } for i, s in enumerate(classement[:TAILLE_FACETTE], 1)],
        })

    stabilite = test_stabilite(parts_sujets, mesures)

    attestes = sum(1 for m in mesures.values() if m["_rang_atteste"])
    return {
        "taille": TAILLE, "taille_facette": TAILLE_FACETTE,
        "rangs_attestes": attestes,
        "rangs_deduits": len(mesures) - attestes,
        "joueurs_classes": len(sujets),
        "participations_classees": len(parts_sujets),
        "joueurs_classiques": len(classiques),
        "facettes": facettes,
        "definitions": [{"cle": c, "libelle": l, "question": q,
                         "mesure": m, "denominateur": d}
                        for c, l, q, m, d, _, _ in FACETTES],
        "top": [dict(_ligne_publiee(s, mesures, cles_par[s["cle"]]),
                     rang_classique=rang_cl.get(s["cle"]))
                for s in sujets[:TAILLE]],
        "top_classique": [{"rang": s["rang"], "nom": s["nom"], "id": s["cle"],
                           "score": round(s["score"], 3),
                           "rang_general": next(x["rang"] for x in sujets
                                                if x["cle"] == s["cle"])}
                          for s in classiques[:TAILLE]],
        "top_saisons": [{"rang": s["rang"], "nom": s["nom"],
                         "score": round(s["score"], 3),
                         "part_top": s["part_top"],
                         "sort": LIBELLE_SORT.get(mesures[s["cle"]]["_sort"],
                                                  mesures[s["cle"]]["_sort"]),
                         "aventurier": mesures[s["cle"]]["_nom"],
                         "saison": mesures[s["cle"]]["_titre"],
                         "annee": mesures[s["cle"]]["_annee"]}
                        for s in parts_sujets[:TAILLE]],
        "sans_titre": [{"rang": s["rang"], "nom": s["nom"],
                        "score": round(s["score"], 3),
                        "part_top": s["part_top"]}
                       for s in sans_titre[:TAILLE_FACETTE]],
        "robustesse": resume_poids,
        "correlations": correl,
        "correlation_moyenne": round(
            float(np.mean([c["rho"] for c in correl])), 3),
        "correlations_bornes": bornes_des_correlations(correl),
        "palmares": {
            "auc": round(auc, 3) if auc is not None else None,
            "rang_median_vainqueurs": int(np.median(
                [s["rang"] for s, v in zip(sujets, est_vainqueur) if v])),
            "rang_median_autres": int(np.median(
                [s["rang"] for s, v in zip(sujets, est_vainqueur) if not v])),
            "vainqueurs_dans_le_top": sum(1 for l in sujets[:TAILLE]
                                          if any(mesures[k]["_sort"] == "vainqueur"
                                                 for k in cles_par[l["cle"]])),
            "vainqueurs_total": len({k[1] for k in mesures
                                     if mesures[k]["_sort"] == "vainqueur"}),
        },
        "hasard": {
            "premier": round(faux[0]["score"], 3),
            "vingt_cinquieme": round(faux[TAILLE - 1]["score"], 3),
            "ecart": round(faux[0]["score"] - faux[TAILLE - 1]["score"], 3),
            "reel_premier": round(sujets[0]["score"], 3),
            "reel_vingt_cinquieme": round(sujets[TAILLE - 1]["score"], 3),
            "reel_ecart": round(sujets[0]["score"] - sujets[TAILLE - 1]["score"], 3),
            "noms": [s["nom"] for s in faux[:5]],
            "courbe_reelle": [round(s["score"], 3) for s in sujets[:TAILLE]],
            "courbe_hasard": [round(s["score"], 3) for s in faux[:TAILLE]],
        },
        "biais_epoque": dict(epoque,
                             depouillement=depouillement_par_periode(saisons,
                                                                     conseils)),
        "stabilite": ({"effectif": stabilite[1]} if stabilite else None),
        "tests": [stabilite[0]] if stabilite else [],
    }
