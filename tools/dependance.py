#!/usr/bin/env python3
"""Les conseils d'une meme saison ne sont pas independants : ce que cela coute.

    tools/atelier python3 tools/dependance.py            # calcule et resume
    tools/atelier python3 tools/dependance.py --ecrire   # ecrit _data/dependance.yml

A lancer APRES tools/build_stats.py : les tests de reference sont ceux du
registre publie (_data/stats.yml).

LA QUESTION. Les tests de permutation du registre rebattent le hasard conseil
par conseil -- l'elimine, le bulletin, la cible -- comme si chaque conseil
etait une experience a part. Ce n'en est pas une : dans une saison, ce sont
les memes joueurs, les memes alliances et les memes rancunes d'un conseil a
l'autre. Si la saison entiere penche d'un cote, ses quinze conseils penchent
ensemble, et le test les compte comme quinze preuves. L'incertitude est donc
sous-estimee. De combien, aucun test ne le disait.

LA METHODE. Un jackknife par saison. Pour chaque test, on recalcule l'ecart
entre l'observe et le hasard en retirant une saison entiere, puis une autre,
une fois par saison terminee. La dispersion de ces ecarts donne une
incertitude qui ne suppose RIEN sur ce qui se passe a l'interieur d'une
saison : les conseils d'une saison peuvent etre aussi lies qu'on voudra.
Seule hypothese restante, que les saisons soient independantes entre elles --
elles ont des castings distincts, a quelques revenants pres.

  * `facteur` : l'incertitude par saison, divisee par celle du hasard conseil
    par conseil. A 1, la dependance ne change rien ; a 2, le test etait deux
    fois trop sur de lui.
  * `z_saison` : l'ecart publie, rapporte a l'incertitude par saison.
  * `p_saison` : sa p bilaterale, loi de Student a (saisons - 1) degres.
  * la correction de Benjamini-Hochberg est REFAITE sur la famille entiere
    (registre et coefficients), ces p a la place des p de permutation :
    c'est elle qui dit quel test retenu le reste.

CE QUE LA METHODE NE FAIT PAS. Elle ne remplace pas le test publie : elle en
mesure la robustesse. Le hasard de chaque recalcul est tire sur TIRAGES
tirages seulement, avec la meme graine, et ce bruit gonfle un peu
l'incertitude : le resultat est prudent, pas flatteur. Le modele de force est
estime une fois sur tout le jeu, et pas a chaque saison retiree.
"""
import os
import sys

import numpy as np
from scipy import stats as lois

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_stats as B  # noqa: E402
import donnees  # noqa: E402
import modeles as M  # noqa: E402
import prevision  # noqa: E402

TIRAGES = 4000
SORTIE = os.path.join(B.RACINE, "_data", "dependance.yml")
ENTETE = """# ATTENTION : fichier genere par tools/dependance.py. Ne pas editer a la main.
# La dependance entre conseils d'une meme saison : un jackknife par saison sur
# chaque test du registre qui rebat le hasard conseil par conseil.
"""

# Les tests dont l'unite n'est pas le conseil : la dependance entre conseils
# d'une saison ne les concerne pas. Ils le disent sur /methode/.
#
# L'HOMOPHILIE N'EST PAS UN TEST AU CONSEIL. Son hasard est deja un bootstrap
# de SAISONS (modeles.homophilie) : son incertitude tient compte de la
# dependance a l'interieur d'une saison. Le passer au jackknife le mesurait
# deux fois -- et, a N_BOOTSTRAP reduit, le bruit du bootstrap gonflait ses
# facteurs (x1,65 publie le 3 nov. pour un test qui vaut x1,01 a 2000
# tirages). Il est donc range ici, et `ecarts` ne le recalcule plus.
UNITE_AUTRE = {
    "homophilie": "une saison : le hasard tire deja des saisons entieres",
    "casting": "une saison et son casting",
    "geographie": "une participation et son departement",
    "audience": "une saison",
    "ruptures": "une saison",
    "pronostic": "une saison et son vainqueur",
    "classement": "un joueur, sur toute sa carriere",
    "finale": "une finale par saison",
}


def reduire():
    """Le hasard de chaque recalcul, a TIRAGES tirages ; les intervalles,
    inutiles ici, au minimum."""
    M.N_PERMUTATIONS = TIRAGES
    M.N_PERMUTATIONS_BULLETINS = TIRAGES
    M.N_PERMUTATIONS_ALLIANCES = TIRAGES
    M.N_BOOTSTRAP = 20
    M.N_BOOTSTRAP_GRAPPES = 2
    M.N_BOOTSTRAP_FORCE = 2


