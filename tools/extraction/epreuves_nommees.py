#!/usr/bin/env python3
"""Le catalogue des epreuves recurrentes de Koh-Lanta, et sa limite.

Le site ecrivait que la nature d'une epreuve -- endurance, equilibre,
precision -- n'etait donnee nulle part de facon exploitable. C'est faux pour
la premiere moitie de la phrase : le wiki Fandom tient une page par epreuve
recurrente, avec son type et la liste des saisons ou elle a ete disputee.

C'est vrai pour la seconde. Ce catalogue ne dit pas dans QUEL EPISODE chaque
epreuve a eu lieu ; il ne donne que la saison, le vainqueur et le gain. Or un
aventurier gagne souvent plusieurs epreuves du meme type dans une saison :
l'appariement avec `_data/epreuves.yml`, qui est episode par episode, reste
alors indecidable. Ce script mesure ce taux de raccord au lieu de l'affirmer,
et il est bas.

    tools/atelier python3 tools/extraction/epreuves_nommees.py --ecrire
"""
import argparse
import collections
import json
import os
import re
import sys
import unicodedata

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
PAGES = os.path.join(RACINE, "specs", "sources", "epreuves")
SORTIE = os.path.join(RACINE, "_data", "epreuves_nommees.yml")

from parse_fandom import slug          # noqa: E402

RE_TABLE = re.compile(r"\{\|[^\n]*article-table.*?\n\|\}", re.S)
RE_LIEN = re.compile(r"\[\[\s*([^\]|]+?)\s*(?:\|\s*([^\]]*?)\s*)?\]\]")
RE_CHAMP = lambda nom: re.compile(r"\|\s*" + nom + r"\s*=\s*([^\n|]*)")

# Les mots que le wiki emploie pour qualifier une epreuve. Une page en porte
# souvent deux (« Rapidite, force ») : on les garde toutes les deux.
# La cle est sans accents -- elle sert a chercher dans un texte normalise ;
# le libelle, lui, est publie et prend les siens.
NATURES = {"statique": "Statique", "force": "Force", "precision": "Précision",
           "rapidite": "Rapidité", "equilibre": "Équilibre", "logique": "Logique",
           "reflexion": "Réflexion", "aquatique": "Aquatique",
           "endurance": "Endurance", "adresse": "Adresse"}


def sansaccents(t):
    t = unicodedata.normalize("NFD", t or "")
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


def propre(cellule):
    """Le texte d'une cellule : liens deroules, gras retire, modeles ecartes."""
    c = re.sub(r"<[^>]*>", "", cellule or "")
    c = RE_LIEN.sub(lambda m: m.group(2) or m.group(1), c)
    c = c.replace("'''", "").replace("''", "")
    c = re.sub(r"\{\{[^}]*\}\}", "", c)
    return re.sub(r"\s+", " ", c).strip(" .:-|")


def liens_ou_texte(cellule):
    """Les noms cites dans une cellule : les liens s'il y en a, sinon le texte."""
    liens = [(m.group(2) or m.group(1)).strip() for m in RE_LIEN.finditer(cellule or "")]
    if liens:
        return liens
    v = propre(cellule)
    return [x.strip() for x in re.split(r"\bet\b|,|&|/", v) if x.strip()] if v else []


def lignes_de_table(bloc):
    """Les lignes d'une table wiki, chacune rendue comme une liste de cellules."""
    sortie = []
    for morceau in re.split(r"\n\|-+[^\n]*", bloc):
        cellules = []
        for m in re.finditer(r"^\|(?!\})(.*)$", morceau, re.M):
            c = m.group(1)
            c = re.sub(r"^[^|\[\{]*\|(?!\|)", "", c)   # attributs de cellule
            cellules.append(c.strip())
        if cellules:
            sortie.append(cellules)
    return sortie


def natures(libelle):
    """Les mots-cles de nature contenus dans le champ « Type d'epreuve »."""
    t = sansaccents(libelle)
    return [n for n in NATURES if n in t]


def genre_du_gain(gain):
    """Confort ou immunite, deduit de ce qui a ete remporte."""
    if not gain:
        return None
    t = sansaccents(gain)
    return "immunite" if ("immunit" in t or "totem" in t or "collier" in t) else "confort"


def lire(saisons):
    par_titre = {}
    for s in saisons:
        if s.get("titre"):
            par_titre[re.sub(r"[^a-z0-9]", "", sansaccents(s["titre"]))] = s["id"]

    def saison_de(cellule):
        t = re.sub(r"^koh[- ]?lanta\s*:?\s*", "", sansaccents(propre(cellule)))
        return par_titre.get(re.sub(r"[^a-z0-9]", "", t))

    catalogue, rapport = [], []
    if not os.path.isdir(PAGES):
        return [], ["specs/sources/epreuves/ absent : lancer fetch_epreuves.py"]
    index = os.path.join(PAGES, "_titres.json")
    titres = json.load(open(index, encoding="utf-8")) if os.path.exists(index) else {}
    for fichier in sorted(os.listdir(PAGES)):
        if not fichier.endswith(".wiki"):
            continue
        texte = open(os.path.join(PAGES, fichier), encoding="utf-8").read()
        champ = RE_CHAMP("Nom de l'épreuve").search(texte)
        # Deux fiches ne remplissent pas le champ ; le titre de la page, lui,
        # est toujours la. On le garde en second recours plutot que de perdre
        # l'epreuve.
        nom = (champ.group(1).strip() if champ and champ.group(1).strip()
               else re.sub(r"^Épreuve (?:de |du |des |d')?", "",
                           titres.get(fichier, "")).strip())
        if not nom:
            rapport.append(f"{fichier} : pas de nom d'epreuve")
            continue
        typ = RE_CHAMP("Type d'épreuve").search(texte)
        apparitions = []
        for table in RE_TABLE.findall(texte):
            for cellules in lignes_de_table(table):
                if len(cellules) < 2:
                    continue
                sid = saison_de(cellules[0])
                if not sid:
                    continue
                gain = propre(cellules[2]) if len(cellules) > 2 else None
                apparitions.append({
                    "saison": sid,
                    "vainqueurs": liens_ou_texte(cellules[1]),
                    "gain": gain or None,
                    "genre": genre_du_gain(gain),
                })
        catalogue.append({
            "nom": nom,
            "type": (typ.group(1).strip() if typ else None),
            "natures": natures(typ.group(1) if typ else ""),
            "apparitions": len(apparitions),
            "saisons": sorted({a["saison"] for a in apparitions}),
            "detail": apparitions,
        })
    catalogue.sort(key=lambda x: (-x["apparitions"], x["nom"]))
    return catalogue, rapport


