#!/usr/bin/env python3
"""Combien de Koh-Lanta se predit, et a partir de quoi.

CE QUE CE MODULE AJOUTE. Le site publie une vingtaine d'associations, chacune
corrigee pour la multiplicite des tests. Une association dit « ceci compte » ;
elle ne dit pas « voici ce qu'on saurait deviner ». C'est une autre question, et
elle se repond d'une seule facon honnete : demander a un modele de designer
l'elimine d'une soiree QU'IL N'A JAMAIS VUE.

LA DISCIPLINE. Une saison est exclue a chaque tour -- le modele apprend sur
toutes les autres et pronostique celle-la. Un decoupage au hasard tricherait :
deux presences d'un meme conseil ne sont pas independantes, et la moitie d'une
soiree suffirait a deviner l'autre. C'est exactement la regle de
`modeles.pronostic`, qui pose la meme question au CASTING ; celle-ci la pose au
JEU.

LE MODELE. Un logit conditionnel : chaque conseil est son propre groupe de
comparaison, le modele ne compare jamais deux soirees entre elles. La taille du
conseil, la saison, l'epoque et la composition du camp disparaissent donc du
calcul sans qu'on ait a les mesurer.

TROIS JEUX DE VARIABLES EMBOITES, pour dire d'ou vient le signal :

    fiche      ce que la production sait au casting : sexe, doyen, benjamin
    place      + la place occupee dans le camp ce soir-la
    jeu        + ce que la soiree elle-meme a produit : immunite, confort,
               voix recues au conseil precedent, voix recues depuis le debut

LE MODELE NUL. Les pronostics sont HORS ECHANTILLON : ils ne dependent pas des
etiquettes qu'on cherche a retrouver. Sous l'hypothese « l'elimine est tire au
hasard parmi les presents », le rang qu'il occupe dans le classement du modele
est donc uniforme, et sa loi se simule exactement -- conseil par conseil, avec
les tailles reelles. Aucun reapprentissage n'est necessaire, et c'est ce qui
rend le test faisable.
"""
import collections

import numpy as np

import modeles

# Un conseil de moins de trois presents n'a pas de classement a produire, et
# une saison de moins de cinq conseils ne peut pas servir de pli.
MIN_PRESENTS = 3
MIN_CONSEILS_PLI = 5
TIRAGES = 10000

JEUX = (
    ("fiche", "La fiche d’inscription",
     ("femme", "doyen", "benjamin"),
     "Le sexe, le plus âgé du camp, le plus jeune. Rien de ce que la soirée a produit."),
    ("place", "La place dans le camp",
     ("femme", "doyen", "benjamin",
      "bandeau_minoritaire", "sexe_minoritaire", "apres_fusion"),
     "On ajoute la position occupée ce soir-là : bandeau et sexe minoritaires, "
     "avant ou après la réunification."),
    ("jeu", "Ce que la soirée a produit",
     ("femme", "doyen", "benjamin",
      "bandeau_minoritaire", "sexe_minoritaire", "apres_fusion",
      "confort", "voix_prec_1_2", "voix_prec_3", "voix_prec_4",
      "voix_cumul_haut"),
     "On ajoute le confort du soir et les voix déjà reçues — celles du conseil "
     "précédent, et le total depuis le début."),
)


def _voix_par_conseil(conseils):
    """Voix recues par chacun a chaque conseil DEPOUILLE, et le rang du conseil.

    Seuls les conseils complets comptent : un depouillement partiel donnerait
    un « zero voix » qui n'est qu'un bulletin manquant. C'est la meme regle que
    partout ailleurs sur ce site.
    """
    par_saison = collections.defaultdict(list)
    for c in conseils:
        if c.get("type") == "elimination":
            par_saison[c.get("saison")].append(c)
    recues = {}
    for sid, lot in par_saison.items():
        lot.sort(key=lambda c: c.get("numero") or 0)
        for c in lot:
            if not c.get("complet"):
                continue
            compte = collections.Counter()
            for b in c.get("votes") or []:
                if b.get("cible_rattachee"):
                    compte[b["cible"]] += 1
            recues[(sid, c["numero"])] = compte
    return recues


