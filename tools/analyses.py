#!/usr/bin/env python3
"""Les analyses ajoutees apres la premiere serie d'indicateurs.

Chaque fonction rend une structure prete a etre versee dans _data/stats.yml.
Aucune ne devine : quand une valeur manque, elle est absente, jamais comblee.

Regle de reproductibilite : ne jamais boucler sur un ensemble sans le trier.
L'ordre d'iteration d'un set de chaines change d'un processus a l'autre, et le
fichier produit changerait avec lui. tools/verifie_site.py le controle.
"""
import itertools
from collections import Counter, defaultdict
from statistics import mean, median

ABANDONS = ("abandon_medical", "abandon_volontaire")


def _survie(p, saisons):
    d = saisons.get(p["saison"], {}).get("duree_jours")
    if not d or not p.get("jour_sortie"):
        return None
    return 100.0 * p["jour_sortie"] / d


def _arr(x, n=1):
    return None if x is None else round(x, n)


# ---------------------------------------------------------------- revenants

def revenants(saisons, parts, personnes):
    """Le paradoxe des revenants, leurs carrieres, leurs duos, leur graphe.

    LE PARADOXE. Compares en bloc aux autres, les revenants tiennent plus
    longtemps -- et on en conclut volontiers que l'experience paie. C'est une
    erreur de lecture : ils ne sont pas rappeles au hasard. En separant leur
    PREMIERE aventure de leurs suivantes, on voit que le tri s'est fait avant
    le retour, et que le retour lui-meme se passe moins bien.
    """
    ordre = {s["id"]: i for i, s in enumerate(
        sorted(saisons.values(), key=lambda s: (s["annee"], s.get("numero") or 0)))}
    par_pers = defaultdict(list)
    for p in parts:
        par_pers[p["id"]].append(p)

    jamais, premieres, suivantes = [], [], []
    for pid in sorted(par_pers):
        lignes = sorted(par_pers[pid], key=lambda p: ordre.get(p["saison"], 0))
        s = [_survie(p, saisons) for p in lignes]
        s = [x for x in s if x is not None]
        if not s:
            continue
        if len(lignes) > 1:
            premieres.append(s[0])
            suivantes.extend(s[1:])
        else:
            jamais.append(s[0])

    paradoxe = [
        {"libelle": "Jamais rappelés", "effectif": len(jamais),
         "survie_moyenne": _arr(mean(jamais))},
        {"libelle": "Revenants, leur première saison", "effectif": len(premieres),
         "survie_moyenne": _arr(mean(premieres))},
        {"libelle": "Revenants, leurs saisons suivantes", "effectif": len(suivantes),
         "survie_moyenne": _arr(mean(suivantes))},
    ]

    # --- carrieres : jours cumules, et part du temps possible
    jours, possible, nb = Counter(), Counter(), Counter()
    for p in parts:
        d = saisons.get(p["saison"], {}).get("duree_jours")
        if d and p.get("jour_sortie"):
            jours[p["id"]] += p["jour_sortie"]
            possible[p["id"]] += d
            nb[p["id"]] += 1
    noms = {x["id"]: x["nom"] for x in personnes}
    carrieres = sorted(
        ({"id": i, "nom": noms.get(i, i), "saisons": nb[i], "jours": jours[i],
          "jours_possibles": possible[i],
          "part_du_temps": _arr(100.0 * jours[i] / possible[i])}
         for i in jours if nb[i] >= 2),
        key=lambda x: (-x["jours"], x["nom"]))

    # --- duos : combien de saisons partagees
    par_saison = defaultdict(set)
    for p in parts:
        par_saison[p["saison"]].add(p["id"])
    croises = Counter()
    for sid in sorted(par_saison):
        for a, b in itertools.combinations(sorted(par_saison[sid]), 2):
            croises[(a, b)] += 1
    duos = sorted(
        ({"a": noms.get(a, a), "b": noms.get(b, b), "saisons": n}
         for (a, b), n in croises.items() if n >= 2),
        key=lambda x: (-x["saisons"], x["a"], x["b"]))

    # --- le graphe : on ne garde que les revenants, sans quoi il est illisible
    revenus = sorted(i for i in nb if nb[i] >= 2)
    rang = {i: k for k, i in enumerate(revenus)}
    aretes = sorted(
        ({"de": rang[a], "vers": rang[b], "poids": n}
         for (a, b), n in croises.items() if a in rang and b in rang),
        key=lambda x: (x["de"], x["vers"]))
    degre = Counter()
    for e in aretes:
        degre[e["de"]] += 1
        degre[e["vers"]] += 1
    premiere_saison = {}
    for p in parts:
        if p["id"] in rang:
            k = ordre.get(p["saison"], 0)
            premiere_saison[p["id"]] = min(premiere_saison.get(p["id"], k), k)
    noeuds = [{"rang": rang[i], "nom": noms.get(i, i), "saisons": nb[i],
               "degre": degre.get(rang[i], 0), "arrivee": premiere_saison.get(i, 0)}
              for i in revenus]

    # Le mieux connecte de TOUS, revenants ou non : la reponse surprend, et
    # c'est justement pour cela qu'elle merite d'etre calculee sur tout le
    # monde et pas seulement sur les revenants.
    degre_total = Counter()
    for sid in sorted(par_saison):
        gens = sorted(par_saison[sid])
        for i in gens:
            degre_total[i] += len(gens) - 1
    connectes = sorted(
        ({"nom": noms.get(i, i), "liens": n, "saisons": nb.get(i, 1)}
         for i, n in degre_total.items()),
        key=lambda x: (-x["liens"], x["nom"]))

    return {
        "paradoxe": paradoxe,
        "carrieres": carrieres[:20],
        "sans_faute": [c for c in carrieres if c["part_du_temps"] == 100.0],
        "duos": duos[:15],
        "nb_duos_recurrents": len(duos),
        "graphe": {"noeuds": noeuds, "aretes": aretes,
                   "nb_liens_total": sum(1 for _ in croises)},
        "les_plus_connectes": connectes[:10],
    }


