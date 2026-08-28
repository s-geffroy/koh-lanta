#!/usr/bin/env python3
"""Compare les prenoms des aventuriers a ceux de la France entiere.

    tools/atelier python3 tools/extraction/prenoms_insee.py --ecrire

LA QUESTION. « Sebastien » revient sept fois a Koh-Lanta. Est-ce beaucoup ?
Sans point de comparaison, non : c'etait un prenom tres donne dans les annees
1970, et les aventuriers sont nes dans ces annees-la. La seule reponse qui
tienne est un ecart a l'attendu.

LA METHODE. L'annee de naissance de chaque aventurier se deduit de l'annee de
sa saison moins son age. Le fichier des prenoms de l'INSEE donne, pour chaque
prenom, chaque sexe et chaque annee, le nombre de naissances. On calcule donc
pour chaque prenom :

    attendu = somme, sur les aventuriers, de p(prenom | annee de naissance, sexe)

c'est-a-dire le nombre d'aventuriers qui porteraient ce prenom si le casting
etait un echantillon ordinaire de la population francaise nee ces annees-la.
L'indice de sur-representation est observe / attendu.

CE QUE LA METHODE NE SAIT PAS FAIRE, et qu'il faut dire :
  * l'age est celui annonce au tournage, pas une date de naissance : l'annee
    deduite peut etre fausse d'un an ;
  * l'INSEE arrondit ses effectifs au multiple de 5 le plus proche ;
  * les prenoms trop rares sont verses dans un seul sac, `_PRENOMS_RARES` :
    pour eux, l'attendu n'est pas calculable, ils sont mis a part ;
  * les aventuriers nes hors de France ne relevent pas de ce fichier.

Le sous-ensemble effectivement lu est ecrit dans specs/sources/insee/ : c'est
la preuve de provenance, et elle permet de refaire le calcul sans redemander
les 4 Mo a l'INSEE.
"""
import csv
import io
import os
import sys
import unicodedata
import urllib.request
import zipfile
from collections import defaultdict

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
EXTRAIT = os.path.join(RACINE, "specs", "sources", "insee", "prenoms-nat-extrait.csv")

# Fichier des prenoms, INSEE, licence ouverte v2. L'adresse porte le millesime :
# la verifier sur https://www.insee.fr/fr/statistiques/8595130 avant de la
# changer, l'INSEE republie chaque annee sous une nouvelle URL.
SOURCE = "https://www.insee.fr/fr/statistiques/fichier/8595130/prenoms-2025-nat_csv.zip"

ENTETE = """# ATTENTION : fichier genere. Ne pas editer a la main.
#
# Les prenoms des aventuriers compares a ceux de la France entiere, nee les
# memes annees. Produit par tools/extraction/prenoms_insee.py a partir du
# fichier des prenoms de l'INSEE (licence ouverte v2) :
#
#     https://www.insee.fr/fr/statistiques/8595130
#
# `attendu` est le nombre d'aventuriers qui porteraient ce prenom si le casting
# etait un echantillon ordinaire des naissances francaises de ces annees-la.
# `indice` est observe / attendu : 1 signifie « exactement la France ».
#
#     tools/atelier python3 tools/extraction/prenoms_insee.py --ecrire
#
"""