def lignes(par_saison, parts, conseils, epreuves, bloc_fusion):
    """Une ligne par presence a un conseil, avec ce qu'on savait AVANT le vote."""
    # Meme construction que modeles.autour_du_feu : l'episode de reunification
    # se lit dans les lignes du bloc `fusion`, pas dans un champ de saison.
    fusion_ep = {l["saison"]: l["episode"]
                 for l in ((bloc_fusion or {}).get("lignes") or [])}

    brutes = modeles._camps(par_saison, parts, conseils, epreuves, fusion_ep)
    recues = _voix_par_conseil(conseils)

    # Numeros de conseil d'une saison, dans l'ordre : « le conseil precedent »
    # est le precedent NUMERO, pas le precedent depouille -- sinon on sauterait
    # par-dessus un conseil sans le dire, et « aucune voix la fois d'avant »
    # deviendrait « aucune voix depuis longtemps ».
    numeros = collections.defaultdict(list)
    for c in conseils:
        if c.get("type") == "elimination":
            numeros[c.get("saison")].append(c.get("numero") or 0)
    for sid in numeros:
        numeros[sid].sort()

    out = []
    for l in brutes:
        sid, num, pid = l["saison"], l["conseil"], l["personne"]
        suite = numeros.get(sid) or []
        try:
            rang = suite.index(num)
        except ValueError:
            continue
        # voix au conseil precedent : connue seulement s'il etait depouille
        prec = suite[rang - 1] if rang > 0 else None
        v_prec = None
        if prec is not None and (sid, prec) in recues:
            v_prec = recues[(sid, prec)].get(pid, 0)
        # voix cumulees sur tous les conseils depouilles AVANT celui-ci
        cumul, depouilles = 0, 0
        for n in suite:
            if n >= num:
                break
            if (sid, n) in recues:
                depouilles += 1
                cumul += recues[(sid, n)].get(pid, 0)

        out.append({
            "saison": sid, "conseil": num, "personne": pid, "nom": l["nom"],
            "sorti": l["sorti"], "risque": l["risque"],
            "femme": l["femme"], "doyen": l["doyen"], "benjamin": l["benjamin"],
            "bandeau_minoritaire": l["bandeau_minoritaire"],
            "sexe_minoritaire": l["sexe_minoritaire"],
            "apres_fusion": 1 if l["apres_fusion"] else 0,
            "immunite": l["immunite"], "confort": l["confort"],
            "voix_prec_1_2": None if v_prec is None else int(v_prec in (1, 2)),
            "voix_prec_3": None if v_prec is None else int(v_prec == 3),
            "voix_prec_4": None if v_prec is None else int(v_prec >= 4),
            # Le cumul se lit RELATIVEMENT au camp : « beaucoup de voix » n'a
            # pas le meme sens au troisieme conseil et au quinzieme.
            "voix_cumul": None if not depouilles else cumul,
            "_depouilles": depouilles,
        })

    # « Haut » veut dire : au-dessus de la mediane du camp, ce soir-la. Un seuil
    # absolu melangerait un debut de saison et une fin.
    par_conseil = collections.defaultdict(list)
    for l in out:
        par_conseil[(l["saison"], l["conseil"])].append(l)
    for lot in par_conseil.values():
        valeurs = [l["voix_cumul"] for l in lot if l["voix_cumul"] is not None]
        seuil = float(np.median(valeurs)) if valeurs else None
        for l in lot:
            l["voix_cumul_haut"] = (None if l["voix_cumul"] is None or seuil is None
                                    else int(l["voix_cumul"] > seuil))
    return out