# ------------------------------------------------------------------- risque

def risque(saisons, parts, pas=10):
    """La courbe de risque : chance de sortir sachant qu'on est encore la.

    Une courbe de survie dit combien il en reste. Celle-ci dit tout autre
    chose : parmi ceux qui sont encore en jeu, quelle part s'en va maintenant.
    C'est le taux de hasard des statisticiens, et c'est la seule forme qui
    montre que le jeu devient plus dangereux a mesure qu'il avance.

    Le temps est ramene en part de saison : les editions ne durent pas toutes
    le meme nombre de jours.
    """
    lot = [p for p in parts
           if not saisons[p["saison"]].get("speciale")
           and not saisons[p["saison"]].get("annulee")
           and p.get("jour_sortie")]
    tranches = Counter()
    for p in lot:
        t = min(100, int(round(_survie(p, saisons) / pas)) * pas)
        tranches[t] += 1

    lignes = []
    restants = len(lot)
    for t in sorted(tranches):
        n = tranches[t]
        if restants <= 0:
            break
        lignes.append({
            "tranche": t,
            "sortants": n,
            "encore_en_jeu": restants,
            "risque": _arr(100.0 * n / restants),
        })
        restants -= n

    jours = Counter(p["jour_sortie"] for p in lot)
    return {
        "effectif": len(lot),
        "pas": pas,
        "tranches": lignes,
        "jours_les_plus_meurtriers": [
            {"jour": j, "sortants": n} for j, n in sorted(
                jours.items(), key=lambda x: (-x[1], x[0]))[:8]],
    }