def cle(prenom):
    """Forme de comparaison : majuscules, sans accents, sans traits d'union.

    L'INSEE ecrit MARIE-CLAUDE, nos sources Marie-Claude, et parfois Marie
    Claude. On aligne les trois.
    """
    t = unicodedata.normalize("NFD", prenom or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return t.upper().replace("-", " ").replace("'", " ").strip()


def telecharger():
    print(f"telechargement : {SOURCE}")
    r = urllib.request.Request(SOURCE, headers={"User-Agent": "koh-lanta/1.0"})
    brut = urllib.request.urlopen(r, timeout=180).read()
    z = zipfile.ZipFile(io.BytesIO(brut))
    nom = z.namelist()[0]
    print(f"  {len(brut)} octets, {nom}")
    return z.read(nom).decode("utf-8", "replace")


def aventuriers():
    """(prenom, sexe INSEE, annee de naissance) pour chaque participation."""
    parts = yaml.safe_load(open(os.path.join(RACINE, "_data", "participations.yml")))
    saisons = {s["id"]: s for s in yaml.safe_load(
        open(os.path.join(RACINE, "_data", "saisons.yml")))}
    out = []
    for p in parts:
        annee = saisons.get(p["saison"], {}).get("annee")
        if not annee or not p.get("age") or not p.get("genre"):
            continue
        out.append({
            "id": p["id"],
            "prenom": p["nom"],
            "cle": cle(p["nom"]),
            "sexe": 2 if p["genre"] == "f" else 1,
            "naissance": annee - p["age"],
        })
    return out


def lire_insee(texte, cles, annees):
    """Ne garde que nos prenoms, nos annees -- plus le total annuel par sexe.

    Le total est indispensable : c'est le denominateur de p(prenom | annee).
    Il se calcule sur TOUTES les lignes, y compris les prenoms qu'on ne garde
    pas, sinon la probabilite serait celle d'un monde ou seuls nos prenoms
    existent.
    """
    lignes = []
    total = defaultdict(int)
    lecteur = csv.reader(io.StringIO(texte), delimiter=";")
    entete = next(lecteur)
    assert entete[:5] == ["sexe", "prenom", "periode", "valeur", "rang"], entete
    for sexe, prenom, periode, valeur, _rang in lecteur:
        if not periode.isdigit():
            continue
        an = int(periode)
        if an not in annees:
            continue
        try:
            n = int(valeur)
        except ValueError:
            continue
        total[(int(sexe), an)] += n
        if cle(prenom) in cles:
            lignes.append((int(sexe), prenom, an, n))
    return lignes, total


def main():
    gens = aventuriers()
    annees = {g["naissance"] for g in gens}
    cles = {g["cle"] for g in gens}
    print(f"aventuriers datables : {len(gens)}  "
          f"({min(annees)}-{max(annees)}, {len(cles)} prenoms distincts)")

    if os.path.exists(EXTRAIT) and "--recharger" not in sys.argv:
        print(f"lecture de l'extrait deja constitue : {EXTRAIT}")
        lignes, total = [], defaultdict(int)
        with open(EXTRAIT, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["prenom"] == "_TOTAL":
                    total[(int(r["sexe"]), int(r["annee"]))] = int(r["naissances"])
                else:
                    lignes.append((int(r["sexe"]), r["prenom"],
                                   int(r["annee"]), int(r["naissances"])))
    else:
        lignes, total = lire_insee(telecharger(), cles, annees)
        os.makedirs(os.path.dirname(EXTRAIT), exist_ok=True)
        with open(EXTRAIT, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["sexe", "prenom", "annee", "naissances"])
            for s, an in sorted(total):
                w.writerow([s, "_TOTAL", an, total[(s, an)]])
            for r in sorted(lignes):
                w.writerow([r[0], r[1], r[2], r[3]])
        print(f"extrait ecrit : {EXTRAIT}  ({len(lignes)} lignes + totaux)")

    # p(prenom | annee, sexe)
    compte = defaultdict(int)
    for sexe, prenom, an, n in lignes:
        compte[(sexe, cle(prenom), an)] += n

    observe = defaultdict(int)
    affichage = {}
    for g in gens:
        observe[g["cle"]] += 1
        affichage.setdefault(g["cle"], g["prenom"])

    # L'attendu d'un prenom se somme sur TOUT le casting, pas sur ses seuls
    # porteurs : la question est « combien d'aventuriers, parmi les 639,
    # s'appelleraient ainsi si le casting etait un echantillon ordinaire ».
    # Le sommer sur les porteurs ne repondrait qu'a « combien d'Alexandra
    # parmi les Alexandra », ce qui ne veut rien dire.
    attendu = defaultdict(float)
    for k in observe:
        s = 0.0
        for g in gens:
            d = total.get((g["sexe"], g["naissance"]), 0)
            if d:
                s += compte.get((g["sexe"], k, g["naissance"]), 0) / d
        attendu[k] = s

    out = []
    for k, obs in observe.items():
        att = attendu.get(k, 0.0)
        # Sous un attendu de 0,05, l'indice explose sans rien signifier : un
        # seul porteur suffirait a afficher un facteur 40. Ces prenoms-la sont
        # introuvables au fichier national sur la periode -- ils sont signales
        # comme tels, jamais classes.
        jamais = att < 0.05
        out.append({
            "prenom": affichage[k],
            "observe": obs,
            "attendu": round(att, 3),
            "indice": None if jamais else round(obs / att, 1),
            "absent_du_fichier": jamais,
        })
    out.sort(key=lambda x: (x["absent_du_fichier"], -(x["indice"] or 0), x["prenom"]))

    classes = [x for x in out if not x["absent_du_fichier"]]
    absents = [x for x in out if x["absent_du_fichier"]]
    print(f"\nprenoms classes  : {len(classes)}")
    print(f"absents du fichier national : {len(absents)} "
          f"({sum(x['observe'] for x in absents)} aventuriers)")
    print("\nles plus sur-representes :")
    for x in classes[:10]:
        print(f"  {x['prenom']:<16} observe {x['observe']:>2}  "
              f"attendu {x['attendu']:>5.2f}  indice x{x['indice']}")
    print("\nles plus sous-representes (au moins 2 porteurs) :")
    for x in [c for c in classes if c["observe"] >= 2][-6:]:
        print(f"  {x['prenom']:<16} observe {x['observe']:>2}  "
              f"attendu {x['attendu']:>5.2f}  indice x{x['indice']}")

    if "--ecrire" in sys.argv:
        chemin = os.path.join(RACINE, "_data", "prenoms.yml")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(ENTETE)
            yaml.safe_dump({
                "periode": {"debut": min(annees), "fin": max(annees)},
                "aventuriers_datables": len(gens),
                "prenoms": out,
            }, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