def sans(par_saison, parts, conseils, epreuves, saison):
    """Le jeu de donnees, une saison retiree."""
    return ({k: v for k, v in par_saison.items() if k != saison},
            [p for p in parts if p["saison"] != saison],
            [c for c in conseils if c["saison"] != saison],
            [e for e in epreuves if e.get("saison") != saison])


def ecarts(par_saison, parts, conseils, epreuves, f):
    """observe - attendu de chaque test rebattu conseil par conseil."""
    fu = M.fusion(par_saison, parts, conseils, epreuves)
    blocs = (
        M.alliances(par_saison, parts, conseils),
        M.trahison(par_saison, parts, conseils),
        M.decimation(par_saison, parts, conseils, epreuves),
        M.avant_apres(par_saison, parts, conseils, epreuves, f, fu),
        M.conditionnelles(par_saison, parts, conseils),
        M.autour_du_feu(par_saison, parts, conseils, epreuves, fu),
        M.pire_place(par_saison, parts, conseils, epreuves),
        M.age_au_conseil(par_saison, parts, conseils, epreuves, fu),
        M.tenant_du_titre(par_saison, parts, conseils, epreuves, f),
    )
    sortie = {}
    for bloc in blocs:
        tests = list(bloc.get("tests") or []) + ([bloc["test"]] if bloc.get("test") else [])
        for t in tests:
            n = t.get("nulle") or {}
            if n.get("observe") is not None and n.get("moyenne_nulle") is not None:
                sortie[t["cle"]] = n["observe"] - n["moyenne_nulle"]
    return sortie


def prevision_par_conseil(par_saison, parts, conseils, epreuves):
    """Le rang du vrai elimine, conseil par conseil, et la saison de chacun.
    Le hasard vaut 0,5 exactement : pas de tirage a refaire."""
    brut = prevision.lignes(par_saison, parts, conseils, epreuves,
                            M.fusion(par_saison, parts, conseils, epreuves))
    colonnes = next(c for cle, _, c, _ in prevision.JEUX if cle == "jeu")
    r = prevision.hors_echantillon(brut, colonnes)
    return np.array(r["rang_moyen"]), np.array(r["saisons"])


def jackknife(complet, partiels):
    """Erreur-type jackknife, sur les seules saisons qui comptent pour ce test :
    une saison dont le retrait ne change rien n'y apporte aucune donnee."""
    valeurs = [v for v in partiels if v is not None and abs(v - complet) > 1e-9]
    s = len(valeurs)
    if s < 3:
        return None, s
    v = np.array(valeurs)
    return float(np.sqrt((s - 1) / s * np.sum((v - v.mean()) ** 2))), s


def complements(modeles):
    """Les coefficients de regression corriges avec le registre : tout noeud
    portant `p` et `p_ajustee` qui n'est pas un test du registre."""
    cles = {t["cle"] for t in modeles["registre"]}
    trouves = []

    def ramasser(noeud, chemin):
        if isinstance(noeud, dict):
            if noeud.get("cle") in cles and "nulle" in noeud:
                return
            if isinstance(noeud.get("p"), (int, float)) and "p_ajustee" in noeud \
                    and "avec_bandeau" not in chemin:
                trouves.append(noeud)
            for cle, valeur in noeud.items():
                if cle not in ("registre", "nulle"):
                    ramasser(valeur, chemin + (cle,))
        elif isinstance(noeud, list):
            for valeur in noeud:
                ramasser(valeur, chemin)

    for cle, bloc in modeles.items():
        if cle != "registre":
            ramasser(bloc, (cle,))
    return trouves