def survie_par_saison(saisons, parts):
    """Une courbe de survie par saison, pour les petits multiples.

    Chaque saison rend le nombre d'aventuriers encore en jeu a chaque dixieme
    de son deroulement. Les axes sont les memes partout : c'est ce qui rend
    les trente-quatre vignettes comparables d'un coup d'oeil.
    """
    par_saison = defaultdict(list)
    for p in parts:
        if p.get("jour_sortie"):
            par_saison[p["saison"]].append(p)

    out = []
    for sid in sorted(par_saison, key=lambda s: (saisons[s]["annee"],
                                                 saisons[s].get("numero") or 0)):
        s = saisons[sid]
        if s.get("annulee"):
            continue
        # Une saison sans duree connue ne peut pas etre ramenee en pourcentage.
        parcours = [x for x in (_survie(p, saisons) for p in par_saison[sid])
                    if x is not None]
        n = len(parcours)
        if not n:
            continue
        points = []
        for t in range(0, 101, 5):
            restants = sum(1 for x in parcours if x > t - 0.001)
            points.append(round(100.0 * restants / n))
        out.append({
            "id": sid, "numero": s.get("numero"), "titre": s["titre"],
            "annee": s["annee"], "speciale": bool(s.get("speciale")),
            "effectif": n, "restants": points,
        })
    return out


# ------------------------------------------------------------------ casting