def _groupes(lignes_, colonnes):
    """Les conseils utilisables pour ce jeu de variables.

    Une variable absente ne veut pas dire la meme chose selon QUI elle
    concerne, et les deux cas se traitent differemment :

    * absente pour TOUT le conseil -- le confort d'un soir a plusieurs
      conseils, les voix d'un conseil precedent non depouille. Elle est alors
      constante dans le groupe, et une constante de groupe DISPARAIT du logit
      conditionnel : elle ne peut ni aider ni nuire au classement. On la pose a
      zero, et le conseil reste. Ce n'est pas une imputation, c'est une
      identite algebrique.
    * absente pour CERTAINS seulement -- un bandeau ni majoritaire ni
      minoritaire, un age qui manque. La, poser zero comparerait des presences
      sur une valeur inventee. Le conseil est ecarte ENTIER : n'en garder qu'une
      partie fausserait le groupe de comparaison, et le vrai elimine pourrait
      ne plus y figurer du tout.
    """
    par_conseil = collections.defaultdict(list)
    for l in lignes_:
        par_conseil[(l["saison"], l["conseil"])].append(l)
    gardes = []
    for cle, lot in sorted(par_conseil.items()):
        # L'IMMUNISE SORT DU CHOIX, il ne devient pas une variable. Qu'il ne
        # puisse pas etre elimine est une regle du jeu, pas une chose a
        # deviner : lui donner un coefficient gonflerait l'adresse du modele
        # avec ce que tout le monde sait deja -- et, techniquement, produirait
        # une separation parfaite que le maximum de vraisemblance ne sait pas
        # ajuster. La ou l'immunise n'est pas connu, personne n'est retire :
        # le choix est simplement plus large, ce qui ne favorise pas le modele.
        lot = [l for l in lot if l["immunite"] != 1]
        if len(lot) < MIN_PRESENTS:
            continue
        if sum(l["sorti"] for l in lot) != 1:
            continue
        valeurs, partielle = {}, False
        for c in colonnes:
            manquants = sum(1 for l in lot if l[c] is None)
            if manquants == 0:
                valeurs[c] = [float(l[c]) for l in lot]
            elif manquants == len(lot):
                valeurs[c] = [0.0] * len(lot)
            else:
                partielle = True
                break
        if partielle:
            continue
        gardes.append((cle, [{**l, **{c: valeurs[c][i] for c in colonnes}}
                             for i, l in enumerate(lot)]))
    return gardes


# La penalite du logit conditionnel. Elle n'est pas un reglage a optimiser :
# c'est une valeur fixe, faible, posee une fois et jamais bougee -- la choisir
# au vu du resultat reviendrait a regarder les saisons tenues a l'ecart. Toutes
# les variables valent 0 ou 1, donc 1.0 sur la somme des carres est une force
# comparable d'un jeu a l'autre. Son role est d'empecher un coefficient de
# partir a l'infini quand une variable separe parfaitement l'echantillon
# d'apprentissage : le maximum de vraisemblance, lui, n'a alors pas de solution
# finie, et l'ajustement echoue.
PENALITE = 1.0


def _ajuster(gardes, colonnes):
    """Logit conditionnel, ajuste ici plutot que par une bibliotheque.

    On n'a besoin que des COEFFICIENTS -- le classement des presents d'un
    conseil ne demande rien d'autre. La vraisemblance conditionnelle vaut, pour
    chaque conseil, le score de celui qui part moins le log-somme-exp des
    scores du camp ; l'intercept et tout ce qui est constant dans le conseil
    disparaissent d'eux-memes.
    """
    from scipy.optimize import minimize

    lots = []
    for _, lot in gardes:
        X = np.array([[float(l[c]) for c in colonnes] for l in lot], dtype=float)
        i = [k for k, l in enumerate(lot) if l["sorti"] == 1][0]
        lots.append((X, i))
    if not lots:
        return None, []
    toutes = np.vstack([X for X, _ in lots])
    vivantes = [j for j in range(toutes.shape[1]) if toutes[:, j].std() > 0]
    if not vivantes:
        return None, []
    lots = [(X[:, vivantes], i) for X, i in lots]

    def objectif(b):
        perte = PENALITE * float(b @ b)
        grad = 2.0 * PENALITE * b
        for X, i in lots:
            s = X @ b
            m = s.max()
            e = np.exp(s - m)
            somme = e.sum()
            perte -= s[i] - (m + np.log(somme))
            grad -= X[i] - (e @ X) / somme
        return perte, grad

    r = minimize(objectif, np.zeros(len(vivantes)), jac=True, method="L-BFGS-B")
    return r.x, vivantes


