#!/usr/bin/env python3
"""Calcule les agregats et ecrit _data/stats.yml.

Pourquoi precalculer ? Le constructeur de GitHub Pages est un Jekyll 3.10, dont
le langage de gabarit n'a meme pas de filtre `sum` : croiser 645 participations
avec 3 400 bulletins a la construction du site est hors de portee. Les calculs
sont donc faits ici, une fois, et le resultat est commite. Le site ne fait plus
qu'afficher.

Deux perimetres coexistent partout :
  * `classiques` -- les saisons regulieres achevees, perimetre par defaut ;
  * `toutes`     -- avec les editions speciales, ou les revenants faussent les
                    moyennes d'age et de longevite.

    tools/atelier python3 tools/build_stats.py
"""
import os
import sys
from collections import Counter, defaultdict
from statistics import mean, median

import yaml

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RACINE, "tools", "extraction"))
from csp import classer, libelles           # noqa: E402

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Produit par tools/build_stats.py a partir de _data/saisons.yml,
# participations.yml, personnes.yml et conseils.yml.
#
#     tools/atelier python3 tools/build_stats.py
#
# Sauf mention contraire, les chiffres portent sur les SAISONS CLASSIQUES
# achevees. Les blocs `toutes` ajoutent les editions speciales.
#
"""

TRANCHES = [(18, 24), (25, 29), (30, 34), (35, 39), (40, 44), (45, 100)]
LIBELLE_TRANCHE = {(18, 24): "18-24 ans", (25, 29): "25-29 ans", (30, 34): "30-34 ans",
                   (35, 39): "35-39 ans", (40, 44): "40-44 ans", (45, 100): "45 ans et plus"}

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


def arrondi(x, n=1):
    return None if x is None else round(float(x), n)


def part(compte, total, n=1):
    return None if not total else round(100.0 * compte / total, n)


def tranche(age):
    for bornes in TRANCHES:
        if bornes[0] <= age <= bornes[1]:
            return LIBELLE_TRANCHE[bornes]
    return None


# --- chargement ------------------------------------------------------------

def charger():
    def lire(nom):
        chemin = os.path.join(RACINE, "_data", nom)
        return yaml.safe_load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else []

    saisons = lire("saisons.yml")
    parts = lire("participations.yml")
    personnes = lire("personnes.yml")
    conseils = lire("conseils.yml")
    epreuves = lire("epreuves.yml")

    par_saison = {s["id"]: s for s in saisons}
    for p in parts:
        s = par_saison.get(p["saison"], {})
        p["_saison"] = s
        p["_speciale"] = bool(s.get("speciale"))
        p["_annee"] = s.get("annee")
        p["_duree"] = s.get("duree_jours")
        p["_csp"] = classer(p.get("profession"))
        d = p.get("jour_sortie")
        p["_survie"] = round(100.0 * d / s["duree_jours"], 1) if d and s.get("duree_jours") else None
    return saisons, parts, personnes, conseils, epreuves, par_saison


def perimetre(parts, avec_speciales):
    out = []
    for p in parts:
        s = p["_saison"]
        if s.get("annulee") or s.get("en_cours"):
            continue
        if not avec_speciales and p["_speciale"]:
            continue
        out.append(p)
    return out


# --- blocs de calcul -------------------------------------------------------

def bloc_vainqueurs(parts):
    v = [p for p in parts if p.get("sort") == "vainqueur"]
    ages = [p["age"] for p in v if p.get("age")]
    if not ages:
        return {}
    return {
        "effectif": len(v),
        "age_moyen": arrondi(mean(ages)),
        "age_median": arrondi(median(ages)),
        "age_min": min(ages),
        "age_max": max(ages),
        "part_40_et_plus": part(sum(1 for a in ages if a >= 40), len(ages)),
        "par_tranche": [
            {"tranche": LIBELLE_TRANCHE[b],
             "effectif": sum(1 for a in ages if b[0] <= a <= b[1]),
             "part": part(sum(1 for a in ages if b[0] <= a <= b[1]), len(ages))}
            for b in TRANCHES],
        "par_genre": [
            {"genre": g, "libelle": "Femmes" if g == "f" else "Hommes",
             "effectif": sum(1 for p in v if p.get("genre") == g),
             "part": part(sum(1 for p in v if p.get("genre") == g), len(v))}
            for g in ("f", "h")],
        "par_couleur": [
            {"couleur": c, "effectif": n, "part": part(n, len(v))}
            for c, n in Counter(p.get("couleur") for p in v if p.get("couleur")).most_common()],
        "par_metier": [
            {"code": c, "libelle": libelles().get(c, c), "effectif": n,
             "part": part(n, len(v))}
            for c, n in Counter(p["_csp"] for p in v if p["_csp"]).most_common()],
    }


def bloc_couleurs(parts):
    out = []
    for couleur in sorted({p.get("couleur") for p in parts if p.get("couleur")}):
        lot = [p for p in parts if p.get("couleur") == couleur]
        survies = [p["_survie"] for p in lot if p["_survie"] is not None]
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        out.append({
            "couleur": couleur,
            "effectif": len(lot),
            "survie_moyenne": arrondi(mean(survies)) if survies else None,
            "victoires": sum(1 for p in lot if p.get("sort") == "vainqueur"),
            "finales": finales,
            "taux_finale": part(finales, len(lot)),
        })
    return sorted(out, key=lambda x: -x["effectif"])


def bloc_metiers(parts):
    lib = libelles()
    out = []
    for code in {p["_csp"] for p in parts if p["_csp"]}:
        lot = [p for p in parts if p["_csp"] == code]
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        survies = [p["_survie"] for p in lot if p["_survie"] is not None]
        ages = [p["age"] for p in lot if p.get("age")]
        out.append({
            "code": code,
            "libelle": lib.get(code, code),
            "effectif": len(lot),
            "part_du_casting": part(len(lot), len(parts)),
            "victoires": sum(1 for p in lot if p.get("sort") == "vainqueur"),
            "finales": finales,
            "taux_finale": part(finales, len(lot)),
            "survie_moyenne": arrondi(mean(survies)) if survies else None,
            "age_moyen": arrondi(mean(ages)) if ages else None,
        })
    return sorted(out, key=lambda x: -x["effectif"])


def bloc_genre(parts):
    resume = []
    for g, lib in (("f", "Femmes"), ("h", "Hommes")):
        lot = [p for p in parts if p.get("genre") == g]
        survies = [p["_survie"] for p in lot if p["_survie"] is not None]
        jours = [p["jour_sortie"] for p in lot if p.get("jour_sortie")]
        ages = [p["age"] for p in lot if p.get("age")]
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        resume.append({
            "genre": g, "libelle": lib, "effectif": len(lot),
            "part_du_casting": part(len(lot), len(parts)),
            "survie_moyenne": arrondi(mean(survies)) if survies else None,
            "jour_moyen": arrondi(mean(jours)) if jours else None,
            "age_moyen": arrondi(mean(ages)) if ages else None,
            "victoires": sum(1 for p in lot if p.get("sort") == "vainqueur"),
            "finales": finales,
            "taux_finale": part(finales, len(lot)),
        })

    decennies = []
    for debut in (2000, 2010, 2020):
        lot = [p for p in parts if p["_annee"] and debut <= p["_annee"] < debut + 10]
        if not lot:
            continue
        ligne = {"decennie": f"{debut}s", "effectif": len(lot)}
        for g, lib in (("f", "femmes"), ("h", "hommes")):
            sous = [p["_survie"] for p in lot if p.get("genre") == g and p["_survie"] is not None]
            ligne[f"survie_{lib}"] = arrondi(mean(sous)) if sous else None
            ligne[f"effectif_{lib}"] = sum(1 for p in lot if p.get("genre") == g)
        decennies.append(ligne)
    return {"resume": resume, "par_decennie": decennies}


def bloc_sorties(parts):
    total = len(parts)
    repartition = [
        {"sort": s, "libelle": LIBELLE_SORT.get(s, s), "effectif": n, "part": part(n, total)}
        for s, n in Counter(p.get("sort") for p in parts if p.get("sort")).most_common()]

    evolution = []
    for debut in (2000, 2010, 2020):
        lot = [p for p in parts if p["_annee"] and debut <= p["_annee"] < debut + 10]
        if not lot:
            continue
        c = Counter(p.get("sort") for p in lot if p.get("sort"))
        evolution.append({
            "decennie": f"{debut}s", "effectif": len(lot),
            "abandons": part(c["abandon_medical"] + c["abandon_volontaire"], len(lot)),
            "conseil": part(c["elimine_conseil"], len(lot)),
            "ambassadeurs": part(c["elimine_ambassadeurs"], len(lot)),
        })
    return {"repartition": repartition, "par_decennie": evolution}


def bloc_age(parts):
    out = []
    for bornes in TRANCHES:
        lot = [p for p in parts if p.get("age") and bornes[0] <= p["age"] <= bornes[1]]
        if not lot:
            continue
        survies = [p["_survie"] for p in lot if p["_survie"] is not None]
        finales = sum(1 for p in lot if p.get("sort") in ("vainqueur", "finaliste"))
        out.append({
            "tranche": LIBELLE_TRANCHE[bornes],
            "effectif": len(lot),
            "part_du_casting": part(len(lot), len(parts)),
            "survie_moyenne": arrondi(mean(survies)) if survies else None,
            "victoires": sum(1 for p in lot if p.get("sort") == "vainqueur"),
            "finales": finales,
            "taux_finale": part(finales, len(lot)),
        })
    return out


def bloc_saisons(saisons, parts):
    par_saison = defaultdict(list)
    for p in parts:
        par_saison[p["saison"]].append(p)
    out = []
    for s in saisons:
        if s.get("annulee"):
            continue
        lot = par_saison.get(s["id"], [])
        ages = [p["age"] for p in lot if p.get("age")]
        femmes = sum(1 for p in lot if p.get("genre") == "f")
        out.append({
            "id": s["id"], "numero": s.get("numero"), "titre": s.get("titre"),
            "annee": s.get("annee"), "speciale": bool(s.get("speciale")),
            "en_cours": bool(s.get("en_cours")),
            "pays": s.get("pays"), "lieu": s.get("lieu"),
            "duree_jours": s.get("duree_jours"),
            "effectif": len(lot),
            "age_moyen": arrondi(mean(ages)) if ages else None,
            "age_min": min(ages) if ages else None,
            "age_max": max(ages) if ages else None,
            "part_femmes": part(femmes, len(lot)) if lot else None,
            "abandons": sum(1 for p in lot
                            if p.get("sort") in ("abandon_medical", "abandon_volontaire")),
            "vainqueurs": s.get("vainqueurs") or [],
        })
    return out


def bloc_records(parts, personnes):
    v = [p for p in parts if p.get("sort") == "vainqueur" and p.get("age")]
    multi = sorted([g for g in personnes if g.get("nb_participations", 0) > 1],
                   key=lambda g: -g["nb_participations"])
    return {
        "plus_jeune_vainqueur": min(v, key=lambda p: p["age"]) if v else None,
        "plus_age_vainqueur": max(v, key=lambda p: p["age"]) if v else None,
        "multi_participants": [
            {"nom": g["nom"], "participations": g["nb_participations"],
             "saisons": g["participations"]}
            for g in multi[:12]],
        "nb_multi_participants": len(multi),
    }


def bloc_conseils(conseils, parts, par_saison):
    utiles = [c for c in conseils
              if not par_saison.get(c["saison"], {}).get("en_cours")]
    complets = [c for c in utiles if c.get("complet")]
    avec_decompte = [c for c in utiles if c.get("votes_exprimes")]

    unanimes = [c for c in avec_decompte
                if c["votes_contre"] and c["votes_contre"] == c["votes_exprimes"]]
    serres = [c for c in avec_decompte
              if c["votes_contre"] and c["votes_exprimes"]
              and c["votes_contre"] <= c["votes_exprimes"] / 2 + 0.5]

    voix_annulees = sum(1 for c in utiles for b in c["votes"] if b.get("annule"))
    conseils_collier = [c for c in utiles if any(b.get("annule") for b in c["votes"])]

    genre = {}
    idx = {(p["saison"], p["id"]): p for p in parts}
    for c in complets:
        for b in c["votes"]:
            v = idx.get((c["saison"], b["votant"]))
            t = idx.get((c["saison"], b["cible"]))
            if v and t and v.get("genre") and t.get("genre"):
                genre[(v["genre"], t["genre"])] = genre.get((v["genre"], t["genre"]), 0) + 1
    total_g = sum(genre.values())

    return {
        "conseils": len(utiles),
        "conseils_avec_decompte": len(avec_decompte),
        "conseils_complets": len(complets),
        "bulletins": sum(len(c["votes"]) for c in utiles),
        "bulletins_conseils_complets": sum(len(c["votes"]) for c in complets),
        "part_unanimes": part(len(unanimes), len(avec_decompte)),
        "part_serres": part(len(serres), len(avec_decompte)),
        "voix_annulees_par_collier": voix_annulees,
        "conseils_avec_collier_joue": len(conseils_collier),
        "vote_par_genre": [
            {"votant": g1, "cible": g2, "effectif": n, "part": part(n, total_g)}
            for (g1, g2), n in sorted(genre.items(), key=lambda x: -x[1])],
    }


def bloc_epreuves(epreuves, conseils, parts, saisons, par_saison):
    """Victoires d'epreuves, et ratios individuels.

    Le denominateur d'un ratio n'est pas le nombre d'epreuves de la saison mais
    le nombre d'epreuves individuelles disputees TANT QUE la personne etait en
    jeu. Il se calcule a partir de l'episode ou elle sort, lu dans les conseils.
    Une personne dont l'episode de sortie reste inconnu garde ses victoires mais
    n'entre dans aucun ratio : mieux vaut un classement plus court qu'un ratio
    fabrique.
    """
    if not epreuves:
        return {}

    # episode de sortie, par (saison, personne)
    sortie = {}
    for c in conseils or []:
        if c.get("elimine_rattache") and c.get("episode"):
            try:
                sortie[(c["saison"], c["elimine"])] = int(c["episode"])
            except (TypeError, ValueError):
                pass
    dernier_episode = {}
    for e in epreuves:
        d = dernier_episode.get(e["saison"], 0)
        dernier_episode[e["saison"]] = max(d, e.get("episode") or 0)
    for p in parts:
        if p.get("sort") in ("vainqueur", "finaliste"):
            sortie.setdefault((p["saison"], p["id"]), dernier_episode.get(p["saison"], 0))

    # epreuves individuelles par saison, ordonnees
    individuelles = defaultdict(list)
    for e in epreuves:
        if e.get("forme") == "individuelle" and e.get("episode"):
            individuelles[e["saison"]].append(e)

    victoires = Counter()
    victoires_type = defaultdict(Counter)
    for e in epreuves:
        for v in e.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                cle = (e["saison"], v["id"])
                victoires[cle] += 1
                victoires_type[cle][e["type"]] += 1

    index = {(p["saison"], p["id"]): p for p in parts}
    lignes = []
    for (sid, pid), gagnees in victoires.items():
        p = index.get((sid, pid))
        if not p:
            continue
        ep_sortie = sortie.get((sid, pid))
        disputees = None
        if ep_sortie:
            disputees = sum(1 for e in individuelles.get(sid, [])
                            if e["episode"] <= ep_sortie)
        lignes.append({
            "personne": p.get("nom_complet") or p.get("nom"),
            "id": pid,
            "saison": sid,
            "titre": par_saison.get(sid, {}).get("titre"),
            "annee": par_saison.get(sid, {}).get("annee"),
            "speciale": bool(par_saison.get(sid, {}).get("speciale")),
            "gagnees": gagnees,
            "immunites": victoires_type[(sid, pid)].get("immunite", 0),
            "conforts": victoires_type[(sid, pid)].get("confort", 0),
            "disputees": disputees,
            "ratio": part(gagnees, disputees) if disputees else None,
            "sort": p.get("sort"),
            "genre": p.get("genre"),
            "age": p.get("age"),
            "csp": p["_csp"],
        })

    SEUIL = 8
    classement = sorted([x for x in lignes if x["disputees"] and x["disputees"] >= SEUIL],
                        key=lambda x: (-(x["ratio"] or 0), -x["gagnees"]))

    cumul = Counter()
    for x in lignes:
        cumul[(x["id"], x["personne"])] += x["gagnees"]

    # profil des vainqueurs d'epreuves individuelles
    par_csp, par_genre, par_age = Counter(), Counter(), Counter()
    effectif_csp, effectif_genre, effectif_age = Counter(), Counter(), Counter()
    for x in lignes:
        if x["speciale"]:
            continue
        if x["csp"]:
            par_csp[x["csp"]] += x["gagnees"]
        if x["genre"]:
            par_genre[x["genre"]] += x["gagnees"]
        if x["age"]:
            t = tranche(x["age"])
            if t:
                par_age[t] += x["gagnees"]
    for p in parts:
        if par_saison.get(p["saison"], {}).get("speciale"):
            continue
        if p["_csp"]:
            effectif_csp[p["_csp"]] += 1
        if p.get("genre"):
            effectif_genre[p["genre"]] += 1
        if p.get("age") and tranche(p["age"]):
            effectif_age[tranche(p["age"])] += 1

    lib = libelles()
    return {
        "epreuves": len(epreuves),
        "saisons_couvertes": len({e["saison"] for e in epreuves}),
        "saisons_sans_donnee": sorted({s["id"] for s in saisons
                                       if not s.get("annulee")}
                                      - {e["saison"] for e in epreuves}),
        "collectives": sum(1 for e in epreuves if e.get("forme") == "collective"),
        "individuelles": sum(1 for e in epreuves if e.get("forme") == "individuelle"),
        "immunites": sum(1 for e in epreuves if e.get("type") == "immunite"),
        "conforts": sum(1 for e in epreuves if e.get("type") == "confort"),
        "seuil_classement": SEUIL,
        "classement_effectif": len(classement),
        "ratio_moyen": arrondi(mean([x["ratio"] for x in classement])) if classement else None,
        "classement_ratio": classement[:15],
        "meilleurs_cumuls": [{"personne": nom, "id": pid, "victoires": n}
                             for (pid, nom), n in cumul.most_common(15)],
        "par_metier": [
            {"code": c, "libelle": lib.get(c, c), "victoires": n,
             "aventuriers": effectif_csp[c],
             "victoires_par_aventurier": arrondi(n / effectif_csp[c], 2)
             if effectif_csp[c] else None}
            for c, n in par_csp.most_common()],
        "par_genre": [
            {"genre": g, "libelle": "Femmes" if g == "f" else "Hommes",
             "victoires": par_genre[g], "aventuriers": effectif_genre[g],
             "victoires_par_aventurier": arrondi(par_genre[g] / effectif_genre[g], 2)
             if effectif_genre[g] else None}
            for g in ("f", "h")],
        "par_age": [
            {"tranche": LIBELLE_TRANCHE[b], "victoires": par_age[LIBELLE_TRANCHE[b]],
             "aventuriers": effectif_age[LIBELLE_TRANCHE[b]],
             "victoires_par_aventurier": arrondi(
                 par_age[LIBELLE_TRANCHE[b]] / effectif_age[LIBELLE_TRANCHE[b]], 2)
             if effectif_age[LIBELLE_TRANCHE[b]] else None}
            for b in TRANCHES],
    }


# --- assemblage ------------------------------------------------------------

def main():
    saisons, parts, personnes, conseils, epreuves, par_saison = charger()
    classiques = perimetre(parts, avec_speciales=False)
    toutes = perimetre(parts, avec_speciales=True)

    stats = {
        "general": {
            "saisons_declarees": len(saisons),
            "saisons_diffusees": sum(1 for s in saisons if not s.get("annulee")),
            "saisons_classiques": sum(1 for s in saisons
                                      if not s.get("annulee") and not s.get("speciale")),
            "saisons_speciales": sum(1 for s in saisons
                                     if not s.get("annulee") and s.get("speciale")),
            "saisons_annulees": sum(1 for s in saisons if s.get("annulee")),
            "participations": len(parts),
            "personnes": len(personnes),
            "premiere_annee": min(s["annee"] for s in saisons if s.get("annee")),
            "derniere_annee": max(s["annee"] for s in saisons if s.get("annee")),
            "pays": len({s["pays"] for s in saisons if s.get("pays")}),
        },
        "vainqueurs": bloc_vainqueurs(classiques),
        "vainqueurs_toutes": bloc_vainqueurs(toutes),
        "couleurs": bloc_couleurs(classiques),
        "metiers": bloc_metiers(classiques),
        "metiers_toutes": bloc_metiers(toutes),
        "genre": bloc_genre(classiques),
        "sorties": bloc_sorties(classiques),
        "sorties_toutes": bloc_sorties(toutes),
        "age": bloc_age(classiques),
        "saisons": bloc_saisons(saisons, parts),
        "records": bloc_records(toutes, personnes),
        "conseils": bloc_conseils(conseils, parts, par_saison),
        "epreuves": bloc_epreuves(epreuves, conseils, parts, saisons, par_saison),
    }

    # les records renvoient des participations entieres : on n'en garde que l'utile
    for cle in ("plus_jeune_vainqueur", "plus_age_vainqueur"):
        p = stats["records"].get(cle)
        if p:
            stats["records"][cle] = {
                "nom": p.get("nom_complet") or p.get("nom"), "age": p.get("age"),
                "saison": p["saison"], "annee": p["_annee"],
                "titre": p["_saison"].get("titre"),
            }

    chemin = os.path.join(RACINE, "_data", "stats.yml")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(ENTETE)
        yaml.safe_dump(stats, f, allow_unicode=True, sort_keys=False, width=100)

    g = stats["general"]
    print(f"ecrit : {chemin}")
    print(f"  {g['saisons_diffusees']} saisons diffusees "
          f"({g['saisons_classiques']} classiques, {g['saisons_speciales']} speciales), "
          f"{g['participations']} participations, {g['personnes']} personnes")
    v = stats["vainqueurs"]
    print(f"  vainqueurs : age moyen {v['age_moyen']} ans, "
          f"{v['part_40_et_plus']} % de 40 ans et plus")
    c = stats["conseils"]
    print(f"  conseils : {c['conseils']} dont {c['conseils_complets']} complets, "
          f"{c['bulletins']} bulletins, {c['voix_annulees_par_collier']} voix annulees")
    e = stats.get("epreuves") or {}
    if e:
        print(f"  epreuves : {e['epreuves']} sur {e['saisons_couvertes']} saisons, "
              f"{e['individuelles']} individuelles, "
              f"{len(e['classement_ratio'])} ratios calculables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