def casting(saisons, parts):
    """L'age du casting : etendue par saison, et generation des aventuriers."""
    par_saison = defaultdict(list)
    for p in parts:
        if p.get("age"):
            par_saison[p["saison"]].append(p)

    etendues = []
    for sid in sorted(par_saison, key=lambda s: (saisons[s]["annee"],
                                                 saisons[s].get("numero") or 0)):
        s = saisons[sid]
        if s.get("annulee"):
            continue
        ages = sorted(p["age"] for p in par_saison[sid])
        if len(ages) < 4:
            continue
        etendues.append({
            "id": sid, "numero": s.get("numero"), "titre": s["titre"],
            "annee": s["annee"], "speciale": bool(s.get("speciale")),
            "min": ages[0], "median": _arr(median(ages)), "max": ages[-1],
            "etendue": ages[-1] - ages[0],
        })

    naissances = Counter()
    for p in parts:
        a = saisons.get(p["saison"], {}).get("annee")
        if a and p.get("age"):
            naissances[(a - p["age"]) // 10 * 10] += 1

    return {
        "etendues": etendues,
        "plus_large": max(etendues, key=lambda x: x["etendue"]) if etendues else None,
        "plus_resserree": min(etendues, key=lambda x: x["etendue"]) if etendues else None,
        "generations": [{"decennie": d, "effectif": n}
                        for d, n in sorted(naissances.items())],
    }


# ---------------------------------------------------------------- programme

def programme(saisons):
    """La frise du programme : quand chaque saison a ete diffusee, et par qui."""
    JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    lignes, jours, mecaniques = [], Counter(), defaultdict(list)
    for s in sorted(saisons.values(), key=lambda s: (s["annee"], s.get("numero") or 0)):
        if s.get("annulee"):
            continue
        d = s.get("diffusion") or {}
        debut, fin = d.get("debut"), d.get("fin")
        if debut:
            jours[JOURS[debut.weekday()]] += 1
        for m in s.get("mecaniques") or []:
            mecaniques[m].append(s["annee"])
        lignes.append({
            "id": s["id"], "numero": s.get("numero"), "titre": s["titre"],
            "annee": s["annee"], "speciale": bool(s.get("speciale")),
            "presentateur": s.get("presentateur"),
            "debut": debut.isoformat() if debut else None,
            "fin": fin.isoformat() if fin else None,
            "jour_semaine": JOURS[debut.weekday()] if debut else None,
            "duree_jours": s.get("duree_jours"),
        })
    return {
        "saisons": lignes,
        "jour_de_lancement": [{"jour": j, "effectif": n}
                              for j, n in jours.most_common()],
        "presentateurs": [{"nom": n, "saisons": k} for n, k in Counter(
            l["presentateur"] for l in lignes if l["presentateur"]).most_common()],
        "mecaniques": sorted(
            ({"code": m, "saisons": len(a), "premiere": min(a), "derniere": max(a)}
             for m, a in mecaniques.items()),
            key=lambda x: (-x["saisons"], x["code"])),
    }


# -------------------------------------------------------------------- votes

def reciprocite(conseils, parts, saisons):
    """« Tu as ecrit mon nom, j'ai ecrit le tien. »

    On ne compte que les conseils au depouillement complet : ailleurs, un
    bulletin manquant ferait passer une reciprocite pour une absence.
    """
    couples = Counter()
    for c in conseils:
        if not c.get("complet"):
            continue
        for b in c.get("votes") or []:
            if b.get("votant_rattache") and b.get("cible_rattachee"):
                couples[(c["saison"], b["votant"], b["cible"])] += 1
    rec = sum(1 for (s, a, b) in couples if (s, b, a) in couples)
    return {
        "couples": len(couples),
        "reciproques": rec,
        "part": _arr(100.0 * rec / len(couples)) if couples else None,
    }


def arc_des_votes(conseils, parts, saisons):
    """Le diagramme en arcs d'une saison : qui a ecrit le nom de qui.

    La saison retenue est celle dont le depouillement est le plus complet --
    choisie par le calcul, pas par gout. Les aventuriers sont ranges dans
    l'ordre de leur sortie : la structure du camp apparait alors seule.
    """
    complets = defaultdict(list)
    for c in conseils:
        if c.get("complet"):
            complets[c["saison"]].append(c)
    if not complets:
        return None
    sid = max(sorted(complets), key=lambda s: sum(len(c["votes"]) for c in complets[s]))

    lot = sorted((p for p in parts if p["saison"] == sid),
                 key=lambda p: (p.get("jour_sortie") or 0, p["nom"]))
    rang = {p["id"]: i for i, p in enumerate(lot)}
    liens = Counter()
    for c in complets[sid]:
        for b in c["votes"]:
            if b.get("votant_rattache") and b.get("cible_rattachee"):
                a, z = rang.get(b["votant"]), rang.get(b["cible"])
                if a is not None and z is not None:
                    liens[(a, z)] += 1
    return {
        "saison": sid,
        "titre": saisons[sid]["titre"],
        "annee": saisons[sid]["annee"],
        "noeuds": [{"rang": rang[p["id"]], "nom": p["nom"],
                    "jour_sortie": p.get("jour_sortie"),
                    "couleur": p.get("couleur")} for p in lot],
        "liens": sorted(({"de": a, "vers": z, "poids": n}
                         for (a, z), n in liens.items()),
                        key=lambda x: (x["de"], x["vers"])),
        "bulletins": sum(liens.values()),
    }


def voix_pour_eliminer(conseils):
    """Combien de bulletins portent le nom de celui qui part."""
    n = Counter(c["votes_contre"] for c in conseils
                if c.get("votes_contre") and c.get("votes_exprimes"))
    total = sum(n.values())
    return {
        "effectif": total,
        "mode": max(n, key=lambda k: (n[k], -k)) if n else None,
        "repartition": [{"voix": v, "effectif": k, "part": _arr(100.0 * k / total)}
                        for v, k in sorted(n.items())],
    }


def premiere_epreuve(saisons, parts, epreuves):
    """Gagner la premiere epreuve individuelle mene-t-il plus loin ?

    L'effectif est petit -- une saison, un cas -- et l'ecart doit se lire avec
    cette reserve. Il est donne avec son nombre d'observations.
    """
    par_saison = defaultdict(list)
    for e in epreuves:
        if e.get("forme") == "individuelle" and e.get("episode"):
            par_saison[e["saison"]].append(e)
    idx = {(p["saison"], p["id"]): p for p in parts}

    gagnants = []
    for sid in sorted(par_saison):
        premiere = min(par_saison[sid], key=lambda e: e["episode"])
        for v in premiere.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                p = idx.get((sid, v["id"]))
                s = _survie(p, saisons) if p else None
                if s is not None:
                    gagnants.append(s)

    ensemble = [_survie(p, saisons) for p in parts]
    ensemble = [x for x in ensemble if x is not None]
    return {
        "effectif": len(gagnants),
        "survie_gagnants": _arr(mean(gagnants)) if gagnants else None,
        "survie_ensemble": _arr(mean(ensemble)) if ensemble else None,
        "saisons_couvertes": len(par_saison),
    }