def mesurer_raccord(catalogue, saisons, parts, epreuves):
    """Combien d'epreuves relevees peuvent recevoir une nature, et pourquoi si peu."""
    par_prenom = collections.defaultdict(list)
    for p in parts:
        par_prenom[(p["saison"], slug(p["nom"]))].append(p)
    tribus = {(s["id"], slug(t["nom"])) for s in saisons for t in (s.get("tribus") or [])}

    personnes, collectives = collections.defaultdict(list), collections.defaultdict(list)
    for e in epreuves:
        for v in e.get("vainqueurs") or []:
            if v.get("type") == "personne" and v.get("id"):
                personnes[(e["saison"], v["id"], e.get("type"))].append(e)
            elif v.get("type") == "tribu" and v.get("libelle"):
                collectives[(e["saison"], slug(v["libelle"]), e.get("type"))].append(e)

    motifs = collections.Counter()
    raccordees = {}
    for entree in catalogue:
        for a in entree["detail"]:
            for nom in a["vainqueurs"]:
                cle = (a["saison"], slug(nom))
                if cle in tribus:
                    lots = collectives.get((a["saison"], slug(nom), a["genre"])) or []
                else:
                    candidats = par_prenom.get(cle)
                    if not candidats:
                        motifs["nom introuvable dans la saison"] += 1
                        continue
                    if len(candidats) > 1:
                        motifs["homonyme"] += 1
                        continue
                    lots = personnes.get((a["saison"], candidats[0]["id"], a["genre"])) or []
                if not lots:
                    motifs["aucune epreuve relevee qui corresponde"] += 1
                elif len(lots) > 1:
                    motifs["plusieurs epreuves possibles, sans episode pour trancher"] += 1
                else:
                    motifs["raccordee"] += 1
                    raccordees[id(lots[0])] = entree["natures"]
    individuelles = [e for e in epreuves if e.get("forme") == "individuelle"]
    return {
        "citations": sum(motifs.values()),
        "motifs": [{"motif": m, "effectif": n} for m, n in motifs.most_common()],
        "epreuves_relevees": len(epreuves),
        "epreuves_raccordees": len(raccordees),
        "part_raccordee": round(100.0 * len(raccordees) / len(epreuves), 1) if epreuves else None,
        "individuelles_relevees": len(individuelles),
        "individuelles_raccordees": sum(1 for e in individuelles if id(e) in raccordees),
    }


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ecrire", action="store_true")
    a = a.parse_args()

    lire_data = lambda n: yaml.safe_load(open(os.path.join(RACINE, "_data", n),
                                              encoding="utf-8"))
    saisons = lire_data("saisons.yml")
    parts = lire_data("participations.yml")
    epreuves = lire_data("epreuves.yml")

    catalogue, rapport = lire(saisons)
    raccord = mesurer_raccord(catalogue, saisons, parts, epreuves)

    par_nature = collections.Counter()
    for e in catalogue:
        for n in e["natures"] or ["non qualifiee"]:
            par_nature[n] += 1

    print(f"{len(catalogue)} epreuves nommees, "
          f"{sum(e['apparitions'] for e in catalogue)} apparitions")
    print("natures :", dict(par_nature.most_common()))
    print(f"raccord avec _data/epreuves.yml : {raccord['epreuves_raccordees']} sur "
          f"{raccord['epreuves_relevees']} ({raccord['part_raccordee']} %) ; "
          f"individuelles {raccord['individuelles_raccordees']}/"
          f"{raccord['individuelles_relevees']}")
    for m in raccord["motifs"]:
        print(f"    {m['motif']:52s} {m['effectif']}")
    for r in rapport:
        print("  " + r)

    sortie = {
        "source": "https://kohlanta.fandom.com/fr/wiki/Catégorie:Épreuves",
        "epreuves": [{k: v for k, v in e.items() if k != "detail"} for e in catalogue],
        "nb_epreuves": len(catalogue),
        "nb_apparitions": sum(e["apparitions"] for e in catalogue),
        "par_nature": [{"nature": n, "libelle": NATURES.get(n, "Non qualifiée"),
                        "effectif": c} for n, c in par_nature.most_common()],
        "raccord": raccord,
    }
    if a.ecrire:
        with open(SORTIE, "w", encoding="utf-8") as f:
            f.write("# Fichier genere par tools/extraction/epreuves_nommees.py.\n"
                    "# Ne pas editer a la main : toute modification sera ecrasee.\n")
            yaml.safe_dump(sortie, f, allow_unicode=True, sort_keys=False, width=100)
        print(f"\necrit : {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