def main():
    stats = donnees.charger(open(os.path.join(B.RACINE, "_data", "stats.yml"), encoding="utf-8"))
    modeles = stats["modeles"]
    registre = modeles["registre"]
    comp = complements(modeles)
    if len(comp) != modeles["coefficients_corriges"]:
        sys.exit(f"famille introuvable : {len(comp)} coefficients au lieu de "
                 f"{modeles['coefficients_corriges']}")

    reduire()
    _, parts, _, conseils, epreuves, _, _, par_saison = B.charger()
    f = M.force(par_saison, parts, conseils, epreuves)
    complet = ecarts(par_saison, parts, conseils, epreuves, f)
    rangs, de_la_saison = prevision_par_conseil(par_saison, parts, conseils, epreuves)

    saisons = sorted({c["saison"] for c in conseils})
    partiels = {}
    for i, s in enumerate(saisons, 1):
        partiels[s] = ecarts(*sans(par_saison, parts, conseils, epreuves, s), f)
        print(f"  {i}/{len(saisons)} sans {s}", flush=True)

    # Une saison qui ne change aucun test (l'edition en cours, exclue de tous
    # les modeles) ne compte pas dans le jackknife : on ne l'annonce pas.
    informatives = [s for s in saisons
                    if any(abs(v - complet.get(k, v)) > 1e-9 for k, v in partiels[s].items())]

    lignes = []
    for t in registre:
        cle = t["cle"]
        ligne = {"cle": cle, "libelle": t["libelle"], "origine": t["origine"],
                 "z": t["ecart_types"], "p": t["p"], "p_ajustee": t["p_ajustee"],
                 "retenu": t["retenu"]}
        if cle == "prevision_conseil":
            garde = [float(rangs[de_la_saison != s].mean()) - 0.5 for s in sorted(set(de_la_saison))]
            se, n = jackknife(float(rangs.mean()) - 0.5, garde)
        elif t["origine"] in UNITE_AUTRE or cle not in complet:
            ligne["unite"] = UNITE_AUTRE.get(t["origine"], "autre")
            lignes.append(ligne)
            continue
        else:
            se, n = jackknife(complet[cle], [partiels[s].get(cle) for s in saisons])
        if se is None or not se:
            ligne["unite"] = "trop peu de saisons pour mesurer"
            lignes.append(ligne)
            continue
        z = (t["nulle"]["observe"] - t["nulle"]["moyenne_nulle"]) / se
        ligne.update({
            "saisons": n,
            "facteur": round(se / t["ecart_type_nul"], 2) if t.get("ecart_type_nul") else None,
            "z_saison": round(z, 2),
            "p_saison": round(float(2 * lois.t.sf(abs(z), n - 1)), 4),
        })
        lignes.append(ligne)

    # La famille entiere, les p par saison a la place des p de permutation.
    p_saison = [l.get("p_saison", l["p"]) for l in lignes]
    ajustees = M.benjamini_hochberg(p_saison + [x["p"] for x in comp])
    controle = M.benjamini_hochberg([l["p"] for l in lignes] + [x["p"] for x in comp])
    for l, pa, pc in zip(lignes, ajustees, controle):
        if abs(pc - l["p_ajustee"]) > 5e-4:
            sys.exit(f"{l['cle']} : la famille ne redonne pas la p ajustee publiee "
                     f"({pc:.4f} contre {l['p_ajustee']})")
        if "p_saison" in l:
            l["p_ajustee_saison"] = round(pa, 4)
            if round(pa, 4) == 0:
                # Arrondie a 4 decimales, elle s'afficherait « 0 ».
                l["p_ajustee_saison_texte"] = "< 0,0001"
            l["retenu_saison"] = bool(pa < 0.05)
            l["bascule"] = l["retenu"] and not l["retenu_saison"]

    mesures = [l for l in lignes if "facteur" in l and l["facteur"] is not None]
    retenus = [l for l in mesures if l["retenu"]]
    resultat = {
        "tirages": TIRAGES,
        "tirages_texte": f"{TIRAGES:,}".replace(",", " "),
        "saisons": len(informatives),
        "mesures": len(mesures),
        "retenus_mesures": len(retenus),
        "tiennent": sum(1 for l in retenus if l["retenu_saison"]),
        "tombent": [l["libelle"] for l in retenus if not l["retenu_saison"]],
        "facteur_median": round(float(np.median([l["facteur"] for l in mesures])), 2),
        "facteur_max": max(l["facteur"] for l in mesures),
        "tests": sorted(lignes, key=lambda l: (-(l.get("facteur") or 0), l["cle"])),
    }

    print(f"\n{len(mesures)} tests mesures, facteur median {resultat['facteur_median']}")
    for l in resultat["tests"]:
        if "facteur" in l:
            print(f"  {'R' if l['retenu'] else ' '}{'R' if l.get('retenu_saison') else ' '} "
                  f"{l['cle']:28} x{l['facteur']:<5} z {l['z']} -> {l['z_saison']}  "
                  f"p_aj {l['p_ajustee']} -> {l['p_ajustee_saison']}  ({l['saisons']} saisons)")
    print("tombent :", ", ".join(resultat["tombent"]) or "aucun")

    if "--ecrire" in sys.argv:
        with open(SORTIE, "w", encoding="utf-8") as fichier:
            fichier.write(ENTETE)
            donnees.ecrire(resultat, fichier, affichage=True, allow_unicode=True,
                           sort_keys=False, width=100)
        print(f"ecrit : {SORTIE}")


if __name__ == "__main__":
    main()