def hors_echantillon(lignes_, colonnes):
    """Une saison exclue a chaque tour. Rend le rang du vrai elimine, conseil par conseil."""
    gardes = _groupes(lignes_, colonnes)
    saisons = sorted({cle[0] for cle, _ in gardes})
    rangs, tailles, premiers = [], [], []
    plis = 0
    for pli in saisons:
        appris = [x for x in gardes if x[0][0] != pli]
        tenus = [x for x in gardes if x[0][0] == pli]
        if len(tenus) < 1 or len(appris) < MIN_CONSEILS_PLI:
            continue
        beta, vivantes = _ajuster(appris, colonnes)
        if beta is None:
            continue
        plis += 1
        for _, lot in tenus:
            score = []
            for l in lot:
                v = [float(l[c]) for c in colonnes]
                score.append(float(np.dot([v[j] for j in vivantes], beta)))
            ordre = np.argsort(-np.array(score), kind="stable")
            place = {int(k): i for i, k in enumerate(ordre)}
            vrai = [i for i, l in enumerate(lot) if l["sorti"] == 1][0]
            n = len(lot)
            rangs.append(place[vrai] / (n - 1.0))
            tailles.append(n)
            premiers.append(1 if place[vrai] == 0 else 0)
    return {
        "conseils": len(rangs), "plis": plis,
        "presences": sum(tailles),
        "rang_moyen": rangs, "tailles": tailles, "premiers": premiers,
    }


def _nulle(tailles, g, tirages=TIRAGES):
    """Loi du rang moyen quand l'elimine est tire au hasard parmi les presents.

    Les pronostics sont hors echantillon : ils ne dependent pas de l'etiquette
    qu'on cherche. Sous cette hypothese, le rang du vrai elimine est uniforme
    sur les n places du conseil, et rien n'a besoin d'etre reappris.
    """
    t = np.array(tailles)
    tirees = g.integers(0, t, size=(tirages, len(t)))
    return (tirees / (t - 1.0)).mean(axis=1)


def _nulle_premiers(tailles, g, tirages=TIRAGES):
    t = np.array(tailles)
    tirees = g.integers(0, t, size=(tirages, len(t)))
    return (tirees == 0).mean(axis=1)


def tout(par_saison, parts, conseils, epreuves, bloc_fusion):
    """Le bloc publie, et le test qui rejoint le registre commun."""
    brut = lignes(par_saison, parts, conseils, epreuves, bloc_fusion)
    if not brut:
        return {}
    g = modeles.rng("prevision")

    resultats, tests = [], []
    for cle, libelle, colonnes, description in JEUX:
        r = hors_echantillon(brut, colonnes)
        if r["conseils"] < 30:
            continue
        rangs = np.array(r["rang_moyen"])
        nulle = _nulle(r["tailles"], g)
        nulle_p = _nulle_premiers(r["tailles"], g)
        premiers = float(np.mean(r["premiers"]))
        resultats.append({
            "cle": cle, "libelle": libelle, "description": description,
            "variables": len(colonnes),
            "conseils": r["conseils"], "plis": r["plis"], "presences": r["presences"],
            "rang_moyen": modeles._arr(float(rangs.mean()), 4),
            "rang_hasard": modeles._arr(float(nulle.mean()), 4),
            "taille_moyenne": modeles._arr(float(np.mean(r["tailles"])), 1),
            "premiers": modeles._arr(100.0 * premiers, 1),
            "premiers_hasard": modeles._arr(100.0 * float(nulle_p.mean()), 1),
            "ecart_types": modeles._arr(
                float((rangs.mean() - nulle.mean()) / (nulle.std() or 1)), 2),
        })
        if cle == "jeu":
            tests.append(modeles._test(
                "prevision_conseil",
                "Deviner qui part, dans une saison jamais vue",
                "Un modèle entraîné sur toutes les saisons sauf une désigne-t-il "
                "l’éliminé de celle-là mieux que le hasard ?",
                float(rangs.mean()), nulle, unite="rang normalisé",
                lecture="Chaque conseil est classé du plus au moins menacé, puis on "
                        "regarde à quelle place s'y trouve celui qui est réellement "
                        "parti — 0 pour la première, 1 pour la dernière. Le hasard "
                        "donne 0,5. Un observé PLUS PETIT veut dire que le modèle "
                        "voit venir la sortie. Une saison est exclue à chaque tour : "
                        "le conseil pronostiqué n'a jamais servi à apprendre."))

    if not resultats:
        return {}
    return {
        "jeux": resultats,
        "tirages": TIRAGES,
        "min_presents": MIN_PRESENTS,
        "tests": tests,
    }
